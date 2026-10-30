#!/bin/sh
# Install magic-remote-unlock onto a rooted LG webOS TV over SSH.
# Usage: ./install.sh <tv-ip> [ssh-user]      (default user: root)
set -e
TV="${1:?usage: $0 <tv-ip> [ssh-user]}"
USER="${2:-root}"
DIR="$(cd "$(dirname "$0")" && pwd)"
DEST=/var/lib/webosbrew/init.d/50-magic-remote-unlock

ssh "$USER@$TV" "mkdir -p /var/lib/webosbrew/init.d && cat > $DEST && chmod 755 $DEST" < "$DIR/scripts/50-magic-remote-unlock"
echo "Installed $DEST on $TV."
echo "Run it now with:  ssh $USER@$TV $DEST     (or just reboot the TV)"
echo "Then put your remote in pairing mode. Log: /tmp/magic-remote-unlock.log on the TV."
