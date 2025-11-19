#!/usr/bin/env node
/**
 * Issue Initing Workflow
 * Creates 8 standard child issues for a parent issue
 *
 * Usage:
 *   npm run issue:init HB21373-XXX              # Create child issues
 *   npm run issue:init HB21373-XXX --dry-run    # Preview without creating
 */

import dotenv from 'dotenv';

dotenv.config();

const DOMAIN = process.env.BACKLOG_DOMAIN!;
const API_KEY = process.env.BACKLOG_API_KEY!;

// Standard child issues template
const CHILD_ISSUES_TEMPLATE = [
  { order: 1, summary: '要件ヘアリング　-- Hearing yêu cầu' },
  { order: 2, summary: '要件定義書作成　-- Làm file spec' },
  { order: 3, summary: '開発　-- Coding' },
  { order: 4, summary: 'テストケース作成  --  Tạo test case' },
  { order: 5, summary: 'テスト実施 -- Thực thi test' },
  { order: 6, summary: 'UAT' },
  { order: 7, summary: 'リリース判定 -- Release' },
  { order: 8, summary: 'ユーザマニュアル作成 -- Làm user manual' }
];

interface ParentIssue {
  id: number;
  issueKey: string;
  projectId: number;
  issueType: {
    id: number;
    projectId: number;
  };
  priority: {
    id: number;
  };
  summary: string;
}

interface CreateIssueParams {
  projectId: number;
  summary: string;
  issueTypeId: number;
  priorityId: number;
  parentIssueId: number;
}

class IssueInitWorkflow {
  private dryRun: boolean;

  constructor(dryRun: boolean = false) {
    this.dryRun = dryRun;
  }

  /**
   * Get parent issue details
   */
  private async getParentIssue(issueKey: string): Promise<ParentIssue> {
    const url = `https://${DOMAIN}/api/v2/issues/${issueKey}?apiKey=${API_KEY}`;

    console.log(`\n🔍 Fetching parent issue: ${issueKey}...\n`);

    const response = await fetch(url);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`Issue ${issueKey} not found. Please check the issue key.`);
      }
      throw new Error(`Failed to fetch issue: ${response.status} ${response.statusText}`);
    }

    const issue = await response.json();

    console.log(`✅ Parent Issue Found:`);
    console.log(`   Key: ${issue.issueKey}`);
    console.log(`   Summary: ${issue.summary}`);
    console.log(`   Project: ${issue.projectId}`);
    console.log(`   Issue Type: ${issue.issueType.name} (ID: ${issue.issueType.id})`);
    console.log(`   Priority: ${issue.priority.name} (ID: ${issue.priority.id})\n`);

    return {
      id: issue.id,
      issueKey: issue.issueKey,
      projectId: issue.projectId,
      issueType: issue.issueType,
      priority: issue.priority,
      summary: issue.summary
    };
  }

  /**
   * Get Subtask issue type ID for the project
   */
  private async getSubtaskIssueTypeId(projectId: number): Promise<number> {
    const url = `https://${DOMAIN}/api/v2/projects/${projectId}/issueTypes?apiKey=${API_KEY}`;

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Failed to fetch issue types: ${response.status} ${response.statusText}`);
    }

    const issueTypes = await response.json();

    // Find Subtask issue type
    const subtaskType = issueTypes.find((type: any) =>
      type.name === 'Subtask' || type.name === 'サブタスク' || type.name === '子課題'
    );

    if (!subtaskType) {
      // If no Subtask type found, use the first available issue type
      console.log(`⚠️  No Subtask issue type found, using default: ${issueTypes[0].name}`);
      return issueTypes[0].id;
    }

    console.log(`📋 Using issue type: ${subtaskType.name} (ID: ${subtaskType.id})\n`);
    return subtaskType.id;
  }

  /**
   * Create a single child issue
   */
  private async createChildIssue(params: CreateIssueParams): Promise<any> {
    if (this.dryRun) {
      return {
        issueKey: 'DRY-RUN',
        summary: params.summary
      };
    }

    const url = `https://${DOMAIN}/api/v2/issues?apiKey=${API_KEY}`;

    const body = new URLSearchParams({
      projectId: String(params.projectId),
      summary: params.summary,
      issueTypeId: String(params.issueTypeId),
      priorityId: String(params.priorityId),
      parentIssueId: String(params.parentIssueId)
    });

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: body.toString()
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to create issue: ${response.status} ${response.statusText}\n${errorText}`);
    }

    return await response.json();
  }

  /**
   * Create all 8 child issues
   */
  private async createChildIssues(parent: ParentIssue): Promise<any[]> {
    console.log(`${this.dryRun ? '🔍 [DRY RUN]' : '🚀'} Creating ${CHILD_ISSUES_TEMPLATE.length} child issues...\n`);

    // Get Subtask issue type ID
    const subtaskTypeId = await getSubtaskIssueTypeId(parent.projectId);

    const createdIssues: any[] = [];
    const delay = 200; // 200ms delay between API calls to avoid rate limiting

    for (const template of CHILD_ISSUES_TEMPLATE) {
      try {
        console.log(`   ${template.order}. Creating: ${template.summary}...`);

        const issue = await this.createChildIssue({
          projectId: parent.projectId,
          summary: template.summary,
          issueTypeId: subtaskTypeId,
          priorityId: parent.priority.id,
          parentIssueId: parent.id
        });

        createdIssues.push(issue);
        console.log(`      ✅ Created: ${issue.issueKey}`);

        // Delay between requests
        if (!this.dryRun && template.order < CHILD_ISSUES_TEMPLATE.length) {
          await new Promise(resolve => setTimeout(resolve, delay));
        }

      } catch (error) {
        console.error(`      ❌ Failed: ${error}`);
        throw error; // Stop on first error
      }
    }

    return createdIssues;
  }

  /**
   * Display summary report
   */
  private displaySummary(parent: ParentIssue, childIssues: any[]): void {
    console.log('\n═══════════════════════════════════════════════════');
    console.log(`${this.dryRun ? '📋 DRY RUN SUMMARY' : '✅ SUCCESS SUMMARY'}`);
    console.log('═══════════════════════════════════════════════════');
    console.log(`\n📦 Parent Issue: ${parent.issueKey}`);
    console.log(`   ${parent.summary}`);
    console.log(`\n📝 Created ${childIssues.length} child issues:\n`);

    childIssues.forEach((issue, index) => {
      console.log(`   ${index + 1}. ${issue.issueKey} - ${issue.summary}`);
    });

    console.log('\n═══════════════════════════════════════════════════');

    if (!this.dryRun) {
      console.log(`\n🔗 View parent issue: https://${DOMAIN}/view/${parent.issueKey}`);
    } else {
      console.log(`\n💡 Run without --dry-run flag to create issues`);
    }

    console.log();
  }

  /**
   * Run the workflow
   */
  async run(parentIssueKey: string): Promise<void> {
    try {
      // Step 1: Get parent issue
      const parent = await this.getParentIssue(parentIssueKey);

      // Step 2: Create child issues
      const childIssues = await this.createChildIssues(parent);

      // Step 3: Display summary
      this.displaySummary(parent, childIssues);

    } catch (error) {
      console.error('\n❌ Workflow failed:', error);
      process.exit(1);
    }
  }
}

// Move this function outside the class so it can be called
async function getSubtaskIssueTypeId(projectId: number): Promise<number> {
  const url = `https://${DOMAIN}/api/v2/projects/${projectId}/issueTypes?apiKey=${API_KEY}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch issue types: ${response.status} ${response.statusText}`);
  }

  const issueTypes = await response.json();

  // Find Subtask issue type
  const subtaskType = issueTypes.find((type: any) =>
    type.name === 'Subtask' || type.name === 'サブタスク' || type.name === '子課題'
  );

  if (!subtaskType) {
    // If no Subtask type found, use the first available issue type
    console.log(`⚠️  No Subtask issue type found, using default: ${issueTypes[0].name}`);
    return issueTypes[0].id;
  }

  console.log(`📋 Using issue type: ${subtaskType.name} (ID: ${subtaskType.id})\n`);
  return subtaskType.id;
}

// Main execution
async function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(`
Issue Initing Workflow
======================

Creates 8 standard child issues for a parent issue:
  1. 要件ヘアリング　-- Hearing yêu cầu
  2. 要件定義書作成　-- Làm file spec
  3. 開発　-- Coding
  4. テストケース作成  --  Tạo test case
  5. テスト実施 -- Thực thi test
  6. UAT
  7. リリース判定 -- Release
  8. ユーザマニュアル作成 -- Làm user manual

Usage:
  npm run issue:init <parent-issue-key> [options]

Examples:
  npm run issue:init HB21373-420              # Create child issues
  npm run issue:init HB21373-420 --dry-run    # Preview without creating

Options:
  --dry-run    Preview what will be created without making changes
  --help, -h   Show this help message
`);
    process.exit(0);
  }

  const parentIssueKey = args.find(arg => !arg.startsWith('--'));
  const dryRun = args.includes('--dry-run');

  if (!parentIssueKey) {
    console.error('❌ Error: Parent issue key is required\n');
    console.error('Usage: npm run issue:init <parent-issue-key>');
    console.error('Example: npm run issue:init HB21373-420\n');
    process.exit(1);
  }

  if (!DOMAIN || !API_KEY) {
    console.error('❌ Error: Missing environment variables');
    console.error('Please ensure .env file contains:');
    console.error('  - BACKLOG_DOMAIN');
    console.error('  - BACKLOG_API_KEY\n');
    process.exit(1);
  }

  const workflow = new IssueInitWorkflow(dryRun);
  await workflow.run(parentIssueKey);
}

main();
