import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import esbuild from 'esbuild';
import postcss from 'postcss';
import tailwindcss from 'tailwindcss';
import autoprefixer from 'autoprefixer';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const outDir = join(root, 'dist');
const assetsDir = join(outDir, 'assets');

process.chdir(root);

async function buildStyles() {
  const input = await readFile(join(root, 'src/app/styles.css'), 'utf8');
  const result = await postcss([tailwindcss(join(root, 'tailwind.config.js')), autoprefixer]).process(input, {
    from: join(root, 'src/app/styles.css'),
    to: join(assetsDir, 'styles.css')
  });
  await writeFile(join(assetsDir, 'styles.css'), result.css);
}

async function buildHtml() {
  const html = await readFile(join(root, 'index.html'), 'utf8');
  await writeFile(join(outDir, 'index.html'), html);
}

async function copyPublic() {
  await cp(join(root, 'public'), outDir, { recursive: true, force: true });
}

async function buildScripts() {
  const entry = await readFile(join(root, 'src/app/main.jsx'), 'utf8');
  await esbuild.build({
    stdin: {
      contents: entry,
      resolveDir: join(root, 'src/app'),
      sourcefile: 'main.jsx',
      loader: 'jsx'
    },
    bundle: true,
    format: 'esm',
    outfile: join(assetsDir, 'app.js'),
    jsx: 'automatic',
    sourcemap: false,
    minify: true,
    logLevel: 'info'
  });
}

await rm(outDir, { recursive: true, force: true });
await mkdir(assetsDir, { recursive: true });
await copyPublic();
await Promise.all([buildHtml(), buildStyles(), buildScripts()]);

console.log(`Client build written to ${dirname(assetsDir)}`);
