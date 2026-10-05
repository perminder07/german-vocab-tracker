# Scheduling `update.sh` on macOS

`update.sh` is safe to run from anywhere (it changes into its own folder, logs to
`logs/update.log`, and stops on the first error). Run it by hand with `./update.sh`.

## Why launchd instead of cron

cron skips a job if the Mac is asleep at the scheduled time. A launchd job with
`StartCalendarInterval` runs the missed job after the Mac wakes (but not if it was powered off).

## Setup

1. Keep the repo outside macOS-protected folders if you can (e.g. `~/code/german-vocab-tracker`
   rather than Documents/Desktop). Jobs started by launchd can be denied access there.
2. Save as `~/Library/LaunchAgents/com.example.german-vocab-tracker.plist`
   (change the path and the label):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.example.german-vocab-tracker</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/ABSOLUTE/PATH/TO/german-vocab-tracker/update.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>20</integer>
        <key>Minute</key><integer>0</integer>
    </dict>
</dict>
</plist>
```

3. Load it, and trigger one run to test:

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.example.german-vocab-tracker.plist
launchctl kickstart -k gui/$(id -u)/com.example.german-vocab-tracker
tail -f /ABSOLUTE/PATH/TO/german-vocab-tracker/logs/update.log
```

Unload with `launchctl bootout gui/$(id -u)/com.example.german-vocab-tracker`.
If you use a virtualenv, create it as `.venv` inside the repo and `update.sh` picks it up.
Git pushes need credentials that work non-interactively (SSH key or a token stored in the
macOS keychain); use a fine-grained token limited to this one repository.
