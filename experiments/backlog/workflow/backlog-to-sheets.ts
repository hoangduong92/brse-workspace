#!/usr/bin/env node
/**
 * Backlog to Google Sheets Sync
 * Automated workflow: Fetch issues from Backlog → Update Google Sheets
 *
 * Usage:
 *   npm run sheets:sync              # Run with default config
 *   npm run sheets:sync -- --dry-run # Preview without updating
 *   npm run sheets:sync -- --test    # Test with 1 issue only
 */

import { BacklogClient } from '../src/backlog-client.js';
import { google } from 'googleapis';
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import dotenv from 'dotenv';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

dotenv.config();

// Load configuration
const configPath = join(dirname(__dirname), 'workflow', 'sheets-sync-config.json');
const config = JSON.parse(readFileSync(configPath, 'utf-8'));

// Parse command line arguments
const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run') || config.execution.dryRun;
const testMode = args.includes('--test') || config.execution.testWithOneIssue;

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

  private constructor() {
    // Private constructor - use create() instead
  }

  static async create(): Promise<BacklogToSheetsSync> {
    const instance = new BacklogToSheetsSync();
    await instance.init();
    return instance;
  }

  private async init() {
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

    // Initialize Google Sheets client
    this.spreadsheetId = config.googleSheets.spreadsheetId;
    this.sheetName = config.googleSheets.sheetName;
    await this.initGoogleSheets();
  }

  private async initGoogleSheets() {
    // Load service account credentials
    const credentialsPath = join(dirname(__dirname), config.googleSheets.credentialsFile);
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
    this.sheetsService = google.sheets({ version: 'v4', auth: authClient as any });
  }

  /**
   * Fetch issues from Backlog by issue keys
   */
  private async fetchBacklogIssues(issueKeys: string[]): Promise<BacklogIssue[]> {
    console.log(`\n📥 Fetching ${issueKeys.length} issues from Backlog...`);

    const issues: BacklogIssue[] = [];
    const backlogDomain = process.env.BACKLOG_DOMAIN;
    const backlogApiKey = process.env.BACKLOG_API_KEY;

    for (const issueKey of issueKeys) {
      try {
        const url = `https://${backlogDomain}/api/v2/issues/${issueKey}?apiKey=${backlogApiKey}`;
        const response = await fetch(url);

        if (!response.ok) {
          console.warn(`⚠️  Issue ${issueKey} not found (${response.status})`);
          continue;
        }

        const issue = await response.json();
        issues.push({
          id: issue.id,
          issueKey: issue.issueKey,
          summary: issue.summary
        });

        console.log(`  ✓ ${issue.issueKey}: ${issue.summary}`);
      } catch (error: any) {
        console.error(`  ✗ Error fetching ${issueKey}: ${error.message}`);
      }
    }

    return issues;
  }

  /**
   * Read existing data from Google Sheet
   */
  private async readSheetData(range: string): Promise<string[][]> {
    const fullRange = `${this.sheetName}!${range}`;

    try {
      const response = await this.sheetsService.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: fullRange
      });

      return response.data.values || [];
    } catch (error: any) {
      console.error(`Error reading sheet: ${error.message}`);
      return [];
    }
  }

  /**
   * Extract issue key from cell value
   */
  private extractIssueKey(cellValue: string): string | null {
    const match = cellValue.match(/HB21373-\d+|COE-\d+/);
    return match ? match[0] : null;
  }

  /**
   * Find row for issue key in existing data
   */
  private findRowForIssueKey(
    issueKey: string,
    existingData: string[][],
    startRow: number
  ): number | null {
    for (let i = 0; i < existingData.length; i++) {
      const cellValue = existingData[i][0] || '';
      const cellIssueKey = this.extractIssueKey(cellValue);

      if (cellIssueKey === issueKey) {
        return startRow + i;
      }
    }

    return null;
  }

  /**
   * Find next empty row in sheet
   */
  private findNextEmptyRow(existingData: string[][], startRow: number): number {
    for (let i = 0; i < existingData.length; i++) {
      const cellValue = existingData[i][0] || '';
      if (cellValue.trim() === '' || cellValue === '(empty)') {
        return startRow + i;
      }
    }

    // If no empty row found, append at the end
    return startRow + existingData.length;
  }

  /**
   * Update Google Sheet with issue data
   */
  private async updateSheet(
    updates: Array<{ row: number; value: string }>
  ): Promise<void> {
    if (updates.length === 0) {
      console.log('\n✓ No updates needed');
      return;
    }

    if (dryRun) {
      console.log('\n🔍 DRY RUN - Would update:');
      updates.forEach(update => {
        console.log(`  Row ${update.row}: ${update.value}`);
      });
      return;
    }

    // Prepare batch update
    const batchData = updates.map(update => ({
      range: `${this.sheetName}!E${update.row}`,
      values: [[update.value]]
    }));

    try {
      const response = await this.sheetsService.spreadsheets.values.batchUpdate({
        spreadsheetId: this.spreadsheetId,
        requestBody: {
          valueInputOption: 'USER_ENTERED',
          data: batchData
        }
      });

      console.log(`\n✓ Updated ${response.data.totalUpdatedCells} cells in Google Sheet`);
    } catch (error: any) {
      console.error(`\n✗ Error updating sheet: ${error.message}`);
      throw error;
    }
  }

  /**
   * Main sync process
   */
  async sync(issueKeys: string[]): Promise<SyncResult[]> {
    console.log('\n═══════════════════════════════════════════════════');
    console.log('  Backlog to Google Sheets Sync');
    console.log('═══════════════════════════════════════════════════');
    console.log(`  Mode: ${dryRun ? 'DRY RUN (Preview)' : testMode ? 'TEST (1 issue)' : 'PRODUCTION'}`);
    console.log(`  Issue Keys: ${issueKeys.length}`);
    console.log('═══════════════════════════════════════════════════\n');

    // Step 1: Fetch issues from Backlog
    const backlogIssues = await this.fetchBacklogIssues(issueKeys);

    if (backlogIssues.length === 0) {
      console.log('\n⚠️  No issues found in Backlog');
      return [];
    }

    // Test mode: only process first issue
    const issuesToProcess = testMode ? backlogIssues.slice(0, 1) : backlogIssues;

    if (testMode) {
      console.log(`\n⚠️  TEST MODE: Processing only 1 issue: ${issuesToProcess[0].issueKey}`);
    }

    // Step 2: Read existing sheet data
    const range = config.googleSheets.range || 'E5:E100';
    const startRow = parseInt(range.split(':')[0].replace(/[A-Z]/g, ''));
    const existingData = await this.readSheetData(range);

    console.log(`\n📊 Read ${existingData.length} rows from sheet`);

    // Step 3: Prepare updates
    const results: SyncResult[] = [];
    const updates: Array<{ row: number; value: string }> = [];

    for (const issue of issuesToProcess) {
      const newValue = `${issue.issueKey} ${issue.summary}`;

      // Check if issue already exists
      const existingRow = this.findRowForIssueKey(issue.issueKey, existingData, startRow);

      if (existingRow !== null) {
        // Update existing row
        const oldValue = existingData[existingRow - startRow][0] || '';

        if (oldValue === newValue) {
          console.log(`  ⏭️  ${issue.issueKey}: Already up to date (row ${existingRow})`);
          results.push({
            issueKey: issue.issueKey,
            summary: issue.summary,
            action: 'skipped',
            row: existingRow
          });
        } else {
          console.log(`  🔄 ${issue.issueKey}: Updating row ${existingRow}`);
          console.log(`     Old: ${oldValue}`);
          console.log(`     New: ${newValue}`);
          updates.push({ row: existingRow, value: newValue });
          results.push({
            issueKey: issue.issueKey,
            summary: issue.summary,
            action: 'updated',
            row: existingRow
          });
        }
      } else {
        // Add to next empty row
        const emptyRow = this.findNextEmptyRow(existingData, startRow);
        console.log(`  ➕ ${issue.issueKey}: Adding to row ${emptyRow}`);
        console.log(`     Value: ${newValue}`);
        updates.push({ row: emptyRow, value: newValue });
        results.push({
          issueKey: issue.issueKey,
          summary: issue.summary,
          action: 'added',
          row: emptyRow
        });
      }
    }

    // Step 4: Update Google Sheet
    await this.updateSheet(updates);

    return results;
  }

  /**
   * Generate sync report
   */
  async generateReport(results: SyncResult[]): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
    const reportPath = join(dirname(__dirname), 'workflow', `sheets-sync-report-${timestamp}.json`);

    const report = {
      timestamp: new Date().toISOString(),
      mode: dryRun ? 'dry-run' : testMode ? 'test' : 'production',
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
    console.log(`\n📄 Report saved to: ${reportPath}`);

    return reportPath;
  }
}

// Main execution
async function main() {
  try {
    const sync = await BacklogToSheetsSync.create();

    // Get issue keys from config
    const issueKeys = config.issueKeys;

    if (!issueKeys || issueKeys.length === 0) {
      console.error('❌ No issue keys specified in config.issueKeys');
      process.exit(1);
    }

    // Run sync
    const results = await sync.sync(issueKeys);

    // Generate report
    await sync.generateReport(results);

    // Summary
    console.log('\n═══════════════════════════════════════════════════');
    console.log('  Summary');
    console.log('═══════════════════════════════════════════════════');
    console.log(`  Total processed: ${results.length}`);
    console.log(`  Added: ${results.filter(r => r.action === 'added').length}`);
    console.log(`  Updated: ${results.filter(r => r.action === 'updated').length}`);
    console.log(`  Skipped: ${results.filter(r => r.action === 'skipped').length}`);
    console.log('═══════════════════════════════════════════════════\n');

    if (dryRun) {
      console.log('💡 This was a DRY RUN. No changes were made.');
      console.log('   Run without --dry-run to apply changes.\n');
    } else if (testMode) {
      console.log('💡 This was TEST MODE. Only 1 issue was processed.');
      console.log('   Run without --test to process all issues.\n');
    }

  } catch (error: any) {
    console.error('\n❌ Error:', error.message);
    process.exit(1);
  }
}

main();
