#!/usr/bin/env python3
"""Fix remaining issues in test_report_generator.py."""

file_path = r".claude\skills\bk-track\tests\test_report_generator.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_next = 0

for i, line in enumerate(lines):
    if skip_next > 0:
        skip_next -= 1
        continue

    # Skip the lines that try to set task attributes
    if 'task.issue_key = task.issue.issue_key' in line:
        # Skip this line and the next 2 lines
        skip_next = 2
        new_lines.append("")  # Keep blank line
        continue

    # Replace metrics={} with health=ProjectHealth(...)
    if 'metrics={},' in line and i < len(lines) - 5:
        # Check if this is in test_format_markdown_max_tasks_displayed
        if any('test_format_markdown_max_tasks_displayed' in lines[j] for j in range(max(0, i-10), i)):
            new_lines.append(line.replace(
                'metrics={},',
                'health=ProjectHealth(total_issues=15, completed=15, in_progress=0, late_count=0, health_score=100.0),'
            ))
        elif any('test_format_summary_basic' in lines[j] for j in range(max(0, i-10), i)):
            new_lines.append(line.replace(
                'metrics={},',
                'health=ProjectHealth(total_issues=3, completed=1, in_progress=1, late_count=1, health_score=80.0),'
            ))
        elif any('test_format_summary_perfect_health' in lines[j] for j in range(max(0, i-10), i)):
            new_lines.append(line.replace(
                'metrics={},',
                'health=ProjectHealth(total_issues=1, completed=1, in_progress=0, late_count=0, health_score=100.0),'
            ))
        elif any('test_format_summary_poor_health' in lines[j] for j in range(max(0, i-10), i)):
            new_lines.append(line.replace(
                'metrics={},',
                'health=ProjectHealth(total_issues=10, completed=2, in_progress=3, late_count=5, health_score=45.0),'
            ))
        elif any('test_format_summary_format' in lines[j] for j in range(max(0, i-10), i)):
            new_lines.append(line.replace(
                'metrics={},',
                'health=ProjectHealth(total_issues=5, completed=2, in_progress=2, late_count=1, health_score=70.0),'
            ))
        else:
            new_lines.append(line)
        continue

    # Remove report.health = MagicMock(...) blocks
    if 'report.health = MagicMock(' in line:
        # Skip until we find the closing parenthesis
        skip_next = 0
        j = i
        while j < len(lines):
            if ')' in lines[j] and 'report.health' not in lines[j+1] if j+1 < len(lines) else True:
                skip_next = j - i
                break
            j += 1
        continue

    new_lines.append(line)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Fixed {file_path}")
