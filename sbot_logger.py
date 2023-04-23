import os
import sys
import time
import shutil
import pathlib
import io
import datetime
import traceback
import inspect
import sublime

try:
    import SbotCommon.sbot_common as sbot
except ModuleNotFoundError:
    sublime.message_dialog('SbotALogger plugin requires SbotCommon plugin')
    raise ImportError('SbotALogger plugin requires SbotCommon plugin')


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
def notify_exception(type, value, tb):
    tb_info = '\n'.join(traceback.extract_tb(tb).format())
    msg = f'{sbot.CAT_EXC} {type}: {value}\n{tb_info}'
    print(msg)
    # Popen(f'notify-send "screenshot.py hit an exception" "{msg}" -a screenshot.py', shell=True,)

sys.excepthook = notify_exception

# 2023-04-23 15:02:33.618 EXC <class 'ZeroDivisionError'>: division by zero
#   File "C:\Program Files\Sublime Text\Lib\python38\sublime_plugin.py", line 1659, in run_
#     return self.run()
#
#   File "C:\Users\cepth\AppData\Roaming\Sublime Text\Packages\SbotDev\sbot_dev.py", line 82, in run
#     i = 222 / 0




#-----------------------------------------------------------------------------------
class SbotALogger(io.TextIOBase):
    # The outputs.
    _console_stdout = None
    _console_stderr = None

    # From settings.
    _log_fn = None
    _time_format = None
    _size = 0
    _ignore_cats = [] #TODO client needs to deal with these???
    _notify_cats = []

    # # Buffer.
    # _current_line = ''
    # _current_cat = '???'
    # _line_time = None

    # Processing unhandled exceptions.
    _exc_count = 0
    _exc_stack_end = False

    def start(self):
        ''' Redirects stdout/stderr. '''
        self.stop()

        # print('*** start()')

        try:
            # Get the settings.
            settings = sublime.load_settings(LOGGER_SETTINGS_FILE)
            self._size = settings.get('size')

            file_path = settings.get('file_path')
            self._log_fn = sbot.get_store_fn(file_path, 'sbot.log')

            # self._notify_cats = settings.get('notify_cats')
            # self._ignore_cats = settings.get('ignore_cats')
            self._time_format = settings.get('time_format')

            # Hook stdio.
            # print("*** Stealing stdout and stderr.")
            self._console_stdout = sys.stdout
            self._console_stderr = sys.stderr
            sys.stdout = self
            sys.stderr = self
            # print("*** Stolen stdout and stderr.")

        except Exception as e:
            # Last ditch debug help. Assumes print() is broken.
            self._trace('Exception!!', e)
            self.stop()

    def stop(self):
        ''' Restore stdout/stderr. '''
        # don't: self.write("*** Restoring stdout and stderr.")
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

        # # self._trace(message)
        # frame = sys._getframe(2)
        # func = frame.f_code.co_name
        # line = frame.f_lineno
        # fn = os.path.basename(frame.f_code.co_filename)
        # self._console_stdout.write(f'Caller:{fn}:{line}\n')
        # self._console_stdout.flush()


        if message[0] == '\r':
            self._console_stdout.write('ret\n')
            self._console_stdout.flush()
            return

        if message[0] == '\n': # TODO win print() adds this
            self._console_stdout.write('newline\n')
            self._console_stdout.flush()
            return

        if len(message) < 2:
            return

        # Format and print the log record.
        cat = '?-?'
        # if self._current_cat not in self._ignore_cats:
        if cat not in self._ignore_cats:
            # # Format time.
            # if self._time_format is None:
            #     out_line = f'{message}'
            # elif len(self._time_format) > 0:
            #     out_line = f'{time.strftime(self._time_format, self._line_time)} {message}'
            # else:
            #     time_str = f'{str(datetime.datetime.now())}'[0:-3]
            #     out_line = f'{time_str} {message} [{func}:{line}]'

            # Format time.
            time_str = f'{str(datetime.datetime.now())}'[0:-3]
            out_line = f'{time_str} {message}'

            # # Always write to console.
            # self._console_stdout.write(out_line + '\n')
            # self._console_stdout.flush()

            # Maybe write to file.
            if self._size > 0:
                # Maybe flip log.
                if (os.path.getsize(self._log_fn) / 1024) > self._size:
                    if os.path.exists(self._log_fn):
                        # Make a backup.
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

        # self._process_current_exc()

        # self._current_line = ''

        return





# ===========================================================================================


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
                    self._current_cat = sbot.CAT_EXC
                    self._current_line = sbot.CAT_EXC + ' 1! ' + message  # insert cat

                # Check for canned category preamble from common slog(). 3 is fixed for all internal logging (see SbotCommon slog().
                # This is a bit brittle - will accept any sentence with four letter start word! Maybe that's not a big deal. TODO fix this.
                elif len(parts[0]) == 3:  
                    self._process_current_exc()
                    self._current_cat = parts[0]
                    self._current_line = message

                # Continue exception stack.
                elif self._current_cat == sbot.CAT_EXC:  # TODO gets stuck on this one
                    self._current_line = sbot.CAT_EXC + ' 2! ' + message  # insert cat

                # Assume loose print() or ST internals, etc.
                else:
                    self._current_cat = sbot.CAT_NON
                    self._current_line = sbot.CAT_NON + ' ' + message  # insert cat

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
                    time_str = f'{str(datetime.datetime.now())}'[0:-3]
                    out_line = f'{time_str} {self._current_line}'

                # Always write to console.
                self._console_stdout.write(out_line)
                self._console_stdout.flush()

                # Maybe write to file.
                if self._size > 0:
                    # Maybe flip log.
                    if (os.path.getsize(self._log_fn) / 1024) > self._size:
                        if os.path.exists(self._log_fn):
                            # Make a backup.
                            bup = self._log_fn.replace('.log', '_old.log')
                            shutil.copyfile(self._log_fn, bup)
                        # Clear current log file.
                        with open(self._log_fn, "w"):
                            pass

                    # Write the record
                    with open(self._log_fn, "a") as log:
                        log.write(out_line)

                if self._current_cat in self._notify_cats:
                    sublime.message_dialog(self._current_line)

            self._process_current_exc()

            self._current_line = ''

    def _process_current_exc(self):
        ''' Handled current unhandled exception if active. '''
        if self._current_cat == sbot.CAT_EXC:
            if self._exc_stack_end:
                if self._exc_count < 1:  # Don't pester the user, do this once.
                    self._exc_count += 1
                    sublime.message_dialog('Unhandled exception!\nGo look in the log.\n' + self._current_line)
                self._exc_stack_end = False

    def _trace(self, message, exc=None):
        ''' Debug helper because stdout is probably broken. '''
        trc_file = self._log_fn.replace('.log', '_trace.log')

        with open(trc_file, 'a') as f:
            f.write(f'{message}\n')
            if exc is not None:
                import traceback
                traceback.print_exc(file=f)


# ================================================================================
# ==================================== old TODO ==================================
# ================================================================================


    def write_with_exc(self, message):
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
                    self._current_cat = sbot.CAT_EXC
                    self._current_line = sbot.CAT_EXC + ' 1! ' + message  # insert cat

                # Check for canned category preamble from common slog(). 3 is fixed for all internal logging (see SbotCommon slog().
                # This is a bit brittle - will accept any sentence with four letter start word! Maybe that's not a big deal. TODO fix this.
                elif len(parts[0]) == 3:  
                    self._process_current_exc()
                    self._current_cat = parts[0]
                    self._current_line = message

                # Continue exception stack.
                elif self._current_cat == sbot.CAT_EXC:  # TODO gets stuck on this one
                    self._current_line = sbot.CAT_EXC + ' 2! ' + message  # insert cat

                # Assume loose print() or ST internals, etc.
                else:
                    self._current_cat = sbot.CAT_NON
                    self._current_line = sbot.CAT_NON + ' ' + message  # insert cat

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
                    time_str = f'{str(datetime.datetime.now())}'[0:-3]
                    out_line = f'{time_str} {self._current_line}'

                # Always write to console.
                self._console_stdout.write(out_line)
                self._console_stdout.flush()

                # Maybe write to file.
                if self._size > 0:
                    # Maybe flip log.
                    if (os.path.getsize(self._log_fn) / 1024) > self._size:
                        if os.path.exists(self._log_fn):
                            # Make a backup.
                            bup = self._log_fn.replace('.log', '_old.log')
                            shutil.copyfile(self._log_fn, bup)
                        # Clear current log file.
                        with open(self._log_fn, "w"):
                            pass

                    # Write the record
                    with open(self._log_fn, "a") as log:
                        log.write(out_line)

                if self._current_cat in self._notify_cats:
                    sublime.message_dialog(self._current_line)

            self._process_current_exc()

            self._current_line = ''


    def write_orig_TODO(self, message):
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
                    self._current_cat = sbot.CAT_EXC
                    self._current_line = sbot.CAT_EXC + ' 1! ' + message  # insert cat

                # Check for canned category preamble from common slog(). 3 is fixed for all internal logging (see SbotCommon slog().
                # This is a bit brittle - will accept any sentence with four letter start word! Maybe that's not a big deal.
                elif len(parts[0]) == 3:  
                    self._process_current_exc()
                    self._current_cat = parts[0]
                    self._current_line = message

                # Continue exception stack.
                elif self._current_cat == sbot.CAT_EXC:  # TODO gets stuck on this one
                    self._current_line = sbot.CAT_EXC + ' 2! ' + message  # insert cat

                # Assume loose print() or ST internals, etc.
                else:
                    self._current_cat = sbot.CAT_NON
                    self._current_line = sbot.CAT_NON + ' ' + message  # insert cat

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
                    time_str = f'{str(datetime.datetime.now())}'[0:-3]
                    out_line = f'{time_str} {self._current_line}'

                # Always write to console.
                self._console_stdout.write(out_line)
                self._console_stdout.flush()

                # Maybe write to file.
                if self._mode != 'off':
                    with open(self._log_fn, "a") as log:
                        log.write(out_line)

                if self._current_cat in self._notify_cats:
                    sublime.message_dialog(self._current_line)

            self._process_current_exc()

            self._current_line = ''
