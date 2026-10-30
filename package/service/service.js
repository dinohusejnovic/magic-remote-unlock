// Installs / removes the boot script that unlocks older Magic Remotes.
// Needs root: the Homebrew Channel elevates this service (rootRequired).
const Service = require('webos-service');
const fs = require('fs');
const path = require('path');
const cp = require('child_process');

const service = new Service('io.github.dinohusejnovic.magicremoteunlock.service');

const SCRIPT_SRC = path.join(__dirname, '50-magic-remote-unlock');
const INIT_DIR = '/var/lib/webosbrew/init.d';
const SCRIPT_DST = path.join(INIT_DIR, '50-magic-remote-unlock');
const LOG = '/tmp/magic-remote-unlock.log';
const MRCU_INFO = '/mnt/lg/cmn_data/mrcu/mrcu1.info';

const isRoot = () => typeof process.getuid === 'function' && process.getuid() === 0;
const read = (f) => { try { return fs.readFileSync(f, 'utf8'); } catch (e) { return ''; } };

function status() {
  const mrcu = read(MRCU_INFO);
  const m = /^Name = (.*)$/m.exec(mrcu);
  return {
    returnValue: true,
    root: isRoot(),
    enabled: fs.existsSync(SCRIPT_DST),
    active: / \/usr\/sbin\/lginput2 /.test(read('/proc/mounts')),
    pairedRemote: m ? m[1].trim() : null,
    log: read(LOG).split('\n').slice(-12).join('\n').trim(),
  };
}

function fail(message, text, code) {
  message.respond({ returnValue: false, errorText: text, errorCode: code });
}

service.register('status', (message) => message.respond(status()));

service.register('enable', (message) => {
  if (!isRoot()) return fail(message, 'Service is not running as root', 1);
  try {
    fs.mkdirSync(INIT_DIR, { recursive: true });
    fs.copyFileSync(SCRIPT_SRC, SCRIPT_DST);
    fs.chmodSync(SCRIPT_DST, 0o755);
    // The script detaches itself; it restarts lginput2 once the patch is in place.
    cp.spawn(SCRIPT_DST, [], { detached: true, stdio: 'ignore' }).unref();
  } catch (e) {
    return fail(message, String(e), 2);
  }
  return message.respond(status());
});

service.register('disable', (message) => {
  if (!isRoot()) return fail(message, 'Service is not running as root', 1);
  try {
    fs.rmSync(SCRIPT_DST, { force: true });
  } catch (e) {
    return fail(message, String(e), 2);
  }
  // The running patch stays active until the next reboot.
  return message.respond(status());
});
