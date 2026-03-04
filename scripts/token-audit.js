#!/usr/bin/env node

/**
 * Token Audit Script
 * Scans all CSS and TSX files for hardcoded visual values that should
 * use design tokens from tokens.css instead.
 *
 * Usage:
 *   node scripts/token-audit.js          # Full audit
 *   node scripts/token-audit.js --fix    # Show suggestions only
 *
 * Exit codes:
 *   0 — No errors (warnings may exist)
 *   1 — Errors found (hardcoded colors, spacing, etc.)
 */

const fs = require("fs");
const path = require("path");

// ─── Configuration ────────────────────────────────────────────────────────────

const ROOT = path.resolve(__dirname, "..");

const SCAN_DIRS = ["app", "components"];

const SCAN_EXTENSIONS = [".css", ".scss", ".tsx", ".jsx"];

// Files/patterns to skip
const SKIP_PATTERNS = [
  /node_modules/,
  /\.next/,
  /tokens\.css$/,       // Don't audit the token file itself
  /globals\.css$/,      // Don't audit the upstream variable definitions
  /tailwind\.config/,   // Don't audit Tailwind config
];

// ─── Token Maps ───────────────────────────────────────────────────────────────

// Hardcoded hex colors → token suggestions
const COLOR_HEX_MAP = {
  "#fff":     "bg-background or bg-card (Tailwind), var(--color-bg) (CSS)",
  "#ffffff":  "bg-background or bg-card (Tailwind), var(--color-bg) (CSS)",
  "#000":     "text-foreground (Tailwind), var(--color-text) (CSS)",
  "#000000":  "text-foreground (Tailwind), var(--color-text) (CSS)",
  "#292a2e":  "text-foreground (Tailwind), var(--color-text) (CSS)",
  "#949494":  "text-muted-foreground (Tailwind), var(--color-text-muted) (CSS)",
};

// Tailwind classes with hardcoded colors (not using semantic tokens)
const HARDCODED_TW_COLORS = [
  // Raw Tailwind color classes that should use semantic tokens
  { pattern: /\btext-(?:red|green|blue|yellow|orange|pink|purple|indigo|cyan|teal|emerald|violet|fuchsia|rose|amber|sky)-\d{2,3}\b/g,
    suggestion: (match) => {
      if (match.includes("green")) return `Use text-success → hsl(var(--color-success-text))`;
      if (match.includes("red"))   return `Use text-destructive → hsl(var(--color-destructive))`;
      return `Replace ${match} with a semantic color token`;
    },
    level: "error",
  },
  { pattern: /\bbg-(?:red|green|blue|yellow|orange|pink|purple|indigo|cyan|teal|emerald|violet|fuchsia|rose|amber|sky)-\d{2,3}\b/g,
    suggestion: (match) => `Replace ${match} with a semantic bg token (bg-primary, bg-secondary, bg-muted, bg-destructive)`,
    level: "error",
  },
  { pattern: /\bborder-(?:red|green|blue|yellow|orange|pink|purple|indigo|cyan|teal|emerald|violet|fuchsia|rose|amber|sky)-\d{2,3}\b/g,
    suggestion: (match) => `Replace ${match} with border-border or border-input`,
    level: "error",
  },
  // bg-white / bg-black should use semantic tokens
  { pattern: /\bbg-white\b/g,
    suggestion: () => "Use bg-background or bg-card instead of bg-white",
    level: "error",
  },
  { pattern: /\bbg-black\b/g,
    suggestion: () => "Use bg-foreground or bg-inverse instead of bg-black",
    level: "error",
  },
  // text-white / text-black should use semantic tokens
  { pattern: /\btext-white\b/g,
    suggestion: () => "Use text-primary-foreground or text-destructive-foreground instead of text-white",
    level: "error",
  },
  { pattern: /\btext-black\b/g,
    suggestion: () => "Use text-foreground instead of text-black",
    level: "error",
  },
  // dark: overrides for colors indicate missing semantic token
  { pattern: /\bdark:text-(?:red|green|blue|yellow|orange|pink|purple|indigo|cyan|teal|emerald|violet|fuchsia|rose|amber|sky)-\d{2,3}\b/g,
    suggestion: (match) => {
      if (match.includes("green")) return `Remove ${match} — use text-success which handles dark mode automatically`;
      if (match.includes("red"))   return `Remove ${match} — use text-destructive which handles dark mode automatically`;
      return `Remove ${match} — semantic tokens handle dark mode automatically`;
    },
    level: "error",
  },
];

// CSS property hardcoded values (for .css/.scss files)
const CSS_HARDCODED_RULES = [
  // Hex colors in CSS
  { pattern: /(?:color|background|background-color|border-color|fill|stroke)\s*:\s*(#[0-9a-fA-F]{3,8})\b/g,
    suggestion: (match, value) => `Replace ${value} with var(--color-*) token`,
    level: "error",
  },
  // rgb/rgba in CSS
  { pattern: /(?:color|background|background-color|border-color)\s*:\s*(rgba?\([^)]+\))/g,
    suggestion: (match, value) => `Replace ${value} with var(--color-*) token`,
    level: "error",
  },
  // Hardcoded px spacing in CSS (not in var() or calc())
  { pattern: /(?:padding|margin|gap|top|right|bottom|left)\s*:\s*(\d+px)\b/g,
    suggestion: (match, value) => `Replace ${value} with var(--space-*) or var(--ds-space-*) token`,
    level: "error",
  },
  // Hardcoded font-size in CSS
  { pattern: /font-size\s*:\s*(\d+(?:\.\d+)?(?:px|rem))\b/g,
    suggestion: (match, value) => `Replace ${value} with var(--font-size-*) token`,
    level: "error",
  },
  // Hardcoded font-weight in CSS
  { pattern: /font-weight\s*:\s*(\d{3})\b/g,
    suggestion: (match, value) => `Replace ${value} with var(--font-weight-*) token`,
    level: "warning",
  },
  // Hardcoded border-radius in CSS
  { pattern: /border-radius\s*:\s*(\d+(?:\.\d+)?(?:px|rem))\b/g,
    suggestion: (match, value) => `Replace ${value} with var(--radius-*) token`,
    level: "warning",
  },
  // Hardcoded box-shadow in CSS (not using var())
  { pattern: /box-shadow\s*:\s*(?!var\()([^;]+)/g,
    suggestion: (match, value) => `Replace box-shadow with var(--shadow-*) token`,
    level: "warning",
  },
  // Hardcoded z-index in CSS
  { pattern: /z-index\s*:\s*(\d+)\b/g,
    suggestion: (match, value) => `Replace z-index: ${value} with var(--z-*) token`,
    level: "warning",
  },
  // Hardcoded transition duration in CSS
  { pattern: /transition(?:-duration)?\s*:[^;]*?(\d+ms|\d+(?:\.\d+)?s)\b/g,
    suggestion: (match, value) => `Replace ${value} with var(--duration-*) token`,
    level: "warning",
  },
];

// Arbitrary Tailwind values (potential issues)
const ARBITRARY_TW_VALUES = [
  // Arbitrary colors: bg-[#xxx], text-[#xxx]
  { pattern: /\b(?:bg|text|border|ring|fill|stroke)-\[#[0-9a-fA-F]+\]/g,
    suggestion: (match) => `Replace ${match} with a semantic Tailwind color class`,
    level: "error",
  },
  // Arbitrary z-index: z-[N]
  { pattern: /\bz-\[\d+\]/g,
    suggestion: (match) => `Replace ${match} with z-0, z-10, z-50 or use var(--z-*) token`,
    level: "warning",
  },
  // Arbitrary pixel heights/widths that could use scale
  { pattern: /\b(?:h|w)-\[\d+px\]/g,
    suggestion: (match) => `Consider replacing ${match} with a scale value or var(--size-*) token`,
    level: "warning",
  },
  // Arbitrary border-radius
  { pattern: /\brounded-\[\d+px\]/g,
    suggestion: (match) => `Replace ${match} with rounded-sm/md/lg/xl/2xl or var(--radius-*) token`,
    level: "warning",
  },
];

// ─── Scanner ──────────────────────────────────────────────────────────────────

function shouldSkip(filePath) {
  return SKIP_PATTERNS.some((p) => p.test(filePath));
}

function getFiles(dir, extensions) {
  const results = [];
  const fullDir = path.join(ROOT, dir);

  if (!fs.existsSync(fullDir)) return results;

  function walk(currentPath) {
    const entries = fs.readdirSync(currentPath, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(currentPath, entry.name);
      if (entry.isDirectory()) {
        if (!shouldSkip(fullPath)) walk(fullPath);
      } else if (extensions.some((ext) => entry.name.endsWith(ext))) {
        if (!shouldSkip(fullPath)) results.push(fullPath);
      }
    }
  }

  walk(fullDir);
  return results;
}

function getLineNumber(content, index) {
  return content.substring(0, index).split("\n").length;
}

function auditFile(filePath) {
  const content = fs.readFileSync(filePath, "utf-8");
  const relativePath = path.relative(ROOT, filePath);
  const isCss = filePath.endsWith(".css") || filePath.endsWith(".scss");
  const isTsx = filePath.endsWith(".tsx") || filePath.endsWith(".jsx");
  const violations = [];

  // Check for hardcoded Tailwind color classes in TSX files
  if (isTsx) {
    for (const rule of HARDCODED_TW_COLORS) {
      let match;
      const regex = new RegExp(rule.pattern.source, rule.pattern.flags);
      while ((match = regex.exec(content)) !== null) {
        const line = getLineNumber(content, match.index);
        violations.push({
          file: relativePath,
          line,
          level: rule.level,
          violation: match[0],
          suggestion: rule.suggestion(match[0]),
        });
      }
    }

    // Check for arbitrary Tailwind values
    for (const rule of ARBITRARY_TW_VALUES) {
      let match;
      const regex = new RegExp(rule.pattern.source, rule.pattern.flags);
      while ((match = regex.exec(content)) !== null) {
        const line = getLineNumber(content, match.index);
        violations.push({
          file: relativePath,
          line,
          level: rule.level,
          violation: match[0],
          suggestion: rule.suggestion(match[0]),
        });
      }
    }

    // Check for inline style objects with hardcoded values
    const styleRegex = /style\s*=\s*\{\{([^}]+)\}\}/g;
    let styleMatch;
    while ((styleMatch = styleRegex.exec(content)) !== null) {
      const line = getLineNumber(content, styleMatch.index);
      // Check for hardcoded color values in style objects
      const styleContent = styleMatch[1];
      if (/#[0-9a-fA-F]{3,8}|rgba?\(/.test(styleContent)) {
        violations.push({
          file: relativePath,
          line,
          level: "error",
          violation: `Inline style with hardcoded color: ${styleMatch[0].substring(0, 60)}...`,
          suggestion: "Move to Tailwind class with semantic color token",
        });
      }
    }
  }

  // Check for hardcoded values in CSS files
  if (isCss) {
    for (const rule of CSS_HARDCODED_RULES) {
      let match;
      const regex = new RegExp(rule.pattern.source, rule.pattern.flags);
      while ((match = regex.exec(content)) !== null) {
        const line = getLineNumber(content, match.index);
        const value = match[1] || match[0];
        violations.push({
          file: relativePath,
          line,
          level: rule.level,
          violation: match[0].trim(),
          suggestion: rule.suggestion(match[0], value),
        });
      }
    }
  }

  return violations;
}

// ─── Reporter ─────────────────────────────────────────────────────────────────

function report(violations) {
  const errors = violations.filter((v) => v.level === "error");
  const warnings = violations.filter((v) => v.level === "warning");

  const separator = "─".repeat(72);

  console.log("");
  console.log("╔══════════════════════════════════════════════════════════════════════╗");
  console.log("║                     DESIGN TOKEN AUDIT REPORT                       ║");
  console.log("╚══════════════════════════════════════════════════════════════════════╝");
  console.log("");

  if (violations.length === 0) {
    console.log("  ✅  All clear! No hardcoded values found.");
    console.log("      All visual values reference design tokens.");
    console.log("");
    return 0;
  }

  // Group by file
  const byFile = {};
  for (const v of violations) {
    if (!byFile[v.file]) byFile[v.file] = [];
    byFile[v.file].push(v);
  }

  // Sort files by error count (most violations first)
  const sortedFiles = Object.entries(byFile).sort(
    (a, b) => b[1].length - a[1].length
  );

  // Print errors first
  if (errors.length > 0) {
    console.log(`  ❌  ERRORS: ${errors.length} hardcoded value(s) must be replaced`);
    console.log(separator);
    console.log("");

    for (const [file, fileViolations] of sortedFiles) {
      const fileErrors = fileViolations.filter((v) => v.level === "error");
      if (fileErrors.length === 0) continue;

      console.log(`  📄 ${file} (${fileErrors.length} error${fileErrors.length > 1 ? "s" : ""})`);
      for (const v of fileErrors) {
        console.log(`     Line ${v.line}: ${v.violation}`);
        console.log(`     └─ 💡 ${v.suggestion}`);
      }
      console.log("");
    }
  }

  // Print warnings
  if (warnings.length > 0) {
    console.log(`  ⚠️  WARNINGS: ${warnings.length} value(s) could be improved`);
    console.log(separator);
    console.log("");

    for (const [file, fileViolations] of sortedFiles) {
      const fileWarnings = fileViolations.filter((v) => v.level === "warning");
      if (fileWarnings.length === 0) continue;

      console.log(`  📄 ${file} (${fileWarnings.length} warning${fileWarnings.length > 1 ? "s" : ""})`);
      for (const v of fileWarnings) {
        console.log(`     Line ${v.line}: ${v.violation}`);
        console.log(`     └─ 💡 ${v.suggestion}`);
      }
      console.log("");
    }
  }

  // Summary
  console.log(separator);
  console.log("");
  console.log("  SUMMARY");
  console.log(`  Files scanned:  ${new Set(violations.map((v) => v.file)).size}`);
  console.log(`  Errors:         ${errors.length}`);
  console.log(`  Warnings:       ${warnings.length}`);
  console.log(`  Total:          ${violations.length}`);
  console.log("");

  if (errors.length > 0) {
    console.log("  ❌  FAIL — Fix all errors before committing.");
    console.log("      Run: node scripts/token-audit.js");
    console.log("");
    return 1;
  } else {
    console.log("  ✅  PASS — No errors. Warnings are advisory.");
    console.log("");
    return 0;
  }
}

// ─── Main ─────────────────────────────────────────────────────────────────────

function main() {
  console.log("Scanning for hardcoded values...");

  const allFiles = [];
  for (const dir of SCAN_DIRS) {
    allFiles.push(...getFiles(dir, SCAN_EXTENSIONS));
  }

  console.log(`Found ${allFiles.length} files to scan.`);

  const allViolations = [];
  for (const file of allFiles) {
    const violations = auditFile(file);
    allViolations.push(...violations);
  }

  const exitCode = report(allViolations);
  process.exit(exitCode);
}

main();
