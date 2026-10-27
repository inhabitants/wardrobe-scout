#!/usr/bin/env node
// Wardrobe Scout: build wardrobe-scout.zip, the plugin as ONE skill.
// Zero dependencies. Node 18+.
//
//   node pack/pack.mjs                     # writes wardrobe-scout.zip at the repo root
//   node pack/pack.mjs --out <file.zip>
//
// Skill marketplaces and the Claude app take one folder with one SKILL.md at its
// root. The plugin has three skills that hand over to each other by name and read
// ${CLAUDE_PLUGIN_ROOT}, which only exists inside a Claude Code plugin. So the
// package is pack/SKILL.md (which picks looks, hunt or list and defines
// ${SKILL_DIR}) plus the three skills as references, rewritten to point inside
// the package. The example's look photos travel with it, so the fictional list
// builds on its own.

import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { deflateRawSync } from 'node:zlib';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const NAME = 'wardrobe-scout';
const outArg = process.argv.indexOf('--out');
const OUT = outArg > -1 ? path.resolve(process.argv[outArg + 1]) : path.join(ROOT, `${NAME}.zip`);

const read = (rel) => readFileSync(path.join(ROOT, rel));
const stripFrontmatter = (text) => text.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n+/, '');

// Each exact swap must hit as many times as expected: if the skill text moved,
// stop instead of shipping a package that still points at the plugin.
const swapExact = (rel, text, from, to, expected = 1) => {
  const hits = text.split(from).length - 1;
  if (hits !== expected) throw new Error(`${rel}: expected ${expected} match(es), found ${hits}: ${from}`);
  return text.split(from).join(to);
};

const LEFTOVER = /CLAUDE_PLUGIN_ROOT|wardrobe-(looks|hunt|list)\b/;

const skill = (name, exact = []) => {
  const rel = `skills/wardrobe-${name}/SKILL.md`;
  let text = stripFrontmatter(read(rel).toString('utf8'));
  for (const [from, to, expected] of exact) text = swapExact(rel, text, from, to, expected);
  text = text
    .replaceAll('${CLAUDE_PLUGIN_ROOT}', '${SKILL_DIR}')
    .replace(/the `wardrobe-(looks|hunt|list)` skill/g, '`references/$1.md`')
    .replace(/`wardrobe-(looks|hunt|list)`/g, '`references/$1.md`');
  const left = text.match(LEFTOVER);
  if (left) throw new Error(`${rel}: plugin reference left behind: ${left[0]}`);
  return Buffer.from(text, 'utf8');
};

const template = (rel) => {
  if (!rel.endsWith('.md')) return read(rel);
  const text = read(rel).toString('utf8').replace(/the `wardrobe-(looks|hunt|list)` skill/g, '`references/$1.md`');
  const left = text.match(LEFTOVER);
  if (left) throw new Error(`${rel}: plugin reference left behind: ${left[0]}`);
  return Buffer.from(text, 'utf8');
};

const example = () => {
  const rel = 'examples/finds.example.json';
  const text = swapExact(rel, read(rel).toString('utf8'), '"../site/img/look-0', '"images/look-0', 3);
  JSON.parse(text);
  return Buffer.from(text, 'utf8');
};

const walk = (rel) => statSync(path.join(ROOT, rel)).isDirectory()
  ? readdirSync(path.join(ROOT, rel)).sort().flatMap((f) => walk(`${rel}/${f}`))
  : [rel];

const entries = [
  ['SKILL.md', read('pack/SKILL.md')],
  ['references/looks.md', skill('looks', [
    ['written by wardrobe-hunt', 'written by references/hunt.md'],
    ['written by wardrobe-list', 'written by references/list.md'],
  ])],
  ['references/hunt.md', skill('hunt', [
    ['${CLAUDE_PLUGIN_ROOT}/skills/wardrobe-hunt/stores.md', '${SKILL_DIR}/references/stores.md'],
  ])],
  ['references/list.md', skill('list')],
  ['references/stores.md', read('skills/wardrobe-hunt/stores.md')],
  ['scripts/generate_look.py', read('scripts/generate_look.py')],
  ['scripts/build_list.py', read('scripts/build_list.py')],
  ...walk('templates').map((rel) => [rel, template(rel)]),
  ['examples/finds.example.json', example()],
  ...['01', '02', '03'].map((n) => [`examples/images/look-${n}.webp`, read(`site/img/look-${n}.webp`)]),
  ['LICENSE', read('LICENSE')],
  ['DISCLAIMER.md', read('DISCLAIMER.md')],
];

const CRC = new Uint32Array(256).map((_, n) => {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c >>> 0;
});
const crc32 = (buf) => {
  let c = 0xffffffff;
  for (const b of buf) c = CRC[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
};

const now = new Date();
const dosTime = (now.getHours() << 11) | (now.getMinutes() << 5) | (now.getSeconds() >> 1);
const dosDate = ((now.getFullYear() - 1980) << 9) | ((now.getMonth() + 1) << 5) | now.getDate();

const locals = [];
const centrals = [];
let offset = 0;
for (const [rel, data] of entries) {
  const packed = deflateRawSync(data, { level: 9 });
  const name = Buffer.from(`${NAME}/${rel}`, 'utf8');
  const crc = crc32(data);

  const local = Buffer.alloc(30);
  local.writeUInt32LE(0x04034b50, 0); local.writeUInt16LE(20, 4); local.writeUInt16LE(0x0800, 6);
  local.writeUInt16LE(8, 8); local.writeUInt16LE(dosTime, 10); local.writeUInt16LE(dosDate, 12);
  local.writeUInt32LE(crc, 14); local.writeUInt32LE(packed.length, 18); local.writeUInt32LE(data.length, 22);
  local.writeUInt16LE(name.length, 26); local.writeUInt16LE(0, 28);
  locals.push(local, name, packed);

  const central = Buffer.alloc(46);
  central.writeUInt32LE(0x02014b50, 0); central.writeUInt16LE(20, 4); central.writeUInt16LE(20, 6);
  central.writeUInt16LE(0x0800, 8); central.writeUInt16LE(8, 10); central.writeUInt16LE(dosTime, 12);
  central.writeUInt16LE(dosDate, 14); central.writeUInt32LE(crc, 16); central.writeUInt32LE(packed.length, 20);
  central.writeUInt32LE(data.length, 24); central.writeUInt16LE(name.length, 28);
  central.writeUInt32LE(offset, 42);
  centrals.push(central, name);

  offset += local.length + name.length + packed.length;
}

const cd = Buffer.concat(centrals);
const end = Buffer.alloc(22);
end.writeUInt32LE(0x06054b50, 0); end.writeUInt16LE(entries.length, 8); end.writeUInt16LE(entries.length, 10);
end.writeUInt32LE(cd.length, 12); end.writeUInt32LE(offset, 16);

writeFileSync(OUT, Buffer.concat([...locals, cd, end]));
console.log(`${OUT}  (${entries.length} files, ${(statSync(OUT).size / 1024).toFixed(0)} KB)`);
entries.forEach(([rel]) => console.log(`  ${NAME}/${rel}`));
