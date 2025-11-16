import { readFileSync, writeFileSync } from 'fs';

// Read the CSV file
const csvContent = readFileSync('rpa-tickets.csv', 'utf-8');
const lines = csvContent.split('\n');

// Keep the header
const header = lines[0];
const dataLines = lines.slice(1).filter(line => line.trim());

// Function to detect if text contains Japanese characters
function hasJapanese(text: string): boolean {
  return /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(text);
}

// Function to detect if text contains Vietnamese characters or common Vietnamese words
function hasVietnamese(text: string): boolean {
  // Check for Vietnamese diacritics
  const hasDiacritics = /[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]/i.test(text);
  // Check for common Vietnamese words
  const hasVnWords = /\b(của|và|trên|cho|với|từ|đến|tại|trong|theo|để|làm|được|các|này|đã|có|sẽ|bị|về|sau|trước|lên|xuống)\b/i.test(text);
  return hasDiacritics || hasVnWords;
}

// Function to reformat summary: [VN/EN] -- [JP]
function reformatSummary(summary: string): string {
  // Remove quotes if present
  let text = summary.replace(/^"|"$/g, '');

  // Try different separator patterns (including full-width space 　)
  const separators = [
    /\s*--\s+/,  // Any whitespace (including full-width) before --, regular space after
    / - /        // Single dash with spaces
  ];

  for (const separator of separators) {
    const parts = text.split(separator);
    if (parts.length === 2) {
      const firstPart = parts[0].trim();
      const secondPart = parts[1].trim();

      // Check if first part has Japanese and second part has Vietnamese/English
      // If so, swap them
      const firstHasJp = hasJapanese(firstPart);
      const secondHasVn = hasVietnamese(secondPart) || !hasJapanese(secondPart);

      if (firstHasJp && secondHasVn) {
        return `${secondPart} -- ${firstPart}`;
      }

      // Already in correct format [VN/EN] -- [JP]
      return text;
    } else if (parts.length > 2 && separator.source.includes(' - ')) {
      // Handle multiple single dashes
      const firstPart = parts[0].trim();
      const lastPart = parts.slice(1).join(' - ').trim();

      const firstHasJp = hasJapanese(firstPart);
      const lastHasVn = hasVietnamese(lastPart) || !hasJapanese(lastPart);

      if (firstHasJp && lastHasVn) {
        return `${lastPart} -- ${firstPart}`;
      }

      return text;
    }
  }

  // No separator found, return as is
  return text;
}

// Process each line
const reformattedLines = dataLines.map(line => {
  // Parse CSV line (simple parser for our format)
  const match = line.match(/^(\d+),"([^"]+)","(.+)"$/);
  if (match) {
    const id = match[1];
    const issueKey = match[2];
    const summary = match[3];

    const reformattedSummary = reformatSummary(summary);

    // Escape quotes in reformatted summary
    const escapedSummary = reformattedSummary.replace(/"/g, '""');

    return `${id},"${issueKey}","${escapedSummary}"`;
  }
  return line;
});

// Create new CSV content
const newCsvContent = header + '\n' + reformattedLines.join('\n');

// Write to new file
const newFilename = 'rpa-tickets-reformatted.csv';
writeFileSync(newFilename, newCsvContent, 'utf-8');

console.log(`✅ Reformatted CSV saved to ${newFilename}`);
console.log(`📝 Format: [VN/EN] -- [JP]`);
