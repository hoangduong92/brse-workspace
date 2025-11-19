import dotenv from 'dotenv';

dotenv.config();

const domain = process.env.BACKLOG_DOMAIN;
const apiKey = process.env.BACKLOG_API_KEY;

console.log('Testing Backlog API authentication...\n');

// Test 1: Get project info (read-only)
async function testGetProject() {
  const url = `https://${domain}/api/v2/projects/47358?apiKey=${apiKey}`;

  try {
    console.log('🔍 Test 1: Fetching project info (read-only)...');
    const response = await fetch(url);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ Failed: ${response.status} ${response.statusText}`);
      console.error(errorText);
      return false;
    }

    const project = await response.json();
    console.log(`✅ Success! Project: ${project.name} (${project.projectKey})\n`);
    return true;

  } catch (error) {
    console.error('❌ Error:', error);
    return false;
  }
}

// Test 2: Get issue info (read-only)
async function testGetIssue() {
  const url = `https://${domain}/api/v2/issues/HB21373-411?apiKey=${apiKey}`;

  try {
    console.log('🔍 Test 2: Fetching issue info (read-only)...');
    const response = await fetch(url);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ Failed: ${response.status} ${response.statusText}`);
      console.error(errorText);
      return false;
    }

    const issue = await response.json();
    console.log(`✅ Success! Issue: ${issue.issueKey} - ${issue.summary}`);
    console.log('\n═══════════════════════════════════════════════════');
    console.log(`📋 Issue Details: ${issue.issueKey}`);
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

    console.log('\n═══════════════════════════════════════════════════\n');
    return true;

  } catch (error) {
    console.error('❌ Error:', error);
    return false;
  }
}

async function runTests() {
  const test1 = await testGetProject();
  const test2 = await testGetIssue();

  if (test1 && test2) {
    console.log('✅ API key is valid for read operations');
    console.log('⚠️  If update fails, the API key may not have write permissions');
  } else {
    console.log('❌ API key validation failed');
  }
}

runTests();
