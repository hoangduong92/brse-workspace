# Excel Diagram Skill - Dynamic Parameters Implementation Plan

**Date**: 2025-12-21
**Project**: excel-diagram-skill-updated
**Objective**: Enable dynamic diagram parameter modification from user prompts instead of rigid templates

---

## Executive Summary

Transform skill from template-based to parameter-driven architecture. Fix critical row range parsing bug, enable per-element customization, implement conditional styling, and clarify template role as reference-only.

**Impact**: High - Enables natural language diagram customization
**Effort**: 10-15 hours total
**Risk**: Low - Backward compatible

---

## Implementation Phases

### Priority 1: Fix Row Range Bug (IMMEDIATE)

**Problem**: Parser only captures start row, ignores end row
- "row 150~200" → extracts 150, ignores 200
- "from row 50 to 100" → extracts 50, ignores 100

**Files to Modify**:
- `~/.claude/skills/excel-diagram-skill-updated/prompt_parameter_parser.py`

**Changes**:

```python
# Line 91-96: Replace existing position patterns
'position': {
    'row_range': r'rows?\s*(\d+)\s*[-~–—]+\s*(\d+)',  # NEW: Range support
    'row_start': r'(?:from|start)\s+row\s*(\d+)',      # NEW: Explicit start
    'row_end': r'(?:to|until|end)\s+row\s*(\d+)',      # NEW: Explicit end
    'row_single': r'row\s*(\d+)',                       # KEEP: Single row
    'excel_range': r'([A-Za-z]+\d+)(?:\s*[:：~–—]+\s*([A-Za-z]+\d+))?',  # ENHANCED
    'coordinates': r'(?:at|position):\s*\(?(\d+)\s*[,:]\s*(\d+)\)?',
    'column': r'(?:col|column)\s*([A-Za-z]+)'
},
```

```python
# Line 320-352: Replace _extract_position method
def _extract_position(self, prompt: str) -> Dict[str, float]:
    """Extract position information from prompt"""
    position = {}

    # Row range (priority: captures 150~200 format)
    range_match = re.search(self.PATTERNS['position']['row_range'], prompt)
    if range_match:
        position['start_row'] = int(range_match.group(1))
        position['end_row'] = int(range_match.group(2))
    else:
        # Check for explicit start/end
        start_match = re.search(self.PATTERNS['position']['row_start'], prompt)
        end_match = re.search(self.PATTERNS['position']['row_end'], prompt)

        if start_match:
            position['start_row'] = int(start_match.group(1))
        if end_match:
            position['end_row'] = int(end_match.group(1))

        # Fallback to single row
        if 'start_row' not in position:
            row_match = re.search(self.PATTERNS['position']['row_single'], prompt)
            if row_match:
                position['row'] = int(row_match.group(1))

    # Excel range (A1:C100 format)
    range_match = re.search(self.PATTERNS['position']['excel_range'], prompt, re.IGNORECASE)
    if range_match:
        cell1 = range_match.group(1)
        cell2 = range_match.group(2) if range_match.group(2) else None

        if cell1:
            position['start_cell'] = cell1
            col_letter = ''.join(filter(str.isalpha, cell1))
            row_number = int(''.join(filter(str.isdigit, cell1)))
            position['start_row'] = row_number
            position['start_col'] = ord(col_letter.upper()) - ord('A') + 1

        if cell2:
            position['end_cell'] = cell2
            col_letter = ''.join(filter(str.isalpha, cell2))
            row_number = int(''.join(filter(str.isdigit, cell2)))
            position['end_row'] = row_number
            position['end_col'] = ord(col_letter.upper()) - ord('A') + 1

    # Coordinates
    coord_match = re.search(self.PATTERNS['position']['coordinates'], prompt)
    if coord_match:
        position['x'] = int(coord_match.group(1))
        position['y'] = int(coord_match.group(2))

    # Column specific
    col_match = re.search(self.PATTERNS['position']['column'], prompt, re.IGNORECASE)
    if col_match:
        col_letter = col_match.group(1).upper()
        position['col'] = ord(col_letter) - ord('A') + 1

    return position
```

**DynamicDiagramBuilder Changes**:

```python
# File: ~/.claude/skills/excel-diagram-skill-updated/dynamic_diagram_builder.py
# Line 80-100: Update _calculate_start_position to use row ranges

def _calculate_start_position(self, params: DiagramParameters) -> Tuple[float, float]:
    """Calculate starting position from parameters"""
    start_left = params.position.get('x', 150.0)
    start_top = params.position.get('y', 100.0)

    # Handle row range for vertical spacing calculation
    if 'start_row' in params.position and 'end_row' in params.position:
        start_row = params.position['start_row']
        end_row = params.position['end_row']

        start_top = (start_row - 1) * self.ROW_HEIGHT_PT

        # Store available vertical space for layout calculation
        self.available_height = (end_row - start_row) * self.ROW_HEIGHT_PT
        self.constrained_layout = True
    elif 'start_row' in params.position:
        start_top = (params.position['start_row'] - 1) * self.ROW_HEIGHT_PT

    if 'start_col' in params.position:
        start_left = (params.position['start_col'] - 1) * self.COLUMN_WIDTH_PT

    # Excel cell reference (priority over individual row/col)
    if 'start_cell' in params.position:
        cell = params.position['start_cell']
        col_letter = ''.join(filter(str.isalpha, cell))
        row_number = int(''.join(filter(str.isdigit, cell)))
        start_left = (ord(col_letter.upper()) - ord('A')) * self.COLUMN_WIDTH_PT
        start_top = (row_number - 1) * self.ROW_HEIGHT_PT

    if 'end_cell' in params.position and 'start_cell' in params.position:
        # Calculate available space from cell range
        end_cell = params.position['end_cell']
        end_row = int(''.join(filter(str.isdigit, end_cell)))
        start_row = int(''.join(filter(str.isdigit, params.position['start_cell'])))

        self.available_height = (end_row - start_row) * self.ROW_HEIGHT_PT
        self.constrained_layout = True

    return start_left, start_top
```

```python
# Add to DynamicDiagramBuilder.__init__
def __init__(self):
    self.builder = DiagramBuilder()
    self.last_shape = None
    self.available_height = None  # NEW: Track available space
    self.constrained_layout = False  # NEW: Flag for constrained layouts
```

```python
# Update _build_vertical_flow to respect row constraints
def _build_vertical_flow(self, steps: List[str], start_left: float, start_top: float,
                        width: float, height: float, fill: str, border: str, text: str):
    """Build vertical flowchart"""
    # Calculate spacing based on constraints
    if self.constrained_layout and self.available_height:
        # Distribute shapes evenly within available space
        num_shapes = len(steps)
        total_shape_height = num_shapes * height
        available_spacing = self.available_height - total_shape_height
        vertical_spacing = available_spacing / (num_shapes + 1) if num_shapes > 0 else 40

        # Ensure minimum spacing
        vertical_spacing = max(vertical_spacing, 20)
    else:
        vertical_spacing = height + 40

    for i, step in enumerate(steps):
        top = start_top + (i * (height + vertical_spacing))

        # Add shape
        shape = self.builder.create_process_box(
            text=step,
            left=start_left,
            top=top,
            width=width,
            height=height,
            fill_color=fill,
            line_color=border
        )

        # Add connector to next step
        if i < len(steps) - 1:
            self.add_connector(
                start_left + width/2,
                top + height,
                start_left + width/2,
                top + height + vertical_spacing,
                arrow_end=2
            )
```

**Testing**:

```python
# Test file: test_row_range_parsing.py
from prompt_parameter_parser import PromptParameterParser
from dynamic_diagram_builder import DynamicDiagramBuilder

def test_row_range_parsing():
    parser = PromptParameterParser()

    # Test case 1: Tilde range
    params1 = parser.parse("draw diagram from row 150~200")
    assert params1.position.get('start_row') == 150
    assert params1.position.get('end_row') == 200

    # Test case 2: Dash range
    params2 = parser.parse("flowchart rows 50-100")
    assert params2.position.get('start_row') == 50
    assert params2.position.get('end_row') == 100

    # Test case 3: "from...to" format
    params3 = parser.parse("diagram from row 10 to row 30")
    assert params3.position.get('start_row') == 10
    assert params3.position.get('end_row') == 30

    # Test case 4: Excel range
    params4 = parser.parse("position in A50:C100")
    assert params4.position.get('start_row') == 50
    assert params4.position.get('end_row') == 100
    assert params4.position.get('start_col') == 1
    assert params4.position.get('end_col') == 3

    print("✅ All row range tests passed")

def test_layout_with_constraints():
    parser = PromptParameterParser()
    builder = DynamicDiagramBuilder()

    # Test constrained vertical layout
    params = parser.parse("flowchart with steps: A, B, C, D, E from row 150~200")
    params.steps = ['A', 'B', 'C', 'D', 'E']  # Manually set for testing

    builder.build_from_parameters(params)

    # Verify shapes fit within constraints
    shapes = builder.builder.shapes
    assert len(shapes) == 5  # 5 steps

    # Check all shapes are within row 150-200 range
    for shape in shapes:
        row_top = (shape.position.top / 15) + 1  # Convert pts to row
        assert 150 <= row_top <= 200, f"Shape at row {row_top} outside range 150-200"

    print("✅ Constrained layout test passed")

if __name__ == '__main__':
    test_row_range_parsing()
    test_layout_with_constraints()
```

**Acceptance Criteria**:
- ✅ "row 150~200" extracts start=150, end=200
- ✅ "from row 50 to 100" extracts start=50, end=100
- ✅ "rows 10-20" extracts start=10, end=20
- ✅ "A50:C100" extracts start_row=50, end_row=100
- ✅ Shapes distributed evenly within row constraints
- ✅ Backward compatible with single row specs

**Estimated Effort**: 2 hours

---

### Priority 2: Implicit Step Inference

**Problem**: "login diagram" doesn't infer login flow steps

**Files to Modify**:
- `prompt_parameter_parser.py`

**Changes**:

```python
# Add new class constant for flow templates
IMPLICIT_FLOWS = {
    'login': ['Start', 'Enter Credentials', 'Validate User', 'Authentication', 'Login Success'],
    'registration': ['Start', 'User Info Form', 'Validate Input', 'Create Account', 'Email Verification', 'Registration Complete'],
    'payment': ['Shopping Cart', 'Checkout', 'Payment Method', 'Process Payment', 'Confirmation'],
    'checkout': ['View Cart', 'Billing Info', 'Shipping Info', 'Review Order', 'Place Order', 'Order Confirmation'],
    'approval': ['Submit Request', 'Manager Review', 'Decision', 'Approved', 'Rejected'],
    'order': ['Create Order', 'Validate Stock', 'Process Payment', 'Ship Order', 'Delivery'],
    'authentication': ['Login Page', 'Enter Credentials', 'Verify', '2FA', 'Access Granted'],
    'error': ['Error Detected', 'Log Error', 'Notify User', 'Retry', 'Fallback'],
    'upload': ['Select File', 'Validate File', 'Upload', 'Process', 'Confirmation'],
    'search': ['Enter Query', 'Search Database', 'Filter Results', 'Display Results'],
}

# Add detection pattern
'implicit_flow': r'\b(login|registration|payment|checkout|approval|order|authentication|error|upload|search)\s+(?:diagram|flow|flowchart|process)',
```

```python
# Update _extract_steps method (line 196-240)
def _extract_steps(self, prompt: str) -> List[str]:
    """Extract steps from prompt using multiple patterns"""
    steps = []

    # Check for implicit flow keywords FIRST
    implicit_match = re.search(self.PATTERNS['steps'].get('implicit_flow', ''), prompt, re.IGNORECASE)
    if implicit_match:
        flow_type = implicit_match.group(1).lower()
        if flow_type in self.IMPLICIT_FLOWS:
            steps = self.IMPLICIT_FLOWS[flow_type].copy()
            return steps  # Return immediately if implicit flow detected

    # Try different extraction patterns (existing code)
    for pattern_type, pattern in self.PATTERNS['steps'].items():
        if pattern_type == 'implicit_flow':
            continue  # Skip, already handled

        matches = re.finditer(pattern, prompt, re.IGNORECASE | re.MULTILINE)

        if pattern_type == 'steps_list':
            # ... existing code
```

**Allow Custom Flow Definitions**:

```python
# Optional: Allow users to extend flows
def register_custom_flow(self, name: str, steps: List[str]):
    """
    Register custom flow template

    Args:
        name: Flow identifier (e.g., 'my_process')
        steps: List of step names
    """
    self.IMPLICIT_FLOWS[name.lower()] = steps
```

**Testing**:

```python
def test_implicit_flows():
    parser = PromptParameterParser()

    # Test login
    params = parser.parse("create login diagram")
    assert 'Enter Credentials' in params.steps
    assert 'Login Success' in params.steps

    # Test payment
    params = parser.parse("payment flowchart")
    assert 'Shopping Cart' in params.steps
    assert 'Confirmation' in params.steps

    # Custom flow
    parser.register_custom_flow('deployment', ['Build', 'Test', 'Deploy', 'Monitor'])
    params = parser.parse("deployment process")
    assert params.steps == ['Build', 'Test', 'Deploy', 'Monitor']

    print("✅ Implicit flow tests passed")
```

**Acceptance Criteria**:
- ✅ "login diagram" → returns login flow steps
- ✅ "payment flowchart" → returns payment steps
- ✅ 10+ common flows pre-defined
- ✅ Custom flow registration supported
- ✅ Explicit steps override implicit flows

**Estimated Effort**: 2-3 hours

---

### Priority 3: Conditional Styling Rules

**Problem**: No way to specify "error steps red, success steps green"

**Architecture**: Add rule-based styling system

**Data Structure**:

```python
# Add to DiagramParameters dataclass
@dataclass
class DiagramParameters:
    # ... existing fields
    styling_rules: List[Dict[str, Any]] = None  # NEW

    def __post_init__(self):
        # ... existing code
        if self.styling_rules is None:
            self.styling_rules = []
```

**Parser Changes**:

```python
# Add pattern for conditional rules
'conditional_styling': r'(\w+(?:\s+\w+)*)\s+(?:steps?|boxes?)\s+(\w+)',
# Matches: "error steps red", "success boxes green", "decision diamond yellow"
```

```python
# New method: _extract_styling_rules
def _extract_styling_rules(self, prompt: str) -> List[Dict[str, Any]]:
    """Extract conditional styling rules"""
    rules = []

    pattern = self.PATTERNS.get('conditional_styling')
    if not pattern:
        return rules

    matches = re.finditer(pattern, prompt, re.IGNORECASE)

    for match in matches:
        keyword = match.group(1).lower()  # e.g., "error", "success"
        property_value = match.group(2).lower()  # e.g., "red", "green"

        # Determine property type (color, shape, etc.)
        if property_value in self.COLOR_MAP:
            rules.append({
                'condition': keyword,
                'property': 'fill_color',
                'value': self._color_to_hex(property_value)
            })
        elif property_value in ['diamond', 'rectangle', 'oval', 'rounded']:
            shape_map = {
                'diamond': 'decision_box',
                'rectangle': 'process_box',
                'oval': 'terminator',
                'rounded': 'process_box'
            }
            rules.append({
                'condition': keyword,
                'property': 'shape_type',
                'value': shape_map.get(property_value, 'process_box')
            })

    return rules
```

```python
# Update parse() method to include rules
def parse(self, prompt: str) -> DiagramParameters:
    # ... existing code

    # Extract styling rules
    params.styling_rules = self._extract_styling_rules(prompt_lower)

    return params
```

**DynamicDiagramBuilder Integration**:

```python
# Add method to apply conditional styling
def _apply_styling_rules(self, text: str, params: DiagramParameters) -> Dict[str, Any]:
    """
    Apply conditional styling rules to determine shape properties

    Args:
        text: Shape text to match against conditions
        params: DiagramParameters with styling rules

    Returns:
        Dict with fill_color, line_color, shape_type overrides
    """
    overrides = {}
    text_lower = text.lower()

    for rule in params.styling_rules:
        condition = rule['condition']

        # Check if condition matches text
        if condition in text_lower or re.search(r'\b' + condition + r'\b', text_lower):
            overrides[rule['property']] = rule['value']

    return overrides
```

```python
# Update _build_vertical_flow to use rules
def _build_vertical_flow(self, steps: List[str], start_left: float, start_top: float,
                        width: float, height: float, fill: str, border: str, text: str):
    """Build vertical flowchart with conditional styling"""
    # ... existing spacing calculation

    for i, step in enumerate(steps):
        top = start_top + (i * (height + vertical_spacing))

        # Apply conditional styling rules
        overrides = self._apply_styling_rules(step, self.params) if hasattr(self, 'params') else {}

        # Use overrides or defaults
        shape_fill = overrides.get('fill_color', fill)
        shape_border = overrides.get('line_color', border)
        shape_type = overrides.get('shape_type', 'process_box')

        # Create shape based on type
        if shape_type == 'decision_box':
            shape = self.builder.create_decision_box(
                text=step, left=start_left, top=top,
                width=width, height=height,
                fill_color=shape_fill, line_color=shape_border
            )
        else:
            shape = self.builder.create_process_box(
                text=step, left=start_left, top=top,
                width=width, height=height,
                fill_color=shape_fill, line_color=shape_border
            )

        # ... connector code
```

```python
# Update build_from_parameters to store params
def build_from_parameters(self, params: DiagramParameters) -> DiagramBuilder:
    """Build diagram from extracted parameters"""
    self.params = params  # NEW: Store for rule application

    # ... rest of existing code
```

**Testing**:

```python
def test_conditional_styling():
    parser = PromptParameterParser()
    builder = DynamicDiagramBuilder()

    # Test color rules
    params = parser.parse("flowchart with steps: Login, Error, Success. Error steps red, success steps green")
    params.steps = ['Login', 'Error Handling', 'Success']

    assert len(params.styling_rules) == 2
    assert any(r['condition'] == 'error' and r['value'] == '#FF0000' for r in params.styling_rules)
    assert any(r['condition'] == 'success' and r['value'] == '#00FF00' for r in params.styling_rules)

    # Build and verify
    builder.build_from_parameters(params)
    shapes = builder.builder.shapes

    # Find error shape
    error_shape = next(s for s in shapes if 'Error' in s.text)
    assert error_shape.fill_color == '#FF0000'

    success_shape = next(s for s in shapes if 'Success' in s.text)
    assert success_shape.fill_color == '#00FF00'

    print("✅ Conditional styling tests passed")
```

**Acceptance Criteria**:
- ✅ "error steps red" → shapes with "error" text are red
- ✅ "success steps green" → shapes with "success" text are green
- ✅ "decision diamond" → shapes with "decision" become diamonds
- ✅ Multiple rules apply correctly
- ✅ Rules override global defaults
- ✅ Case-insensitive matching

**Estimated Effort**: 3-4 hours

---

### Priority 4: Template Documentation Refactor

**Problem**: Templates appear as execution code, confuse AI agents

**Changes**:

**Directory Restructure**:
```
excel-diagram-skill-updated/
├── SKILL.md                          # UPDATED: Dynamic-first approach
├── prompt_parameter_parser.py        # Enhanced parser
├── dynamic_diagram_builder.py        # Primary builder
├── excel_diagram_renderer.py         # Renderer only
├── excel_diagram_template.py         # Base classes ONLY (Shape, Position, Colors, Defaults)
├── examples/                          # NEW: Reference code
│   ├── README.md                     # Explains template role
│   ├── example_login_flow.py        # Sample login diagram code
│   ├── example_decision_tree.py     # Sample decision diagram code
│   ├── example_parallel_flow.py     # Sample parallel processes
│   └── example_custom_styling.py    # Sample conditional styling
└── tests/                            # NEW: Test suite
    ├── test_parser.py
    ├── test_builder.py
    └── test_integration.py
```

**SKILL.md Rewrite** (Key Sections):

```markdown
## How This Skill Works (UPDATED)

**Dynamic Parameter Extraction → Diagram Building → Rendering**

1. **Parse User Prompt**: `PromptParameterParser` extracts:
   - Diagram type, layout, position, size, colors
   - Steps/elements (explicit or inferred from keywords)
   - Conditional styling rules

2. **Build Diagram**: `DynamicDiagramBuilder` constructs diagram from parameters

3. **Render to Excel**: `excel_diagram_renderer` creates .xlsx with real shapes

**IMPORTANT: Templates are REFERENCE ONLY**
- Located in `examples/` directory
- Show sample code patterns for AI agents
- NEVER execute templates directly
- ALWAYS use DynamicDiagramBuilder

## When to Use Examples

Examples provide reference patterns when:
- Building complex custom layouts
- Implementing new diagram types
- Learning framework API

**Do NOT**:
- Execute example files directly
- Use templates as primary workflow
- Rely on hardcoded templates for user requests

## Quick Start

User: "Create login flowchart from row 150-200, error steps red"

AI Agent Response:
```python
from prompt_parameter_parser import PromptParameterParser
from dynamic_diagram_builder import DynamicDiagramBuilder

# Parse prompt
parser = PromptParameterParser()
params = parser.parse("Create login flowchart from row 150-200, error steps red")

# Build diagram
builder = DynamicDiagramBuilder()
builder.build_and_render(params, "login_flow.json", "login_flow.xlsx")

# Result: Excel file with login diagram in rows 150-200, error steps highlighted red
```
```

**examples/README.md**:

```markdown
# Example Diagram Patterns

These files demonstrate diagram building patterns for AI agent reference.

## Purpose

Examples show:
- Common diagram structures (login, payment, approval flows)
- Advanced features (conditional styling, mixed layouts)
- Best practices for API usage

## Usage

**For AI Agents**: Review examples to understand:
- How to structure diagram building code
- Framework API usage patterns
- Common parameter combinations

**For Developers**: Use as:
- Learning resources
- Code snippets for custom diagrams
- Testing references

## DO NOT

- Execute examples directly for user requests
- Use as templates in production
- Hardcode example patterns

## Instead

Always use `DynamicDiagramBuilder` with `PromptParameterParser` for user requests.

## Available Examples

- `example_login_flow.py` - Authentication flow with decisions
- `example_decision_tree.py` - Multi-branch decision logic
- `example_parallel_flow.py` - Concurrent processes with merge
- `example_custom_styling.py` - Conditional styling rules
```

**excel_diagram_template.py Simplification**:

Remove all template methods, keep only:
- Base classes (Shape, Position, DiagramBuilder)
- Constants (Colors, Defaults, ShapeType, etc.)
- Core builder methods

**Acceptance Criteria**:
- ✅ SKILL.md emphasizes dynamic-first approach
- ✅ Templates moved to examples/ with clear README
- ✅ excel_diagram_template.py contains only base classes
- ✅ No execution paths reference templates
- ✅ Documentation clearly states reference-only role

**Estimated Effort**: 1 hour

---

### Priority 5: Per-Element Property Overrides (OPTIONAL)

**Problem**: Can't specify "step 2 blue 200x80, step 3 red 150x60"

**When to Implement**: Only if users frequently request per-element customization

**Architecture**: Index-based property overrides

**Parser Pattern**:

```python
# Pattern for element-specific properties
'element_override': r'step\s*(\d+)[:\s]+([^,]+?)(?:\s+(\w+))?(?:\s+(\d+)x(\d+))?'
# Matches: "step 2: Validate blue 200x80"
```

**Data Structure**:

```python
@dataclass
class ElementOverride:
    index: int
    text: Optional[str] = None
    fill_color: Optional[str] = None
    line_color: Optional[str] = None
    width: Optional[float] = None
    height: Optional[float] = None
    shape_type: Optional[str] = None

@dataclass
class DiagramParameters:
    # ... existing fields
    element_overrides: List[ElementOverride] = None
```

**Priority Order**:
1. Element-specific overrides (highest priority)
2. Conditional styling rules
3. Global parameters
4. Framework defaults (lowest priority)

**Acceptance Criteria**:
- ✅ "step 2 blue" → second element is blue
- ✅ "step 1: Login 200x80" → first element 200x80
- ✅ Overrides take precedence over rules and globals
- ✅ Partial overrides work (only color, only size, etc.)

**Estimated Effort**: 4-6 hours

---

## Testing Strategy

### Unit Tests

```python
# test_parser.py
- test_row_range_formats()  # ~, -, to, various formats
- test_implicit_flows()      # All predefined flows
- test_conditional_rules()   # Color, shape, multi-rule
- test_element_overrides()   # Index-based customization
- test_backward_compat()     # Existing prompts still work
```

### Integration Tests

```python
# test_integration.py
- test_full_workflow()       # Parse → Build → Render
- test_constraint_layout()   # Row range respected
- test_rule_application()    # Conditional styling applied
- test_complex_prompts()     # Multiple features combined
```

### Regression Tests

```python
# test_regression.py
- test_existing_prompts()    # Previous working prompts
- test_json_compatibility()  # Old JSON files still render
- test_api_stability()       # Public API unchanged
```

**Test Coverage Target**: >90%

---

## Rollout Plan

### Phase 1: Priority 1 (Week 1)
- Fix row range bug
- Update parser and builder
- Test with diverse prompts
- Deploy to skill directory

### Phase 2: Priorities 2-3 (Week 2)
- Implement implicit flows
- Add conditional styling
- Integration testing
- Update SKILL.md

### Phase 3: Priority 4 (Week 2)
- Refactor templates to examples/
- Update documentation
- Create example files
- User communication

### Phase 4: Priority 5 (Future - if needed)
- Monitor user requests
- Implement if demand exists
- Otherwise defer

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| Parser too complex | Modular regex patterns, extensive tests |
| Performance degradation | Benchmark parser, optimize hot paths |
| Breaking changes | Comprehensive regression suite |
| AI confusion | Clear SKILL.md, examples/ with README |
| Feature creep | Stick to priorities, defer optional features |

---

## Success Metrics

**Functional**:
- Row range bug fixed (Priority 1)
- 10+ implicit flows recognized (Priority 2)
- Conditional styling works (Priority 3)
- Templates clarified as reference (Priority 4)

**Non-Functional**:
- Parser <100ms for typical prompts
- 90%+ test coverage
- Zero breaking changes to existing functionality
- Clear documentation with examples

**User Experience**:
- Natural language prompts work intuitively
- AI agents understand dynamic-first approach
- Fewer clarification questions needed

---

## Implementation Sequence

1. **Fix Row Range Bug** (2h)
   - Update parser regex
   - Modify builder constraint handling
   - Test thoroughly

2. **Implicit Flow Inference** (3h)
   - Add flow dictionary
   - Update step extraction
   - Register custom flows

3. **Conditional Styling** (4h)
   - Add rule parsing
   - Implement rule application
   - Test with multiple rules

4. **Template Refactor** (1h)
   - Move to examples/
   - Update SKILL.md
   - Create example README

5. **Testing & Documentation** (2h)
   - Write comprehensive tests
   - Update all documentation
   - Create migration guide

**Total Estimated Effort**: 12 hours

---

## Files to Create/Modify

### Create New:
- `examples/README.md`
- `examples/example_login_flow.py`
- `examples/example_decision_tree.py`
- `examples/example_parallel_flow.py`
- `examples/example_custom_styling.py`
- `tests/test_parser.py`
- `tests/test_builder.py`
- `tests/test_integration.py`
- `tests/test_row_range_parsing.py`

### Modify Existing:
- `prompt_parameter_parser.py` - Add patterns, methods
- `dynamic_diagram_builder.py` - Constraint handling, rule application
- `SKILL.md` - Dynamic-first approach, clarify templates
- `excel_diagram_template.py` - Simplify to base classes only
- `README.md` - Update architecture description

---

## Next Actions

1. **Review & Approve Plan** - Stakeholder sign-off
2. **Setup Test Environment** - Create tests/ directory
3. **Implement Priority 1** - Fix row range bug first
4. **Incremental Deployment** - Test each priority before next
5. **Gather Feedback** - Monitor user requests, iterate

---

## Unresolved Questions

1. **Custom Flow Persistence**: Should user-defined flows persist across sessions?
   - Option A: In-memory only (session-scoped)
   - Option B: Save to config file (persistent)
   - Recommendation: Start with A, add B if requested

2. **Rule Conflict Resolution**: What if multiple rules match same element?
   - Option A: First match wins
   - Option B: Last match wins
   - Option C: Most specific match wins
   - Recommendation: C (most specific)

3. **Parser Error Handling**: How verbose should failures be?
   - Option A: Silent fallback to defaults
   - Option B: Warning messages with defaults
   - Option C: Strict errors requiring user fix
   - Recommendation: B (helpful but non-blocking)

4. **Performance Monitoring**: Should we add telemetry?
   - Track: Parse time, build time, render time
   - Report: Performance regressions
   - Recommendation: Yes, add simple timing logs

5. **Backward Compatibility Window**: How long to support old API?
   - Option A: Indefinite (no breaking changes)
   - Option B: 6 months deprecation notice
   - Recommendation: A (fully backward compatible)

---

**END OF IMPLEMENTATION PLAN**
