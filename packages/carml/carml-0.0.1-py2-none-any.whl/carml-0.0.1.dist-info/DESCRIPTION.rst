carml
=====

``carml`` is a command-line tool to query and control a running Tor
(including Tor Browser Bundle).

It is written in Python and uses Tor's control-port and cookie
authentication via the `txtorcon library <https://txtorcon.readthedocs.org>`_.

The name is supposed to conjure up visions of onions, which is kind-of
the generic name for Tor-related things (hence avoiding the "Tor"
trademark).

.. warning::
   This is early-Alpha code. *DO NOT USE for production*
   needs. "Release early, release often" gives you a chance to try
   things out at the expense of the very real possibility of serious
   bugs! (Please report them using github)


Overview
--------

``carml`` works via sub-commands, not unlike programs such as
"git". There are "shared" options -- which any subcommand can take --
and also options specific to subcommands. In general a command will
look like::

   carml [shared options] subcommand [specific options]

``carml help`` will explain all the subcommands and general
options. ``carml help subcommand`` explains that sub-command's
options. See below for instructions on how to extend ``carml`` with
new subcommands.


Releases
--------

``carml`` is in active, early development; don't expect options to
stay the same. If something doesn't work, it could be a bug. Maybe
it's even a feature!

If you believe you've found one (a bug, not a feature), use GitHub to
file a report. You can also find the author "meejah" on `#tor-dev
<irc://irc.oftc.net/tor-dev>`_ in the OFTC network. Pull-requests,
feature-requests, code-reviews are all welcome! Or, contact the author
via `meejah.ca <https://meejah.ca>_


General Options
---------------

All subcommands understand the following general options.

``--connect, -c``
    A string telling ``carml`` how to connect to Tor. This uses
    Twisted client endpoint strings or an ip:port pair. By default we
    use localhost:9151 (what Tor Browser Bundle currently ships
    with). Examples::

      -c tcp:localhost:9151
      --connect unix:/var/run/tor/control
      -c localhost:9051

``--password, -p``
    If you're using password authentication, you'll need this
    option. Cookie authentication is more convenient, and recommended.

``--timestamps, -t``
    Prepend timestamps to the beginning of lines. Note that you may
    also turn on ``twistd``s logging capabilities if you want "real"
    syslog logging.

``--color, -C``
    Colorize the output with ANSI commands. ``auto``, ``always`` or
    ``never`` accepted. ``auto`` is the default which only does color
    if you're currently using a TTY.

``--no-color, -n``
    Equivalent to ``--color=never``

``--help``


Sub-Command: monitor
--------------------

Especially with the ``--follow, -f`` option, this command allows you to
see what Tor is up to. Without the option, it dumps the state once and
exits. You can ask for the status of:

 * ``--streams, -s``
 * ``--circuits, -c``
 * ``--addr, -a``: address mappings
 * ``--guards, -g``: current entry guards
 * ``--verbose, -v``: more information (e.g. AS#, geodata for routers)

For example, ``carml monitor -scagf`` will dump everything and then
contiuously monitor Tor for new events. When monitoring, it simply
prints out information for any events (circuits being extended,
streams opening and closing, etcetera).

Address-map expiries are tracked independantly of Tor by ``txtorcon``
based on the timestamps Tor sends.


Sub-Command: cmd
----------------

This attemps to run whatever you type after ``cmd`` as a Tor
controller command and prints out the response. For example::

   carml cmd getinfo info/names
   carml cmd signal newnym
   carml cmd setconf SOCKSPort 9999

If you pass ``-`` as the command, then commands are read from standard
input one line at a time and executed. (FIXME)

.. note::
   Some of Tor's commands have top-level ``carml`` equivalents. For
   example, ``setconf`` for somewhat esoteric reasons (Tor sometimes
   relys on a series of setconf commands coming in the "same
   command").


Sub-Command: circ
--------------------------

This command allow you to manipulate circuits. You may list them
(``-L, --list``) and delete them by ID (``--delete ID
[--if-unused]``), or create them (``--build``).


Sub-Command: stream
--------------------------

This command allow you to manipulate streams.

You may list them (``-L, --list``) and close them by ID (``--close
ID``). Running the ``stream`` sub-command with ``--attach circ_id``
causes any future streams at all to be attached to that particular
circuit; this continues until ``carml`` exits (e.g. control-C) at
which point Tor again decides which streams to attach to which
circuits.


