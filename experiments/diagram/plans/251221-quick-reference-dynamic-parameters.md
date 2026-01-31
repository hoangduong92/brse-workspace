# Quick Reference - Excel Diagram Dynamic Parameters

**Implementation Plan**: See `251221-excel-diagram-dynamic-parameters-implementation.md`

---

## Quick Fixes for Immediate Issues

### Fix Row Range Bug (URGENT)

**Problem**: "row 150~200" only captures 150

**File**: `~/.claude/skills/excel-diagram-skill-updated/prompt_parameter_parser.py`

**Line 91-96, Add**:
```python
'row_range': r'rows?\s*(\d+)\s*[-~–—]+\s*(\d+)',  # Captures 150~200
```

**Line 320-352, Replace `_extract_position`**:
```python
def _extract_position(self, prompt: str) -> Dict[str, float]:
    position = {}

    # Row range (priority)
    range_match = re.search(self.PATTERNS['position']['row_range'], prompt)
    if range_match:
        position['start_row'] = int(range_match.group(1))
        position['end_row'] = int(range_match.group(2))

    # ... rest of method
```

**File**: `dynamic_diagram_builder.py`

**Line 80-100, Update `_calculate_start_position`**:
```python
# Handle row range
if 'start_row' in params.position and 'end_row' in params.position:
    start_row = params.position['start_row']
    end_row = params.position['end_row']
    start_top = (start_row - 1) * self.ROW_HEIGHT_PT
    self.available_height = (end_row - start_row) * self.ROW_HEIGHT_PT
    self.constrained_layout = True
```

**Test**:
```bash
cd ~/.claude/skills/excel-diagram-skill-updated
python -c "
from prompt_parameter_parser import PromptParameterParser
p = PromptParameterParser()
params = p.parse('diagram from row 150~200')
print(f'Start: {params.position.get(\"start_row\")}')
print(f'End: {params.position.get(\"end_row\")}')
# Expected: Start: 150, End: 200
"
```

---

## Priority Implementation Order

1. **Row Range Bug** (2h) - Fix immediately
2. **Implicit Flows** (3h) - Add "login diagram" → auto-generates steps
3. **Conditional Styling** (4h) - "error steps red"
4. **Template Docs** (1h) - Clarify reference-only role
5. **Per-Element** (4-6h) - Optional, defer if not needed

**Total**: 10-15 hours

---

## Architecture Changes Summary

**Before** (Template-driven):
```
User prompt → Template selection → Hardcoded diagram → Render
```

**After** (Parameter-driven):
```
User prompt → Parse parameters → Dynamic builder → Render
              ↓
         [Examples for reference only]
```

**Key Principle**: Templates = documentation, not execution

---

## Testing Checklist

### Parser Tests
- [ ] Row range: "150~200", "50-100", "from 10 to 20"
- [ ] Implicit: "login diagram" → infers steps
- [ ] Rules: "error red, success green"
- [ ] Overrides: "step 2 blue 200x80"

### Builder Tests
- [ ] Shapes fit within row constraints
- [ ] Conditional styling applied correctly
- [ ] Rule priority: override > rule > global > default

### Integration Tests
- [ ] Full workflow: parse → build → render
- [ ] Backward compatibility with old prompts
- [ ] Complex prompts with multiple features

---

## Common Patterns

### Row Range Specifications
```
"row 150~200"          → start=150, end=200
"rows 50-100"          → start=50, end=100
"from row 10 to 20"    → start=10, end=20
"A50:C100"             → start_row=50, end_row=100, start_col=1, end_col=3
```

### Implicit Flows
```
"login diagram"        → ['Start', 'Enter Credentials', 'Validate', ...]
"payment flow"         → ['Cart', 'Checkout', 'Payment', 'Confirmation']
"approval process"     → ['Submit', 'Review', 'Decision', 'Approved/Rejected']
```

### Conditional Styling
```
"error steps red"              → errors = #FF0000
"success boxes green"          → success = #00FF00
"decision diamond yellow"      → decisions = diamond shape + #FFFF00
```

### Per-Element Overrides
```
"step 1 blue"                  → element[0].fill = blue
"step 2: Validate 200x80"      → element[1] = 200x80, text="Validate"
"step 3 red diamond"           → element[2] = red diamond
```

---

## Files Modified Summary

### High Priority (Must Change)
- `prompt_parameter_parser.py` - Add patterns, methods
- `dynamic_diagram_builder.py` - Constraint handling, rule application
- `SKILL.md` - Update to dynamic-first approach

### Medium Priority (Should Change)
- `excel_diagram_template.py` - Simplify to base classes
- `README.md` - Update architecture docs

### Low Priority (Nice to Have)
- Create `examples/` directory with reference code
- Create `tests/` directory with test suite

---

## Rollback Plan

If issues occur:

1. **Git revert** to previous version
2. **Disable new features** via feature flags
3. **Fallback parser** - use old regex patterns
4. **Emergency fix** - deploy hotfix for critical bugs

**Rollback Time**: <5 minutes

---

## Monitoring After Deployment

Track:
- Parser success rate (target: >95%)
- Parse time (target: <100ms)
- User clarification requests (target: <10%)
- Error rates (target: <1%)

Log warnings for:
- Failed regex matches
- Ambiguous prompts
- Performance outliers

---

## Quick Commands

**Run tests**:
```bash
cd ~/.claude/skills/excel-diagram-skill-updated
python -m pytest tests/ -v
```

**Test specific prompt**:
```bash
python -c "
from prompt_parameter_parser import PromptParameterParser
from dynamic_diagram_builder import DynamicDiagramBuilder

parser = PromptParameterParser()
params = parser.parse('YOUR PROMPT HERE')
print('Parsed:', params)

builder = DynamicDiagramBuilder()
builder.build_and_render(params, 'test.json', 'test.xlsx')
"
```

**Check parser performance**:
```bash
python -m timeit -n 1000 "
from prompt_parameter_parser import PromptParameterParser
p = PromptParameterParser()
p.parse('create login flowchart from row 150~200, error steps red')
"
```

---

## Common Pitfalls

### ❌ Don't
- Execute template files directly
- Hardcode diagram structures
- Ignore row range constraints
- Apply rules after overrides

### ✅ Do
- Use DynamicDiagramBuilder for all requests
- Parse prompts comprehensively
- Respect layout constraints
- Apply priority: override > rule > global > default

---

## Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| Templates = reference only | Reduce AI confusion, enforce dynamic approach | 2025-12-21 |
| Hybrid rule + override system | Flexibility + precision for all use cases | 2025-12-21 |
| Backward compatible changes | Preserve existing functionality | 2025-12-21 |
| Row range priority fix | Critical bug affecting user experience | 2025-12-21 |

---

**For detailed implementation, see**: `251221-excel-diagram-dynamic-parameters-implementation.md`
