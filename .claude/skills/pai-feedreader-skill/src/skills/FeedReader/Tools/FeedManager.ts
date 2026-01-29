#!/usr/bin/env bun
/**
 * FeedManager - YAML feed list manager for FeedReader
 *
 * Commands:
 *   list [--format table|json|brief]  - List all feeds
 *   add --url <url> [--name <name>] [--category <cat>] [--priority <pri>]
 *   remove --url <url>
 *   find <query>                       - Search feeds by URL or name
 *   validate                           - Validate feeds.yaml structure
 */

import { parse, stringify } from "yaml";
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "fs";
import { homedir } from "os";
import { join, dirname } from "path";

interface Feed {
  url: string;
  name: string;
  category: "blog" | "twitter" | "newsletter" | "youtube";
  priority: "high" | "medium" | "low";
  notes?: string;
}

interface FeedsFile {
  feeds: Feed[];
}

const FEEDS_PATH = join(homedir(), ".claude", "skills", "FeedReader", "feeds.yaml");
const TEMPLATE_PATH = join(dirname(import.meta.dir), "Data", "feeds.yaml");

function ensureDir(filePath: string): void {
  const dir = dirname(filePath);
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
}

function loadFeeds(): FeedsFile {
  if (!existsSync(FEEDS_PATH)) {
    // Create from template if exists
    if (existsSync(TEMPLATE_PATH)) {
      const template = readFileSync(TEMPLATE_PATH, "utf-8");
      ensureDir(FEEDS_PATH);
      writeFileSync(FEEDS_PATH, template);
      return parse(template) as FeedsFile;
    }
    return { feeds: [] };
  }

  try {
    const data = readFileSync(FEEDS_PATH, "utf-8");
    return parse(data) as FeedsFile;
  } catch (error) {
    console.error("Error parsing feeds.yaml:", error);
    return { feeds: [] };
  }
}

function saveFeeds(data: FeedsFile): void {
  ensureDir(FEEDS_PATH);
  const yaml = stringify(data, { lineWidth: 0 });
  writeFileSync(FEEDS_PATH, yaml);
}

function detectCategory(url: string): Feed["category"] {
  const lowerUrl = url.toLowerCase();

  if (lowerUrl.includes("twitter.com") || lowerUrl.includes("x.com")) {
    return "twitter";
  }
  if (lowerUrl.includes("youtube.com") || lowerUrl.includes("youtu.be")) {
    return "youtube";
  }
  if (lowerUrl.includes("substack.com") || lowerUrl.includes("newsletter")) {
    return "newsletter";
  }

  return "blog";
}

function extractName(url: string): string {
  try {
    const urlObj = new URL(url);
    // Remove www. and get domain
    let name = urlObj.hostname.replace(/^www\./, "");

    // For twitter, extract username
    if (name.includes("twitter.com") || name.includes("x.com")) {
      const match = urlObj.pathname.match(/^\/([^\/]+)/);
      if (match) {
        return `@${match[1]}`;
      }
    }

    // For youtube, try to get channel name from path
    if (name.includes("youtube.com")) {
      const match = urlObj.pathname.match(/^\/@?([^\/]+)/);
      if (match) {
        return match[1];
      }
    }

    return name;
  } catch {
    return url.slice(0, 30);
  }
}

// Commands

function cmdList(format: string = "table"): void {
  const data = loadFeeds();

  if (data.feeds.length === 0) {
    console.log("No feeds configured.");
    console.log('Add feeds with: "add feed https://example.com"');
    return;
  }

  if (format === "json") {
    console.log(JSON.stringify(data.feeds, null, 2));
    return;
  }

  if (format === "brief") {
    data.feeds.forEach((feed, i) => {
      console.log(`${i + 1}. ${feed.name} (${feed.category}, ${feed.priority})`);
    });
    return;
  }

  // Table format (default)
  const byCategory: Record<string, Feed[]> = {};
  data.feeds.forEach(feed => {
    if (!byCategory[feed.category]) {
      byCategory[feed.category] = [];
    }
    byCategory[feed.category].push(feed);
  });

  console.log(`# Your Feeds (${data.feeds.length} total)\n`);

  for (const [category, feeds] of Object.entries(byCategory)) {
    console.log(`## ${category.charAt(0).toUpperCase() + category.slice(1)} (${feeds.length})`);
    console.log("| Name | URL | Priority |");
    console.log("|------|-----|----------|");
    feeds.forEach(feed => {
      const shortUrl = feed.url.replace(/^https?:\/\/(www\.)?/, "").slice(0, 40);
      console.log(`| ${feed.name} | ${shortUrl} | ${feed.priority} |`);
    });
    console.log("");
  }

  // Summary
  const high = data.feeds.filter(f => f.priority === "high").length;
  const medium = data.feeds.filter(f => f.priority === "medium").length;
  const low = data.feeds.filter(f => f.priority === "low").length;

  console.log("## Summary");
  console.log(`- High priority: ${high}`);
  console.log(`- Medium priority: ${medium}`);
  console.log(`- Low priority: ${low}`);
}

function cmdAdd(options: {
  url: string;
  name?: string;
  category?: string;
  priority?: string;
  notes?: string;
}): void {
  const data = loadFeeds();

  // Check for duplicate
  if (data.feeds.some(f => f.url === options.url)) {
    console.error(`URL already exists: ${options.url}`);
    process.exit(1);
  }

  const newFeed: Feed = {
    url: options.url,
    name: options.name || extractName(options.url),
    category: (options.category as Feed["category"]) || detectCategory(options.url),
    priority: (options.priority as Feed["priority"]) || "medium",
  };

  if (options.notes) {
    newFeed.notes = options.notes;
  }

  data.feeds.push(newFeed);
  saveFeeds(data);

  console.log("Added feed:");
  console.log(`  URL: ${newFeed.url}`);
  console.log(`  Name: ${newFeed.name}`);
  console.log(`  Category: ${newFeed.category}`);
  console.log(`  Priority: ${newFeed.priority}`);
  console.log(`\nYou now have ${data.feeds.length} feeds total.`);
}

function cmdRemove(url: string): void {
  const data = loadFeeds();
  const index = data.feeds.findIndex(f => f.url === url);

  if (index === -1) {
    console.error(`Feed not found: ${url}`);
    process.exit(1);
  }

  const removed = data.feeds.splice(index, 1)[0];
  saveFeeds(data);

  console.log("Removed feed:");
  console.log(`  Name: ${removed.name}`);
  console.log(`  URL: ${removed.url}`);
  console.log(`\nYou now have ${data.feeds.length} feeds remaining.`);
}

function cmdFind(query: string): void {
  const data = loadFeeds();
  const lowerQuery = query.toLowerCase();

  const matches = data.feeds.filter(feed =>
    feed.url.toLowerCase().includes(lowerQuery) ||
    feed.name.toLowerCase().includes(lowerQuery)
  );

  if (matches.length === 0) {
    console.log(`No feeds found matching: ${query}`);
    return;
  }

  console.log(`Found ${matches.length} feed(s):\n`);
  matches.forEach((feed, i) => {
    console.log(`${i + 1}. ${feed.name}`);
    console.log(`   URL: ${feed.url}`);
    console.log(`   Category: ${feed.category}, Priority: ${feed.priority}`);
    if (feed.notes) {
      console.log(`   Notes: ${feed.notes}`);
    }
    console.log("");
  });
}

function cmdValidate(): void {
  const data = loadFeeds();
  let valid = true;
  const errors: string[] = [];

  data.feeds.forEach((feed, i) => {
    if (!feed.url) {
      errors.push(`Feed ${i + 1}: Missing URL`);
      valid = false;
    }
    if (!feed.name) {
      errors.push(`Feed ${i + 1}: Missing name`);
      valid = false;
    }
    if (!["blog", "twitter", "newsletter", "youtube"].includes(feed.category)) {
      errors.push(`Feed ${i + 1}: Invalid category "${feed.category}"`);
      valid = false;
    }
    if (!["high", "medium", "low"].includes(feed.priority)) {
      errors.push(`Feed ${i + 1}: Invalid priority "${feed.priority}"`);
      valid = false;
    }

    // Validate URL format
    try {
      new URL(feed.url);
    } catch {
      errors.push(`Feed ${i + 1}: Invalid URL format "${feed.url}"`);
      valid = false;
    }
  });

  if (valid) {
    console.log(`feeds.yaml is valid (${data.feeds.length} feeds)`);
  } else {
    console.log("Validation errors:");
    errors.forEach(e => console.log(`  - ${e}`));
    process.exit(1);
  }
}

function cmdHelp(): void {
  console.log(`
FeedManager - YAML feed list manager for FeedReader

Usage:
  bun run FeedManager.ts <command> [options]

Commands:
  list [--format table|json|brief]     List all feeds
  add --url <url> [options]            Add a new feed
  remove --url <url>                   Remove a feed
  find <query>                         Search feeds
  validate                             Validate feeds.yaml
  help                                 Show this help

Add options:
  --url <url>          URL to add (required)
  --name <name>        Display name (auto-detected if not provided)
  --category <cat>     blog|twitter|newsletter|youtube (auto-detected)
  --priority <pri>     high|medium|low (default: medium)
  --notes <notes>      Optional notes

Examples:
  bun run FeedManager.ts list
  bun run FeedManager.ts add --url "https://example.com" --name "My Blog"
  bun run FeedManager.ts find "twitter"
  bun run FeedManager.ts remove --url "https://example.com"
`);
}

// Parse arguments
function parseArgs(args: string[]): Record<string, string> {
  const result: Record<string, string> = {};

  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--")) {
      const key = args[i].slice(2);
      const value = args[i + 1] && !args[i + 1].startsWith("--") ? args[i + 1] : "true";
      result[key] = value;
      if (value !== "true") i++;
    } else if (!result._positional) {
      result._positional = args[i];
    }
  }

  return result;
}

// Main
const [, , command, ...args] = process.argv;
const options = parseArgs(args);

switch (command) {
  case "list":
    cmdList(options.format || "table");
    break;
  case "add":
    if (!options.url) {
      console.error("Missing --url");
      process.exit(1);
    }
    cmdAdd({
      url: options.url,
      name: options.name,
      category: options.category,
      priority: options.priority,
      notes: options.notes,
    });
    break;
  case "remove":
    if (!options.url) {
      console.error("Missing --url");
      process.exit(1);
    }
    cmdRemove(options.url);
    break;
  case "find":
    if (!options._positional) {
      console.error("Missing search query");
      process.exit(1);
    }
    cmdFind(options._positional);
    break;
  case "validate":
    cmdValidate();
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
