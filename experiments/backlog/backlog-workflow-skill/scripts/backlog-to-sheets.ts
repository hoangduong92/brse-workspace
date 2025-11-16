#!/usr/bin/env node
/**
 * Backlog to Google Sheets Sync (User-Config Compatible)
 * Manual sync: Syncs specific issues from user config to Google Sheets
 *
 * Usage:
 *   npm run sheets:sync              # Sync configured issues
 *   npm run sheets:sync -- --dry-run # Preview without updating
 *   npm run sheets:sync -- --test    # Test with 1 issue only
 */

import { BacklogClient } from '../../src/backlog-client.js';
import { google } from 'googleapis';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import dotenv from 'dotenv';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

dotenv.config();

// Load user-specific configuration
const configPath = 'workflow/user-config.json';
if (!existsSync(configPath)) {
  console.error('❌ user-config.json not found');
  console.error('Run interactive setup with Claude');
  process.exit(1);
}

const config = JSON.parse(readFileSync(configPath, 'utf-8'));

// Verify Google Sheets configuration
if (!config.googleSheets?.spreadsheetId || config.googleSheets.spreadsheetId.startsWith('<')) {
  console.error('❌ Google Sheets not configured in user-config.json');
  console.error('Add Google Sheets settings to workflow/user-config.json:');
  console.error('  "googleSheets": {');
  console.error('    "spreadsheetId": "your-spreadsheet-id",');
  console.error('    "sheetName": "Sheet1",');
  console.error('    "range": "E5:E100",');
  console.error('    "credentialsFile": "path/to/credentials.json"');
  console.error('  }');
  process.exit(1);
}

// Check for issue keys
if (!config.sheetsSync?.issueKeys || config.sheetsSync.issueKeys.length === 0) {
  console.error('❌ No issue keys configured for manual sync');
  console.error('Add issue keys to workflow/user-config.json:');
  console.error('  "sheetsSync": {');
  console.error('    "issueKeys": ["HB21373-399", "HB21373-397", ...]');
  console.error('  }');
  console.error('\nOr use auto-sync instead: npm run sheets:auto');
  process.exit(1);
}

// Parse command line arguments
const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run') || config.execution?.dryRun || false;
const testMode = args.includes('--test') || config.execution?.testWithOneIssue || false;

interface BacklogIssue {
  id: number;
  issueKey: string;
  summary: string;
}

interface SyncResult {
  issueKey: string;
  summary: string;
  action: 'added' | 'updated' | 'skipped';
  row?: number;
  error?: string;
}

class BacklogToSheetsSync {
  private backlogClient!: BacklogClient;
  private sheetsService: any;
  private spreadsheetId!: string;
  private sheetName!: string;
  private range!: string;

  private constructor() {}

  static async create(): Promise<BacklogToSheetsSync> {
    const instance = new BacklogToSheetsSync();
    await instance.init();
    return instance;
  }

  private async init() {
    console.log('🔧 Initializing Backlog to Sheets sync...\n');

    // Initialize Backlog client
    const backlogDomain = process.env.BACKLOG_DOMAIN;
    const backlogApiKey = process.env.BACKLOG_API_KEY;

    if (!backlogDomain || !backlogApiKey) {
      throw new Error('Missing BACKLOG_DOMAIN or BACKLOG_API_KEY in .env');
    }

    this.backlogClient = new BacklogClient({
      domain: backlogDomain,
      apiKey: backlogApiKey
    });

    // Initialize Google Sheets
    this.spreadsheetId = config.googleSheets.spreadsheetId;
    this.sheetName = config.googleSheets.sheetName;
    this.range = config.googleSheets.range || 'A1:A100';
    await this.initGoogleSheets();

    console.log(`✅ Connected to Backlog project: ${config.backlog.projectKey}`);
    console.log(`✅ Connected to Google Sheet: ${this.sheetName}`);
    console.log();
  }

  private async initGoogleSheets() {
    // Load service account credentials
    const credentialsFile = config.googleSheets.credentialsFile || 'backlog/ggsheet-mcp-09921a7c3245.json';

    if (!existsSync(credentialsFile)) {
      throw new Error(`Credentials file not found: ${credentialsFile}\nUpdate credentialsFile in user-config.json`);
    }

    const credentials = JSON.parse(readFileSync(credentialsFile, 'utf-8'));

    // Authenticate with service account
    const auth = new google.auth.GoogleAuth({
      credentials,
      scopes: [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
      ]
    });

    const authClient = await auth.getClient();
    this.sheetsService = google.sheets({ version: 'v4', auth: authClient as any });
  }

  /**
   * Fetch issues from Backlog
   */
  private async fetchBacklogIssues(issueKeys: string[]): Promise<Map<string, BacklogIssue>> {
    console.log(`📥 Fetching ${issueKeys.length} issues from Backlog...\n`);

    const issueMap = new Map<string, BacklogIssue>();

    for (const issueKey of issueKeys) {
      try {
        // Fetch via API
        const url = `https://${process.env.BACKLOG_DOMAIN}/api/v2/issues/${issueKey}`;
        const response = await fetch(url + `?apiKey=${process.env.BACKLOG_API_KEY}`);

        if (response.ok) {
          const issue = await response.json();
          issueMap.set(issueKey, {
            id: issue.id,
            issueKey: issue.issueKey,
            summary: issue.summary
          });
          console.log(`  ✓ ${issueKey}: ${issue.summary}`);
        } else {
          console.error(`  ✗ ${issueKey}: Not found (${response.status})`);
        }
      } catch (error) {
        console.error(`  ✗ ${issueKey}: Error - ${error}`);
      }
    }

    console.log(`\n✅ Fetched ${issueMap.size} / ${issueKeys.length} issues\n`);
    return issueMap;
  }

  /**
   * Read current Google Sheet data
   */
  private async readSheetData(): Promise<Map<number, string>> {
    console.log('📖 Reading current Google Sheet data...\n');

    const sheetData = new Map<number, string>();

    try {
      const response = await this.sheetsService.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: `${this.sheetName}!${this.range}`
      });

      const rows = response.data.values || [];
      rows.forEach((row: string[], index: number) => {
        if (row[0]) {
          const rangeStart = this.range.match(/(\d+)/)?.[1] || '1';
          const actualRow = parseInt(rangeStart) + index;
          sheetData.set(actualRow, row[0]);
        }
      });

      console.log(`  ✓ Read ${sheetData.size} non-empty cells\n`);
    } catch (error: any) {
      console.error(`  ✗ Error reading sheet: ${error.message}\n`);
    }

    return sheetData;
  }

  /**
   * Find row by issue key
   */
  private findIssueRow(sheetData: Map<number, string>, issueKey: string): number | null {
    for (const [row, value] of sheetData.entries()) {
      if (value.includes(issueKey)) {
        return row;
      }
    }
    return null;
  }

  /**
   * Find first empty row
   */
  private findFirstEmptyRow(sheetData: Map<number, string>): number {
    const rangeStart = parseInt(this.range.match(/(\d+)/)?.[1] || '1');
    const rangeEnd = parseInt(this.range.match(/(\d+)$/)?.[0] || '100');

    for (let row = rangeStart; row <= rangeEnd; row++) {
      if (!sheetData.has(row)) {
        return row;
      }
    }

    return rangeEnd; // Fallback to end of range
  }

  /**
   * Sync issues to Google Sheets
   */
  private async syncToSheets(
    issues: Map<string, BacklogIssue>,
    sheetData: Map<number, string>
  ): Promise<SyncResult[]> {
    console.log('🔄 Syncing issues to Google Sheets...\n');

    const results: SyncResult[] = [];
    const updates: Array<{ row: number; value: string }> = [];

    for (const [issueKey, issue] of issues.entries()) {
      const cellValue = `${issueKey} ${issue.summary}`;
      const existingRow = this.findIssueRow(sheetData, issueKey);

      if (existingRow) {
        // Update existing row
        const currentValue = sheetData.get(existingRow) || '';
        if (currentValue !== cellValue) {
          console.log(`  🔄 [${issueKey}] Update at row ${existingRow}`);
          console.log(`     Old: ${currentValue}`);
          console.log(`     New: ${cellValue}\n`);

          updates.push({ row: existingRow, value: cellValue });
          results.push({
            issueKey,
            summary: issue.summary,
            action: 'updated',
            row: existingRow
          });
        } else {
          console.log(`  ✓ [${issueKey}] Already up to date at row ${existingRow}\n`);
          results.push({
            issueKey,
            summary: issue.summary,
            action: 'skipped',
            row: existingRow
          });
        }
      } else {
        // Add to empty row
        const emptyRow = this.findFirstEmptyRow(sheetData);
        console.log(`  ➕ [${issueKey}] Add to row ${emptyRow}`);
        console.log(`     Value: ${cellValue}\n`);

        updates.push({ row: emptyRow, value: cellValue });
        sheetData.set(emptyRow, cellValue); // Update map so next iteration knows this row is taken
        results.push({
          issueKey,
          summary: issue.summary,
          action: 'added',
          row: emptyRow
        });
      }
    }

    if (dryRun) {
      console.log(`🔍 DRY RUN MODE - No actual updates will be made`);
      console.log(`📊 Would update ${updates.length} cells\n`);
      return results;
    }

    if (testMode && updates.length > 0) {
      console.log(`🧪 TEST MODE - Updating only 1 cell\n`);
      updates.splice(1); // Keep only first update
    }

    // Perform batch update
    if (updates.length > 0) {
      try {
        const batchData = updates.map(update => ({
          range: `${this.sheetName}!${this.range.split(':')[0].replace(/\d+/, update.row.toString())}`,
          values: [[update.value]]
        }));

        await this.sheetsService.spreadsheets.values.batchUpdate({
          spreadsheetId: this.spreadsheetId,
          requestBody: {
            data: batchData,
            valueInputOption: 'RAW'
          }
        });

        console.log(`✅ Updated ${updates.length} cell(s) in Google Sheets\n`);
      } catch (error: any) {
        console.error(`❌ Error updating sheets: ${error.message}\n`);
        results.forEach(r => r.error = error.message);
      }
    }

    return results;
  }

  /**
   * Generate report
   */
  private async generateReport(results: SyncResult[]) {
    const timestamp = new Date().toISOString().split('T')[0];
    const reportPath = `workflow/sheets-sync-report-${timestamp}.json`;

    const report = {
      timestamp: new Date().toISOString(),
      mode: dryRun ? 'dry-run' : testMode ? 'test' : 'production',
      config: {
        spreadsheetId: this.spreadsheetId,
        sheetName: this.sheetName,
        range: this.range,
        issueKeys: config.sheetsSync.issueKeys
      },
      summary: {
        total: results.length,
        added: results.filter(r => r.action === 'added').length,
        updated: results.filter(r => r.action === 'updated').length,
        skipped: results.filter(r => r.action === 'skipped').length,
        failed: results.filter(r => r.error).length
      },
      results
    };

    writeFileSync(reportPath, JSON.stringify(report, null, 2));

    console.log('='.repeat(60));
    console.log('📊 Summary\n');
    console.log(`Total issues: ${report.summary.total}`);
    console.log(`Added: ${report.summary.added}`);
    console.log(`Updated: ${report.summary.updated}`);
    console.log(`Skipped: ${report.summary.skipped}`);
    console.log(`Failed: ${report.summary.failed}`);
    console.log(`\n📄 Report saved: ${reportPath}`);
  }

  /**
   * Main execution
   */
  async run() {
    try {
      const issueKeys = testMode
        ? [config.sheetsSync.issueKeys[0]]
        : config.sheetsSync.issueKeys;

      const issues = await this.fetchBacklogIssues(issueKeys);
      const sheetData = await this.readSheetData();
      const results = await this.syncToSheets(issues, sheetData);
      await this.generateReport(results);
    } catch (error) {
      console.error('\n❌ Sync failed:', error);
      process.exit(1);
    }
  }
}

// Run sync
BacklogToSheetsSync.create().then(sync => sync.run());
