# SbotALogger

- The 'A' is to force this to load first so logging is set up early.
- Intercepts the console write and copies to a file.
- Adds optional timestamp.
- Examines the first word to identify as a user supplied category. These are fixed at
  four characters to match the slog(cat, message) function in [SbotCommon](https://github.com/cepthomas/SbotCommon).
- If the category appear in `notify_cats`, a dialog is presented. Those in `ignore_cats` are ignored.
- Displays the stack trace from unhandled exceptions once (assumes you have to go fix your problem before continuing).
  Note that this doesn't show up until the current view loses focus.


Built for ST4 on Windows and Linux.

## Commands
None


## Settings
| Setting            | Description                     | Options   |
| :--------          | :-------                        | :------   |
| `file_path`        | Full path to the log file       | if empty default is `%data_dir%\Packages\User\SbotStore` |
| `mode`             | File add mode                   | `append` OR `clean` (on start) OR `off` |
| `time_format`      | How to format (strftime)        | `strftime format` OR empty (default timestamp) OR null (no timestamp) |
| `ignore_cats`      | Ignore these user categories    | comma separated strings |
| `notify_cats`      | Notify user if in categories    | comma separated strings |
