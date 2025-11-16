/**
 * MCP Client Bridge
 *
 * Implements the Anthropic pattern for calling MCP tools from generated code.
 * Since Claude Code doesn't expose MCP tools to generated code, we call
 * the underlying APIs directly - achieving the same result.
 *
 * Pattern from: https://www.anthropic.com/news/code-execution-mcp
 */

import { BacklogClient } from './backlog-client.js';
import dotenv from 'dotenv';

dotenv.config();

// Initialize Backlog client
const backlogClient = new BacklogClient({
  domain: process.env.BACKLOG_DOMAIN || '',
  apiKey: process.env.BACKLOG_API_KEY || ''
});

/**
 * Call an MCP tool
 *
 * This function mimics the Anthropic article's callMCPTool pattern.
 * Instead of calling actual MCP servers (not available in generated code),
 * we call the underlying APIs directly.
 *
 * @param toolName - MCP tool name (e.g., 'mcp__backlog__get_issues')
 * @param params - Tool parameters
 * @returns Tool result
 */
export async function callMCPTool<T = any>(
  toolName: string,
  params: any
): Promise<T> {
  // Route to appropriate API based on tool name
  if (toolName.startsWith('mcp__backlog__')) {
    return callBacklogTool(toolName, params) as T;
  }

  throw new Error(`Unknown MCP tool: ${toolName}`);
}

/**
 * Call Backlog MCP tools
 */
async function callBacklogTool(toolName: string, params: any): Promise<any> {
  switch (toolName) {
    case 'mcp__backlog__get_issues':
      // Call Backlog API and filter immediately
      return backlogClient.getIssuesFiltered(params);

    case 'mcp__backlog__count_issues':
      return backlogClient.getIssuesCount(params);

    case 'mcp__backlog__get_project_list':
      // For now, return empty - would need to implement in BacklogClient
      return [];

    default:
      throw new Error(`Unknown Backlog tool: ${toolName}`);
  }
}
