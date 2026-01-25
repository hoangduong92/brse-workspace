#!/usr/bin/env bun
/**
 * YouTubeHandler - YouTube RSS feed integration
 *
 * Handles YouTube channel URLs and RSS feed parsing
 * Supports: @handle, /channel/UC..., /c/customname formats
 */

export interface YouTubeVideo {
  id: string;
  title: string;
  description: string;
  publishedAt: string;
  thumbnailUrl: string;
  channelName: string;
  channelId: string;
}

export interface Transcript {
  success: boolean;
  text?: string;
  language?: string;
  video_id: string;
  error?: string;
}

export interface TranscriptOptions {
  languages?: string[];
  maxWords?: number;  // Truncate to first N words for digest
}

const USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36";
const REQUEST_TIMEOUT = 10000; // 10s timeout

/**
 * Simple XML tag value extractor
 * @param xml - XML string
 * @param tag - Tag name to extract
 * @param all - Extract all occurrences (default: false)
 * @returns Extracted value(s)
 */
function extractXmlTag(xml: string, tag: string, all: boolean = false): string | string[] {
  const pattern = new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, all ? 'g' : '');
  if (all) {
    const matches: string[] = [];
    let match;
    const regex = new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, 'g');
    while ((match = regex.exec(xml)) !== null) {
      matches.push(match[1]);
    }
    return matches;
  }
  const match = xml.match(pattern);
  return match ? match[1] : '';
}

/**
 * Extract attribute from XML tag
 * @param xml - XML string
 * @param tag - Tag name
 * @param attr - Attribute name
 * @returns Attribute value
 */
function extractXmlAttr(xml: string, tag: string, attr: string): string {
  const pattern = new RegExp(`<${tag}[^>]*${attr}="([^"]+)"`, '');
  const match = xml.match(pattern);
  return match ? match[1] : '';
}

/**
 * Extract channel ID from various YouTube URL formats
 * @param url - YouTube channel URL (@handle, /channel/UC..., /c/customname)
 * @returns Channel ID (UC... format)
 */
export async function extractChannelId(url: string): Promise<string> {
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.toLowerCase();

    // Validate it's a YouTube URL
    if (!hostname.includes("youtube.com") && !hostname.includes("youtu.be")) {
      throw new Error("Not a valid YouTube URL");
    }

    const path = urlObj.pathname;

    // Format 1: /channel/UC... - Direct channel ID
    const channelMatch = path.match(/^\/channel\/(UC[\w-]+)/);
    if (channelMatch) {
      return channelMatch[1];
    }

    // Format 2: /@handle - Need to fetch page
    const handleMatch = path.match(/^\/@([\w-]+)/);
    if (handleMatch) {
      return await extractChannelIdFromPage(url);
    }

    // Format 3: /c/customname or /user/username - Need to fetch page
    const customMatch = path.match(/^\/(c|user)\/([\w-]+)/);
    if (customMatch) {
      return await extractChannelIdFromPage(url);
    }

    throw new Error(`Unable to parse channel ID from URL: ${url}`);
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to extract channel ID: ${error.message}`);
    }
    throw error;
  }
}

/**
 * Fetch channel page and extract channel ID from HTML
 * @param url - Full YouTube channel URL
 * @returns Channel ID (UC... format)
 */
async function extractChannelIdFromPage(url: string): Promise<string> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

    let response: Response;
    try {
      response = await fetch(url, {
        headers: { "User-Agent": USER_AGENT },
        signal: controller.signal,
      });
    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      if (fetchError.name === 'AbortError') {
        throw new Error(`Request timeout after ${REQUEST_TIMEOUT / 1000}s`);
      }
      throw fetchError;
    }

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const html = await response.text();

    // Try multiple patterns to find channel ID
    // Pattern 1: "channelId":"UC..."
    let match = html.match(/"channelId":"(UC[\w-]+)"/);
    if (match) return match[1];

    // Pattern 2: "browse_id":"UC..."
    match = html.match(/"browse_id":"(UC[\w-]+)"/);
    if (match) return match[1];

    // Pattern 3: <link rel="canonical" href="https://www.youtube.com/channel/UC...">
    match = html.match(/youtube\.com\/channel\/(UC[\w-]+)/);
    if (match) return match[1];

    // Pattern 4: externalId in JSON-LD
    match = html.match(/"externalId":"(UC[\w-]+)"/);
    if (match) return match[1];

    throw new Error("Channel ID not found in page HTML");
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to fetch channel page: ${error.message}`);
    }
    throw error;
  }
}

/**
 * Build RSS feed URL from channel ID
 * @param channelId - Channel ID (UC... format)
 * @returns RSS feed URL
 */
export function buildRssUrl(channelId: string): string {
  if (!channelId.startsWith("UC")) {
    throw new Error(`Invalid channel ID format: ${channelId}`);
  }
  return `https://www.youtube.com/feeds/videos.xml?channel_id=${channelId}`;
}

/**
 * Fetch and parse YouTube RSS feed
 * @param channelId - Channel ID (UC... format)
 * @returns Array of recent videos (sorted by publish date descending)
 */
export async function fetchChannelFeed(channelId: string): Promise<YouTubeVideo[]> {
  try {
    const rssUrl = buildRssUrl(channelId);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

    let response: Response;
    try {
      response = await fetch(rssUrl, {
        headers: { "User-Agent": USER_AGENT },
        signal: controller.signal,
      });
    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      if (fetchError.name === 'AbortError') {
        throw new Error(`Request timeout after ${REQUEST_TIMEOUT / 1000}s`);
      }
      throw fetchError;
    }

    clearTimeout(timeoutId);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error("Channel not found or has no public videos");
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const xml = await response.text();

    // Parse Atom XML feed manually
    const channelName = (extractXmlTag(xml, "name") as string) ||
                       (extractXmlTag(xml, "title") as string) ||
                       "Unknown Channel";

    // Extract all entries
    const entryMatches = xml.match(/<entry>[\s\S]*?<\/entry>/g);
    if (!entryMatches || entryMatches.length === 0) {
      return []; // No videos in feed
    }

    // Map entries to YouTubeVideo format
    const videos: YouTubeVideo[] = entryMatches
      .map((entryXml: string) => {
        const videoId = extractXmlTag(entryXml, "yt:videoId") as string;
        if (!videoId) return null;

        const title = extractXmlTag(entryXml, "title") as string || "Untitled";
        const description = extractXmlTag(entryXml, "media:description") as string || "";
        const publishedAt = extractXmlTag(entryXml, "published") as string || new Date().toISOString();
        const thumbnailUrl = extractXmlAttr(entryXml, "media:thumbnail", "url") || "";

        return {
          id: videoId,
          title,
          description,
          publishedAt,
          thumbnailUrl,
          channelName,
          channelId,
        };
      })
      .filter((video): video is YouTubeVideo => video !== null);

    // Sort by publish date descending
    videos.sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime());

    return videos;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to fetch channel feed: ${error.message}`);
    }
    throw error;
  }
}

/**
 * Get YouTube channel feed from any URL format
 * @param url - YouTube channel URL
 * @returns Array of recent videos
 */
export async function getYouTubeFeed(url: string): Promise<YouTubeVideo[]> {
  const channelId = await extractChannelId(url);
  return fetchChannelFeed(channelId);
}

/**
 * Extract transcript from YouTube video
 * @param videoId - YouTube video ID (11 alphanumeric characters)
 * @param options - Transcript extraction options
 * @returns Transcript object with text and metadata
 */
export async function extractTranscript(
  videoId: string,
  options: TranscriptOptions = {}
): Promise<Transcript> {
  try {
    // Validate video ID format
    if (!/^[a-zA-Z0-9_-]{11}$/.test(videoId)) {
      return {
        success: false,
        video_id: videoId,
        error: "Invalid video ID format (expected 11 alphanumeric characters)"
      };
    }

    const languages = options.languages || ['en', 'ja', 'vi'];
    const scriptPath = new URL("../scripts/extract-transcript.py", import.meta.url).pathname;

    // Windows path fix: remove leading slash
    const cleanScriptPath = scriptPath.startsWith('/') && scriptPath.includes(':')
      ? scriptPath.slice(1)
      : scriptPath;

    const proc = Bun.spawn(
      ["python", cleanScriptPath, videoId, languages.join(',')],
      { timeout: 30000 }
    );

    const output = await new Response(proc.stdout).text();
    const result = JSON.parse(output) as Transcript;

    // Truncate if maxWords specified
    if (result.success && result.text && options.maxWords) {
      const words = result.text.split(/\s+/);
      if (words.length > options.maxWords) {
        result.text = words.slice(0, options.maxWords).join(' ') + '...';
      }
    }

    return result;
  } catch (error) {
    return {
      success: false,
      video_id: videoId,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

// CLI interface
if (import.meta.main) {
  const [, , command, ...args] = process.argv;

  switch (command) {
    case "extract-id":
      if (!args[0]) {
        console.error("Usage: bun run YouTubeHandler.ts extract-id <url>");
        process.exit(1);
      }
      extractChannelId(args[0])
        .then(id => console.log(id))
        .catch(err => {
          console.error(err.message);
          process.exit(1);
        });
      break;

    case "fetch":
      if (!args[0]) {
        console.error("Usage: bun run YouTubeHandler.ts fetch <url|channel_id>");
        process.exit(1);
      }
      (async () => {
        try {
          let channelId = args[0];
          if (!channelId.startsWith("UC")) {
            channelId = await extractChannelId(args[0]);
          }
          const videos = await fetchChannelFeed(channelId);
          console.log(JSON.stringify(videos, null, 2));
        } catch (err) {
          console.error(err instanceof Error ? err.message : String(err));
          process.exit(1);
        }
      })();
      break;

    case "transcript":
      if (!args[0]) {
        console.error("Usage: bun run YouTubeHandler.ts transcript <videoId> [languages]");
        process.exit(1);
      }
      (async () => {
        try {
          const videoId = args[0];
          const languages = args[1] ? args[1].split(',') : undefined;
          const result = await extractTranscript(videoId, { languages });
          console.log(JSON.stringify(result, null, 2));
        } catch (err) {
          console.error(err instanceof Error ? err.message : String(err));
          process.exit(1);
        }
      })();
      break;

    case "help":
    default:
      console.log(`
YouTubeHandler - YouTube RSS feed integration & transcript extraction

Usage:
  bun run YouTubeHandler.ts <command> [args]

Commands:
  extract-id <url>              Extract channel ID from YouTube URL
  fetch <url>                   Fetch and display recent videos from channel
  transcript <videoId> [langs]  Extract transcript for video (langs: comma-separated)
  help                          Show this help

Examples:
  bun run YouTubeHandler.ts extract-id "https://youtube.com/@lexfridman"
  bun run YouTubeHandler.ts fetch "https://youtube.com/@lexfridman"
  bun run YouTubeHandler.ts fetch "UCxxxxxxxxxx"
  bun run YouTubeHandler.ts transcript "dQw4w9WgXcQ"
  bun run YouTubeHandler.ts transcript "dQw4w9WgXcQ" "en,ja,vi"
`);
      break;
  }
}
