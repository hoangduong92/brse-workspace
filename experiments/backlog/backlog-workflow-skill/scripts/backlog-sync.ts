#!/usr/bin/env node
/**
 * Backlog Issue Summary Sync (User-Config Compatible)
 * Automated workflow: Fetch → Translate → Update
 *
 * Usage:
 *   npm run sync              # Run with user-config.json
 *   npm run sync -- --dry-run # Preview without updating
 *   npm run sync -- --test    # Test with 1 issue only
 */

import { BacklogClient } from '../../src/backlog-client.js';
import { Translator } from './translator.js';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import dotenv from 'dotenv';

dotenv.config();

// Load user-specific configuration
const configPath = 'workflow/user-config.json';
if (!existsSync(configPath)) {
  console.error('❌ user-config.json not found');
  console.error('Run interactive setup with Claude, or copy from:');
  console.error('  backlog/backlog-workflow-skill/references/config-template.json');
  process.exit(1);
}

const config = JSON.parse(readFileSync(configPath, 'utf-8'));

// Parse command line arguments
const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run') || config.execution?.dryRun || false;
const testMode = args.includes('--test') || config.execution?.testWithOneIssue || false;

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

    // Initialize translator with language pair from user config
    this.translator = new Translator(
      config.translation?.enableCache ?? true,
      config.translation?.languagePair || 'vi-ja',
      config.translation?.customDictionary || {}
    );
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
      const separator = config.translation?.format?.includes('--') ? ' -- ' : ' | ';
      return `${parsed.vnen}${separator}${parsed.jp}`;
    }

    // Only VN/EN, need JP translation
    if (parsed.vnen && !parsed.jp) {
      const jpTranslation = await this.translator.translate(parsed.vnen);
      const separator = config.translation?.format?.includes('--') ? ' -- ' : ' | ';
      return `${parsed.vnen}${separator}${jpTranslation}`;
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

    const filters = config.filters || {};
    const issues = await this.client.getIssuesFiltered({
      projectId: [config.backlog.projectId],
      statusId: filters.statusId || [1, 2, 3],
      createdSince: filters.createdSince,
      createdUntil: filters.createdUntil,
      count: filters.count || 100
    });

    console.log(`✅ Fetched ${issues.length} issues\n`);
    return issues.map((issue: any) => ({
      id: issue.id,
      issueKey: issue.issueKey,
      summary: issue.summary
    }));
  }

  /**
   * Process issues
   */
  private async processIssues(issues: Issue[]): Promise<ProcessedIssue[]> {
    console.log('🔄 Processing issues...\n');

    const processed: ProcessedIssue[] = [];

    for (const issue of issues) {
      const originalSummary = issue.summary;
      const formattedSummary = await this.formatSummary(originalSummary);

      const needsTranslation = originalSummary !== formattedSummary;

      if (needsTranslation) {
        console.log(`📝 [${issue.issueKey}]`);
        console.log(`   Before: ${originalSummary}`);
        console.log(`   After:  ${formattedSummary}\n`);
      }

      processed.push({
        ...issue,
        needsTranslation,
        formattedSummary,
        updated: false
      });
    }

    return processed;
  }

  /**
   * Update issues in Backlog
   */
  private async updateIssues(issues: ProcessedIssue[]): Promise<void> {
    const toUpdate = issues.filter(i => i.needsTranslation);

    if (toUpdate.length === 0) {
      console.log('✅ All issues already have correct format');
      return;
    }

    if (dryRun) {
      console.log(`🔍 DRY RUN MODE - No actual updates will be made`);
      console.log(`📊 Would update: ${toUpdate.length} issues`);
      return;
    }

    const limit = testMode ? 1 : toUpdate.length;
    console.log(`🚀 Updating ${limit} issue(s)...\n`);

    for (let i = 0; i < limit; i++) {
      const issue = toUpdate[i];

      try {
        // Update via direct API call
        const url = `https://${this.domain}/api/v2/issues/${issue.id}`;
        const response = await fetch(url, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: new URLSearchParams({
            apiKey: this.apiKey,
            summary: issue.formattedSummary!
          })
        });

        if (response.ok) {
          issue.updated = true;
          console.log(`✅ [${issue.issueKey}] Updated`);
        } else {
          issue.error = `HTTP ${response.status}`;
          console.error(`❌ [${issue.issueKey}] Failed: ${issue.error}`);
        }

        // Rate limiting
        const delay = config.execution?.delayBetweenUpdates || 200;
        await new Promise(resolve => setTimeout(resolve, delay));

      } catch (error) {
        issue.error = error instanceof Error ? error.message : String(error);
        console.error(`❌ [${issue.issueKey}] Error: ${issue.error}`);
      }
    }

    if (testMode) {
      console.log(`\n✅ Updated 1 issue (test mode)`);
      console.log(`Visit Backlog to verify: https://${this.domain}/view/${toUpdate[0].issueKey}`);
    }
  }

  /**
   * Generate report
   */
  private async generateReport(issues: ProcessedIssue[]): Promise<void> {
    const timestamp = Date.now();
    const reportPath = `workflow/sync-report-${timestamp}.json`;

    const needsTranslation = issues.filter(i => i.needsTranslation);
    const updated = issues.filter(i => i.updated);
    const failed = issues.filter(i => i.error);
    const alreadyCorrect = issues.filter(i => !i.needsTranslation);

    const report = {
      timestamp: new Date().toISOString(),
      mode: dryRun ? 'dry-run' : testMode ? 'test' : 'production',
      config: {
        projectId: config.backlog.projectId,
        projectKey: config.backlog.projectKey,
        languagePair: config.translation?.languagePair || 'vi-ja'
      },
      summary: {
        total: issues.length,
        needsTranslation: needsTranslation.length,
        updated: updated.length,
        failed: failed.length,
        alreadyCorrect: alreadyCorrect.length
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

    writeFileSync(reportPath, JSON.stringify(report, null, 2));

    console.log(`\n${'='.repeat(60)}`);
    console.log('📊 Summary\n');
    console.log(`Total issues: ${report.summary.total}`);
    console.log(`Needs translation: ${report.summary.needsTranslation}`);
    console.log(`Updated: ${report.summary.updated}`);
    console.log(`Failed: ${report.summary.failed}`);
    console.log(`Already correct: ${report.summary.alreadyCorrect}`);
    console.log(`\n📄 Report saved: ${reportPath}`);
  }

  /**
   * Main execution
   */
  async run(): Promise<void> {
    try {
      const issues = await this.fetchIssues();
      const processed = await this.processIssues(issues);
      await this.updateIssues(processed);
      await this.generateReport(processed);
    } catch (error) {
      console.error('\n❌ Sync failed:', error);
      process.exit(1);
    }
  }
}

// Run sync
const sync = new BacklogSync();
sync.run();
