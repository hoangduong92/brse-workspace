import { readFileSync, writeFileSync } from 'fs';

// Read the issues data
const issuesData = JSON.parse(readFileSync('issues-to-update.json', 'utf-8'));

// Define special cases that need manual correction
const specialCases: Record<string, string> = {
  'HB21373-324': '要件定義書作成 -- Làm file thiết kế',
  'HB21373-323': '35_RPA Check ExcelDLL trước khi đăng ký MOCS -- 35_RPA_MOCS登録前のExcelDLL不備対応'
};

// Update the issues data
issuesData.forEach((issue: any) => {
  if (specialCases[issue.issueKey]) {
    console.log(`✏️  Fixing ${issue.issueKey}`);
    console.log(`   Before: ${issue.finalSummary}`);
    issue.finalSummary = specialCases[issue.issueKey];
    console.log(`   After:  ${issue.finalSummary}\n`);
  }
});

// Save updated data
writeFileSync('issues-to-update.json', JSON.stringify(issuesData, null, 2), 'utf-8');

// Regenerate CSV
const csvRows = ['ID,Issue Key,Summary'];
issuesData.forEach((issue: any) => {
  const escapedSummary = issue.finalSummary.replace(/"/g, '""');
  csvRows.push(`${issue.id},"${issue.issueKey}","${escapedSummary}"`);
});

const csvContent = csvRows.join('\n');
writeFileSync('rpa-tickets-final.csv', csvContent, 'utf-8');

console.log('✅ Special cases fixed!');
console.log('✅ Updated issues-to-update.json');
console.log('✅ Regenerated rpa-tickets-final.csv');
