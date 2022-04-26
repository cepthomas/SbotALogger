import os
import sys
import time
import shutil
import pathlib
import io
from datetime import datetime
import sublime

try:
    from SbotCommon.sbot_common import get_store_fn
except ModuleNotFoundError as e:
    raise ImportError('SbotALogger plugin requires SbotCommon plugin')


# The singleton logger.
_logger = None


# Internal categories.
CAT_UEXC = 'UEXC'
CAT_OTHER = '----'


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
    # The outputs.
    _console_stdout = None
    _console_stderr = None

    # From settings.
    _log_fn = None
    _time_format = None
    _mode = None
    _ignore_cats = None
    _notif_cats = None

    # Buffer.
    _current_line = ''
    _current_cat = '????'
    _line_time = None

    # Processing unhandled exceptions.
    _exc_count = 0
    _exc_stack_end = False

    # Debugging.
    _enable_trace = False

    def start(self):
        ''' Redirects stdout/stderr. '''
        self.stop()

        try:
            # Get the settings.
            settings = sublime.load_settings("SbotALogger.sublime-settings")
            self._mode = settings.get('mode')

            file_path = settings.get('file_path')
            self._log_fn = get_store_fn(file_path, 'sbot.log')

            self._notif_cats = settings.get('notify_cats')
            self._ignore_cats = settings.get('ignore_cats')
            self._time_format = settings.get('time_format')

            # Maybe clean old log.
            if self._mode == 'clean':
                if os.path.exists(self._log_fn):
                    # Make a backup.
                    bup = self._log_fn.replace('.log', '_old.log')
                    shutil.copyfile(self._log_fn, bup)
                # Clear log file.
                with open(self._log_fn, "w"):
                    pass

            # Hook stdio.
            print("Stealing stdout and stderr.")
            self._console_stdout = sys.stdout
            self._console_stderr = sys.stderr
            sys.stdout = self
            sys.stderr = self
            # print("Stolen stdout and stderr.")

        except Exception as e:
            # Last ditch debug help. Assumes print() is broken.
            self._trace('Exception!!', e)
            self.stop()

    def stop(self):
        ''' Restore stdout/stderr. '''
        print("Restoring stdout and stderr.")
        if self._console_stdout is not None:
            sys.stdout = self._console_stdout
        if self._console_stderr is not None:
            sys.stderr = self._console_stderr

    def write(self, message):
        ''' Process one part of text to stdout.
        Strings arrive but have to be concatenated until EOL appears.
        Process unhandled exceptions and notify user.
        Warning! Do not print() in here - recursive death.
        '''

        # Test for imminent end of exception stack by looking for a single colon. This is a bit clumsy.
        # ZeroDivisionError: division by zero arrives as sequence 'ZeroDivisionError', ': ', 'division by zero\n'.
        if message.strip() == ':':
            self._exc_stack_end = True

        # Either starting a new line or in the middle of one.
        if len(self._current_line) == 0:
            # Start a new line.
            self._line_time = time.localtime()

            # Check for category.
            parts = message.split(' ')

            if len(parts) > 0:
                # Check for new exception stack.
                if parts[0] == 'Traceback':
                    self._process_current_exc()
                    self._current_cat = CAT_UEXC
                    self._current_line = CAT_UEXC + ' ' + message  # insert cat

                # Check for canned category preamble from common slog(). 4 is fixed for all internal logging (SbotCommon.slog().
                # This is a bit brittle - will accept any sentence with four letter start word! Maybe that's not a big deal.
                elif len(parts[0]) == 4:  
                    self._process_current_exc()
                    self._current_cat = parts[0]
                    self._current_line = message

                # Continue exception stack.
                elif self._current_cat == CAT_UEXC:
                    self._current_line = CAT_UEXC + ' ' + message  # insert cat

                # Assume loose print() or ST internals, etc.
                else:
                    self._current_cat = CAT_OTHER
                    self._current_line = CAT_OTHER + ' ' + message  # insert cat

        else:  # continuing line
            self._current_line += message

        # Check for line complete.
        if '\n' in self._current_line:
            # Format and print the log record.
            if self._current_cat not in self._ignore_cats:
                # Format time.
                if self._time_format is None:
                    out_line = f'{self._current_line}'
                elif len(self._time_format) > 0:
                    out_line = f'{time.strftime(self._time_format, self._line_time)} {self._current_line}'
                else:
                    time_str = f'{str(datetime.now())}'[0:-3]
                    out_line = f'{time_str} {self._current_line}'

                # Always write to console.
                self._console_stdout.write(out_line)
                self._console_stdout.flush()

                # Maybe write to file.
                if self._mode != 'off':
                    with open(self._log_fn, "a") as log:
                        log.write(out_line)

                if self._current_cat in self._notif_cats:
                    sublime.message_dialog(self._current_line)

            self._process_current_exc()

            self._current_line = ''

    def _process_current_exc(self):
        ''' Handled current unhandled exception if active. '''
        if self._current_cat == CAT_UEXC:
            if self._exc_stack_end:
                if self._exc_count < 1:  # Don't pester the user, do this once.
                    self._exc_count += 1
                    sublime.message_dialog('Unhandled exception!\nGo look in the log.\n' + self._current_line)
                self._exc_stack_end = False

    def _trace(self, message, exc=None):
        ''' Debug helper because stdout is probably broken. '''
        if self._enable_trace:
            trc_file = self._log_fn.replace('.log', '_trace.log')

            with open(trc_file, 'a') as f:
                f.write(f'{message}\n')
                if exc is not None:
                    import traceback
                    traceback.print_exc(file=f)
