/**
 * Backlog API Client - Fetch và filter data trực tiếp
 * Không dùng MCP để tránh lưu raw data vào conversation
 */

interface BacklogConfig {
  domain: string;
  apiKey: string;
}

interface BacklogIssue {
  id: number;
  issueKey: string;
  summary: string;
}

export class BacklogClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(config: BacklogConfig) {
    this.baseUrl = `https://${config.domain}/api/v2`;
    this.apiKey = config.apiKey;
  }

  /**
   * Get issues với filtering ngay lập tức
   * Chỉ return id, key, summary để tiết kiệm tokens
   */
  async getIssuesFiltered(params: {
    projectId: number[];
    issueTypeId?: number[];
    statusId?: number[];
    createdSince?: string;
    createdUntil?: string;
    count?: number;
    offset?: number;
  }): Promise<BacklogIssue[]> {
    const queryParams = new URLSearchParams({
      apiKey: this.apiKey,
      ...this.buildQueryParams(params)
    });

    const url = `${this.baseUrl}/issues?${queryParams}`;

    try {
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Backlog API error: ${response.status} ${response.statusText}`);
      }

      const rawData = await response.json();

      // Filter NGAY - chỉ lấy fields cần thiết
      return rawData.map((issue: any) => ({
        id: issue.id,
        issueKey: issue.issueKey,
        summary: issue.summary
      }));
    } catch (error) {
      throw new Error(`Failed to fetch issues: ${error}`);
    }
  }

  /**
   * Get issues count
   */
  async getIssuesCount(params: {
    projectId: number[];
    issueTypeId?: number[];
    statusId?: number[];
  }): Promise<number> {
    const queryParams = new URLSearchParams({
      apiKey: this.apiKey,
      ...this.buildQueryParams(params)
    });

    const url = `${this.baseUrl}/issues/count?${queryParams}`;

    try {
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Backlog API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data.count;
    } catch (error) {
      throw new Error(`Failed to fetch issues count: ${error}`);
    }
  }

  private buildQueryParams(params: any): Record<string, string> {
    const result: Record<string, string> = {};

    for (const [key, value] of Object.entries(params)) {
      if (value === undefined) continue;

      if (Array.isArray(value)) {
        value.forEach((v, i) => {
          result[`${key}[${i}]`] = String(v);
        });
      } else {
        result[key] = String(value);
      }
    }

    return result;
  }
}

/**
 * Display filtered issues in table format
 */
export function displayFilteredIssues(issues: BacklogIssue[]): void {
  if (issues.length === 0) {
    console.log('No issues found.');
    return;
  }

  // Calculate column widths
  const idWidth = Math.max(4, ...issues.map(i => i.id.toString().length));
  const keyWidth = Math.max(8, ...issues.map(i => i.issueKey.length));
  const summaryWidth = Math.max(10, ...issues.map(i => i.summary.length));

  // Header
  const separator = `+${'-'.repeat(idWidth + 2)}+${'-'.repeat(keyWidth + 2)}+${'-'.repeat(summaryWidth + 2)}+`;
  console.log(separator);
  console.log(
    `| ${'ID'.padEnd(idWidth)} | ${'Issue Key'.padEnd(keyWidth)} | ${'Summary'.padEnd(summaryWidth)} |`
  );
  console.log(separator);

  // Rows
  issues.forEach(issue => {
    console.log(
      `| ${issue.id.toString().padEnd(idWidth)} | ${issue.issueKey.padEnd(keyWidth)} | ${issue.summary.padEnd(summaryWidth)} |`
    );
  });
  console.log(separator);
}
