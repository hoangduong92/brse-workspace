/**
 * Count issues in Backlog project
 *
 * This follows the Anthropic MCP code execution pattern.
 * Auto-generated TypeScript interface for mcp__backlog__count_issues
 */

import { callMCPTool } from '../../src/mcp-client.js';

export interface CountIssuesInput {
  /** Project ID(s) to query */
  projectId: number[];
  /** Issue type IDs to filter (optional) */
  issueTypeId?: number[];
  /** Status IDs to filter (optional) */
  statusId?: number[];
  /** Created since date in YYYY-MM-DD format (optional) */
  createdSince?: string;
  /** Created until date in YYYY-MM-DD format (optional) */
  createdUntil?: string;
}

export interface CountIssuesOutput {
  /** Total count of issues matching the criteria */
  count: number;
}

/**
 * Get count of issues matching criteria (without fetching all data).
 *
 * Use this before fetching issues to plan pagination or estimate token usage.
 *
 * @example
 * const { count } = await countIssues({ projectId: [47358], statusId: [4] });
 * console.log(`Found ${count} closed issues`);
 */
export async function countIssues(
  input: CountIssuesInput
): Promise<CountIssuesOutput> {
  return callMCPTool<CountIssuesOutput>('mcp__backlog__count_issues', input);
}
