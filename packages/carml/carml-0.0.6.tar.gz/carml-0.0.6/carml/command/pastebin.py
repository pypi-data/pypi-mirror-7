from __future__ import print_function
import sys
import time
import functools

import zope.interface
from twisted.python import usage, log
from twisted.plugin import IPlugin
from twisted.internet import reactor
from twisted.internet import defer
from twisted.internet.endpoints import serverFromString
from twisted.web.http import HTTPChannel
from twisted.web.static import Data
from twisted.web.resource import Resource
from twisted.web.server import Site

from carml.interface import ICarmlCommand
from carml import util
import txtorcon
from txtorcon import TCPHiddenServiceEndpoint


class PasteBinOptions(usage.Options):
    """
    """

    optFlags = [
        ('dry-run', 'd', 'Test locally; no Tor launch.'),
        ('once', '', 'Same as --count=1.'),
    ]

    optParameters = [
        ('file', 'f', None, 'Filename to use as input (instead of stdin)'),
        ('count', 'n', None, 'Number of requests to serve.', int),
    ]


class _PasteBinHTTPChannel(HTTPChannel):
    def connectionMade(self):
        HTTPChannel.connectionMade(self)
        self.site._got_client()

    def connectionLost(self, reason):
        HTTPChannel.connectionLost(self, reason)
        self.site._lost_client()


class PasteBinSite(Site):
    """
    See https://github.com/habnabit/polecat/blob/master/polecat.py for
    the inspriation behind this.

    This class exists so we can count active connections and support a
    command-line option for serving a particular number of
    requests. We need to wait until pending data is written on any
    valid connections that are still active when we reach our limit.
    """

    protocol = _PasteBinHTTPChannel

    def __init__(self, *args, **kw):
        self.active_clients = 0
        self.active_requests = set()
        self._max_requests = kw['max_requests']
        del kw['max_requests']
        self._request_count = 0
        self._stopping_deferred = None
        Site.__init__(self, *args, **kw)

    def getResourceFor(self, request):
        "Override Site so we can track active requests"
        if request.requestHeaders.hasHeader('user-agent'):
            ua = ' '.join(request.requestHeaders.getRawHeaders('user-agent'))
            print('{}: Serving request to User-Agent "{}".'.format(time.asctime(), ua))
        else:
            print('{}: Serving request with no incoming User-Agent header.'.format(time.asctime()))

        # track requsts currently being serviced, so we can nicely
        # shut them off
        self.active_requests.add(request)
        request.notifyFinish().addBoth(self._forget_request, request)

        # see if we've reached the maximum requests
        self._request_count += 1
        if self._max_requests is not None:
            if self._request_count >= self._max_requests:
                d = self.gracefully_stop()
                d.addBoth(lambda x: reactor.stop())

        # call through to parent
        return Site.getResourceFor(self, request)

    def _forget_request(self, request, _):
        self.active_requests.discard(request)

    def _got_client(self):
        self.active_clients += 1

    def _lost_client(self):
        self.active_clients -= 1
        if self.active_clients <= 0 and self._stopping_deferred:
            self._stopping_deferred.callback(None)
            self._stopping_deferred = None

    def gracefully_stop(self):
        "Returns a Deferred that fires when all clients have disconnected."
        if not self.active_clients:
            return defer.succeed(None)
        for request in self.active_requests:
            request.setHeader('connection', 'close')
        self._stopping_deferred = defer.Deferred()
        return self._stopping_deferred


class PasteBinCommand(object):
    """
    Read stdin and then post it as text/plain at a freshly-created
    hidden-service.
    """
    zope.interface.implements(ICarmlCommand, IPlugin)

    name = 'pastebin'
    help_text = """Put stdin (or a file) on a fresh hidden-service easily."""
    build_state = False
    controller_connection = False
    options_class = PasteBinOptions

    def validate(self, options, mainoptions):
        "ICarmlCommand API"
        if options['count'] is not None and options['count'] < 1:
            raise RuntimeError("Count should be 1 or greater.")

    def progress(self, percent, tag, message):
        prog = util.pretty_progress(percent)
        print('\b' * len(prog), end='')
        if percent == 100:
            print(util.colors.green('connected.      '))
        else:
            print(prog, end='')
        sys.stdout.flush()

    @defer.inlineCallbacks
    def run(self, options, mainoptions, connection):
        "ICarmlCommand API"

        to_share = None
        self.progress_dots = 0
        if options['file']:
            to_share = open(options['file'], 'r').read()
        else:
            to_share = sys.stdin.read()

        print(len(to_share), "bytes to share.")
        sys.stdout.flush()
        if options['dry-run']:
            print('Not launching a Tor, listening on 8899.')
            ep = serverFromString(reactor, 'tcp:8899:interface=127.0.0.1')
        else:
            print("Launching Tor:", util.pretty_progress(0), end='')
            ep = TCPHiddenServiceEndpoint.global_tor(reactor, 80)
            txtorcon.IProgressProvider(ep).add_progress_listener(self.progress)

        root = Resource()
        data = Data(to_share, 'text/plain')
        root.putChild('', data)

        count = 1 if options['once'] else options['count']
        port = yield ep.listen(PasteBinSite(root, max_requests=count))
        host = port.getHost()
        if options['dry-run']:
            print("Try it locally via http://127.0.0.1:8899")
        else:
            print("People using Tor Browser Bundle can find your paste at (once the descriptor uploads):")
            print("\n   http://{0}\n".format(host.onion_uri))
            if not count:
                print("Type Control-C to stop serving and shut down the Tor we launched.")
            print("If you wish to keep the hidden-service keys, they're in (until we shut down):")
            print(ep.hidden_service_dir)

        # FIXME this is colossally fragile (i.e. parsing INFO
        # messages) but I can't think of or find a better way to
        # determine "yes, we've uploaded our descriptor 1 time"
        # "right way" is probably a new event or something in Tor
        if not options['dry-run']:
            print('Awaiting descriptor upload...')
            # look for log messages indicating our hidden-sevice descriptor is published
            config = yield txtorcon.get_global_tor(reactor)
            got_upload = defer.Deferred()

            def find_upload(msg):
                if not got_upload.called and 'Uploaded rendezvous descriptor' in msg:
                    got_upload.callback(msg)
            config.protocol.add_event_listener('INFO', find_upload)
            m = yield got_upload
            print('Descriptor uploaded; hidden-service should be reachable.')

        reactor.addSystemEventTrigger('before', 'shutdown',
                                      lambda: print(util.colors.red('Shutting down.')))
        # we never callback() on this, so we serve forever
        d = defer.Deferred()
        yield d

# the IPlugin/getPlugin stuff from Twisted picks up any object from
# here than implements ICarmlCommand -- so we need to instantiate one
cmd = PasteBinCommand()
