#!/usr/bin/env tsx
/**
 * Verify the updates by reading specific cells from Google Sheet
 */

import { google } from 'googleapis';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function verifyUpdates() {
  // Load service account credentials
  const credentialsPath = join(__dirname, 'ggsheet-mcp-09921a7c3245.json');
  const credentials = JSON.parse(readFileSync(credentialsPath, 'utf-8'));

  // Authenticate
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/spreadsheets']
  });

  const authClient = await auth.getClient();
  const sheets = google.sheets({ version: 'v4', auth: authClient as any });

  const spreadsheetId = '1f0dNgvBcLSbh2ckMkczWYQnwUi8zoj9mb42usR10Qfo';
  const sheetName = 'スケジュール';

  // Read some sample updated cells
  const sampleRows = [23, 24, 33, 80, 88, 90];

  console.log('Verifying updates in Google Sheet...\n');

  for (const row of sampleRows) {
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId,
      range: `${sheetName}!E${row}`
    });

    const value = response.data.values?.[0]?.[0] || '(empty)';
    console.log(`E${row}: ${value}\n`);
  }

  console.log('✓ Verification complete');
}

verifyUpdates().catch(console.error);
