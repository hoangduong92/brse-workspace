#!/usr/bin/env python3
"""Fix test_report_generator.py TaskStatus and ReportData instances."""

import re

file_path = r".claude\skills\bk-track\tests\test_report_generator.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix TaskStatus instances with old structure
# Pattern: TaskStatus(issue=MagicMock(...), status="...", days_overdue=N, risk_level=RiskLevel.XXX)
old_task_pattern = r'TaskStatus\(\s*issue=MagicMock\(([^)]*)\),\s*status="([^"]*)",\s*days_overdue=(\d+),\s*risk_level=RiskLevel\.(\w+)\s*\)'

def replace_task(match):
    issue_attrs = match.group(1)
    status = match.group(2)
    days_late = match.group(3)
    risk = match.group(4).lower()

    # Extract issue_key and summary if present
    issue_key = "TEST-X"
    summary = "Task"

    if "issue_key=" in issue_attrs:
        key_match = re.search(r'issue_key="([^"]*)"', issue_attrs)
        if key_match:
            issue_key = key_match.group(1)

    if "summary=" in issue_attrs:
        sum_match = re.search(r'summary="([^"]*)"', issue_attrs)
        if sum_match:
            summary = sum_match.group(1)

    return f'TaskStatus(issue_key="{issue_key}", summary="{summary}", status="{status}", days_late={days_late}, risk_level="{risk}")'

content = re.sub(old_task_pattern, replace_task, content)

# Fix ReportData with metrics parameter
content = content.replace(
    'metrics={"health_score": 80, "progress": 50},',
    'health=ProjectHealth(total_issues=3, completed=1, in_progress=1, late_count=1, health_score=80.0),'
)

content = content.replace(
    'metrics={"health_score": 100},',
    'health=ProjectHealth(total_issues=1, completed=1, in_progress=0, late_count=0, health_score=100.0),'
)

content = content.replace(
    'metrics={"health_score": 45},',
    'health=ProjectHealth(total_issues=10, completed=2, in_progress=3, late_count=5, health_score=45.0),'
)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed {file_path}")
