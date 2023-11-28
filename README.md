# SbotALogger

A simple logger for use by the sbot family of plugins. It works in conjunction with `def slog(str, message)` in
`sbot_common.py`. If this plugin is imported, slog() uses it otherwise slog() writes to stdout.

Built for ST4 on Windows and Linux.

- Intercepts the ST console write and copies to a file.
- Adds timestamp and (three letter) category.
- If the category appear in `notify_cats`, a dialog is presented. Those in `ignore_cats` are ignored.
- The 'A' in the name enforces loading before other Sbot components.
- Log files are in `%data_dir%\Packages\User\.SbotStore`.

## Exceptions

These are the categories of exceptions in the Sublime python implementation:
- User-handled with the standard `try/except` mechanism.
- Plugin command syntax and functional errors are intercepted and logged by a custom `sys.excepthook` in `sbot_logger.py`.
- Errors in scripts that are executed by sublime internals e.g. `load_module()` are not caught by the above hook but go straight
  to stdout. It *works* but is not as tightly integrated as preferred.

## Commands

None


## Settings

| Setting            | Description                     | Options                                       |
| :--------          | :-------                        | :------                                       |
| file_size          | Max log file before rollover    | in kbytes (0 means disabled)                  |
| ignore_cats        | Ignore these user categories    | comma separated strings                       |
| notify_cats        | Notify user if in categories    | comma separated strings                       |
