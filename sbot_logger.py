import os
import sys
import time
import shutil
import pathlib
from datetime import datetime
import sublime




# TODO more debugging tools for plugins. More print() funcs?

#TODO from inspect import currentframe, getframeinfo
# frameinfo = getframeinfo(currentframe())
# print(frameinfo.filename, frameinfo.lineno)
#
# from inspect import currentframe, getframeinfo
# cf = currentframe()
# filename = getframeinfo(cf).filename
# print "This is line 5, python says line ", cf.f_lineno 
# print "The filename is ", filename
# 
# def Deb(msg = None):
# print(f"Debug {sys._getframe().f_back.f_lineno}: {msg if msg is not None else ''}")
# 
# Handy if used in a common file - prints file name, line number and function of the caller:
# import inspect
# def getLineInfo():
#     print(inspect.stack()[1][1],":",inspect.stack()[1][2],":",
#           inspect.stack()[1][3])



# Do something with exceptions? Bare lines?
# reloading python 3.3 plugin SublimeLinter.status_bar_view
# reloading python 3.3 plugin SublimeLinter.sublime_linter
# plugins loaded
# FUN SbotDev.sbot_dev.plugin_loaded ()
# 2022-04-16 09:11:29.892 INF Stolen stdout and stderr!
# 2022-04-16 09:11:29.893 MTH SbotHighlight.sbot_highlight.HighlightEvent.on_init ([View(12), View(13), View(14)],)
# 2022-04-16 09:11:29.894 MTH SbotHighlight.sbot_highlight.HighlightEvent._open_hls (Window(2),)
# ...
# 2022-04-16 09:14:33.250 reloading plugin SbotSignet.sbot_signet
# 2022-04-16 09:14:33.266 Traceback (most recent call last):
# 2022-04-16 09:14:33.267   File "C:\Program Files\Sublime Text\Lib\python38\sublime_plugin.py", line 306, in reload_plugin
# 2022-04-16 09:14:33.269 m = importlib.reload(m)
# 2022-04-16 09:14:33.270   File "./python3.8/importlib/__init__.py", line 169, in reload
# 2022-04-16 09:14:33.272   File "<frozen importlib._bootstrap>", line 604, in _exec
# 2022-04-16 09:14:33.274   File "<frozen importlib._bootstrap_external>", line 808, in exec_module
# 2022-04-16 09:14:33.276   File "<frozen importlib._bootstrap>", line 219, in _call_with_frames_removed
# 2022-04-16 09:14:33.278   File "C:\Users\cepth\AppData\Roaming\Sublime Text\Packages\SbotSignet\sbot_signet.py", line 8, in <module>
# 2022-04-16 09:14:33.279 from SbotCommon.sbot_common import trace_functionX, trace_method, get_store_fn
# 2022-04-16 09:14:33.280 ImportError
# 2022-04-16 09:14:33.281 :
# 2022-04-16 09:14:33.282 cannot import name 'trace_functionX' from 'SbotCommon.sbot_common' (C:\Users\cepth\AppData\Roaming\Sublime Text\Packages\SbotCommon\sbot_common.py)
# 2022-04-16 09:15:27.722 MTH SbotHighlight.sbot_highlight.HighlightEvent.on_load (View(19),)
# 2022-04-16 09:15:27.724 MTH SbotHighlight.sbot_highlight.HighlightEvent._init_view (View(19),)
# 2022-04-16 09:16:45.275 reloading plugin SbotDev.sbot_dev
# 2022-04-16 09:16:45.287 FUN SbotDev.sbot_dev.plugin_loaded ()
# 2022-04-16 09:17:01.215 reloading plugin SbotDev.sbot_dev
# 2022-04-16 09:17:01.227 FUN SbotDev.sbot_dev.plugin_loaded ()


# 2022-04-16 11:20:23.088 reloading plugin SbotDev.sbot_dev
# 2022-04-16 11:20:23.092 Traceback (most recent call last):
# 2022-04-16 11:20:23.093   File "C:\Program Files\Sublime Text\Lib\python38\sublime_plugin.py", line 306, in reload_plugin
# 2022-04-16 11:20:23.094 m = importlib.reload(m)
# 2022-04-16 11:20:23.095   File "./python3.8/importlib/__init__.py", line 169, in reload
# 2022-04-16 11:20:23.096   File "<frozen importlib._bootstrap>", line 604, in _exec
# 2022-04-16 11:20:23.097   File "<frozen importlib._bootstrap_external>", line 804, in exec_module
# 2022-04-16 11:20:23.100   File "<frozen importlib._bootstrap_external>", line 941, in get_code
# 2022-04-16 11:20:23.101   File "<frozen importlib._bootstrap_external>", line 871, in source_to_code
# 2022-04-16 11:20:23.103   File "<frozen importlib._bootstrap>", line 219, in _call_with_frames_removed
# 2022-04-16 11:20:23.104   File "C:\Users\cepth\AppData\Roaming\Sublime Text\Packages\SbotDev\sbot_dev.py", line 71
# 2022-04-16 11:20:23.105 def run(self):
# 2022-04-16 11:20:23.106 ^
# 2022-04-16 11:20:23.106 IndentationError
# 2022-04-16 11:20:23.107 :
# 2022-04-16 11:20:23.108 unexpected indent
# 2022-04-16 11:20:24.749 MTH SbotSignet.sbot_signet.SignetEvent.on_deactivated (View(34),)


# These go directly to console via _LogWriter(). Our hooks don't intercept. Must load before our stuff.
# sublime.log_commands(True/False) - Controls command logging. If enabled, all commands run from key bindings and the menu will be logged to the console.    
# sublime.log_input(True/False) - Controls input logging. If enabled, all key presses will be logged to the console.  
# sublime.log_result_regex(True/False) - Controls result regex logging. This is useful for debugging regular expressions used in build systems.  
# sublime.log_control_tree(True/False) - When enabled, clicking with Ctrl+Alt will log the control tree under the mouse to the console.
# sublime.log_fps(True/False) - When enabled, logs the number of frames per second being rendered for the user interface
# ===
# command: drag_select {"event": {"button": 1, "x": 706.1, "y": 49.3}}
# command: drag_select {"event": {"button": 1, "x": 9.3, "y": 650.9}}
# 2022-04-16 09:59:43.491 MTH SbotSignet.sbot_signet.SignetEvent.on_deactivated (View(12),)
# 2022-04-16 09:59:43.492 MTH SbotSignet.sbot_signet.SignetEvent._collect_sigs (View(12),)
# command: drag_select {"event": {"button": 1, "x": 27.7, "y": 603.7}}
# command: drag_select {"event": {"button": 1, "x": 7.7, "y": 594.9}}
# command: copy
# command: move {"by": "lines", "extend": true, "forward": true}


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
        ''' Redirects stdout/stderr. '''
        if self._console_stdout is None:
            try:
                # Get the settings.
                settings = sublime.load_settings("SbotLogger.sublime-settings")
                self._mode = settings.get('mode')

                file_path = settings.get('file_path')
                if file_path is None or len(file_path) == 0:
                    file_path = os.path.join(sublime.packages_path(), 'User', 'SbotStore')
                pathlib.Path(file_path).mkdir(parents=True, exist_ok=True)
                self._log_fn = os.path.join(file_path, 'sbot.log')

                self._notif_cats = settings.get('notify_cats')
                self._ignore_cats = settings.get('ignore_cats')
                self._time_format = settings.get('time_format')

                # Clean old log maybe.
                if self._mode == 'clean':
                    # Make a backup.
                    bup = self._log_fn.replace('.log', '_old.log')
                    shutil.copyfile(self._log_fn, bup)
                    with open(self._log_fn, "w") as log:
                        pass

                # print("INF Stealing stdout and stderr!")
                self._console_stdout = sys.stdout
                self._console_stderr = sys.stderr
                sys.stdout = self
                sys.stderr = self
                print("INF Stolen stdout and stderr!")
            except Exception as e:
                print(f'ERR {sys.exc_info()}')
                self.stop()

    def stop(self):
        ''' Restores stdout/stderr. '''
        print("INF Restore stdout and stderr!")
        if self._console_stdout is not None:
            sys.stdout = self._console_stdout
        if self._console_stderr is not None:
            sys.stderr = self._console_stderr

    def write(self, message):
        ''' Write one. '''
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
                # self._console_stdout.write(f'ffff:{outmsg}')
                self._console_stdout.write(outmsg)
                self._console_stdout.flush()

                # Maybe write to file.
                if self._mode is not None:
                    with open(self._log_fn, "a") as log:
                        log.write(outmsg)

                if cat in self._notif_cats:
                    sublime.message_dialog(cmsg)
