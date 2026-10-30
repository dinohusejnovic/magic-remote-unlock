Adds **Magic Remote Unlock** (`io.github.dinohusejnovic.magicremoteunlock`).

2025 webOS TVs reject older Magic Remotes at pairing ("This remote is not supported by this TV."). The cause is a
model-year check in `lginput2` (`lginput_util_isNewYearRemote`), not a Bluetooth limitation. The app installs a
`/var/lib/webosbrew/init.d` script that raises the year of older Bluetooth Magic Remote entries (MR18 to MR24) in a runtime copy of `lginput2` and
bind-mounts it. Nothing on the system partition is written, and nothing from LG is redistributed. If the table layout
isn't found, it does nothing.

Source: https://github.com/dinohusejnovic/magic-remote-unlock

**AI disclosure:** I used Claude (Claude Code, Anthropic) to build this. It reverse-engineered the year check in
`lginput2` over SSH on my TV, and wrote the boot script, the service and the packaging. I supplied the hardware and
tested on it: pairing an MR20 on an LG C5 (webOS 10.3.1), a reboot to confirm the boot script re-applies the patch, and
installing, elevating and toggling the package through the system installer. I am responsible for the code.

Testing is limited to one TV and one remote (MR20); the other models are unlocked by the same table change but untested. `rootRequired: true` because the service writes to `/var/lib/webosbrew/init.d`.
