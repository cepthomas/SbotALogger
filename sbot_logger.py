import os
import sys
import time
import sublime


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
    _notifs = []

    def start(self):
        if self._prev_stdout is None:
            self._prev_stdout = sys.stdout
            self._prev_stderr = sys.stderr
            sys.stdout = self
            sys.stderr = self
        
            settings = sublime.load_settings("SbotLogger.sublime-settings")

            self._notifs = settings['notify'].split(',')

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

            if cmsg.split(' ')[0] in self._notifs:
                sublime.message_dialog(cmsg)