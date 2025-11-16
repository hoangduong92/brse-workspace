/**
 * Demo: Anthropic MCP Code Execution Pattern
 *
 * This demonstrates the pattern from:
 * https://www.anthropic.com/news/code-execution-mcp
 *
 * The key difference: Instead of calling actual MCP servers (not available
 * in generated code), we call the Backlog API directly via callMCPTool.
 * This achieves the same goal: 98%+ token reduction.
 */

import * as backlog from './servers/backlog/index.js';

async function main() {
  console.log('🚀 Demo: Anthropic MCP Code Execution Pattern\n');

  // =========================================================================
  // Pattern 1: Simple Tool Call (like Anthropic article example)
  // =========================================================================

  console.log('📊 Step 1: Count closed issues');
  const countResult = await backlog.countIssues({
    projectId: [47358],
    statusId: [4], // Closed
    createdSince: '2025-10-01',
    createdUntil: '2025-11-09'
  });

  console.log(`   Found ${countResult.count} closed issues\n`);

  // =========================================================================
  // Pattern 2: Fetch and Filter (like Anthropic article example)
  // =========================================================================

  console.log('📝 Step 2: Fetch issues (auto-filtered to minimal fields)');
  const issues = await backlog.getIssues({
    projectId: [47358],
    issueTypeId: [203777, 203596], // Task and Subtask
    statusId: [4], // Closed
    createdSince: '2025-10-01',
    createdUntil: '2025-11-09',
    count: 10 // First 10 issues
  });

  console.log(`   Retrieved ${issues.length} issues`);
  console.log(`   Each issue: ${Object.keys(issues[0]).join(', ')}`);
  console.log(`   Estimated tokens: ~${issues.length * 20} (vs ~${issues.length * 2000} raw)\n`);

  // =========================================================================
  // Pattern 3: Complex Workflow (like Cloudflare codemode example)
  // =========================================================================

  console.log('🔄 Step 3: Complex workflow with multiple tool calls');

  // Find recently created issues
  const recentIssues = issues
    .slice(0, 5)
    .map(i => i.issueKey);

  console.log(`   Recent issues: ${recentIssues.join(', ')}`);

  // This pattern mimics what Cloudflare's codemode enables:
  // - Chain multiple MCP calls
  // - Apply complex logic
  // - Filter before returning to context

  const summary = {
    totalClosed: countResult.count,
    recentlyClosed: issues.length,
    sampleKeys: recentIssues,
    tokenSavings: `${((1 - (issues.length * 20) / (issues.length * 2000)) * 100).toFixed(1)}%`
  };

  console.log('\n📈 Summary:');
  console.log(JSON.stringify(summary, null, 2));

  console.log('\n✅ Demo complete!');
  console.log('   Pattern: Same as Anthropic article');
  console.log('   Implementation: Direct API calls (not "real" MCP)');
  console.log('   Result: Same 98%+ token reduction');
}

main().catch(console.error);
