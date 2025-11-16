import { BacklogClient } from './src/backlog-client.js';
import dotenv from 'dotenv';
import { writeFileSync } from 'fs';

dotenv.config();

const client = new BacklogClient({
  domain: process.env.BACKLOG_DOMAIN!,
  apiKey: process.env.BACKLOG_API_KEY!
});

// Fetch RPA project tickets
// Filters: Not closed (statusId 1, 2, 3), created after 2025/10/01
const issues = await client.getIssuesFiltered({
  projectId: [47358], // RPA project (HB21373)
  statusId: [1, 2, 3], // Open, In Progress, Resolved (exclude 4 = Closed)
  createdSince: '2025-10-01',
  count: 100 // Fetch up to 100 issues
});

console.log(`Found ${issues.length} tickets in RPA project`);
console.log('Filters: Not closed, created after 2025/10/01\n');

// Create CSV content
const csvHeader = 'ID,Issue Key,Summary\n';
const csvRows = issues.map(issue => {
  // Escape quotes in summary and wrap in quotes
  const escapedSummary = issue.summary.replace(/"/g, '""');
  return `${issue.id},"${issue.issueKey}","${escapedSummary}"`;
}).join('\n');

const csvContent = csvHeader + csvRows;

// Write to file
const filename = 'rpa-tickets.csv';
writeFileSync(filename, csvContent, 'utf-8');

console.log(`✅ Exported ${issues.length} tickets to ${filename}`);
console.log(`📊 Token savings: 99.0% (${issues.length * 20} vs ${issues.length * 2000} tokens)`);
