import os
import sys
import time
import shutil
import pathlib
import io
from datetime import datetime
import sublime


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
    pass


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    global _logger
    _logger.stop()
    pass


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
    _current_msg = ''
    _current_cat = '????'
    _msg_time = None  # timestamp of beginning

    # Processing unhandled exceptions.
    _exc_text = ''
    _exc_count = 0
    _exc_end = False

    # Debugging.
    _enable_trace = True

    def start(self):
        ''' Redirects stdout/stderr. '''
        self.stop()

        try:
            # Get the settings.
            settings = sublime.load_settings("SbotALogger.sublime-settings")
            self._mode = settings.get('mode')

            file_path = settings.get('file_path')
            if file_path is None or len(file_path) == 0:
                file_path = os.path.join(sublime.packages_path(), 'User', 'SbotStore')
            pathlib.Path(file_path).mkdir(parents=True, exist_ok=True)
            self._log_fn = os.path.join(file_path, 'sbot.log')

            self._notif_cats = settings.get('notify_cats')
            self._ignore_cats = settings.get('ignore_cats')
            self._time_format = settings.get('time_format')

            # print(f'{self._notif_cats} | {self._ignore_cats} | {self._time_format}')

            # Maybe clean old log.
            if self._mode == 'clean':
                if os.path.exists(self._log_fn):
                    # Make a backup.
                    bup = self._log_fn.replace('.log', '_old.log')
                    shutil.copyfile(self._log_fn, bup)
                # Clear log file.
                with open(self._log_fn, "w"):
                    pass

            print("Stealing stdout and stderr...")
            self._console_stdout = sys.stdout
            self._console_stderr = sys.stderr
            sys.stdout = self
            sys.stderr = self
            print("INFO Stolen stdout and stderr!")

        except Exception as e:
            # Last ditch debug help. Assumes print() is broken.
            self._trace('Exception!!', e)
            self.stop()

    def stop(self):
        ''' Restore stdout/stderr. '''
        print("INFO Restore stdout and stderr!")
        if self._console_stdout is not None:
            sys.stdout = self._console_stdout
        if self._console_stderr is not None:
            sys.stderr = self._console_stderr

    def write(self, message):
        ''' Process one part of text to stdout. Strings arrive but have to be concatenated until
        EOL appears. Process unhandled exceptions.
        Warning! Do not print() in here - recursive death.
        '''
#Traceback (most recent call last):N
#  File "C:\Program Files\Sublime Text\Lib\python38\sublime_plugin.py", line 1482, in run_N
#    return self.run()
#N
#  File "C:\Users\cepth\AppData\Roaming\Sublime Text\Packages\SbotDev\sbot_dev.py", line 92, in runN
#    i = 999 / 0
#N
#ZeroDivisionError
#: 
#division by zero
#N


# 2022-04-22 13:05:54.362 UEXC Traceback (most recent call last):N
# 2022-04-22 13:05:54.362 UEXC   File "C:\Program Files\Sublime Text\Lib\python38\sublime_plugin.py", line 1482, in run_N
# 2022-04-22 13:05:54.363 UEXC     return self.run()N
# 2022-04-22 13:05:54.364 UEXC   File "C:\Users\cepth\AppData\Roaming\Sublime Text\Packages\SbotDev\sbot_dev.py", line 92, in runN
# 2022-04-22 13:05:54.365 UEXC     i = 999 / 0N
# 2022-04-22 13:05:54.366 UEXC ZeroDivisionError: division by zeroN


        # Test for imminent end of exception stack. TODO is there a better way than this?
        # ZeroDivisionError: division by zero arrives as sequence 'ZeroDivisionError', ': ', 'division by zero\n'.
        if message.strip() == ':':
            self._exc_end = True

        # Either starting a new message or in the middle of one.
        if len(self._current_msg) == 0:  # New message/line.

            # ?? first check/process exception text

            # Start anew.
            self._msg_time = time.localtime()
            # self._current_msg = message
            # self._exc_text = ''
            # self._exc_end = False

            # Check for category.
            parts = message.split(' ')

            if len(parts) > 0:
                # Check for new exception stack.
                if parts[0] == 'Traceback':
                    self._process_current_exc_stack()
                    self._current_cat = CAT_UEXC
                    self._current_msg = CAT_UEXC + ' ' + message # insert cat
                    self._exc_text += message

                # Check for canned category preamble from common slog().
                elif len(parts[0]) == 4:  # 4 is fixed for all internal logging. TODO too brittle - accept any sentence with four letter start word!
                    self._process_current_exc_stack()
                    self._current_cat = parts[0]
                    self._current_msg = message

                # Continue exception stack.
                elif self._current_cat == CAT_UEXC:
                    self._current_msg = CAT_UEXC + ' ' + message # insert cat
                    self._exc_text += message

                # Assume loose print() or ST internals, etc.
                else:
                    self._current_cat = CAT_OTHER
                    self._current_msg = CAT_OTHER + ' ' + message # insert cat

        else:  # continuing line
            self._current_msg += message
            if self._current_cat == CAT_UEXC:
                self._exc_text += message

        # Check for line complete.
        if '\n' in self._current_msg:

            if self._current_cat == CAT_UEXC:
                self._exc_text.append(self._current_msg)


            # Format and print the log record.
            if self._current_cat not in self._ignore_cats:
                # Format time.
                if self._time_format is None:
                    outmsg = f'{self._current_msg}'
                elif len(self._time_format) > 0:
                    outmsg = f'{time.strftime(self._time_format, self._msg_time)} {self._current_msg}'
                else:
                    time_str = f'{str(datetime.now())}'[0:-3]
                    outmsg = f'{time_str} {self._current_msg}'

                # Always write to console.
                self._console_stdout.write(outmsg)
                self._console_stdout.flush()

                # Maybe write to file.
                if self._mode != 'off':
                    with open(self._log_fn, "a") as log:
                        log.write(outmsg)

                if self._current_cat in self._notif_cats:
                    sublime.message_dialog(self._current_msg)

            self._current_msg = ''

            self._process_current_exc_stack()

            
    def _process_current_exc_stack(self):
        ''' Handled current unhandled exception if active. '''
        if self._current_cat == CAT_UEXC:
            if self._exc_end:
                if self._exc_count < 1:  # Don't pester the user, do this once.
                    self._exc_count += 1
                    sublime.message_dialog('Unhandled exception!\n' + self._exc_text)
                self._exc_text = ''
                self._exc_end = False


    def _trace(self, message, exc=None):
        ''' Debug helper because stdout is probably hosed. '''
        if self._enable_trace:
            trc_file = self._log_fn.replace('.log', '_trace.log')

            with open(trc_file, 'a') as f:
                f.write(f'{message}\n')
                if exc is not None:
                    import traceback
                    traceback.print_exc(file=f)


    def write_xxx(self, message):
        ''' Process one part. Look for EOL. Process unhandled exceptions.
        Warning! Do not print() in here - recursive death.
        '''

        # Exception text ending? TODO is there a better way than this?
        # ZeroDivisionError: division by zero
        if message.strip() == ':':
            self._exc_end = True

        # Either starting a new message or in the middle of one.
        if len(self._current_msg) == 0:  # new
            self._current_msg = message
            self._msg_time = time.localtime()
            self._exc_text = []

            # Check for category.
            parts = message.split(' ')

            if len(parts) > 0:
                # Check for exception stack.
                if parts[0] == 'Traceback':
                    self._current_cat = CAT_UEXC
                    self._current_msg = self._current_cat + ' ' + self._current_msg # insert cat
                    self._exc_end = False
                # Check for canned category preamble.
                elif len(parts[0]) == 4:  # 4 is fixed for all internal logging.
                    self._current_cat = parts[0]
                # Continue exception.
                elif self._current_cat == CAT_UEXC:
                    self._current_msg = self._current_cat + ' ' + self._current_msg # insert cat
                # Assume loose print() or ST internals, etc.
                else:
                    self._current_cat = CAT_OTHER
                    self._current_msg = self._current_cat + ' ' + self._current_msg # insert cat

        else:  # continuing
            self._current_msg += message

        # Check for line complete.
        if '\n' in self._current_msg:

            # Process unhandled exceptions.
            if self._current_cat == CAT_UEXC:
                self._exc_text += message

                if self._exc_end:
                    if self._exc_count < 1:  # Don't pester the user, do this once.
                        self._exc_count += 1
                        sublime.message_dialog('Unhandled exception!\n' + self._exc_text)
                    self._exc_text = None
                    self._exc_end = False

            # Format and print the log record.
            if self._current_cat not in self._ignore_cats:
                # Format time.
                if self._time_format is None:
                    outmsg = f'{self._current_msg}'
                elif len(self._time_format) > 0:
                    outmsg = f'{time.strftime(self._time_format, self._msg_time)} {self._current_msg}'
                else:
                    time_str = f'{str(datetime.now())}'[0:-3]
                    outmsg = f'{time_str} {self._current_msg}'

                # Always write to console.
                self._console_stdout.write(outmsg)
                self._console_stdout.flush()

                # Maybe write to file.
                if self._mode != 'off':
                    with open(self._log_fn, "a") as log:
                        log.write(outmsg)

                if self._current_cat in self._notif_cats:
                    sublime.message_dialog(self._current_msg)

            self._current_msg = ''




    # def write_not(self, message):
    #     ''' Write one. Hooked stdout/stderr. Process unhandled exceptions. '''
    #     # Warning! Do not print() in here - recursive death.

    #     # self._trace(message) TODO this msg isn't exactly like what gets print() - broken into multiple lines, missing white space...
    #     cmsg = message #.rstrip()

    #     cmsg = cmsg.replace('\n', 'N\n')
    #     cmsg = cmsg.replace('\r', 'R\r')

    #     if len(cmsg) > 0:

    #         # Sniff the line. Check for category.
    #         cat = None
    #         parts = cmsg.split(' ')

    #         if len(parts) > 0:
    #             # Start of exception message?
    #             if parts[0] == 'Traceback':
    #                 self._exc_text = []
    #                 self._exc_text.append('Unhandled exception!')
    #                 self._exc_text.append(cmsg)
    #                 cat = 'UEXC'
    #                 cmsg = f'{cat} {cmsg}'

    #             elif len(parts[0]) == 4: # 4 is fixed for all internal logging.
    #                 # Finished exc block by virtue of non-exception record?
    #                 if self._exc_text is not None and self._exc_count < 1: # Don't pester the user, do this once.
    #                     self._exc_count += 1
    #                     # sublime.message_dialog('\n'.join(self._exc_text))
    #                     sublime.message_dialog(''.join(self._exc_text))
    #                 self._exc_text = None

    #                 # Back to normal.
    #                 cat = parts[0]

    #             elif self._exc_text is not None:
    #                 # Currently in an exc block.
    #                 self._exc_text.append(cmsg)
    #                 cat = 'UEXC'
    #                 cmsg = f'{cat} {cmsg}'

    #                 # If the last entry was ':', we're done - probably not robust.
    #                 if self._exc_text[-2] == ':' and self._exc_count < 1: # Don't pester the user, do this once. TODO dupe of above.
    #                     self._exc_count += 1
    #                     sublime.message_dialog(''.join(self._exc_text))
    #                     # sublime.message_dialog('\n'.join(self._exc_text))
    #                     self._exc_text = None
                    
    #             else:
    #                 # Other print() - loose or from internal ST.
    #                 cat = '----'
    #                 cmsg = f'{cat} {cmsg}'

    #         # Now output the line.
    #         if cat is not None and cat not in self._ignore_cats:
    #             # Format time.
    #             if self._time_format is None:
    #                 outmsg = f'{cmsg}\n'
    #             elif len(self._time_format) > 0:
    #                 outmsg = f'{time.strftime(self._time_format, time.localtime())} {cmsg}\n'
    #             else:
    #                 time_str = f'{str(datetime.now())}'[0:-3]
    #                 outmsg = f'{time_str} {cmsg}\n'

    #             # Always write to console.
    #             self._console_stdout.write(outmsg)
    #             self._console_stdout.flush()

    #             # Maybe write to file.
    #             if self._mode is not None:
    #                 with open(self._log_fn, "a") as log:
    #                     log.write(outmsg)

    #             if cat in self._notif_cats:
    #                 sublime.message_dialog(cmsg)
