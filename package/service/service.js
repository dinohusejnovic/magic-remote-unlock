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
const NOPOINTER_FLAG = '/var/lib/webosbrew/magic-remote-unlock.nopointer';
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
    pointerDisabled: fs.existsSync(NOPOINTER_FLAG),
    active: / \/usr\/sbin\/lginput2 /.test(read('/proc/mounts')),
    pairedRemote: m ? m[1].trim() : null,
    log: read(LOG).split('\n').slice(-12).join('\n').trim(),
  };
}

function fail(message, text, code) {
  message.respond({ returnValue: false, errorText: text, errorCode: code });
}

function installScript() {
  fs.mkdirSync(INIT_DIR, { recursive: true });
  fs.copyFileSync(SCRIPT_SRC, SCRIPT_DST);
  fs.chmodSync(SCRIPT_DST, 0o755);
}

service.register('status', (message) => message.respond(status()));

service.register('enable', (message) => {
  if (!isRoot()) return fail(message, 'Service is not running as root', 1);
  try {
    installScript();
    // The script detaches itself; --reapply makes the running patch match the pointer setting.
    cp.spawn(SCRIPT_DST, ['--reapply'], { detached: true, stdio: 'ignore' }).unref();
  } catch (e) {
    return fail(message, String(e), 2);
  }
  return message.respond(status());
});

// Keep the remote on Bluetooth but turn the on-screen pointer (and wheel) off, or back on.
service.register('setPointer', (message) => {
  if (!isRoot()) return fail(message, 'Service is not running as root', 1);
  const disable = !(message.payload && message.payload.enabled);
  try {
    if (disable) fs.writeFileSync(NOPOINTER_FLAG, '');
    else fs.rmSync(NOPOINTER_FLAG, { force: true });
    if (fs.existsSync(SCRIPT_DST)) {
      installScript();  // make sure the boot copy is the packaged (current) version
      cp.spawn(SCRIPT_DST, ['--reapply'], { detached: true, stdio: 'ignore' }).unref();
    }
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
