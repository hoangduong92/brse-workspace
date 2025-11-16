#!/usr/bin/env tsx
/**
 * Compare Google Sheet data with Backlog CSV and update matching entries
 */

import { google } from 'googleapis';
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

interface BacklogIssue {
  id: string;
  issueKey: string;
  summary: string;
}

interface SheetRow {
  row: number;
  cell: string;
  value: string;
  issueKeys: string[];
}

// Extract issue keys from text (HB21373-XXX or COE-XXX)
function extractIssueKeys(text: string | undefined): string[] {
  if (!text) return [];

  const patterns = [
    /HB21373-\d+/g,
    /COE-\d+/g
  ];

  const keys: string[] = [];
  for (const pattern of patterns) {
    const matches = text.match(pattern);
    if (matches) {
      keys.push(...matches);
    }
  }

  return [...new Set(keys)]; // Remove duplicates
}

// Parse CSV file
function parseCSV(content: string): string[][] {
  const lines = content.trim().split('\n');
  const rows: string[][] = [];

  for (const line of lines) {
    const row: string[] = [];
    let inQuote = false;
    let currentField = '';

    for (let i = 0; i < line.length; i++) {
      const char = line[i];

      if (char === '"') {
        if (inQuote && line[i + 1] === '"') {
          currentField += '"';
          i++; // Skip next quote
        } else {
          inQuote = !inQuote;
        }
      } else if (char === ',' && !inQuote) {
        row.push(currentField);
        currentField = '';
      } else {
        currentField += char;
      }
    }

    row.push(currentField); // Add last field
    rows.push(row);
  }

  return rows;
}

async function updateSheetFromBacklog() {
  try {
    console.log('Step 1: Reading Backlog CSV (rpa-tickets-final.csv)...\n');

    // Read Backlog CSV
    const backlogCsvPath = join(__dirname, 'rpa-tickets-final.csv');
    const backlogCsvContent = readFileSync(backlogCsvPath, 'utf-8');
    const backlogRows = parseCSV(backlogCsvContent);

    // Parse Backlog issues (skip header)
    const backlogIssues: BacklogIssue[] = backlogRows.slice(1).map(row => ({
      id: row[0],
      issueKey: row[1],
      summary: row[2]
    }));

    console.log(`Found ${backlogIssues.length} Backlog issues\n`);

    // Create a map for quick lookup
    const backlogMap = new Map<string, BacklogIssue>();
    backlogIssues.forEach(issue => {
      backlogMap.set(issue.issueKey, issue);
    });

    console.log('Step 2: Reading Google Sheet export (sheet-export.csv)...\n');

    // Read Sheet export
    const sheetCsvPath = join(__dirname, 'sheet-export.csv');
    const sheetCsvContent = readFileSync(sheetCsvPath, 'utf-8');
    const sheetRows = parseCSV(sheetCsvContent);

    // Parse sheet rows (skip header)
    const sheetData: SheetRow[] = sheetRows.slice(1)
      .filter(row => row.length >= 3) // Ensure row has enough columns
      .map(row => ({
        row: parseInt(row[0]),
        cell: row[1],
        value: row[2] || '',
        issueKeys: extractIssueKeys(row[2])
      }));

    console.log(`Found ${sheetData.length} rows in Google Sheet\n`);

    console.log('Step 3: Matching and preparing updates...\n');

    // Find matches and prepare updates
    const updates: Array<{
      row: number;
      cell: string;
      oldValue: string;
      newValue: string;
      issueKey: string;
    }> = [];

    for (const sheetRow of sheetData) {
      if (sheetRow.issueKeys.length === 0) continue;

      // Check if any issue key matches Backlog
      for (const issueKey of sheetRow.issueKeys) {
        const backlogIssue = backlogMap.get(issueKey);

        if (backlogIssue) {
          // Found a match - prepare update
          // Keep the issue key prefix and update the rest
          const newValue = `${issueKey} ${backlogIssue.summary}`;

          updates.push({
            row: sheetRow.row,
            cell: sheetRow.cell,
            oldValue: sheetRow.value,
            newValue: newValue,
            issueKey: issueKey
          });

          console.log(`✓ Match found: ${issueKey}`);
          console.log(`  Row: ${sheetRow.row}`);
          console.log(`  Old: ${sheetRow.value.substring(0, 80)}...`);
          console.log(`  New: ${newValue}`);
          console.log('');

          break; // Only update once per row
        }
      }
    }

    if (updates.length === 0) {
      console.log('No matches found. Nothing to update.');
      return;
    }

    console.log(`\nStep 4: Updating ${updates.length} cells in Google Sheet...\n`);

    // Load service account credentials
    const credentialsPath = join(__dirname, 'ggsheet-mcp-09921a7c3245.json');
    const credentials = JSON.parse(readFileSync(credentialsPath, 'utf-8'));

    // Authenticate with service account
    const auth = new google.auth.GoogleAuth({
      credentials,
      scopes: [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
      ]
    });

    const authClient = await auth.getClient();
    const sheets = google.sheets({ version: 'v4', auth: authClient as any });

    const spreadsheetId = '1f0dNgvBcLSbh2ckMkczWYQnwUi8zoj9mb42usR10Qfo';
    const sheetName = 'スケジュール';

    // Prepare batch update
    const batchData = updates.map(update => ({
      range: `${sheetName}!E${update.row}`,
      values: [[update.newValue]]
    }));

    // Execute batch update
    const response = await sheets.spreadsheets.values.batchUpdate({
      spreadsheetId,
      requestBody: {
        valueInputOption: 'USER_ENTERED',
        data: batchData
      }
    });

    console.log(`✓ Successfully updated ${response.data.totalUpdatedCells} cells\n`);

    // Save update report
    const reportPath = join(__dirname, 'update-report.json');
    writeFileSync(reportPath, JSON.stringify(updates, null, 2), 'utf-8');
    console.log(`✓ Update report saved to: ${reportPath}\n`);

    // Summary
    console.log('=== Update Summary ===');
    console.log(`Total matches found: ${updates.length}`);
    console.log(`Cells updated: ${response.data.totalUpdatedCells}`);
    console.log(`Rows updated: ${response.data.totalUpdatedRows}`);

    return updates;

  } catch (error: any) {
    console.error('Error updating sheet:', error.message);

    if (error.code === 403) {
      console.error('\nPermission denied. Make sure the spreadsheet is shared with:');
      console.error('  mcp-sheets-service@ggsheet-mcp.iam.gserviceaccount.com');
    }

    throw error;
  }
}

// Run the function
updateSheetFromBacklog()
  .then(() => {
    console.log('\n✓ Complete');
  })
  .catch((error) => {
    console.error('\nFailed:', error.message);
    process.exit(1);
  });

export { updateSheetFromBacklog };
