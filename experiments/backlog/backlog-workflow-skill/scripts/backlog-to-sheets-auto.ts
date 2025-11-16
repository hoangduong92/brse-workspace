#!/usr/bin/env node
/**
 * Proactive Backlog to Google Sheets Sync (User-Config Compatible)
 * Auto-sync: Intelligently evaluates and syncs issues that need updating
 *
 * Intelligence:
 * - Scans ALL issues from Backlog project
 * - Evaluates which have bilingual format
 * - Compares with Google Sheet to detect differences
 * - Only syncs what needs updating
 *
 * Usage:
 *   npm run sheets:auto              # Auto-evaluate and sync
 *   npm run sheets:auto -- --dry-run # Preview what needs syncing
 */

import { BacklogClient } from '../../src/backlog-client.js';
import { google } from 'googleapis';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
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
  console.error('Add Google Sheets settings first');
  process.exit(1);
}

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
  private range!: string;

  private constructor() {}

  static async create(): Promise<ProactiveSheetSync> {
    const instance = new ProactiveSheetSync();
    await instance.init();
    return instance;
  }

  private async init() {
    console.log('🤖 Initializing Proactive Auto-Sync...\n');

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
    this.range = config.googleSheets.range || 'A1:A100';

    const credentialsFile = config.googleSheets.credentialsFile || 'backlog/ggsheet-mcp-09921a7c3245.json';

    if (!existsSync(credentialsFile)) {
      throw new Error(`Credentials file not found: ${credentialsFile}`);
    }

    const credentials = JSON.parse(readFileSync(credentialsFile, 'utf-8'));

    const auth = new google.auth.GoogleAuth({
      credentials,
      scopes: [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
      ]
    });

    const authClient = await auth.getClient();
    this.sheetsService = google.sheets({ version: 'v4', auth: authClient as any });

    console.log(`✅ Connected to Backlog project: ${config.backlog.projectKey}`);
    console.log(`✅ Connected to Google Sheet: ${this.sheetName}`);
    console.log();
  }

  /**
   * Check if summary has bilingual format
   * Supports multiple separators based on config
   */
  private hasBilingualFormat(summary: string): boolean {
    const separator = config.translation?.format?.includes('--') ? ' -- ' : ' | ';

    if (!summary.includes(separator)) {
      return false;
    }

    const parts = summary.split(separator);
    if (parts.length < 2) {
      return false;
    }

    const [first, second] = parts;

    // Check if second part has Japanese
    const hasJapanese = /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(second);

    // Check if first part has no Japanese
    const firstHasJapanese = /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(first);

    return hasJapanese && !firstHasJapanese;
  }

  /**
   * Fetch ALL issues from Backlog project
   */
  private async fetchAllBacklogIssues(): Promise<BacklogIssue[]> {
    console.log('📥 Fetching ALL issues from Backlog project...\n');

    const filters = config.filters || {
      statusId: [1, 2, 3], // Open, In Progress, Resolved
      count: 100
    };

    try {
      const issues = await this.backlogClient.getIssuesFiltered({
        projectId: [config.backlog.projectId],
        statusId: filters.statusId,
        createdSince: filters.createdSince,
        count: filters.count
      });

      console.log(`  ✓ Fetched ${issues.length} issues\n`);
      return issues;
    } catch (error: any) {
      console.error(`  ✗ Error fetching issues: ${error.message}`);
      return [];
    }
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

    return rangeEnd;
  }

  /**
   * Evaluate all issues
   */
  private evaluateIssues(
    issues: BacklogIssue[],
    sheetData: Map<number, string>
  ): EvaluationResult[] {
    console.log('🔍 Evaluating issues...\n');

    const evaluations: EvaluationResult[] = [];

    for (const issue of issues) {
      const hasBilingual = this.hasBilingualFormat(issue.summary);
      const existingRow = this.findIssueRow(sheetData, issue.issueKey);
      const cellValue = `${issue.issueKey} ${issue.summary}`;

      let needsSync = false;
      let reason = '';
      let action: 'add' | 'update' | 'skip' = 'skip';

      if (!hasBilingual) {
        reason = 'Missing bilingual format (VN/EN -- JP)';
        action = 'skip';
      } else if (!existingRow) {
        reason = 'Has bilingual format, needs to be added to sheet';
        needsSync = true;
        action = 'add';
      } else {
        const currentValue = sheetData.get(existingRow) || '';
        if (currentValue !== cellValue) {
          reason = 'Sheet value differs from Backlog';
          needsSync = true;
          action = 'update';
        } else {
          reason = 'Already synced and up to date';
          action = 'skip';
        }
      }

      const evaluation: EvaluationResult = {
        issueKey: issue.issueKey,
        summary: issue.summary,
        hasBilingualFormat: hasBilingual,
        existsInSheet: existingRow !== null,
        sheetRow: existingRow || undefined,
        sheetValue: existingRow ? sheetData.get(existingRow) : undefined,
        needsSync,
        reason,
        action
      };

      evaluations.push(evaluation);

      // Display evaluation result
      if (needsSync) {
        console.log(`🔄 ${issue.issueKey}`);
        console.log(`   Status: ${reason}`);
        console.log(`   Action: ${action.toUpperCase()}`);
        if (action === 'update') {
          console.log(`   Old: ${evaluation.sheetValue}`);
          console.log(`   New: ${cellValue}`);
        } else if (action === 'add') {
          console.log(`   Value: ${cellValue}`);
        }
        console.log();
      } else if (hasBilingual) {
        console.log(`✓ ${issue.issueKey}`);
        console.log(`   Status: ${reason}`);
        console.log(`   Action: SKIP\n`);
      }
    }

    return evaluations;
  }

  /**
   * Sync evaluated issues to sheets
   */
  private async syncToSheets(
    evaluations: EvaluationResult[],
    sheetData: Map<number, string>
  ) {
    const toSync = evaluations.filter(e => e.needsSync);

    if (toSync.length === 0) {
      console.log('✅ All issues are already up to date\n');
      return;
    }

    console.log(`\n${'='.repeat(60)}`);
    console.log('📊 Evaluation Summary\n');
    console.log(`Total issues: ${evaluations.length}`);
    console.log(`Has bilingual format: ${evaluations.filter(e => e.hasBilingualFormat).length}`);
    console.log(`Already in sheet: ${evaluations.filter(e => e.existsInSheet).length}`);
    console.log(`Needs syncing: ${toSync.length}`);
    console.log(`  - To add: ${toSync.filter(e => e.action === 'add').length}`);
    console.log(`  - To update: ${toSync.filter(e => e.action === 'update').length}`);
    console.log();

    if (dryRun) {
      console.log('🔍 DRY RUN MODE - No actual updates will be made');
      return;
    }

    console.log('🚀 Syncing to Google Sheets...\n');

    const updates: Array<{ row: number; value: string }> = [];

    for (const eval of toSync) {
      const cellValue = `${eval.issueKey} ${eval.summary}`;

      if (eval.action === 'update' && eval.sheetRow) {
        updates.push({ row: eval.sheetRow, value: cellValue });
        console.log(`  ✓ [${eval.issueKey}] Updated at row ${eval.sheetRow}`);
      } else if (eval.action === 'add') {
        const emptyRow = this.findFirstEmptyRow(sheetData);
        updates.push({ row: emptyRow, value: cellValue });
        sheetData.set(emptyRow, cellValue);
        console.log(`  ✓ [${eval.issueKey}] Added at row ${emptyRow}`);
      }
    }

    // Batch update
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

        console.log(`\n✅ Synced ${updates.length} issue(s) to Google Sheets\n`);
      } catch (error: any) {
        console.error(`\n❌ Error updating sheets: ${error.message}\n`);
      }
    }
  }

  /**
   * Generate report
   */
  private async generateReport(evaluations: EvaluationResult[]) {
    const timestamp = new Date().toISOString().split('T')[0];
    const reportPath = `workflow/sheets-auto-sync-report-${timestamp}.json`;

    const toSync = evaluations.filter(e => e.needsSync);

    const report = {
      timestamp: new Date().toISOString(),
      mode: dryRun ? 'dry-run' : 'production',
      config: {
        projectId: config.backlog.projectId,
        projectKey: config.backlog.projectKey,
        spreadsheetId: this.spreadsheetId,
        sheetName: this.sheetName,
        languagePair: config.translation?.languagePair || 'vi-ja'
      },
      summary: {
        totalIssues: evaluations.length,
        hasBilingualFormat: evaluations.filter(e => e.hasBilingualFormat).length,
        alreadyInSheet: evaluations.filter(e => e.existsInSheet).length,
        synced: dryRun ? 0 : toSync.length,
        added: toSync.filter(e => e.action === 'add').length,
        updated: toSync.filter(e => e.action === 'update').length
      },
      evaluations
    };

    writeFileSync(reportPath, JSON.stringify(report, null, 2));

    console.log('📄 Report saved:', reportPath);
  }

  /**
   * Main execution
   */
  async run() {
    try {
      const issues = await this.fetchAllBacklogIssues();
      const sheetData = await this.readSheetData();
      const evaluations = this.evaluateIssues(issues, sheetData);
      await this.syncToSheets(evaluations, sheetData);
      await this.generateReport(evaluations);
    } catch (error) {
      console.error('\n❌ Auto-sync failed:', error);
      process.exit(1);
    }
  }
}

// Run sync
ProactiveSheetSync.create().then(sync => sync.run());
