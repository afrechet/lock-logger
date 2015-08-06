#!/usr/bin/env python
import gobject
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import os
import argparse
import logging
import datetime
import atexit


#Setup arguments.
parser = argparse.ArgumentParser(
          description=
          """Logs times when screen locked and unlocked.""",
          epilog=
          """by Alexandre Frechette (frechette@google.com)"""
          )
parser.add_argument('--log-file',
 dest='log_file',
  default='~/locktimes.csv',
   help='the file to which times should be appended. (default: %(default)s)')
parser.add_argument('--time-format',
 dest='time_format',
  default="%Y-%m-%d %H:%M:%S",
   help='the format of the time logged. (default: %(default)s)')

def parseLogLevel(loglevel):
  numeric_level = getattr(logging, loglevel.upper(), None)
  if not isinstance(numeric_level, int):
    parser.error('Invalid log level: %s' % loglevel)
  return numeric_level
parser.add_argument('--log-level',
          dest = 'log_level',
          type=parseLogLevel,
          default=logging.INFO,
          help='the level of logging to display (default: %(default)s)'
          )

#Parse argument.
args = parser.parse_args()

#Setup logging.
logging.basicConfig(level=args.log_level,
  format='[%(asctime)s] %(levelname)s - %(message)s')

#Reading up parameters.
logging.debug('Reading parameters...')
time_format = args.time_format
logging.debug('Time logging format will be: "%s".' % time_format)
log_file_path = os.path.expanduser(args.log_file)
logging.debug('Log will be: "%s".' % log_file_path)
f = open(log_file_path,'w+')

logging.info('Launching lock time logger...')

#Setup event methods.
def _log(message):
  logging.debug('Getting current time...')
  now = datetime.datetime.now()
  logging.debug('Writing to logfile "%s"...' % log_file_path)
  f.write('%s,%s\n' % (message,now.strftime(time_format)))
  f.flush()
  return

def receiver(*args,**kwargs):
  logging.debug('Received a signal: args:"%s" and kwargs:"%s"' %
    (str(args),str(kwargs)))
  logging.debug(args)
  logging.debug(kwargs)

  if args[0] == True:
    logging.info('Screen lock.')
    _log('lock')
  else:
    logging.info('Screen unlock.')
    _log('unlock')

atexit.register(_log, message='stop')

_log('start')
logging.debug('Setting up signal receiver ...')
DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
bus.add_signal_receiver(receiver,
 interface_keyword='org.cinnamon.ScreenSaver',
  member_keyword='signal',
   signal_name='ActiveChanged')

logging.debug('Setting up main loop ...')
mainloop = gobject.MainLoop()
logging.debug('Running main loop ...')
mainloop.run()
f.close()
logging.info('... done!')

