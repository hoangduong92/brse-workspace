import { BacklogClient, displayFilteredIssues } from './src/backlog-client.js';
import dotenv from 'dotenv';

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

console.log(`\nFound ${issues.length} tickets in RPA project`);
console.log('Filters: Not closed, created after 2025/10/01\n');

displayFilteredIssues(issues);

// Show token savings
const rawTokens = issues.length * 2000; // Estimated tokens without filtering
const filteredTokens = issues.length * 20; // With minimal selection (id, key, summary)
const savings = rawTokens > 0 ? ((rawTokens - filteredTokens) / rawTokens * 100).toFixed(1) : '0';

console.log(`\n📊 Token savings: ${savings}% (${filteredTokens} vs ${rawTokens} tokens)`);
