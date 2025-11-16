/**
 * Get issues from Backlog project
 *
 * This follows the Anthropic MCP code execution pattern.
 * Auto-generated TypeScript interface for mcp__backlog__get_issues
 */

import { callMCPTool } from '../../src/mcp-client.js';

export interface GetIssuesInput {
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
  /** Maximum number of issues to return (optional, default: 100) */
  count?: number;
  /** Offset for pagination (optional) */
  offset?: number;
}

export interface GetIssuesOutput {
  /** Issue ID */
  id: number;
  /** Issue key (e.g., "HB21373-400") */
  issueKey: string;
  /** Issue summary */
  summary: string;
}

/**
 * Fetch issues from Backlog project (filtered to minimal fields).
 *
 * This tool automatically filters the response to only return essential
 * fields (id, issueKey, summary) to minimize token consumption.
 *
 * Raw Backlog API returns ~2000 tokens per issue.
 * This filtered version returns ~20 tokens per issue (99% reduction).
 */
export async function getIssues(
  input: GetIssuesInput
): Promise<GetIssuesOutput[]> {
  return callMCPTool<GetIssuesOutput[]>('mcp__backlog__get_issues', input);
}
