import { readFileSync } from 'fs';
import dotenv from 'dotenv';

dotenv.config();

const domain = process.env.BACKLOG_DOMAIN;
const apiKey = process.env.BACKLOG_API_KEY;

if (!domain || !apiKey) {
  console.error('❌ Missing BACKLOG_DOMAIN or BACKLOG_API_KEY in .env');
  process.exit(1);
}

// Read issues data
const issuesData = JSON.parse(readFileSync('issues-to-update.json', 'utf-8'));

// Select the first issue that was translated as test
const testIssue = issuesData.find((issue: any) =>
  issue.originalSummary !== issue.finalSummary
);

if (!testIssue) {
  console.error('❌ No issues found that need updating');
  process.exit(1);
}

console.log('🧪 TEST UPDATE - Single Issue');
console.log('==============================\n');
console.log(`Issue Key: ${testIssue.issueKey}`);
console.log(`Issue ID: ${testIssue.id}`);
console.log(`\nCurrent Summary:\n  ${testIssue.originalSummary}`);
console.log(`\nNew Summary:\n  ${testIssue.finalSummary}`);
console.log('\n==============================\n');

// Update the issue via Backlog API
async function updateIssue() {
  // Put apiKey in URL, summary in body
  const url = `https://${domain}/api/v2/issues/${testIssue.issueKey}?apiKey=${apiKey}`;

  // Prepare form data
  const formData = new URLSearchParams({
    summary: testIssue.finalSummary
  });

  try {
    console.log('🔄 Updating issue in Backlog...\n');

    const response = await fetch(url, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData.toString()
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Backlog API error: ${response.status} ${response.statusText}\n${errorText}`);
    }

    const result = await response.json();

    console.log('✅ Issue updated successfully!');
    console.log(`\nUpdated Issue Details:`);
    console.log(`  ID: ${result.id}`);
    console.log(`  Key: ${result.issueKey}`);
    console.log(`  Summary: ${result.summary}`);
    console.log(`  URL: https://${domain}/view/${result.issueKey}`);

  } catch (error) {
    console.error('❌ Failed to update issue:', error);
    process.exit(1);
  }
}

updateIssue();
