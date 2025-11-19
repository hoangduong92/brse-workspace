import dotenv from 'dotenv';

dotenv.config();

const ISSUE_KEY = 'HB21373-411';
const DOMAIN = process.env.BACKLOG_DOMAIN!;
const API_KEY = process.env.BACKLOG_API_KEY!;

async function getIssueDetails() {
  try {
    // Backlog API: GET /api/v2/issues/:issueIdOrKey
    const url = `https://${DOMAIN}/api/v2/issues/${ISSUE_KEY}?apiKey=${API_KEY}`;

    console.log(`\nFetching issue: ${ISSUE_KEY}...\n`);

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Backlog API error: ${response.status} ${response.statusText}`);
    }

    const issue = await response.json();

    // Display issue details in a readable format
    console.log('═══════════════════════════════════════════════════');
    console.log(`📋 Issue: ${issue.issueKey}`);
    console.log('═══════════════════════════════════════════════════');
    console.log(`\n📌 Summary:\n   ${issue.summary}`);
    console.log(`\n📝 Description:\n   ${issue.description || '(No description)'}`);
    console.log(`\n📊 Status: ${issue.status?.name || 'N/A'}`);
    console.log(`⚡ Priority: ${issue.priority?.name || 'N/A'}`);
    console.log(`🏷️  Issue Type: ${issue.issueType?.name || 'N/A'}`);

    if (issue.assignee) {
      console.log(`👤 Assignee: ${issue.assignee.name}`);
    } else {
      console.log(`👤 Assignee: (Unassigned)`);
    }

    console.log(`\n📅 Created: ${new Date(issue.created).toLocaleString()}`);
    console.log(`📅 Updated: ${new Date(issue.updated).toLocaleString()}`);

    if (issue.dueDate) {
      console.log(`⏰ Due Date: ${issue.dueDate}`);
    }

    if (issue.category && issue.category.length > 0) {
      console.log(`\n🏷️  Categories: ${issue.category.map((c: any) => c.name).join(', ')}`);
    }

    if (issue.milestone && issue.milestone.length > 0) {
      console.log(`🎯 Milestones: ${issue.milestone.map((m: any) => m.name).join(', ')}`);
    }

    if (issue.customFields && issue.customFields.length > 0) {
      console.log(`\n📋 Custom Fields:`);
      issue.customFields.forEach((field: any) => {
        const value = field.value || '(Empty)';
        console.log(`   ${field.name}: ${value}`);
      });
    }

    console.log('\n═══════════════════════════════════════════════════');
    console.log('\n💾 Full JSON data:\n');
    console.log(JSON.stringify(issue, null, 2));

  } catch (error) {
    console.error('\n❌ Error fetching issue:', error);
    console.error('\n💡 Tips:');
    console.error('   - Make sure .env file has BACKLOG_DOMAIN and BACKLOG_API_KEY');
    console.error('   - Check if issue key HB21373-411 exists in Backlog');
    console.error('   - Verify API key has read permissions');
  }
}

getIssueDetails();
