# SbotLogger

Intercepts the console write and copies to a file. Adds optional timestamp.




## Commands
None


## Settings
| Setting            | Description                     | Options   |
| :--------          | :-------                        | :------   |
| `file_path`        | Full path to the log file       | if empty default is `%data_dir%\Packages\User\SbotStore\sbot.log`  |
| `mode`             | File add mode                   | `append` OR `clean` (on start) OR `off` |
| `time_format`      | How to format (strftime)        | `strftime format` OR empty (no timestamp) |
| `notify`           | Notify user if text begins with | comma separated strings |
