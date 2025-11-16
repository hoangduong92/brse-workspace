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
  const url = `https://${domain}/api/v2/issues/HB21373-394?apiKey=${apiKey}`;

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
    console.log(`✅ Success! Issue: ${issue.issueKey} - ${issue.summary}\n`);
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
