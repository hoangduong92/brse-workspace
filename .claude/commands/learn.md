---
description: "Học về file code hoặc topic cụ thể với Socratic method"
argument: "<file_path|topic> - Path đến file code hoặc tên topic muốn học"
---

# /learn Command

User muốn học về một file code hoặc một topic cụ thể.

## Input Analysis

### Nếu input là file path:
1. Đọc file bằng `Read` tool
2. Phân tích code structure
3. Identify key concepts trong file:
   - Design patterns được sử dụng
   - Language-specific features
   - Architecture decisions
   - Code quality practices
4. Bắt đầu teaching flow

### Nếu input là topic (không phải file):
1. Xác định topic thuộc category nào:
   - Syntax/Language: `async/await`, `generics`, `decorators`...
   - Design Pattern: `singleton`, `factory`, `observer`...
   - Architecture: `microservices`, `event-driven`, `CQRS`...
   - Principles: `SOLID`, `DRY`, `KISS`, `clean code`...
2. Tìm examples trong codebase hiện tại nếu có
3. Bắt đầu teaching flow với examples

## Teaching Flow

### Step 1: Warm-up Question
```
Trước khi mình đi vào [topic], cho mình hỏi:
- Bạn đã từng nghe về [related concept] chưa?
- Bạn nghĩ [topic] dùng để làm gì?
```

### Step 2: Core Explanation
```
## 🎯 [Topic Name]

### Context
[Tại sao concept này tồn tại, problem nó giải quyết]

### How It Works
[Giải thích step-by-step với code examples]

### Code Example
[Code từ codebase user hoặc minimal example]
```

### Step 3: Socratic Questions
```
### 🤔 Let's Think Together

1. Tại sao developer chọn approach này thay vì X?
2. Nếu requirement thay đổi thành Y, bạn sẽ modify như thế nào?
3. Có cách nào đơn giản hơn không? Trade-off là gì?
```

### Step 4: Knowledge Check
```
### ✍️ Mini Quiz

Câu 1: [Question về concept]
Câu 2: [Question về application]
Câu 3: [Question về edge cases]

(Trả lời khi bạn sẵn sàng, mình sẽ feedback)
```

### Step 5: Related Topics
```
### 📚 Học Tiếp

Dựa trên [topic], bạn có thể explore thêm:
1. **[Related Topic 1]**: [Why it connects]
2. **[Related Topic 2]**: [Why it connects]
3. **[Related Topic 3]**: [Why it connects]

Bạn muốn đi sâu vào topic nào?
```

## Example Usage

### Learning from file:
```
User: /learn src/services/auth-service.ts
```
→ Đọc file, identify: JWT pattern, dependency injection, error handling
→ Giải thích từng concept, hỏi user về understanding

### Learning topic:
```
User: /learn dependency injection
```
→ Giải thích DI concept, tìm examples trong codebase
→ Show how it's used, why it matters

## Output Guidelines

1. **Bắt đầu bằng câu hỏi** - Không dump info ngay
2. **Chunk information** - Chia nhỏ, dễ tiêu hóa
3. **Use analogies** - So sánh với real-world concepts
4. **Interactive** - Đợi user respond trước khi tiếp
5. **Encourage questions** - "Có chỗ nào chưa rõ không?"
