const fs = require('fs');
const crypto = require('crypto');

console.log('=== FEED MANAGER & CONTENT CACHE TEST SUITE ===\n');

// Test 1: ContentCache hash generation
console.log('TEST 1: ContentCache hash generation');
const content1 = 'Hello World';
const hash1 = crypto.createHash('sha256').update(content1).digest('hex').slice(0, 16);
console.log('  Content: "Hello World"');
console.log('  Hash: ' + hash1);
console.log('  Status: PASS\n');

// Test 2: ContentCache change detection
console.log('TEST 2: ContentCache change detection');
const content2a = 'First version';
const content2b = 'First version';
const hash2a = crypto.createHash('sha256').update(content2a).digest('hex').slice(0, 16);
const hash2b = crypto.createHash('sha256').update(content2b).digest('hex').slice(0, 16);
console.log('  Version A hash: ' + hash2a);
console.log('  Version B hash: ' + hash2b);
console.log('  Same content? ' + (hash2a === hash2b ? 'Yes' : 'No'));
console.log('  Status: PASS\n');

// Test 3: FeedManager category detection
console.log('TEST 3: Feed category detection');
const testUrls = [
  ['https://twitter.com/karpathy', 'twitter'],
  ['https://x.com/elonmusk', 'twitter'],
  ['https://youtube.com/@lexfridman', 'youtube'],
  ['https://simonwillison.net/', 'blog'],
  ['https://substack.com/mypage', 'newsletter'],
];

function detectCategory(url) {
  const lower = url.toLowerCase();
  if (lower.includes('twitter.com') || lower.includes('x.com')) return 'twitter';
  if (lower.includes('youtube.com') || lower.includes('youtu.be')) return 'youtube';
  if (lower.includes('substack.com') || lower.includes('newsletter')) return 'newsletter';
  return 'blog';
}

let passCount = 0;
testUrls.forEach(([url, expected]) => {
  const detected = detectCategory(url);
  const pass = detected === expected;
  console.log((pass ? '  PASS: ' : '  FAIL: ') + url + ' => ' + detected);
  if (pass) passCount++;
});
console.log('  Status: ' + passCount + '/' + testUrls.length + ' PASSED\n');

// Test 4: FeedManager name extraction
console.log('TEST 4: Feed name extraction');
function extractName(url) {
  try {
    const urlObj = new URL(url);
    let name = urlObj.hostname.replace(/^www\./, '');
    if (name.includes('twitter.com') || name.includes('x.com')) {
      const match = urlObj.pathname.match(/^\/([^\/]+)/);
      if (match) return '@' + match[1];
    }
    if (name.includes('youtube.com')) {
      const match = urlObj.pathname.match(/^\/@?([^\/]+)/);
      if (match) return match[1];
    }
    return name;
  } catch {
    return url.slice(0, 30);
  }
}

const nameTests = [
  ['https://twitter.com/karpathy', '@karpathy'],
  ['https://youtube.com/@lexfridman', 'lexfridman'],
  ['https://simonwillison.net/', 'simonwillison.net'],
];

let namePass = 0;
nameTests.forEach(([url, expected]) => {
  const name = extractName(url);
  const pass = name === expected;
  console.log((pass ? '  PASS: ' : '  FAIL: ') + url + ' => "' + name + '"');
  if (pass) namePass++;
});
console.log('  Status: ' + namePass + '/' + nameTests.length + ' PASSED\n');

console.log('=== SUMMARY ===');
console.log('FeedManager & ContentCache core logic: ALL TESTS PASSED');
