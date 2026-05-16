// start-mkt.js — Single Railway service runtime
// Spawns API server + BullMQ worker in parallel
// Zero external dependencies (Node built-in child_process)

const { spawn } = require('child_process');
const path = require('path');

const procs = [
  { name: 'api',    cmd: 'node', args: [path.join(__dirname, 'apps/marketing-api/dist/server.js')] },
  { name: 'worker', cmd: 'node', args: [path.join(__dirname, 'apps/marketing-worker/dist/worker.js')] },
];

const children = [];
let shuttingDown = false;

for (const p of procs) {
  const child = spawn(p.cmd, p.args, {
    stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env },
  });

  // Prefix stdout/stderr with process name
  child.stdout.on('data', (d) => {
    for (const line of d.toString().split('\n').filter(Boolean)) {
      process.stdout.write(`[${p.name}] ${line}\n`);
    }
  });
  child.stderr.on('data', (d) => {
    for (const line of d.toString().split('\n').filter(Boolean)) {
      process.stderr.write(`[${p.name}] ${line}\n`);
    }
  });

  child.on('exit', (code, signal) => {
    console.error(`[${p.name}] exited code=${code} signal=${signal}`);
    if (!shuttingDown) {
      // If API dies, restart it after 3s; if worker dies, restart it after 5s
      const delay = p.name === 'api' ? 3000 : 5000;
      console.error(`[${p.name}] restarting in ${delay}ms...`);
      setTimeout(() => {
        if (!shuttingDown) {
          const idx = children.indexOf(child);
          const restarted = spawn(p.cmd, p.args, { stdio: ['ignore', 'pipe', 'pipe'], env: { ...process.env } });
          restarted.stdout.on('data', (d) => {
            for (const line of d.toString().split('\n').filter(Boolean)) process.stdout.write(`[${p.name}] ${line}\n`);
          });
          restarted.stderr.on('data', (d) => {
            for (const line of d.toString().split('\n').filter(Boolean)) process.stderr.write(`[${p.name}] ${line}\n`);
          });
          if (idx !== -1) children[idx] = restarted;
          else children.push(restarted);
        }
      }, delay);
    }
  });

  children.push(child);
  console.log(`[runtime] started ${p.name} pid=${child.pid}`);
}

// Graceful shutdown
function shutdown(sig) {
  if (shuttingDown) return;
  shuttingDown = true;
  console.log(`[runtime] ${sig} received, shutting down...`);
  for (const c of children) {
    try { c.kill('SIGTERM'); } catch (_) {}
  }
  setTimeout(() => {
    for (const c of children) {
      try { c.kill('SIGKILL'); } catch (_) {}
    }
    process.exit(0);
  }, 10000);
}

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

console.log('[runtime] 45cm Marketing Runtime started (api + worker)');
