import { readFileSync } from 'fs';

// Read the reformatted CSV
const csvContent = readFileSync('rpa-tickets-reformatted.csv', 'utf-8');
const lines = csvContent.split('\n');
const dataLines = lines.slice(1).filter(line => line.trim());

function hasJapanese(text: string): boolean {
  return /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(text);
}

interface Issue {
  id: string;
  issueKey: string;
  summary: string;
  needsTranslation: boolean;
}

const issues: Issue[] = [];

dataLines.forEach(line => {
  const match = line.match(/^(\d+),"([^"]+)","(.+)"$/);
  if (match) {
    const id = match[1];
    const issueKey = match[2];
    const summary = match[3];

    const needsTranslation = !hasJapanese(summary);

    issues.push({
      id,
      issueKey,
      summary,
      needsTranslation
    });
  }
});

const needsTranslation = issues.filter(i => i.needsTranslation);
const alreadyHasJapanese = issues.filter(i => !i.needsTranslation);

console.log(`Total issues: ${issues.length}`);
console.log(`Already has Japanese: ${alreadyHasJapanese.length}`);
console.log(`Needs translation: ${needsTranslation.length}\n`);

console.log('Issues that need Japanese translation:');
console.log('=====================================');
needsTranslation.forEach((issue, index) => {
  console.log(`${index + 1}. [${issue.issueKey}] ${issue.summary}`);
});
