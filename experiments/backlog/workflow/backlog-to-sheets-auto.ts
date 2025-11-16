#!/usr/bin/env node
/**
 * Proactive Backlog to Google Sheets Sync
 * Automatically evaluates and syncs issues that need updating
 *
 * Intelligence:
 * - Scans ALL issues from Backlog project
 * - Evaluates which ones need syncing (bilingual format check)
 * - Compares with Google Sheet to detect differences
 * - Only syncs what needs updating
 *
 * Usage:
 *   npm run sheets:auto              # Auto-evaluate and sync
 *   npm run sheets:auto -- --dry-run # Preview what needs syncing
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
const dryRun = args.includes('--dry-run');

interface BacklogIssue {
  id: number;
  issueKey: string;
  summary: string;
}

interface EvaluationResult {
  issueKey: string;
  summary: string;
  hasBilingualFormat: boolean;
  existsInSheet: boolean;
  sheetRow?: number;
  sheetValue?: string;
  needsSync: boolean;
  reason: string;
  action: 'add' | 'update' | 'skip';
}

class ProactiveSheetSync {
  private backlogClient!: BacklogClient;
  private sheetsService: any;
  private spreadsheetId!: string;
  private sheetName!: string;

  private constructor() {}

  static async create(): Promise<ProactiveSheetSync> {
    const instance = new ProactiveSheetSync();
    await instance.init();
    return instance;
  }

  private async init() {
    // Initialize Backlog
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

    const credentialsPath = join(dirname(__dirname), config.googleSheets.credentialsFile);
    const credentials = JSON.parse(readFileSync(credentialsPath, 'utf-8'));

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
   * Check if summary has bilingual format (VN/EN -- JP)
   */
  private hasBilingualFormat(summary: string): boolean {
    // Check for " -- " separator
    if (!summary.includes(' -- ')) {
      return false;
    }

    const parts = summary.split(' -- ');
    if (parts.length < 2) {
      return false;
    }

    const [first, second] = parts;

    // Check if second part has Japanese
    const hasJapanese = /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(second);

    // Check if first part has Vietnamese/English (no Japanese)
    const firstHasJapanese = /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(first);

    return hasJapanese && !firstHasJapanese;
  }

  /**
   * Fetch ALL issues from Backlog project
   */
  private async fetchAllBacklogIssues(): Promise<BacklogIssue[]> {
    console.log('\n📥 Fetching ALL issues from Backlog project...');

    const filters = config.filters || {
      statusId: [1, 2, 3], // Open, In Progress, Resolved
      count: 100
    };

    try {
      const issues = await this.backlogClient.getIssuesFiltered({
        projectId: [config.backlog.projectId],
        ...filters
      });

      console.log(`  ✓ Fetched ${issues.length} issues\n`);
      return issues;
    } catch (error: any) {
      console.error(`  ✗ Error fetching issues: ${error.message}`);
      return [];
    }
  }

  /**
   * Read existing data from Google Sheet
   */
  private async readSheetData(): Promise<Map<string, { row: number; value: string }>> {
    const range = config.googleSheets.range || 'E5:E100';
    const fullRange = `${this.sheetName}!${range}`;
    const startRow = parseInt(range.split(':')[0].replace(/[A-Z]/g, ''));

    try {
      const response = await this.sheetsService.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: fullRange
      });

      const values = response.data.values || [];
      const sheetMap = new Map<string, { row: number; value: string }>();

      values.forEach((row: string[], index: number) => {
        const cellValue = row[0] || '';
        const issueKeyMatch = cellValue.match(/HB21373-\d+|COE-\d+/);

        if (issueKeyMatch) {
          const issueKey = issueKeyMatch[0];
          sheetMap.set(issueKey, {
            row: startRow + index,
            value: cellValue
          });
        }
      });

      return sheetMap;
    } catch (error: any) {
      console.error(`Error reading sheet: ${error.message}`);
      return new Map();
    }
  }

  /**
   * Evaluate each issue to determine if it needs syncing
   */
  private evaluateIssue(
    issue: BacklogIssue,
    sheetData: Map<string, { row: number; value: string }>
  ): EvaluationResult {
    const hasBilingual = this.hasBilingualFormat(issue.summary);
    const sheetEntry = sheetData.get(issue.issueKey);
    const existsInSheet = !!sheetEntry;

    const expectedValue = `${issue.issueKey} ${issue.summary}`;

    let needsSync = false;
    let reason = '';
    let action: 'add' | 'update' | 'skip' = 'skip';

    if (!hasBilingual) {
      // Issue doesn't have bilingual format - skip it
      reason = 'Missing bilingual format (VN/EN -- JP)';
      action = 'skip';
      needsSync = false;
    } else if (!existsInSheet) {
      // Issue has bilingual format but not in sheet - add it
      reason = 'Has bilingual format, needs to be added to sheet';
      action = 'add';
      needsSync = true;
    } else if (sheetEntry.value !== expectedValue) {
      // Issue exists but value is different - update it
      reason = 'Sheet value differs from Backlog';
      action = 'update';
      needsSync = true;
    } else {
      // Issue exists and matches - skip
      reason = 'Already synced and up to date';
      action = 'skip';
      needsSync = false;
    }

    return {
      issueKey: issue.issueKey,
      summary: issue.summary,
      hasBilingualFormat: hasBilingual,
      existsInSheet,
      sheetRow: sheetEntry?.row,
      sheetValue: sheetEntry?.value,
      needsSync,
      reason,
      action
    };
  }

  /**
   * Find next empty row in sheet
   */
  private async findNextEmptyRow(): Promise<number> {
    const range = config.googleSheets.range || 'E5:E100';
    const startRow = parseInt(range.split(':')[0].replace(/[A-Z]/g, ''));
    const fullRange = `${this.sheetName}!${range}`;

    try {
      const response = await this.sheetsService.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: fullRange
      });

      const values = response.data.values || [];

      // Find first empty cell
      for (let i = 0; i < values.length; i++) {
        const cellValue = (values[i][0] || '').trim();
        if (cellValue === '' || cellValue === '(empty)') {
          return startRow + i;
        }
      }

      // No empty row found, append at end
      return startRow + values.length;
    } catch (error: any) {
      return 5; // Default to row 5
    }
  }

  /**
   * Main evaluation and sync process
   */
  async evaluateAndSync(): Promise<void> {
    console.log('\n═══════════════════════════════════════════════════');
    console.log('  🤖 Proactive Backlog to Google Sheets Sync');
    console.log('═══════════════════════════════════════════════════');
    console.log(`  Mode: ${dryRun ? '🔍 DRY RUN (Preview)' : '▶️  PRODUCTION'}`);
    console.log('═══════════════════════════════════════════════════\n');

    // Step 1: Fetch all issues from Backlog
    const backlogIssues = await this.fetchAllBacklogIssues();

    if (backlogIssues.length === 0) {
      console.log('⚠️  No issues found in Backlog');
      return;
    }

    // Step 2: Read existing sheet data
    console.log('📊 Reading Google Sheet data...');
    const sheetData = await this.readSheetData();
    console.log(`  ✓ Found ${sheetData.size} issues already in sheet\n`);

    // Step 3: Evaluate each issue
    console.log('🔍 Evaluating issues...\n');
    const evaluations: EvaluationResult[] = [];

    for (const issue of backlogIssues) {
      const evaluation = this.evaluateIssue(issue, sheetData);
      evaluations.push(evaluation);

      // Log evaluation result
      const icon = evaluation.needsSync ? '🔄' : '✓';
      const color = evaluation.needsSync ? '\x1b[33m' : '\x1b[32m'; // Yellow or Green
      const reset = '\x1b[0m';

      console.log(`${color}${icon} ${evaluation.issueKey}${reset}`);
      console.log(`   Status: ${evaluation.reason}`);
      console.log(`   Action: ${evaluation.action.toUpperCase()}`);

      if (evaluation.needsSync) {
        if (evaluation.action === 'update') {
          console.log(`   Old: ${evaluation.sheetValue}`);
          console.log(`   New: ${evaluation.issueKey} ${evaluation.summary}`);
        } else {
          console.log(`   Value: ${evaluation.issueKey} ${evaluation.summary}`);
        }
      }
      console.log('');
    }

    // Step 4: Prepare updates
    const toSync = evaluations.filter(e => e.needsSync);

    console.log('\n═══════════════════════════════════════════════════');
    console.log('  📊 Evaluation Summary');
    console.log('═══════════════════════════════════════════════════');
    console.log(`  Total issues: ${evaluations.length}`);
    console.log(`  Has bilingual format: ${evaluations.filter(e => e.hasBilingualFormat).length}`);
    console.log(`  Already in sheet: ${evaluations.filter(e => e.existsInSheet).length}`);
    console.log(`  Needs syncing: ${toSync.length}`);
    console.log(`    - To add: ${toSync.filter(e => e.action === 'add').length}`);
    console.log(`    - To update: ${toSync.filter(e => e.action === 'update').length}`);
    console.log('═══════════════════════════════════════════════════\n');

    if (toSync.length === 0) {
      console.log('✅ Everything is already synced! Nothing to do.\n');
      return;
    }

    if (dryRun) {
      console.log('💡 This was a DRY RUN. No changes were made.');
      console.log(`   Run without --dry-run to sync ${toSync.length} issue(s).\n`);
      return;
    }

    // Step 5: Perform sync
    console.log(`\n🔄 Syncing ${toSync.length} issue(s) to Google Sheets...\n`);

    const updates: Array<{ range: string; values: string[][] }> = [];
    let nextEmptyRow = await this.findNextEmptyRow();

    for (const evaluation of toSync) {
      const value = `${evaluation.issueKey} ${evaluation.summary}`;
      let row: number;

      if (evaluation.action === 'update' && evaluation.sheetRow) {
        row = evaluation.sheetRow;
      } else {
        row = nextEmptyRow;
        nextEmptyRow++;
      }

      updates.push({
        range: `${this.sheetName}!E${row}`,
        values: [[value]]
      });

      console.log(`  ${evaluation.action === 'add' ? '➕' : '🔄'} ${evaluation.issueKey} → Row ${row}`);
    }

    try {
      const response = await this.sheetsService.spreadsheets.values.batchUpdate({
        spreadsheetId: this.spreadsheetId,
        requestBody: {
          valueInputOption: 'USER_ENTERED',
          data: updates
        }
      });

      console.log(`\n✅ Successfully synced ${response.data.totalUpdatedCells} cells!\n`);
    } catch (error: any) {
      console.error(`\n❌ Error syncing to sheet: ${error.message}\n`);
      throw error;
    }

    // Step 6: Generate report
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
    const reportPath = join(dirname(__dirname), 'workflow', `sheets-auto-sync-report-${timestamp}.json`);

    const report = {
      timestamp: new Date().toISOString(),
      mode: dryRun ? 'dry-run' : 'production',
      summary: {
        totalIssues: evaluations.length,
        hasBilingualFormat: evaluations.filter(e => e.hasBilingualFormat).length,
        alreadyInSheet: evaluations.filter(e => e.existsInSheet).length,
        synced: toSync.length,
        added: toSync.filter(e => e.action === 'add').length,
        updated: toSync.filter(e => e.action === 'update').length
      },
      evaluations
    };

    writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`📄 Report saved to: ${reportPath}\n`);
  }
}

// Main execution
async function main() {
  try {
    const sync = await ProactiveSheetSync.create();
    await sync.evaluateAndSync();
  } catch (error: any) {
    console.error('\n❌ Error:', error.message);
    process.exit(1);
  }
}

main();
