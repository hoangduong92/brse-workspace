# Facebook Lessons Learned

Platform-specific patterns from content analysis.

---

## ✅ Pattern: Concise Over Complete
- **Source**: 2026-01-24 | Technical tutorial (Claude Code Hooks)
- **Context**: Draft had 288 lines, 6+ code blocks. Production reduced to 90 lines, 1 diagram.
- **Lesson**: Reduce technical content to <100 lines. Keep concept diagrams, remove code implementation details.
- **Apply when**: Converting technical/dev content to Facebook

## ✅ Pattern: Visual Content Essential
- **Source**: 2026-01-24 | Technical tutorial
- **Context**: Production added 2 images where draft had none
- **Lesson**: Always include relevant images/diagrams for Facebook posts
- **Apply when**: Any Facebook post, especially technical content

## ❌ Anti-Pattern: Missing Discussion CTA
- **Source**: 2026-01-24 | Technical tutorial
- **Issue**: No question prompting comments at end of post
- **Fix**: Add "Bạn có [relevant question]? Comment bên dưới!" or similar
- **Why matters**: Facebook algorithm heavily favors comments over likes/reactions

## ❌ Anti-Pattern: Long Technical Hook
- **Source**: 2026-01-24 | Technical tutorial
- **Issue**: Title "Hooks Trong Skills: Cách Tạo Skill Tự Update..." gets truncated in preview
- **Fix**: Keep first line under 125 chars. Use story/curiosity hook format instead of descriptive title.
- **Why matters**: Facebook truncates after ~125 chars. Hook must work before "See more"
