# SbotLogger

Intercepts the console write and copies to a file. Adds optional timestamp.
Examines the first word to identify as a user supplied category.

Simple categories by prefacing message with meaningful strings. If they appear in
`notify_cats`, a dialog is presented. Those in `ignore_cats` are ignored.

## Commands
None


## Settings
| Setting            | Description                     | Options   |
| :--------          | :-------                        | :------   |
| `file_path`        | Full path to the log file       | if empty default is `%data_dir%\Packages\User\SbotStore\sbot.log`  |
| `mode`             | File add mode                   | `append` OR `clean` (on start) OR `off` |
| `time_format`      | How to format (strftime)        | `strftime format` OR empty (default timestamp) OR null (no timestamp) |
| `ignore_cats`      | Ignore these user categories    | comma separated strings |
| `notify_cats`      | Notify user if in categories    | comma separated strings |
