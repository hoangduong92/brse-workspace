import { readFileSync, writeFileSync } from 'fs';
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

// Filter out the already tested issue
const alreadyUpdated = 'HB21373-394';
const issuesToUpdate = issuesData.filter((issue: any) => issue.issueKey !== alreadyUpdated);

console.log('🚀 BULK UPDATE - All Remaining Issues');
console.log('======================================\n');
console.log(`Total issues: ${issuesData.length}`);
console.log(`Already updated: 1 (${alreadyUpdated})`);
console.log(`To update: ${issuesToUpdate.length}\n`);
console.log('======================================\n');

interface UpdateResult {
  issueKey: string;
  success: boolean;
  error?: string;
}

const results: UpdateResult[] = [];

async function updateIssue(issue: any): Promise<boolean> {
  const url = `https://${domain}/api/v2/issues/${issue.issueKey}?apiKey=${apiKey}`;

  const formData = new URLSearchParams({
    summary: issue.finalSummary
  });

  try {
    const response = await fetch(url, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData.toString()
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`${response.status} ${response.statusText}: ${errorText}`);
    }

    return true;

  } catch (error) {
    throw error;
  }
}

async function updateAll() {
  let successCount = 0;
  let errorCount = 0;

  for (let i = 0; i < issuesToUpdate.length; i++) {
    const issue = issuesToUpdate[i];
    const progress = `[${i + 1}/${issuesToUpdate.length}]`;

    try {
      process.stdout.write(`${progress} Updating ${issue.issueKey}... `);

      await updateIssue(issue);

      console.log('✅');
      successCount++;
      results.push({ issueKey: issue.issueKey, success: true });

      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 200));

    } catch (error) {
      console.log(`❌ Error: ${error}`);
      errorCount++;
      results.push({
        issueKey: issue.issueKey,
        success: false,
        error: String(error)
      });
    }
  }

  console.log('\n======================================');
  console.log('📊 UPDATE SUMMARY');
  console.log('======================================\n');
  console.log(`✅ Successfully updated: ${successCount}`);
  console.log(`❌ Failed: ${errorCount}`);
  console.log(`📝 Total processed: ${issuesToUpdate.length}\n`);

  if (errorCount > 0) {
    console.log('Failed issues:');
    results.filter(r => !r.success).forEach(r => {
      console.log(`  - ${r.issueKey}: ${r.error}`);
    });
    console.log('');
  }

  // Save results to file
  writeFileSync('update-results.json', JSON.stringify(results, null, 2), 'utf-8');
  console.log('✅ Results saved to update-results.json');

  if (successCount > 0) {
    console.log(`\n🎉 All updates complete! Check Backlog project: https://${domain}/projects/HB21373`);
  }
}

updateAll();
