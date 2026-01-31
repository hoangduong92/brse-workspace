"""Weekly report generator for bk-track (stub for now - will be implemented later)."""


class ReportGenerator:
    """Weekly report generator (placeholder)."""

    def __init__(self, period_days=7):
        """Initialize generator.

        Args:
            period_days: Report period in days
        """
        self.period_days = period_days
        self.period = period_days  # Alias for backward compatibility

    def generate(self, project_key=None):
        """Generate report data (placeholder).

        Args:
            project_key: Backlog project key

        Returns:
            Report data dict or None
        """
        # TODO: Implement weekly report generation
        return None

    def format_markdown(self, data):
        """Format data as markdown (placeholder).

        Args:
            data: Report data dict

        Returns:
            Markdown string
        """
        return "Weekly report generation not yet implemented in bk-track.\nUse 'bk-track status' for project status reports."

    def format_summary(self, data):
        """Format summary (placeholder).

        Args:
            data: Report data dict

        Returns:
            Summary string
        """
        return "Weekly report summary not yet implemented."
