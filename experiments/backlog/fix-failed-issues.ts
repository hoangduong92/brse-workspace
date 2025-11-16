import dotenv from 'dotenv';

dotenv.config();

const domain = process.env.BACKLOG_DOMAIN;
const apiKey = process.env.BACKLOG_API_KEY;

// Define the two failed issues with corrected summaries
const failedIssues = [
  {
    issueKey: 'HB21373-374',
    // Remove tab character and format properly
    summary: 'Update spec robot BS1部003_解約リスト更新 -- COE-174 案件名：【CS本部】BS1部003_解約リスト更新　改修依頼'
  },
  {
    issueKey: 'HB21373-335',
    // Add Vietnamese/English first, Japanese second
    summary: 'Thiết kế app show data của bảng phát hiện gian lận lên Kintone -- 不正検知テーブルデータのKintoneアプリ設計'
  }
];

async function updateIssue(issueKey: string, summary: string): Promise<boolean> {
  const url = `https://${domain}/api/v2/issues/${issueKey}?apiKey=${apiKey}`;

  const formData = new URLSearchParams({
    summary: summary
  });

  try {
    console.log(`\n🔄 Updating ${issueKey}...`);
    console.log(`   Summary: ${summary}`);

    const response = await fetch(url, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData.toString()
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.log(`   ❌ Error: ${response.status} ${response.statusText}`);
      console.log(`   ${errorText}`);
      return false;
    }

    const result = await response.json();
    console.log(`   ✅ Success!`);
    console.log(`   URL: https://${domain}/view/${result.issueKey}`);
    return true;

  } catch (error) {
    console.log(`   ❌ Error: ${error}`);
    return false;
  }
}

async function fixFailedIssues() {
  console.log('🔧 Fixing Failed Issues');
  console.log('========================\n');

  let successCount = 0;

  for (const issue of failedIssues) {
    const success = await updateIssue(issue.issueKey, issue.summary);
    if (success) successCount++;
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  console.log('\n========================');
  console.log(`✅ Successfully fixed: ${successCount}/${failedIssues.length}`);
  console.log('========================\n');
}

fixFailedIssues();
