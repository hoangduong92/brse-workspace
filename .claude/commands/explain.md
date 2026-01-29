---
description: "Giải thích code đang được select trong IDE"
argument: "(optional) specific question về selected code"
---

# /explain Command

User đã select một đoạn code trong IDE và muốn được giải thích.

## Context Detection

IDE selection được inject vào conversation với tag `<ide_selection>`.
Đọc và phân tích đoạn code được select.

## Analysis Steps

### 1. Identify Code Type
- Function/Method definition
- Class/Interface definition
- Configuration/Setup code
- Business logic
- Utility/Helper code
- Test code

### 2. Identify Concepts
Scan for:
- **Syntax features:** async/await, generics, decorators, spread operators...
- **Patterns:** Factory, Observer, Singleton, Module...
- **Principles:** SRP, OCP, DIP, composition...
- **Practices:** Error handling, validation, logging...

### 3. Determine Explanation Depth
- Simple syntax → Quick explanation + why it's used
- Complex pattern → Deep dive with alternatives
- Architecture decision → Context + trade-offs

## Teaching Flow

### Step 1: Acknowledgment
```
Mình thấy bạn đang nhìn vào đoạn code [brief description].
Có vài điểm thú vị ở đây mình muốn discuss...
```

### Step 2: Highlight Key Points
```
## 🔍 Code Analysis

### Điểm đáng chú ý:
1. **[Point 1]**: [Observation]
2. **[Point 2]**: [Observation]
3. **[Point 3]**: [Observation]
```

### Step 3: Explain Each Concept
```
### [Concept Name]

**What:** [Brief definition]
**Why here:** [Why developer used it in this context]
**Alternative:** [Other approach and trade-off]

```code
// Annotated version of the selected code
```
```

### Step 4: Socratic Questions
```
### 🤔 Questions for You

1. Tại sao bạn nghĩ developer không dùng [alternative]?
2. Nếu data source thay đổi, phần nào cần modify?
3. Có potential issue nào bạn thấy không?
```

### Step 5: Deeper Understanding (if complex)
```
### 🔬 Under the Hood

[Explain how it works internally]
[Memory implications, performance, etc.]
```

### Step 6: Related Learning
```
### 📚 Related Concepts

Để hiểu sâu hơn về code này, nên tìm hiểu:
- **[Concept 1]**: [Why relevant]
- **[Concept 2]**: [Why relevant]

Muốn mình explain thêm về concept nào?
```

## Example Scenarios

### Scenario 1: User selects async function
```typescript
async function fetchUserData(userId: string): Promise<User> {
  try {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  } catch (error) {
    throw new UserNotFoundError(userId);
  }
}
```

**Explain:**
- `async/await` syntax và Promise
- Error handling pattern
- Custom error class usage
- Type safety với return type

### Scenario 2: User selects class with dependency injection
```typescript
@Injectable()
export class AuthService {
  constructor(
    private readonly userRepo: UserRepository,
    private readonly jwtService: JwtService,
  ) {}
}
```

**Explain:**
- Dependency Injection pattern
- `@Injectable` decorator purpose
- `readonly` modifier meaning
- Why inject instead of create

## Output Guidelines

1. **Start with what they see** - Don't overwhelm with unrelated info
2. **Layered explanation** - Simple first, deep dive if asked
3. **Always ask** - "Có muốn mình explain thêm phần nào?"
4. **Connect to bigger picture** - How this fits in the system
5. **Practical focus** - When would you write similar code?

## Special Cases

### If selection is unclear
```
Mình thấy bạn select đoạn code này. Bạn muốn mình focus vào:
1. Syntax/language features?
2. Design pattern/architecture?
3. Logic flow?
4. Tất cả?
```

### If selection is too large
```
Đoạn code này khá dài. Để mình hiệu quả hơn:
- Highlight phần bạn confused nhất
- Hoặc mình sẽ break down từng section

Bắt đầu từ đâu?
```

### If no selection detected
```
Mình không thấy code nào được select.
Bạn có thể:
1. Select code trong IDE rồi gõ /explain
2. Hoặc dùng /learn <file> để học về cả file
```
