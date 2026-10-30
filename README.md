# magic-remote-unlock

Use an older LG Magic Remote, like the MR20, on a 2025 webOS TV. Pointer included.

I have an LG C5 and didn't like the remote it came with. My old MR20 has Bluetooth and the TV has
Bluetooth, so it should just work. It doesn't: the TV says "Registering..." and then "This remote
is not supported by this TV." This repo gets rid of that message.

Tested on one TV (C5, webOS 10.3.1) with one remote (MR20). See [Other remotes](#other-remotes).

## What's actually going on

Nothing is wrong with Bluetooth. The Magic Remote service on the TV, `/usr/sbin/lginput2`, keeps a
table of remote names and the year each one came out, and it refuses anything older than the
TV's "support start year". On 2025 sets that year is 2025. The log on the TV says so directly
(`/tmp/var/log/dbg-log`):

```
remote Support Start Year: 2025
[lginput_util_isNewYearRemote] Fail: LGE MR20 is old mrcu! (2020)
Only specific Magic Remote model can be paired.
```

The firmware already knows the MR20 by name and has the pointer code for it. Only that year
check gets in the way.

## What this does

At boot it copies the TV's own `lginput2` to `/tmp`, bumps the year for the remotes you list
(MR20 by default) from 2020 to 2025 in that copy, bind-mounts the copy over `/usr/sbin/lginput2`
and restarts the service.

- The system partition is never written to. Reboot without the script and the TV is stock again.
- No LG binary is included here. The patch is applied to your TV's own file, and it finds the
  table entry by searching for the remote's name instead of using a fixed offset. If a firmware
  update changes the layout, the script finds nothing, patches nothing and leaves the TV alone.

## Install

You need a rooted TV with the [Homebrew Channel](https://www.webosbrew.org/) installed. The
patch script needs `python3`, which webOS 10 has.

**Through the Homebrew Channel** (once it's listed there): search for "Magic Remote Unlock",
install it, open it and press Enable. The package needs root, so the Homebrew Channel will
offer to elevate its service on install.

**By hand over SSH:**

```sh
./install.sh <tv-ip>
ssh root@<tv-ip> /var/lib/webosbrew/init.d/50-magic-remote-unlock   # apply now, or just reboot
```

Then pair the remote. It can't be connected to another device at the time (forget it there
first). Point it at the TV and hold Home + Back for about five seconds, or hold the wheel. The
TV keeps one Magic Remote at a time, so pairing the MR20 replaces the one that came with it.
Pair that one again later the usual way if you want it back.

## Uninstall

Remove the app in the Homebrew Channel, or run `./uninstall.sh <tv-ip>`, then reboot.

## Other remotes

Only the MR20 has been tested. The firmware's table also lists MR19, MR21 through MR25 and the
2018 to 2019 remotes. To try one, put its name on its own line in
`/var/lib/webosbrew/magic-remote-unlock.conf` on the TV, for example `LGE MR21`, and reboot. If it
works (or doesn't) for you, please open an issue with the TV model and webOS version.

The script logs to `/tmp/magic-remote-unlock.log` on the TV.

## Building the package

```sh
python3 tools/build_ipk.py     # writes dist/*.ipk and dist/*.manifest.json
```

It needs nothing but Python 3. `tools/make_icons.py` regenerates the icons.

## Built with AI

I used Claude (Claude Code, from Anthropic) to build this. It did the digging through
`lginput2` over SSH on my TV to find the year check, wrote the boot script and the Homebrew
package, and wrote the first version of this README. I supplied the TV and the remote, did the
pairing, and checked on the real hardware that the MR20 pairs and works, and that it survives
a reboot. Treat it with the same caution as any script that patches a system service on your
TV, and read `scripts/50-magic-remote-unlock` before running it. It's short.

## Caveats

It changes how a system service behaves on your own TV, so use it at your own risk. The Homebrew
startup failsafe disables customizations if a boot crashes. This project isn't affiliated with
or endorsed by LG.

MIT licensed.
