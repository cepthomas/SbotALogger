import os
import sys
import time
from datetime import datetime
import sublime


# The singleton logger.
_logger = None


#-----------------------------------------------------------------------------------
def plugin_loaded():
    # This should only be called once per ST instance.
    global _logger
    _logger = SbotLogger()
    _logger.start()


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    global _logger
    _logger.stop()


#-----------------------------------------------------------------------------------
class SbotLogger():

    _console_stdout = None
    _console_stderr = None
    _log_fn = None
    _time_format = None
    _mode = None
    _ignore_cats = None
    _notif_cats = None

    def start(self):
        if self._console_stdout is None:
            try:
                # Get the settings.
                settings = sublime.load_settings("SbotLogger.sublime-settings")
                self._mode = settings.get('mode')
                fp = settings.get("file_path")
                self._log_fn = fp if len(fp) > 0 else os.path.join(sublime.packages_path(), 'User', 'SbotStore', 'sbot.log')
                self._notif_cats = settings.get('notify_cats')
                self._ignore_cats = settings.get('ignore_cats')
                self._time_format = settings.get('time_format')

                # Clean old log maybe.
                if self._mode == 'clean':
                    with open(self._log_fn, "w") as log:
                        pass

                # print("INF Stealing stdout and stderr!")
                self._console_stdout = sys.stdout
                self._console_stderr = sys.stderr
                sys.stdout = self
                sys.stderr = self
                print("INF Stolen stdout and stderr!")
            except Exception as e:
                logging.exception(e)

    def stop(self):
        if self._console_stdout is not None:
            sys.stdout = self._console_stdout
            sys.stderr = self._console_stderr
            print("INF Restored stdout and stderr!")

    def write(self, message):
        # Write one.

        cmsg = message.rstrip()
        if len(cmsg) > 0:
            # Dig out possible category.
            cat = None
            parts = cmsg.split(' ')
            if len(parts) > 0:
                cat = parts[0]

            if cat not in self._ignore_cats:
                # Format time.
                if self._time_format is None:
                    outmsg = f'{cmsg}\n'
                elif len(self._time_format) > 0:
                    outmsg = f'{time.strftime(self._time_format, time.localtime())} {cmsg}\n'
                else:
                    time_str = f'{str(datetime.now())}'[0:-3]
                    outmsg = f'{time_str} {cmsg}\n'

                # Always write to console.
                self._console_stdout.write(outmsg)
                self._console_stdout.flush()

                # Maybe write to file.
                if self._mode is not None:
                    with open(self._log_fn, "a") as log:
                        log.write(f'{cat} {outmsg}')

                if cat in self._notif_cats:
                    sublime.message_dialog(cmsg)