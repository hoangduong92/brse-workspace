#!/usr/bin/env bun
/**
 * ContentCache - Hash-based change detection for FeedReader
 *
 * Commands:
 *   load                    - Load cache from file
 *   save <json>             - Save cache to file
 *   check <url> <hash>      - Check if content changed
 *   remove <url>            - Remove URL from cache
 *   stats                   - Get cache statistics
 *   clear                   - Clear all cache
 */

import { createHash } from "crypto";
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "fs";
import { homedir } from "os";
import { join, dirname } from "path";

interface CacheEntry {
  url: string;
  contentHash: string;
  lastChecked: string;
  lastChanged: string;
  checkCount: number;
}

interface Cache {
  version: string;
  entries: Record<string, CacheEntry>;
}

const CACHE_PATH = join(homedir(), ".claude", "skills", "FeedReader", "cache.json");

function ensureDir(filePath: string): void {
  const dir = dirname(filePath);
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
}

function loadCache(): Cache {
  if (!existsSync(CACHE_PATH)) {
    return { version: "1.0", entries: {} };
  }
  try {
    const data = readFileSync(CACHE_PATH, "utf-8");
    return JSON.parse(data);
  } catch {
    return { version: "1.0", entries: {} };
  }
}

function saveCache(cache: Cache): void {
  ensureDir(CACHE_PATH);
  writeFileSync(CACHE_PATH, JSON.stringify(cache, null, 2));
}

function hashContent(content: string): string {
  return createHash("sha256").update(content).digest("hex").slice(0, 16);
}

function formatDate(date: Date): string {
  return date.toISOString();
}

function relativeTime(isoDate: string): string {
  const date = new Date(isoDate);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins} minutes ago`;
  if (diffHours < 24) return `${diffHours} hours ago`;
  if (diffDays < 7) return `${diffDays} days ago`;
  return date.toLocaleDateString();
}

// Commands

function cmdLoad(): void {
  const cache = loadCache();
  console.log(JSON.stringify(cache, null, 2));
}

function cmdSave(jsonData: string): void {
  try {
    const data = JSON.parse(jsonData);
    const cache = loadCache();

    // Merge entries
    for (const [url, entry] of Object.entries(data)) {
      cache.entries[url] = entry as CacheEntry;
    }

    saveCache(cache);
    console.log(`Cache saved with ${Object.keys(cache.entries).length} entries`);
  } catch (error) {
    console.error("Error saving cache:", error);
    process.exit(1);
  }
}

function cmdCheck(url: string, newHash: string): void {
  const cache = loadCache();
  const now = formatDate(new Date());

  const existing = cache.entries[url];

  if (!existing) {
    // New URL
    cache.entries[url] = {
      url,
      contentHash: newHash,
      lastChecked: now,
      lastChanged: now,
      checkCount: 1,
    };
    saveCache(cache);
    console.log("new");
    return;
  }

  // Update check count and time
  existing.lastChecked = now;
  existing.checkCount++;

  if (existing.contentHash !== newHash) {
    // Content changed
    existing.contentHash = newHash;
    existing.lastChanged = now;
    saveCache(cache);
    console.log("updated");
    return;
  }

  // No change
  saveCache(cache);
  console.log("unchanged");
}

function cmdRemove(url: string): void {
  const cache = loadCache();

  if (cache.entries[url]) {
    delete cache.entries[url];
    saveCache(cache);
    console.log(`Removed: ${url}`);
  } else {
    console.log(`Not found: ${url}`);
  }
}

function cmdStats(): void {
  const cache = loadCache();
  const entries = Object.values(cache.entries);

  if (entries.length === 0) {
    console.log("Cache is empty. Run 'daily digest' to populate.");
    return;
  }

  const stats = {
    totalEntries: entries.length,
    lastChecked: entries
      .map(e => e.lastChecked)
      .sort()
      .reverse()[0],
    entriesWithChanges: entries.filter(e => e.lastChanged === e.lastChecked).length,
    avgCheckCount: Math.round(entries.reduce((sum, e) => sum + e.checkCount, 0) / entries.length),
  };

  console.log("Cache Statistics:");
  console.log(`  Total entries: ${stats.totalEntries}`);
  console.log(`  Last checked: ${relativeTime(stats.lastChecked)}`);
  console.log(`  Recent changes: ${stats.entriesWithChanges}`);
  console.log(`  Avg checks/URL: ${stats.avgCheckCount}`);
  console.log("");
  console.log("Recent activity:");

  entries
    .sort((a, b) => b.lastChecked.localeCompare(a.lastChecked))
    .slice(0, 5)
    .forEach(e => {
      const changed = e.lastChanged === e.lastChecked ? " (new content)" : "";
      console.log(`  ${relativeTime(e.lastChecked)}: ${e.url}${changed}`);
    });
}

function cmdClear(): void {
  saveCache({ version: "1.0", entries: {} });
  console.log("Cache cleared");
}

function cmdHelp(): void {
  console.log(`
ContentCache - Hash-based change detection for FeedReader

Usage:
  bun run ContentCache.ts <command> [args]

Commands:
  load                    Load and display cache
  save <json>             Save entries to cache
  check <url> <hash>      Check if URL content changed (returns: new|updated|unchanged)
  remove <url>            Remove URL from cache
  stats                   Display cache statistics
  clear                   Clear all cache entries
  help                    Show this help

Examples:
  bun run ContentCache.ts load
  bun run ContentCache.ts check "https://example.com" "abc123def456"
  bun run ContentCache.ts stats
`);
}

// Main
const [, , command, ...args] = process.argv;

switch (command) {
  case "load":
    cmdLoad();
    break;
  case "save":
    cmdSave(args[0]);
    break;
  case "check":
    cmdCheck(args[0], args[1]);
    break;
  case "remove":
    cmdRemove(args[0]);
    break;
  case "stats":
    cmdStats();
    break;
  case "clear":
    cmdClear();
    break;
  case "help":
  case "--help":
  case "-h":
    cmdHelp();
    break;
  default:
    console.error(`Unknown command: ${command}`);
    cmdHelp();
    process.exit(1);
}
