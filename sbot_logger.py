import os
import sys
import time
import sublime

# TODO add category, like print("ERR", "blabla") then filter to taste

# Because ST takes ownership of the python module loading and execution, it just dumps any load/parse and runtime exceptions
# to the console. This can be annoying because it means you have to have the console open pretty much all the time.
# First attempt was to hook the console stdout but it was not very cooperative. So now there are try/except around all the
# ST callback functions and this works to catch runtime errors and pop up a message box. Import/parse errors still go to the
# console so you have to keep an eye open there while developing but they should resolve quickly.

# ====================== ST internal logger (sublime.py) =======================
# class _LogWriter(io.TextIOBase):
#     def __init__(self):
#         self.buf = None
# 
#     def flush(self):
#         b = self.buf
#         self.buf = None
#         if b is not None and len(b):
#             sublime_api.log_message(b)
# 
#     def write(self, s):
#         if self.buf is None:
#             self.buf = s
#         else:
#             self.buf += s
#         if '\n' in s or '\r' in s:
#             self.flush()
# 
# 
# sys.stdout = _LogWriter()
# sys.stderr = _LogWriter()
# 


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

    _prev_stdout = None
    _prev_stderr = None
    _log_fn = None
    _time_format = None
    _mode = None

    def start(self):
        if self._prev_stdout is None:
            self._prev_stdout = sys.stdout
            self._prev_stderr = sys.stderr
            sys.stdout = self
            sys.stderr = self
        
            settings = sublime.load_settings("SbotLogger.sublime-settings")

            if settings['mode'] != 'off':
                self._mode = settings['mode']
                if len(settings["file_path"]) > 0:
                    self._log_fn = settings["file_path"] 
                else:
                    self._log_fn = os.path.join(sublime.packages_path(), 'User', 'SbotStore', 'sbot.log')

            if len(settings['time_format']) > 0:
                self._time_format = settings['time_format']  # TODO msec

            # Clean old log maybe.
            if self._mode == 'clean':
                with open(self._log_fn, "w") as log:
                    pass

    def stop(self):
        if self._prev_stdout is not None:
            sys.stdout = self._prev_stdout
            sys.stderr = self._prev_stderr

    def write(self, message):
        cmsg = message.rstrip()
        if len(cmsg) > 0:
            if self._time_format is not None:
                outmsg = f'{time.strftime(self._time_format, time.localtime())} {cmsg}\n'
            else:
                outmsg = f'{cmsg}\n'

            self._prev_stdout.write(outmsg)
            self._prev_stdout.flush()

            if self._mode is not None:
                with open(self._log_fn, "a") as log:
                    log.write(outmsg)
