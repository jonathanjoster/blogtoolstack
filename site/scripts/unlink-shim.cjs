// Workaround for this sandboxed environment: the connected-folder mount blocks
// the unlink syscall (EPERM), even for files this same process just created
// (e.g. astro build's own temporary dist/pages/*.mjs SSR entry chunks that it
// deletes as a post-build cleanup step). That cleanup failure is not a real
// build failure -- the actual site output (dist/index.html etc.) is already
// written by the time this runs. Swallow ONLY EPERM unlink errors so the
// build process can report success normally; every other error still throws.
const fs = require('node:fs');

const realUnlink = fs.unlink.bind(fs);
fs.unlink = function (path, callback) {
  realUnlink(path, (err) => {
    if (err && err.code === 'EPERM') {
      console.error(`[unlink-shim] ignoring EPERM unlinking ${path} (known sandbox limitation)`);
      return callback(null);
    }
    callback(err);
  });
};

const realUnlinkSync = fs.unlinkSync.bind(fs);
fs.unlinkSync = function (path) {
  try {
    return realUnlinkSync(path);
  } catch (err) {
    if (err && err.code === 'EPERM') {
      console.error(`[unlink-shim] ignoring EPERM unlinking ${path} (known sandbox limitation)`);
      return undefined;
    }
    throw err;
  }
};

if (fs.promises && fs.promises.unlink) {
  const realUnlinkPromise = fs.promises.unlink.bind(fs.promises);
  fs.promises.unlink = async function (path) {
    try {
      return await realUnlinkPromise(path);
    } catch (err) {
      if (err && err.code === 'EPERM') {
        console.error(`[unlink-shim] ignoring EPERM unlinking ${path} (known sandbox limitation)`);
        return undefined;
      }
      throw err;
    }
  };
}
