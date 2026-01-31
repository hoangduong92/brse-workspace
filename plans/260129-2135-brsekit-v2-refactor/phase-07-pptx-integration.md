# Phase 7: PPTX Integration (bk-track --format pptx)

## Context Links
- [Phase 2: bk-track](./phase-02-bk-track.md)
- [PPTX Skill](c:/Users/duongbibo/brse-workspace/.claude/skills/document-skills/pptx/SKILL.md)
- [html2pptx.md](c:/Users/duongbibo/brse-workspace/.claude/skills/document-skills/pptx/html2pptx.md)

## Overview
- **Priority:** P2
- **Status:** 100% complete (formatter + 7 templates done)
- **Effort:** 2h
- **Description:** Implement PPTX output for bk-track report using existing pptx skill

## Key Insights
- pptx skill provides html2pptx workflow (HTML → PPTX)
- Create HTML slides, convert via html2pptx.js
- Visual thumbnail validation available
- Keep slide design simple, professional

## Requirements

### Functional
- `/bk-track report --format pptx` - Generate PPTX report
- Slides: Title, Summary, Accomplishments, In-Progress, Risks, Next Steps
- Automatic date range in title
- Chart support for metrics (optional)

### Non-Functional
- PPTX generation <30s
- Valid PPTX file (opens in PowerPoint/LibreOffice)
- Professional, clean design
- Japanese text support

## Architecture

```
.claude/skills/bk-track/
├── scripts/
│   └── formatters/
│       └── pptx_formatter.py   # Main implementation
├── templates/
│   └── slides/
│       ├── title.html          # Slide 1
│       ├── summary.html        # Slide 2
│       ├── accomplishments.html # Slide 3
│       ├── in_progress.html    # Slide 4
│       ├── risks.html          # Slide 5
│       └── next_steps.html     # Slide 6
└── static/
    └── styles.css              # Shared slide styles
```

### Slide Design

**Color Palette (Classic Blue)**
- Primary: #1C2833 (Deep navy)
- Secondary: #2E4053 (Slate gray)
- Accent: #3498DB (Blue)
- Background: #F4F6F6 (Off-white)
- Text: #2C3E50 (Dark gray)

**Layout: 16:9 (720pt × 405pt)**

## Related Code Files

### Create
- `.claude/skills/bk-track/scripts/formatters/pptx_formatter.py`
- `.claude/skills/bk-track/templates/slides/title.html`
- `.claude/skills/bk-track/templates/slides/summary.html`
- `.claude/skills/bk-track/templates/slides/accomplishments.html`
- `.claude/skills/bk-track/templates/slides/in_progress.html`
- `.claude/skills/bk-track/templates/slides/risks.html`
- `.claude/skills/bk-track/templates/slides/next_steps.html`
- `.claude/skills/bk-track/static/styles.css`
- `.claude/skills/bk-track/tests/test_pptx_formatter.py`

### Reuse
- `.claude/skills/document-skills/pptx/scripts/html2pptx.js`
- `.claude/skills/document-skills/pptx/scripts/thumbnail.py` (validation)

## Implementation Steps

1. **Create HTML slide templates**

   **title.html**
   ```html
   <div style="width:720pt;height:405pt;background:#1C2833;">
     <h1 style="color:#F4F6F6;font-size:48pt;text-align:center;padding-top:150pt;">
       {{project_name}}
     </h1>
     <p style="color:#AAB7B8;font-size:24pt;text-align:center;">
       Weekly Report: {{date_range}}
     </p>
   </div>
   ```

   **summary.html**
   ```html
   <div style="width:720pt;height:405pt;background:#F4F6F6;">
     <h2 style="color:#1C2833;font-size:32pt;">Summary</h2>
     <ul style="font-size:18pt;color:#2C3E50;">
       <li>Completed: {{completed_count}} tasks</li>
       <li>In Progress: {{in_progress_count}} tasks</li>
       <li>At Risk: {{at_risk_count}} tasks</li>
     </ul>
   </div>
   ```

2. **Implement pptx_formatter.py (100 lines)**
   ```python
   class PptxFormatter:
       def __init__(self, report_data: ReportData):
           self.data = report_data
           self.pptx_skill = Path(".claude/skills/document-skills/pptx")

       def generate(self, output_path: str) -> str:
           # 1. Render HTML templates with data
           slides_html = self._render_slides()

           # 2. Write HTML files to temp dir
           temp_dir = self._write_html_files(slides_html)

           # 3. Call html2pptx.js
           self._convert_to_pptx(temp_dir, output_path)

           # 4. Validate with thumbnail
           self._validate_output(output_path)

           return output_path
   ```

3. **Create styles.css (40 lines)**
   - Font: Arial (web-safe)
   - Consistent margins/padding
   - Color variables

4. **Integrate with main.py CLI**
   - Add --format pptx flag handling
   - Call PptxFormatter when format=pptx
   - Default output: `./weekly-reports/YYYYMMDD_project-weekly.pptx`

5. **Implement template rendering**
   - Use Jinja2 or simple string substitution
   - Handle list rendering (bullets)
   - Japanese text encoding (UTF-8)

6. **Write tests**
   - test_pptx_formatter.py: HTML generation
   - Integration test: Full PPTX generation
   - Validate with thumbnail.py

## Slide Content Mapping

| Slide | Data Source | Content |
|-------|-------------|---------|
| Title | project.name, date_range | Project name, period |
| Summary | metrics | Completed, In-progress, At-risk counts |
| Accomplishments | completed_tasks | Bullet list of completed tasks |
| In Progress | in_progress_tasks | Bullet list with assignees |
| Risks | at_risk_tasks + late_tasks | Risk items with dates |
| Next Steps | next_week_tasks | Planned tasks for next week |

## Todo List

- [ ] Create HTML slide templates (6 files)
- [ ] Create styles.css
- [ ] Implement PptxFormatter class
- [ ] Implement template rendering
- [ ] Integrate with bk-track CLI
- [ ] Test HTML generation
- [ ] Test PPTX conversion
- [ ] Validate with thumbnails
- [ ] Test Japanese text rendering

## Success Criteria

- [ ] `/bk-track report --format pptx` generates valid PPTX
- [ ] All 6 slides render correctly
- [ ] Japanese text displays properly
- [ ] PPTX opens in PowerPoint/LibreOffice
- [ ] Generation time <30s
- [ ] Thumbnail validation passes

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| html2pptx.js issues | Low | Use existing pptx skill workflow |
| Japanese font missing | Medium | Use system fonts, test on Windows |
| Long task lists overflow | Medium | Truncate or split slides |

## Security Considerations

- PPTX generated locally (no cloud)
- No embedded macros
- UTF-8 encoding for Japanese

## Next Steps

- Future: Custom templates selection
- Future: Chart/graph support
- Future: Customer branding option
