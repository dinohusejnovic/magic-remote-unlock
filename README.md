# magic-remote-unlock

Use an **older LG Magic Remote (e.g. MR20) with a 2025+ webOS TV** (tested: C5, webOS 10.3.1) —
including the pointer.

2025 TVs refuse older remotes during pairing: the TV shows *"Registering…"* and then
*"This remote is not supported by this TV."* This is a software policy, not a Bluetooth
incompatibility.

## Why it happens

The Magic Remote service (`/usr/sbin/lginput2`, `com.webos.service.mrcu`) contains a table of
known remote names, each with a model year. On pairing it calls `lginput_util_isNewYearRemote`,
which fails any remote older than the TV's *support start year* (2025 on 2025 models):

```
UTIL:       remote Support Start Year: 2025
NEW_REMOTE: [lginput_util_isNewYearRemote] Fail: LGE MR20 is old mrcu! (2020)
DEVMNGR:    Only specific Magic Remote model can be paired.
NOTI:       createToast ... "This remote is not supported by this TV."
```

(See `/tmp/var/log/dbg-log` on the TV.) The firmware already knows the MR20's name and has the
pointer/motion code for it; only the year gate stops it.

## What this does

A boot script for the [Homebrew Channel](https://github.com/webosbrew/webos-homebrew-channel)
`init.d` hook. At boot it:

1. copies the TV's own `lginput2` to `/tmp`,
2. locates the table entry for each configured remote name by pattern and raises its year to 2025
   (**no LG binary is shipped in this repo**, and the offset isn't hard-coded, so it survives
   firmware updates unless the table layout changes — in that case it skips and leaves the TV stock),
3. bind-mounts the copy over `/usr/sbin/lginput2` and restarts the service.

The read-only system partition is never modified; the change lives in RAM, so a reboot without
the script (or `umount`) returns the TV to stock.

## Requirements

- Rooted webOS TV with the Homebrew Channel (provides `/var/lib/webosbrew/init.d`) and SSH access
- `python3` on the TV (present on webOS 10)

## Install

```sh
./install.sh <tv-ip>          # copies scripts/50-magic-remote-unlock to the TV's init.d
ssh root@<tv-ip> /var/lib/webosbrew/init.d/50-magic-remote-unlock   # apply now (or reboot)
```

Then pair the remote: it must not be connected to another device (remove it there first), and be
in pairing mode — point it at the TV and hold **Home + Back** (or the wheel/OK) for ~5 s.
Pairing a new remote may replace the one currently paired.

Unlock other remotes by listing their names (one per line) in
`/var/lib/webosbrew/magic-remote-unlock.conf`, e.g. `LGE MR19`, `LGE MR21`. Only **MR20** has been
tested. Names come from the table in `lginput2`; `LGE MR20` is the BLE name the remote advertises.

Log: `/tmp/magic-remote-unlock.log` on the TV.

## Uninstall

```sh
./uninstall.sh <tv-ip>   # then reboot
```

## Caveats

- Use at your own risk; this modifies the behaviour of a system service on your own TV. The
  Homebrew startup failsafe will disable customizations if a boot crashes.
- Tested on one model/firmware only. Reports for other TVs and remotes welcome.
- Not affiliated with or endorsed by LG.
