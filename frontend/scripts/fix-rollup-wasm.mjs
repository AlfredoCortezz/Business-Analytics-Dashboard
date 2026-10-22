/**
 * Algunos equipos Windows aplican politicas de control de aplicaciones (WDAC/AppLocker)
 * que bloquean el binario nativo rollup.win32-x64-msvc.node, impidiendo que Vite arranque.
 *
 * Este script redirige el paquete `rollup` hacia `@rollup/wasm-node` (implementacion
 * WebAssembly, sin binario nativo). Si el binario nativo funciona con normalidad,
 * no hace nada y deja Rollup tal cual (rendimiento optimo en despliegue).
 */
import { existsSync, readFileSync, writeFileSync, rmSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const nodeModules = join(root, "node_modules");
const rollupDir = join(nodeModules, "rollup");
const wasmDir = join(nodeModules, "@rollup", "wasm-node");
const marker = join(rollupDir, ".wasm-proxy");

function nativeRollupWorks() {
  try {
    const loadPath = require.resolve("@rollup/rollup-win32-x64-msvc", { paths: [root] });
    require(loadPath);
    return true;
  } catch {
    return false;
  }
}

if (!existsSync(rollupDir) || !existsSync(wasmDir)) {
  console.log("[rollup-wasm] rollup o wasm-node no encontrado. Nada que hacer.");
  process.exit(0);
}

if (process.platform !== "win32") {
  console.log("[rollup-wasm] Plataforma no Windows. Sin cambios.");
  process.exit(0);
}

if (nativeRollupWorks()) {
  console.log("[rollup-wasm] Binario nativo de Rollup disponible. Sin cambios.");
  process.exit(0);
}

console.log("[rollup-wasm] Binario nativo bloqueado. Redirigiendo rollup -> @rollup/wasm-node.");

const proxy = {
  name: "rollup",
  version: "4.0.0",
  type: "module",
  main: "./index.cjs",
  module: "./index.mjs",
  exports: {
    ".": {
      require: "./index.cjs",
      import: "./index.mjs",
    },
    "./parseAst": {
      require: "./parseAst.cjs",
      import: "./parseAst.mjs",
    },
    "./loadConfigFile": {
      require: "./index.cjs",
      import: "./index.mjs",
    },
    "./dist/*": "./dist/*",
  },
};

const cjs = `module.exports = require('@rollup/wasm-node');\n`;
const mjs = `export * from '@rollup/wasm-node';\n`;
const parseAstCjs = `module.exports = require('@rollup/wasm-node/parseAst');\n`;
const parseAstMjs = `export * from '@rollup/wasm-node/parseAst';\n`;

writeFileSync(join(rollupDir, "package.json"), JSON.stringify(proxy, null, 2));
writeFileSync(join(rollupDir, "index.cjs"), cjs);
writeFileSync(join(rollupDir, "index.mjs"), mjs);
writeFileSync(join(rollupDir, "parseAst.cjs"), parseAstCjs);
writeFileSync(join(rollupDir, "parseAst.mjs"), parseAstMjs);
writeFileSync(marker, new Date().toISOString());

console.log("[rollup-wasm] Listo. Vite y Vitest usaran Rollup en WebAssembly.");
