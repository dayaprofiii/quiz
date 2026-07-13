import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { spawn } from 'node:child_process';

const root = process.cwd();
const python = existsSync(join(root, '.venv', 'Scripts', 'python.exe'))
  ? join(root, '.venv', 'Scripts', 'python.exe')
  : 'python';

const child = spawn(python, ['-m', 'pytest', '-p', 'no:cacheprovider', 'backend/tests'], {
  cwd: root,
  env: {
    ...process.env,
    PYTHONPATH: join(root, 'backend'),
    AUTO_CREATE_DB: 'false',
    SEED_DEMO_DATA: 'false'
  },
  stdio: 'inherit',
  shell: false
});

child.on('exit', (code) => process.exit(code ?? 0));
