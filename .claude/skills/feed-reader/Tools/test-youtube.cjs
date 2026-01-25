#!/usr/bin/env node
const path = require('path');

// Test direct channel ID parsing
const url1 = "https://youtube.com/channel/UCSHZKyawb77ixDdsGog4iWA";
const urlObj = new URL(url1);
const pathPart = urlObj.pathname;
console.log(`URL: ${url1}`);
console.log(`Pathname: ${pathPart}`);
const match = pathPart.match(/^\/channel\/(UC[\w-]+)/);
console.log(`Match result:`, match);
if (match) {
  console.log(`Channel ID: ${match[1]}`);
}
