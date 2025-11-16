import { readFileSync, writeFileSync } from 'fs';

// Read translations
const translations = JSON.parse(readFileSync('translations.json', 'utf-8'));

// Read the reformatted CSV
const csvContent = readFileSync('rpa-tickets-reformatted.csv', 'utf-8');
const lines = csvContent.split('\n');
const header = lines[0];
const dataLines = lines.slice(1).filter(line => line.trim());

function hasJapanese(text: string): boolean {
  return /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(text);
}

interface FinalIssue {
  id: string;
  issueKey: string;
  originalSummary: string;
  finalSummary: string;
}

const finalIssues: FinalIssue[] = [];

dataLines.forEach(line => {
  const match = line.match(/^(\d+),"([^"]+)","(.+)"$/);
  if (match) {
    const id = match[1];
    const issueKey = match[2];
    const summary = match[3];

    let finalSummary = summary;

    // If summary doesn't have Japanese, add translation
    if (!hasJapanese(summary)) {
      const japaneseTranslation = translations[summary];
      if (japaneseTranslation) {
        finalSummary = `${summary} -- ${japaneseTranslation}`;
      } else {
        console.warn(`⚠️  No translation found for: ${summary}`);
      }
    }

    finalIssues.push({
      id,
      issueKey,
      originalSummary: summary,
      finalSummary
    });
  }
});

// Generate final CSV
const csvRows = finalIssues.map(issue => {
  const escapedSummary = issue.finalSummary.replace(/"/g, '""');
  return `${issue.id},"${issue.issueKey}","${escapedSummary}"`;
});

const finalCsvContent = header + '\n' + csvRows.join('\n');

// Write to file
writeFileSync('rpa-tickets-final.csv', finalCsvContent, 'utf-8');

console.log(`✅ Generated final CSV with ${finalIssues.length} issues`);
console.log('📝 All summaries now in [VN/EN] -- [JP] format\n');

// Show sample
console.log('Sample entries:');
console.log('===============');
finalIssues.slice(0, 10).forEach(issue => {
  console.log(`[${issue.issueKey}]`);
  if (issue.originalSummary !== issue.finalSummary) {
    console.log(`  Before: ${issue.originalSummary}`);
    console.log(`  After:  ${issue.finalSummary}`);
  } else {
    console.log(`  ${issue.finalSummary}`);
  }
  console.log('');
});

// Export issues data for Backlog update script
writeFileSync('issues-to-update.json', JSON.stringify(finalIssues, null, 2), 'utf-8');
console.log('✅ Exported issues data to issues-to-update.json');
