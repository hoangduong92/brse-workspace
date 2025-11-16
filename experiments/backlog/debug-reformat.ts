import { readFileSync } from 'fs';

// Read actual line from CSV
const csvContent = readFileSync('rpa-tickets.csv', 'utf-8');
const lines = csvContent.split('\n');

// Get line 2 (index 1)
const line2 = lines[1];
console.log('Raw line:', line2);
console.log('\n');

// Extract summary (after second quote pair)
const match = line2.match(/^(\d+),"([^"]+)","(.+)"$/);
if (match) {
  const summary = match[3];
  console.log('Summary:', summary);
  console.log('\n');

  // Find the dash-like characters
  const dashIndex = summary.indexOf('--');
  if (dashIndex > -1) {
    console.log('Found -- at index:', dashIndex);
    const surrounding = summary.substring(Math.max(0, dashIndex - 5), dashIndex + 10);
    console.log('Surrounding text:', surrounding);
    console.log('Character codes:', Array.from(surrounding).map((c, i) => `[${i}]${c}(${c.charCodeAt(0)})`).join(' '));
  }
}
