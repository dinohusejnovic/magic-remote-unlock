#!/bin/sh
# Remove magic-remote-unlock from a rooted LG webOS TV and restore stock behaviour.
# Usage: ./uninstall.sh <tv-ip> [ssh-user]
set -e
TV="${1:?usage: $0 <tv-ip> [ssh-user]}"
USER="${2:-root}"
ssh "$USER@$TV" '
rm -f /var/lib/webosbrew/init.d/50-magic-remote-unlock
echo "Removed boot script. Reboot the TV to restore the stock lginput2"
echo "(or: systemctl stop lginput2; umount /usr/sbin/lginput2; systemctl start lginput2)."
'
