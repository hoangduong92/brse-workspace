#!/usr/bin/env tsx
/**
 * Read values from a specific range in Google Sheets
 * Similar to get_sheet_data() from ggsheet.py
 */

import { google } from 'googleapis';
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function getSheetData(
  spreadsheetId: string,
  sheetName: string,
  range: string
) {
  try {
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

    // Build Sheets service
    const sheets = google.sheets({ version: 'v4', auth: authClient as any });

    // Construct the full range
    const fullRange = `${sheetName}!${range}`;

    console.log(`Reading from spreadsheet: ${spreadsheetId}`);
    console.log(`Range: ${fullRange}\n`);

    // Get the values
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId,
      range: fullRange
    });

    const values = response.data.values || [];

    if (values.length === 0) {
      console.log('No data found in the specified range.');
      return [];
    }

    console.log(`Found ${values.length} row(s) of data:\n`);

    // Display the values
    values.forEach((row, index) => {
      const rowNumber = 5 + index; // Starting from E5
      const cellValue = row[0] || '(empty)';
      console.log(`E${rowNumber}: ${cellValue}`);
    });

    // Export to CSV
    const csvContent = [
      'Row,Cell,Value', // Header
      ...values.map((row, index) => {
        const rowNumber = 5 + index;
        const cellValue = (row[0] || '').replace(/"/g, '""'); // Escape quotes
        return `${rowNumber},E${rowNumber},"${cellValue}"`;
      })
    ].join('\n');

    const csvFilePath = join(__dirname, 'sheet-export.csv');
    writeFileSync(csvFilePath, csvContent, 'utf-8');
    console.log(`\n✓ Data exported to: ${csvFilePath}`);

    return values;

  } catch (error: any) {
    console.error('Error reading sheet data:', error.message);

    if (error.code === 403) {
      console.error('\nPermission denied. Make sure the spreadsheet is shared with:');
      console.error('  mcp-sheets-service@ggsheet-mcp.iam.gserviceaccount.com');
    } else if (error.code === 404) {
      console.error('\nSpreadsheet or sheet not found. Check:');
      console.error(`  - Spreadsheet ID: ${spreadsheetId}`);
      console.error(`  - Sheet name: ${sheetName}`);
    }

    throw error;
  }
}

// Run the function
const spreadsheetId = '1f0dNgvBcLSbh2ckMkczWYQnwUi8zoj9mb42usR10Qfo';
const sheetName = 'スケジュール';
const range = 'E5:E100';

getSheetData(spreadsheetId, sheetName, range)
  .then((values) => {
    console.log(`\n✓ Complete - ${values.length} rows read`);
  })
  .catch((error) => {
    console.error('\nFailed:', error.message);
    process.exit(1);
  });

export { getSheetData };
