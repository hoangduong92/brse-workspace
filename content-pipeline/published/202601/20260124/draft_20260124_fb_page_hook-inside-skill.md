# Hooks Trong Skills: Cách Tạo Skill Tự Update Trong Claude Code

> Khi mentor AI có thể "nhớ" và adapt theo từng session với user

---

## TL;DR

Claude Code hỗ trợ hooks trong skills - cho phép skill chạy code tự động khi events xảy ra. Mình đã dùng feature này để tạo một **mentor skill tự update learner profile** sau mỗi session, giúp AI "nhớ" tiến độ học và adapt teaching style.

---

## Hooks Là Gì?

Hooks trong Claude Code là các "event listeners" - chạy script khi có sự kiện cụ thể xảy ra trong session. Có 12 hook events:

| Hook | Khi Nào Chạy |
|------|--------------|
| `SessionStart` | Session bắt đầu hoặc resume |
| `UserPromptSubmit` | User submit prompt |
| `PreToolUse` | Trước khi tool chạy |
| `PostToolUse` | Sau khi tool chạy thành công |
| `Stop` | Claude kết thúc response |
| `SessionEnd` | Session kết thúc |
| ... | và các events khác |

---

## Hooks Trong Skills vs Settings

**Settings hooks** (trong `.claude/settings.json`): Chạy globally cho toàn bộ project.

**Skill hooks** (trong `SKILL.md` frontmatter): Chạy **chỉ khi skill đó được activate**.

Đây là điểm khác biệt quan trọng - skill hooks cho phép bạn tạo behavior scoped riêng cho từng skill.

---

## Cấu Trúc Hook Trong Skill

```yaml
---
name: my-skill
description: A skill with hooks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"
  Stop:
    - hooks:
        - type: command
          command: "node ./scripts/on-stop.js"
---
```

**Supported events cho skills**: `PreToolUse`, `PostToolUse`, `Stop`

**Đặc biệt cho skills**: Option `once: true` để hook chỉ chạy 1 lần/session.

---

## Use Case: Self-Updating Mentor Skill

### Problem

Tạo AI Mentor skill mà có thể:
- Nhớ topics đã học qua các sessions
- Track teaching satisfaction từ implicit feedback
- Adapt teaching style dựa trên user preferences

### Solution Architecture

```
SKILL.md (sb skill)
    └── Stop hook
            └── swe-learning-memory.cjs
                    ├── Parse transcript
                    ├── Detect learning activity
                    ├── Analyze sentiment
                    └── Update learner-profile.md
```

### Implementation

#### 1. Skill Frontmatter

```yaml
---
name: sb
description: AI Mentor + PM cho 12-month solo builder journey
hooks:
  Stop:
    - hooks:
        - type: command
          command: node ".claude/hooks/swe-learning-memory.cjs"
      env:
        LEARNER_PROFILE_PATH: "projects/solo-builder-12months/progress/learner-profile.md"
---
```

#### 2. Hook Script Logic

```javascript
// swe-learning-memory.cjs (simplified)

async function main() {
  // 1. Đọc transcript từ stdin
  const input = JSON.parse(fs.readFileSync(0, 'utf-8'));
  const transcriptPath = input.transcript_path;

  // 2. Parse transcript tìm learning activity
  const activity = await parseLearningActivity(transcriptPath);

  if (activity.hasLearningActivity) {
    // 3. Analyze sentiment từ user messages
    const sentiment = analyzeSentiment(activity.userMessages);

    // 4. Update learner profile
    appendToProfile(activity, sentiment);
  }
}
```

#### 3. Learning Activity Detection

```javascript
const learningPatterns = [
  'giải thích', 'explain', 'tại sao', 'why',
  'how', 'như thế nào', 'what is', 'là gì'
];

// Detect quiz patterns
if (text.includes('🤔') || text.includes('Quiz')) {
  result.quizCount++;
}
```

#### 4. Implicit Sentiment Analysis

```javascript
// Không hỏi user "bạn có hài lòng không?"
// Mà detect từ implicit signals:

const POSITIVE_SIGNALS = [
  'thanks', 'cảm ơn', 'hiểu rồi', 'got it',
  'aha', 'great', 'tuyệt', 'hay quá'
];

const NEGATIVE_SIGNALS = [
  'confused', 'không hiểu', 'chậm lại',
  'khó hiểu', 'quá nhanh'
];
```

#### 5. Profile Auto-Update

```markdown
## 📊 Overview

| Metric | Value |
|--------|-------|
| First session | 2026-01-15 |
| Total sessions | 12 |
| Last active | 2026-01-24 11:30 |

## 😊 Teaching Feedback

### Satisfaction Trend
| Date | Rating | Sentiment | Summary |
|------|--------|-----------|---------|
| 2026-01-24 | 8/10 | 😊 positive | Good engagement |
| 2026-01-23 | 6/10 | 😐 neutral | Some confusion |

### What Works Well
- Code examples first, theory after
- Vietnamese explanations

### Pain Points
- Too fast pacing
- Abstract concepts without examples
```

---

## Kết Quả

Mỗi khi session với `/sb learn` kết thúc:

1. **Hook tự động chạy** - không cần user action
2. **Phân tích conversation** - detect topics, questions, quiz attempts
3. **Track sentiment** - từ implicit signals trong messages
4. **Update profile** - persistent memory cho session tiếp theo

Lần sau user quay lại, AI đọc profile và **adapt accordingly**:
- User hay confused -> slow down, more examples
- User thích code-first -> skip theory, show code ngay
- User đã master topic X -> không repeat basics

---

## Hook Output & Control

### Exit Codes

| Exit Code | Behavior |
|-----------|----------|
| 0 | Success, stdout vào context (với UserPromptSubmit/SessionStart) |
| 2 | Blocking error, stderr shown to Claude |
| Other | Non-blocking error, continue |

### JSON Output (Advanced)

```json
{
  "decision": "block",
  "reason": "Missing required context, please provide more details"
}
```

---

## Best Practices

### 1. Keep Hooks Fast
Stop hooks chạy mỗi khi Claude kết thúc response - nếu slow sẽ ảnh hưởng UX.

### 2. Use Environment Variables
```yaml
env:
  LEARNER_PROFILE_PATH: "path/to/profile.md"
```
Giúp reuse hook scripts cho multiple skills.

### 3. Handle Errors Gracefully
```javascript
try {
  // Hook logic
  process.exit(0);
} catch (error) {
  console.error(`[hook] Error: ${error.message}`);
  process.exit(0); // Don't block session
}
```

### 4. Validate Input
```javascript
const stdin = fs.readFileSync(0, 'utf-8').trim();
if (!stdin) {
  process.exit(0);
}
const input = JSON.parse(stdin);
```

---

## Security Considerations

- Hooks chạy arbitrary shell commands - review kỹ trước khi dùng
- Validate và sanitize inputs
- Dùng absolute paths
- Avoid `.env`, credentials trong hook logic

---

## Conclusion

Hooks trong skills mở ra khả năng tạo **stateful AI experiences**:
- Mentor skills nhớ progress
- Code review skills track patterns
- Project management skills accumulate context

Thay vì AI "quên sạch" mỗi session, hooks giúp tạo **persistent memory** cho các use cases phức tạp.

---

## References

- [Claude Code Hooks Reference](https://code.claude.com/docs/hooks)
- [Skills Documentation](https://code.claude.com/docs/skills)
- Example: [sb skill](https://github.com/your-repo/.claude/skills/sb/SKILL.md)

---

*Published: 2026-01-24*
*Tags: #ClaudeCode #Hooks #Skills #AIMemory #LearningMentor*
