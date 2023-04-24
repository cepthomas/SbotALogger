# SbotALogger

A tool to make debugging plugins a bit easier.

- Intercepts the ST console write and copies to a file.
- Adds (optional) timestamp.
- Examines the first word to identify as a user supplied category. These are fixed at
  four characters to match the slog(cat, message) function in [SbotCommon](https://github.com/cepthomas/SbotCommon).
  SbotCommon slog() is not required but works nicely with this plugin.
- If the category appear in `notify_cats`, a dialog is presented. Those in `ignore_cats` are ignored.
- Captures unhandled exceptions (e.g. ST internal) and notifies the user. This is done once - assumes you have to go fix your problem before continuing.
  Note that this doesn't show up until the current view loses focus.
- The 'A' in the name enforces loading before other Sbot components.
- Log files are in `%data_dir%\Packages\User\.SbotStore`.


Built for ST4 on Windows and Linux.

## Commands

None


## Settings

| Setting            | Description                     | Options                                                               |
| :--------          | :-------                        | :------                                                               |
| `file_size`        | Max log file before rollover    | in kbytes (0 means disabled)                                          |
| `ignore_cats`      | Ignore these user categories    | comma separated strings                                               |
| `notify_cats`      | Notify user if in categories    | comma separated strings                                               |
