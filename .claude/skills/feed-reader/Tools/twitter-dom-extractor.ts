/**
 * twitter-dom-extractor.ts
 * DOM extraction logic for Twitter scraping
 */

export interface Tweet {
  id: string;
  text: string;
  createdAt: string;
  author: string;
  likes: number;
  retweets: number;
  replies: number;
  mediaUrls: string[];
  isThread: boolean;
}

/**
 * Extract tweets from page DOM
 * This runs in browser context via page.evaluate()
 */
export function extractTweetsLogic(): Tweet[] {
  const tweets: Tweet[] = [];
  const tweetElements = document.querySelectorAll('[data-testid="tweet"]');

  tweetElements.forEach((element) => {
    try {
      // Extract tweet ID from link
      const linkElement = element.querySelector('a[href*="/status/"]');
      const href = linkElement?.getAttribute('href') || '';
      const idMatch = href.match(/\/status\/(\d+)/);
      const id = idMatch ? idMatch[1] : '';

      // Extract text
      const textElement = element.querySelector('[data-testid="tweetText"]');
      const text = textElement?.textContent || '';

      // Extract timestamp
      const timeElement = element.querySelector('time');
      const createdAt = timeElement?.getAttribute('datetime') || new Date().toISOString();

      // Extract author
      const authorElement = element.querySelector('[data-testid="User-Name"] a');
      const authorHref = authorElement?.getAttribute('href') || '';
      const author = authorHref.replace('/', '').split('/')[0] || '';

      // Extract engagement metrics (likes, retweets, replies)
      const metricsButtons = element.querySelectorAll('[role="group"] button');
      let likes = 0, retweets = 0, replies = 0;

      metricsButtons.forEach((button) => {
        const ariaLabel = button.getAttribute('aria-label') || '';
        const numMatch = ariaLabel.match(/(\d+)/);
        const num = numMatch ? parseInt(numMatch[1], 10) : 0;

        if (ariaLabel.includes('Like') || ariaLabel.includes('like')) {
          likes = num;
        } else if (ariaLabel.includes('Repost') || ariaLabel.includes('retweet')) {
          retweets = num;
        } else if (ariaLabel.includes('Repl') || ariaLabel.includes('reply')) {
          replies = num;
        }
      });

      // Extract media URLs
      const mediaUrls: string[] = [];
      const imageElements = element.querySelectorAll('img[src*="media"]');
      imageElements.forEach((img) => {
        const src = img.getAttribute('src');
        if (src && !src.includes('profile_images')) {
          mediaUrls.push(src);
        }
      });

      // Check if it's a thread
      const showMoreElement = element.querySelector('[data-testid="tweet-text-show-more-link"]');
      const isThread = !!showMoreElement;

      if (id && text) {
        tweets.push({
          id,
          text,
          createdAt,
          author,
          likes,
          retweets,
          replies,
          mediaUrls,
          isThread,
        });
      }
    } catch (err) {
      console.error('Error extracting tweet:', err);
    }
  });

  return tweets;
}
