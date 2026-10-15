#!/usr/bin/env node
/**
 * Regenerates the "Hex (approx.)" column in specs/foundations/color.md from the
 * HSL triplets in the same tables, so the spec cannot drift from tokens.css.
 * Usage: node scripts/spec-hex.js
 */
const fs = require("fs");
const path = require("path");

const FILE = path.resolve(__dirname, "../specs/foundations/color.md");

function hslToHex(h, s, l) {
  s /= 100;
  l /= 100;
  const a = s * Math.min(l, 1 - l);
  const f = (n) => {
    const k = (n + h / 30) % 12;
    const c = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
    return Math.round(255 * c).toString(16).padStart(2, "0");
  };
  return `#${f(0)}${f(8)}${f(4)}`;
}

const out = fs
  .readFileSync(FILE, "utf8")
  .split("\n")
  .map((line) => {
    // | `--ds-x` | `H S% L%` | `#hex` | usage |
    const m = line.match(/^\|\s*`--ds-[^`]+`\s*\|\s*`([\d.]+) ([\d.]+)% ([\d.]+)%`\s*\|\s*`#[0-9a-fA-F.]+`/);
    if (!m) return line;
    return line.replace(/`#[0-9a-fA-F.]+`/, `\`${hslToHex(+m[1], +m[2], +m[3])}\``);
  })
  .join("\n");

fs.writeFileSync(FILE, out);
console.log("Updated hex columns in specs/foundations/color.md");
