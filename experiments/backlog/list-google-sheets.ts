#!/usr/bin/env tsx
/**
 * List Google Spreadsheets accessible by the service account
 * Similar to list_spreadsheets() from ggsheet.py
 */

import { google } from 'googleapis';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function listSpreadsheets() {
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

    // Build Drive service
    const drive = google.drive({ version: 'v3', auth: authClient as any });

    // Query for spreadsheets
    const query = "mimeType='application/vnd.google-apps.spreadsheet'";

    console.log('Searching for spreadsheets accessible by service account...\n');

    const response = await drive.files.list({
      q: query,
      spaces: 'drive',
      includeItemsFromAllDrives: true,
      supportsAllDrives: true,
      fields: 'files(id, name, createdTime, modifiedTime, owners)',
      orderBy: 'modifiedTime desc',
      pageSize: 50
    });

    const spreadsheets = response.data.files || [];

    if (spreadsheets.length === 0) {
      console.log('No spreadsheets found.');
      console.log('\nNote: Service account can only access spreadsheets that have been explicitly shared with:');
      console.log('  mcp-sheets-service@ggsheet-mcp.iam.gserviceaccount.com');
      return [];
    }

    console.log(`Found ${spreadsheets.length} spreadsheet(s):\n`);

    spreadsheets.forEach((sheet, index) => {
      console.log(`${index + 1}. ${sheet.name}`);
      console.log(`   ID: ${sheet.id}`);
      console.log(`   Modified: ${sheet.modifiedTime}`);
      console.log(`   Created: ${sheet.createdTime}`);
      if (sheet.owners && sheet.owners.length > 0) {
        console.log(`   Owner: ${sheet.owners[0].displayName || sheet.owners[0].emailAddress}`);
      }
      console.log('');
    });

    return spreadsheets;

  } catch (error: any) {
    console.error('Error listing spreadsheets:', error.message);
    if (error.code === 'ENOENT') {
      console.error('\nCredentials file not found. Make sure ggsheet-mcp-09921a7c3245.json exists.');
    }
    throw error;
  }
}

// Run the function
listSpreadsheets()
  .then(() => {
    console.log('✓ Complete');
  })
  .catch((error) => {
    console.error('Failed:', error.message);
    process.exit(1);
  });

export { listSpreadsheets };
