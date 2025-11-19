import dotenv from 'dotenv';

dotenv.config();

const PARENT_ISSUE_KEY = 'HB21373-411';
const DOMAIN = process.env.BACKLOG_DOMAIN!;
const API_KEY = process.env.BACKLOG_API_KEY!;

async function getChildIssues() {
  try {
    console.log(`\n🔍 Fetching child issues of ${PARENT_ISSUE_KEY}...\n`);

    // Step 1: Get the parent issue to get its ID
    const parentUrl = `https://${DOMAIN}/api/v2/issues/${PARENT_ISSUE_KEY}?apiKey=${API_KEY}`;
    const parentResponse = await fetch(parentUrl);

    if (!parentResponse.ok) {
      throw new Error(`Failed to fetch parent issue: ${parentResponse.status} ${parentResponse.statusText}`);
    }

    const parentIssue = await parentResponse.json();
    console.log(`📋 Parent Issue: ${parentIssue.issueKey} - ${parentIssue.summary}\n`);

    // Step 2: Get child issues using parentIssueId filter
    const childrenUrl = `https://${DOMAIN}/api/v2/issues?apiKey=${API_KEY}&parentIssueId[]=${parentIssue.id}&count=100`;
    const childrenResponse = await fetch(childrenUrl);

    if (!childrenResponse.ok) {
      throw new Error(`Failed to fetch child issues: ${childrenResponse.status} ${childrenResponse.statusText}`);
    }

    const childIssues = await childrenResponse.json();

    if (childIssues.length === 0) {
      console.log('📭 No child issues found for this ticket.\n');
      return;
    }

    console.log(`📦 Found ${childIssues.length} child issue(s):\n`);
    console.log('═══════════════════════════════════════════════════');

    childIssues.forEach((issue: any, index: number) => {
      console.log(`\n${index + 1}. ${issue.issueKey}`);
      console.log(`   ${issue.summary}`);
    });

    console.log('\n═══════════════════════════════════════════════════\n');

    // Also display in table format
    console.log('📊 Summary Table:\n');
    const maxKeyLength = Math.max(8, ...childIssues.map((i: any) => i.issueKey.length));
    const maxSummaryLength = Math.max(10, ...childIssues.map((i: any) => i.summary.length));

    const separator = `+${'-'.repeat(maxKeyLength + 2)}+${'-'.repeat(maxSummaryLength + 2)}+`;
    console.log(separator);
    console.log(`| ${'Issue Key'.padEnd(maxKeyLength)} | ${'Summary'.padEnd(maxSummaryLength)} |`);
    console.log(separator);

    childIssues.forEach((issue: any) => {
      console.log(`| ${issue.issueKey.padEnd(maxKeyLength)} | ${issue.summary.padEnd(maxSummaryLength)} |`);
    });

    console.log(separator);
    console.log();

  } catch (error) {
    console.error('❌ Error:', error);
  }
}

getChildIssues();
