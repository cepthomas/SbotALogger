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

_enable_trace = True


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
    # The outputs:
    _console_stdout = None
    _console_stderr = None

    # From settings:
    _log_fn = None
    _time_format = None
    _mode = None
    _ignore_cats = None
    _notif_cats = None

    # Processing unhandled exceptions:
    _exc_text = None
    _exc_count = 0

    def start(self):
        ''' Redirects stdout/stderr. '''
        if self._console_stdout is None:
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

                # Clean old log maybe.
                if self._mode == 'clean':
                    if os.path.exists(self._log_fn):
                        # Make a backup.
                        bup = self._log_fn.replace('.log', '_old.log')
                        shutil.copyfile(self._log_fn, bup)
                    # Clear log file.
                    with open(self._log_fn, "w") as log:
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
        ''' Write one. Hooked stdout/stderr. Process unhandled exceptions. '''
        # Warning! Do not print() in here - recursive death.


        # self._trace(message) TODO this msg isn't exactly like what gets print() - broken into multiple lines, missing white space...
        cmsg = message #.rstrip()

        cmsg = cmsg.replace('\n', 'N\n')
        cmsg = cmsg.replace('\r', 'R\r')


        if len(cmsg) > 0:

            # Sniff the line. Check for category.
            cat = None
            parts = cmsg.split(' ')

            if len(parts) > 0:
                # Start of exception message?
                if parts[0] == 'Traceback':
                    self._exc_text = []
                    self._exc_text.append('Unhandled exception!')
                    self._exc_text.append(cmsg)
                    cat = 'UEXC'
                    cmsg = f'{cat} {cmsg}'

                elif len(parts[0]) == 4: # 4 is fixed for all internal logging.
                    # Finished exc block by virtue of non-exception record?
                    if self._exc_text is not None and self._exc_count < 1: # Don't pester the user, do this once.
                        self._exc_count += 1
                        sublime.message_dialog('\n'.join(self._exc_text))
                    self._exc_text = None

                    # Back to normal.
                    cat = parts[0]

                elif self._exc_text is not None:
                    # Currently in an exc block.
                    self._exc_text.append(cmsg)
                    cat = 'UEXC'
                    cmsg = f'{cat} {cmsg}'

                    # If the last entry was ':', we're done - probably not robust.
                    if self._exc_text[-2] == ':' and self._exc_count < 1: # Don't pester the user, do this once.
                        self._exc_count += 1
                        sublime.message_dialog('\n'.join(self._exc_text))
                        self._exc_text = None
                    
                else:
                    # Other print() - loose or from internal ST.
                    cat = '----'
                    cmsg = f'{cat} {cmsg}'

            # Now output the line.
            if cat is not None and cat not in self._ignore_cats:
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
                        log.write(outmsg)

                if cat in self._notif_cats:
                    sublime.message_dialog(cmsg)

    def _trace(self, message, exc=None):
        ''' Debug helper because stdout is probably hosed. '''
        if _enable_trace:
            trc_file = self._log_fn.replace('.log', '_trace.log')

            with open(trc_file, 'a') as f:
                f.write(f'{message}\n')
                if exc is not None:
                    import traceback
                    traceback.print_exception(exc, file=f)
