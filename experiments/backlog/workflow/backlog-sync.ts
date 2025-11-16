#!/usr/bin/env node
/**
 * Backlog Issue Summary Sync
 * Automated workflow: Fetch → Translate → Update
 *
 * Usage:
 *   npm run sync              # Run with default config
 *   npm run sync -- --dry-run # Preview without updating
 *   npm run sync -- --test    # Test with 1 issue only
 */

import { BacklogClient } from '../src/backlog-client.js';
import { Translator } from './translator.js';
import { readFileSync, writeFileSync } from 'fs';
import dotenv from 'dotenv';

dotenv.config();

// Load configuration
const config = JSON.parse(readFileSync('workflow/config.json', 'utf-8'));

// Parse command line arguments
const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run') || config.execution.dryRun;
const testMode = args.includes('--test') || config.execution.testWithOneIssue;

interface Issue {
  id: number;
  issueKey: string;
  summary: string;
}

interface ProcessedIssue extends Issue {
  needsTranslation: boolean;
  translatedSummary?: string;
  formattedSummary?: string;
  updated: boolean;
  error?: string;
}

class BacklogSync {
  private client: BacklogClient;
  private translator: Translator;
  private domain: string;
  private apiKey: string;

  constructor() {
    this.domain = process.env.BACKLOG_DOMAIN!;
    this.apiKey = process.env.BACKLOG_API_KEY!;

    if (!this.domain || !this.apiKey) {
      throw new Error('Missing BACKLOG_DOMAIN or BACKLOG_API_KEY in .env');
    }

    this.client = new BacklogClient({
      domain: this.domain,
      apiKey: this.apiKey
    });

    this.translator = new Translator(config.translation.enableCache);
  }

  /**
   * Check if text contains Japanese
   */
  private hasJapanese(text: string): boolean {
    return /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(text);
  }

  /**
   * Check if text contains Vietnamese/English
   */
  private hasVietnamese(text: string): boolean {
    const hasDiacritics = /[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]/i.test(text);
    const hasVnWords = /\b(của|và|trên|cho|với|từ|đến|tại|trong|theo|để|làm|được|các|này|đã|có|sẽ|bị|về|sau|trước|lên|xuống|Làm|Tạo|Viết|Update|Review)\b/i.test(text);
    return hasDiacritics || hasVnWords;
  }

  /**
   * Parse summary to extract VN/EN and JP parts
   */
  private parseSummary(summary: string): { vnen?: string; jp?: string } {
    // Try different separator patterns
    const separators = [/\s*--\s+/, / - /];

    for (const separator of separators) {
      const parts = summary.split(separator);
      if (parts.length >= 2) {
        const first = parts[0].trim();
        const second = parts.slice(1).join(' -- ').trim();

        const firstHasJp = this.hasJapanese(first);
        const secondHasJp = this.hasJapanese(second);

        if (firstHasJp && !secondHasJp) {
          return { jp: first, vnen: second };
        } else if (!firstHasJp && secondHasJp) {
          return { vnen: first, jp: second };
        } else if (firstHasJp && secondHasJp) {
          // Both have Japanese, assume first is JP
          return { jp: first, vnen: second };
        }
      }
    }

    // No separator found
    if (this.hasJapanese(summary)) {
      return { jp: summary };
    } else {
      return { vnen: summary };
    }
  }

  /**
   * Format summary to [VN/EN] -- [JP]
   */
  private async formatSummary(summary: string): Promise<string> {
    const parsed = this.parseSummary(summary);

    // Already has both parts
    if (parsed.vnen && parsed.jp) {
      return `${parsed.vnen} -- ${parsed.jp}`;
    }

    // Only VN/EN, need JP translation
    if (parsed.vnen && !parsed.jp) {
      const jpTranslation = await this.translator.translate(parsed.vnen);
      return `${parsed.vnen} -- ${jpTranslation}`;
    }

    // Only JP, need VN/EN (rare case, just keep as is)
    if (parsed.jp && !parsed.vnen) {
      console.warn(`⚠️  Issue has only Japanese text: ${summary}`);
      return summary;
    }

    return summary;
  }

  /**
   * Fetch issues from Backlog
   */
  private async fetchIssues(): Promise<Issue[]> {
    console.log('📥 Fetching issues from Backlog...');

    const issues = await this.client.getIssuesFiltered({
      projectId: [config.backlog.projectId],
      statusId: config.filters.statusId,
      createdSince: config.filters.createdSince,
      count: config.filters.count
    });

    console.log(`✅ Fetched ${issues.length} issues\n`);
    return issues;
  }

  /**
   * Process issues (analyze and translate)
   */
  private async processIssues(issues: Issue[]): Promise<ProcessedIssue[]> {
    console.log('🔄 Processing issues...\n');

    const processed: ProcessedIssue[] = [];

    for (const issue of issues) {
      const formattedSummary = await this.formatSummary(issue.summary);
      const needsUpdate = formattedSummary !== issue.summary;

      processed.push({
        ...issue,
        needsTranslation: needsUpdate,
        formattedSummary,
        updated: false
      });

      if (needsUpdate) {
        console.log(`📝 [${issue.issueKey}]`);
        console.log(`   Before: ${issue.summary}`);
        console.log(`   After:  ${formattedSummary}\n`);
      }
    }

    return processed;
  }

  /**
   * Update issue in Backlog
   */
  private async updateIssue(issueKey: string, summary: string): Promise<void> {
    const url = `https://${this.domain}/api/v2/issues/${issueKey}?apiKey=${this.apiKey}`;

    const formData = new URLSearchParams({ summary });

    const response = await fetch(url, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString()
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`${response.status} ${response.statusText}: ${errorText}`);
    }
  }

  /**
   * Update issues in Backlog
   */
  private async updateIssues(issues: ProcessedIssue[]): Promise<ProcessedIssue[]> {
    const toUpdate = issues.filter(i => i.needsTranslation);

    if (toUpdate.length === 0) {
      console.log('✅ All issues already in correct format!\n');
      return issues;
    }

    console.log(`\n🚀 Updating ${toUpdate.length} issues in Backlog...\n`);

    if (dryRun) {
      console.log('🔍 DRY RUN MODE - No actual updates will be made\n');
      return issues;
    }

    if (testMode) {
      console.log('🧪 TEST MODE - Updating only 1 issue\n');
      toUpdate.splice(1); // Keep only first issue
    }

    let successCount = 0;
    let errorCount = 0;

    for (let i = 0; i < toUpdate.length; i++) {
      const issue = toUpdate[i];
      const progress = `[${i + 1}/${toUpdate.length}]`;

      try {
        process.stdout.write(`${progress} ${issue.issueKey}... `);

        await this.updateIssue(issue.issueKey, issue.formattedSummary!);

        console.log('✅');
        issue.updated = true;
        successCount++;

        // Delay to avoid rate limiting
        if (i < toUpdate.length - 1) {
          await new Promise(resolve => setTimeout(resolve, config.execution.delayBetweenUpdates));
        }

      } catch (error) {
        console.log(`❌ ${error}`);
        issue.error = String(error);
        errorCount++;
      }
    }

    console.log(`\n📊 Results: ✅ ${successCount} succeeded, ❌ ${errorCount} failed\n`);
    return issues;
  }

  /**
   * Generate report
   */
  private generateReport(issues: ProcessedIssue[]): void {
    const report = {
      timestamp: new Date().toISOString(),
      config,
      summary: {
        total: issues.length,
        needsTranslation: issues.filter(i => i.needsTranslation).length,
        updated: issues.filter(i => i.updated).length,
        failed: issues.filter(i => i.error).length,
        alreadyCorrect: issues.filter(i => !i.needsTranslation).length
      },
      issues: issues.map(i => ({
        issueKey: i.issueKey,
        originalSummary: i.summary,
        formattedSummary: i.formattedSummary,
        needsTranslation: i.needsTranslation,
        updated: i.updated,
        error: i.error
      }))
    };

    const reportFile = `workflow/sync-report-${Date.now()}.json`;
    writeFileSync(reportFile, JSON.stringify(report, null, 2), 'utf-8');

    console.log(`📄 Report saved to: ${reportFile}\n`);

    // Print summary
    console.log('📊 SUMMARY');
    console.log('==========');
    console.log(`Total issues:        ${report.summary.total}`);
    console.log(`Already correct:     ${report.summary.alreadyCorrect}`);
    console.log(`Needs translation:   ${report.summary.needsTranslation}`);
    console.log(`Updated:             ${report.summary.updated}`);
    console.log(`Failed:              ${report.summary.failed}`);

    if (dryRun) {
      console.log('\n🔍 DRY RUN - No changes were made to Backlog');
    }

    if (testMode) {
      console.log('\n🧪 TEST MODE - Only 1 issue was updated');
    }
  }

  /**
   * Main execution
   */
  async run(): Promise<void> {
    console.log('\n🚀 Backlog Issue Summary Sync');
    console.log('==============================\n');
    console.log(`Project: ${config.backlog.projectKey} (ID: ${config.backlog.projectId})`);
    console.log(`Mode: ${dryRun ? 'DRY RUN' : testMode ? 'TEST (1 issue)' : 'PRODUCTION'}\n`);

    try {
      // Step 1: Fetch issues
      const issues = await this.fetchIssues();

      // Step 2: Process issues (analyze & translate)
      const processed = await this.processIssues(issues);

      // Step 3: Update issues in Backlog
      const updated = await this.updateIssues(processed);

      // Step 4: Generate report
      this.generateReport(updated);

      console.log('\n✅ Sync completed successfully!\n');

    } catch (error) {
      console.error('\n❌ Error:', error);
      process.exit(1);
    }
  }
}

// Run the sync
const sync = new BacklogSync();
sync.run();
