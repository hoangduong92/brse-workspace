/**
 * twitter-retry-handler.ts
 * Retry logic with exponential backoff for Twitter scraping
 */

async function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retry a function with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  delays = [5000, 15000, 45000]
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      const delay = delays[i] || delays[delays.length - 1];
      console.error(`Attempt ${i + 1} failed, retrying in ${delay / 1000}s...`);
      await sleep(delay);
    }
  }
  throw new Error('Max retries exceeded');
}

/**
 * Rate limiting state
 */
let lastRequestTime = 0;
const MIN_REQUEST_INTERVAL = 10000; // 10 seconds

/**
 * Enforce rate limiting between requests
 */
export async function enforceRateLimit(): Promise<void> {
  const now = Date.now();
  const elapsed = now - lastRequestTime;
  if (elapsed < MIN_REQUEST_INTERVAL) {
    await sleep(MIN_REQUEST_INTERVAL - elapsed);
  }
  lastRequestTime = Date.now();
}

/**
 * Handle rate limit errors
 */
export async function handleRateLimit(error: any): Promise<void> {
  if (error?.message?.includes('429') || error?.response?.status === 429) {
    console.error('Rate limit detected, waiting 60s...');
    await sleep(60000);
    throw error; // Re-throw to trigger retry
  }
  throw error;
}
