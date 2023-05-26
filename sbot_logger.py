import os
import sys
import shutil
import io
import datetime
import traceback
import sublime
from . import sbot_common as sc


# The singleton logger.
_logger = None

LOGGER_SETTINGS_FILE = "SbotALogger.sublime-settings"


#-----------------------------------------------------------------------------------
def plugin_loaded():
    # Called once per ST instance.
    global _logger
    _logger = SbotALogger()
    _logger.start()


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    global _logger
    _logger.stop()


#-----------------------------------------------------------------------------------
class SbotALogger(io.TextIOBase):
    # The original outputs to ST console.
    _console_stdout = None
    _console_stderr = None

    # From settings.
    _log_fn = None
    _file_size = 0
    _ignore_cats = []
    _notify_cats = []
    _write_to_console = True  # Could be in settings.

    def start(self):
        ''' Redirects stdout/stderr. '''
        self.stop()

        try:
            # Get the settings.
            settings = sublime.load_settings(LOGGER_SETTINGS_FILE)
            self._log_fn = sc.get_store_fn('sbot.log')
            self._file_size = settings.get('file_size')
            self._notify_cats = settings.get('notify_cats')
            self._ignore_cats = settings.get('ignore_cats')

            # Hook stdio.
            # print("*** Stealing stdout and stderr.")
            self._console_stdout = sys.stdout
            self._console_stderr = sys.stderr
            sys.stdout = self
            sys.stderr = self
            # print("*** Stolen stdout and stderr.")

        except Exception as e:
            # Last ditch debug help. Assumes print() is broken.
            sublime.error_message(f'Fatal:{e}')
            self._trace('Fatal:', e)
            self.stop()

    def stop(self):
        ''' Restore stdout/stderr. '''
        # don't: self.write("*** Restoring stdout and stderr.")
        if self._console_stdout is not None:
            sys.stdout = self._console_stdout
        if self._console_stderr is not None:
            sys.stderr = self._console_stderr

    def write(self, message):
        ''' Format record and write to file and/or stdout. Warning! Do not print() in here - recursive death.'''

        # Sometimes get stray lines.
        if len(message) == 0:
            return
        if len(message) == 1 and message[0] == '\n':
            return

        # Get the category. This is a bit clumsy.
        # Looks like:date time CAT text text ...
        parts = message.split(' ')
        cat = parts[0] if len(parts) >= 2 else ''

        if cat not in self._ignore_cats:
            # Format and print the log record.
            time_str = f'{str(datetime.datetime.now())}'[0:-3]
            out_line = f'{time_str} {message}'

            # Write to console also.
            if self._write_to_console:
                self._write_console(out_line)

            # Maybe write to file.
            if self._file_size > 0:
                # Maybe flip log.
                if os.path.exists(self._log_fn):
                    if (os.path.getsize(self._log_fn) / 1024) > self._file_size:
                        # Roll over.
                        bup = self._log_fn.replace('.log', '_old.log')
                        shutil.copyfile(self._log_fn, bup)
                        # Clear current log file.
                        with open(self._log_fn, "w"):
                            pass

                # Write the record
                with open(self._log_fn, "a") as log:
                    log.write(out_line + '\n')
                    log.flush()

            # if self._current_cat in self._notify_cats:
            if cat in self._notify_cats:
                sublime.message_dialog(message)

    def _write_console(self, msg):
        ''' Write default console. '''
        if self._console_stdout is not None:
            self._console_stdout.write(f'{msg}\n')
            self._console_stdout.flush()

    def _trace(self, message, exc=None):
        ''' Debug helper because stdout is probably broken. '''
        if self._enable_trace:
            trc_file = self._log_fn.replace('.log', '_trace.log')

            with open(trc_file, 'a') as f:
                f.write(f'{message}\n')
                if exc is not None:
                    import traceback
                    traceback.print_exc(file=f)

#-----------------------------------------------------------------------------------
def _notify_exception(type, value, tb):
    ''' Process unhandled exceptions and log, notify user. '''
    tb_info = '\n'.join(traceback.extract_tb(tb).format())  # TODO sometimes get extra blank lines
    msg = f'{sc.CAT_EXC} {type}: {value}\n{tb_info}'

    print(msg)


# Connect the hook.
sys.excepthook = _notify_exception
