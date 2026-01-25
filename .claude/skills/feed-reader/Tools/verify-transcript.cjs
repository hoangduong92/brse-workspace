#!/usr/bin/env node
// Simple verification without TypeScript to avoid compilation issues

const { spawn } = require('child_process');
const path = require('path');

const videoId = process.argv[2] || 'dQw4w9WgXcQ';
const languages = process.argv[3] || 'en';

const scriptPath = path.join(__dirname, '..', 'scripts', 'extract-transcript.py');

console.log(`Testing transcript extraction for video: ${videoId}`);
console.log(`Script path: ${scriptPath}`);
console.log('---');

const proc = spawn('python', [scriptPath, videoId, languages]);

let output = '';
let error = '';

proc.stdout.on('data', (data) => {
  output += data.toString();
});

proc.stderr.on('data', (data) => {
  error += data.toString();
});

proc.on('close', (code) => {
  if (code !== 0) {
    console.error(`Process exited with code ${code}`);
    console.error('Error:', error);
    process.exit(1);
  }

  try {
    const result = JSON.parse(output);
    console.log(JSON.stringify(result, null, 2));

    if (result.success) {
      const wordCount = result.text.split(/\s+/).length;
      console.log(`\n✓ Success! Transcript has ${wordCount} words`);
      console.log(`Language: ${result.language}`);
    } else {
      console.log(`\n✗ Failed: ${result.error}`);
    }
  } catch (e) {
    console.error('Failed to parse JSON:', e.message);
    console.error('Raw output:', output);
    process.exit(1);
  }
});
