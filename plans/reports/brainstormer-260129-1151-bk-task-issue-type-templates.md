# Brainstorm Report: bk-task Issue Type Templates

**Date:** 2026-01-29
**Context:** VN-JA bilingual development team working with Japanese clients
**Scope:** Comprehensive templates for all 8 Backlog issue types

---

## Problem Statement

The bk-task skill needs structured templates for each issue type to:
1. Parse unstructured VN/JA mixed input into proper Backlog issues
2. Format bilingual titles (`VN -- JA` for internal, pure JA for customer-facing)
3. Support both Waterfall (WBS-based) and Ad-hoc (request-based) workflows
4. Auto-detect fields where possible, prompt for required fields when missing

---

## Title Format Convention

| Context | Format | Example |
|---------|--------|---------|
| **Internal** | `{JA_prefix}/{JA_category}/{JA_summary} -- {VN_summary}` | `RPA/開発/ログイン機能実装 -- Implement chuc nang login` |
| **Customer-facing** | `{JA_prefix}/{JA_category}/{JA_summary}` | `RPA/開発/ログイン機能実装` |
| **Simple internal** | `{JA_summary} -- {VN_summary}` | `ログイン不具合修正 -- Fix loi login` |

**Prefix Convention by Project Type:**
- `RPA/` - RPA automation projects
- `WEB/` - Web development projects
- `API/` - API development projects
- No prefix - Generic/ad-hoc tasks

---

## Issue Type Templates

### 1. Task (タスク/Cong viec)

Standard work item - the default for most development activities.

```yaml
task:
  type_id: "Task"
  title_format:
    internal: "{prefix}/{category}/{ja_summary} -- {vn_summary}"
    customer: "{prefix}/{category}/{ja_summary}"

  description_structure:
    required:
      - objective       # 目的 / Muc tieu
      - acceptance      # 完了条件 / Dieu kien hoan thanh
    optional:
      - background      # 背景 / Boi canh
      - related_docs    # 関連資料 / Tai lieu lien quan
      - notes           # 備考 / Ghi chu

  required_fields:
    - summary
    - issue_type_id
    - priority_id

  optional_fields:
    - assignee_id
    - due_date
    - start_date
    - estimated_hours
    - milestone_id
    - category_id
    - parent_issue_id   # For linking to parent

  auto_fill_logic:
    priority: "normal"  # Default unless urgency keywords detected
    due_date: "detect_from_text"  # 明日まで, 今週中, etc.
    estimated_hours: "detect_from_text"  # 8時間, 4h, etc.
    assignee: "detect_from_text"  # 田中さん, Tanaka-san
    category: "detect_from_prefix"  # RPA/ -> RPA category

  detection_keywords:
    ja: ["タスク", "作業", "対応", "実装", "作成", "開発"]
    vn: ["task", "cong viec", "implement", "tao", "phat trien"]
    en: ["task", "work", "implement", "create", "develop"]

  example:
    input: |
      明日までにログイン画面の実装をお願いします。田中さん担当で8時間。
      - Yeu cau: implement login screen
      - Assignee: Tanaka
    output:
      title: "WEB/開発/ログイン画面実装 -- Implement man hinh login"
      priority: "normal"
      due_date: "2026-01-30"  # tomorrow
      estimated_hours: 8
      assignee_hint: "田中"
      description: |
        ## 目的 / Muc tieu
        ログイン画面の実装

        ## 完了条件 / Dieu kien hoan thanh
        - ログイン画面が表示される
        - ユーザー認証が動作する
```

---

### 2. Subtask (子課題/Subtask)

Child of main task - inherits parent context, more granular work unit.

```yaml
subtask:
  type_id: "Subtask"
  title_format:
    internal: "{parent_prefix}/{phase}/{ja_summary} -- {vn_summary}"
    customer: "{parent_prefix}/{phase}/{ja_summary}"

  # Phase prefixes for Waterfall WBS
  phase_prefixes:
    - "要件定義"      # Requirements
    - "設計"          # Design
    - "開発"          # Development
    - "テスト"        # Testing
    - "リリース"      # Release

  description_structure:
    required:
      - scope           # 作業範囲 / Pham vi cong viec
    optional:
      - dependencies    # 依存関係 / Phu thuoc
      - deliverables    # 成果物 / San pham

  required_fields:
    - summary
    - parent_issue_id   # MUST have parent
    - issue_type_id
    - priority_id

  optional_fields:
    - assignee_id
    - due_date
    - estimated_hours

  auto_fill_logic:
    parent_issue_id: "required_prompt"  # Must be specified
    priority: "inherit_from_parent"
    due_date: "inherit_or_detect"
    assignee: "inherit_or_detect"
    prefix: "inherit_from_parent"
    estimated_hours: "standard_by_phase"  # Use template defaults

  # Standard hours by phase (from feature-dev.json pattern)
  standard_hours_by_phase:
    "要件定義/ヒアリング": 2.0
    "要件定義/要件定義書作成": 4.0
    "要件定義/要件定義書レビュー": 2.0
    "開発/開発": 8.0
    "開発/テストケース作成": 2.0
    "開発/テスト": 4.0
    "開発/テスト後の修正": 4.0
    "開発/UAT": 4.0
    "リリース判定/マニュアル作成": 2.0
    "リリース判定/リリース判定": 1.0

  detection_keywords:
    ja: ["子課題", "サブタスク", "分割", "詳細"]
    vn: ["subtask", "cong viec con", "chi tiet"]
    en: ["subtask", "sub-task", "breakdown"]

  example:
    input: |
      Parent: BKT-123 (Login Implementation)
      Create subtask for coding phase, 8 hours, Yamada-san
    output:
      title: "WEB/開発/開発 -- Coding"
      parent_issue_id: "BKT-123"
      priority: "normal"  # inherited
      estimated_hours: 8
      assignee_hint: "山田"
```

---

### 3. Bug (不具合/Loi)

Defect tracking - requires reproduction steps and environment info.

```yaml
bug:
  type_id: "Bug"
  title_format:
    internal: "[BUG] {ja_summary} -- {vn_summary}"
    customer: "[不具合] {ja_summary}"

  description_structure:
    required:
      - symptom         # 現象 / Hien tuong
      - environment     # 環境 / Moi truong
      - repro_steps     # 再現手順 / Cac buoc tai hien
    optional:
      - expected        # 期待動作 / Hanh vi mong doi
      - actual          # 実際の動作 / Hanh vi thuc te
      - workaround      # 回避策 / Cach giai quyet tam thoi
      - logs            # ログ / Log
      - screenshots     # スクリーンショット / Screenshot

  required_fields:
    - summary
    - issue_type_id
    - priority_id
    - description       # Must include repro steps

  optional_fields:
    - assignee_id
    - due_date
    - estimated_hours
    - severity          # custom field if exists
    - affected_version  # custom field if exists

  auto_fill_logic:
    priority: "high_if_production"  # Production bugs = high priority
    due_date: "today_if_urgent"     # 緊急, 至急 -> today
    category: "auto_bug"

  # Priority escalation rules
  priority_rules:
    - condition: "本番環境|production|prod"
      priority: "high"
    - condition: "データ消失|data loss|データ破損"
      priority: "high"
    - condition: "緊急|至急|ASAP|urgent"
      priority: "high"
    - condition: "動作しない|cannot|できない"
      priority: "normal"
    - condition: "表示|UI|見た目"
      priority: "low"

  detection_keywords:
    ja: ["不具合", "バグ", "エラー", "障害", "動かない", "表示されない", "クラッシュ"]
    vn: ["bug", "loi", "error", "khong hoat dong", "crash"]
    en: ["bug", "error", "defect", "crash", "broken", "not working"]

  example:
    input: |
      緊急：本番でログインボタンが反応しません
      環境: Chrome 120, Windows 11
      手順: 1. トップページ開く 2. ログインクリック 3. 何も起きない
    output:
      title: "[BUG] ログインボタン無反応 -- Login button khong phan hoi"
      priority: "high"
      due_date: "2026-01-29"  # today (urgent)
      description: |
        ## 現象 / Hien tuong
        本番環境でログインボタンが反応しない

        ## 環境 / Moi truong
        - Browser: Chrome 120
        - OS: Windows 11
        - Environment: Production

        ## 再現手順 / Cac buoc tai hien
        1. トップページを開く
        2. ログインボタンをクリック
        3. 画面遷移なし、反応なし
```

---

### 4. Risk (リスク/Rui ro)

Project risk tracking - requires impact assessment and mitigation plan.

```yaml
risk:
  type_id: "Risk"
  title_format:
    internal: "[RISK] {ja_summary} -- {vn_summary}"
    customer: "[リスク] {ja_summary}"

  description_structure:
    required:
      - risk_description  # リスク内容 / Noi dung rui ro
      - impact           # 影響 / Anh huong
      - probability      # 発生確率 / Xac suat xay ra
    optional:
      - mitigation       # 対策 / Bien phap phong ngua
      - contingency      # 緊急対応 / Xu ly khi xay ra
      - owner            # 責任者 / Nguoi chiu trach nhiem
      - trigger          # トリガー / Dieu kien kich hoat

  required_fields:
    - summary
    - issue_type_id
    - priority_id
    - description

  optional_fields:
    - assignee_id       # Risk owner
    - due_date          # Review date
    - custom_risk_level # High/Medium/Low

  auto_fill_logic:
    priority: "map_from_risk_level"
    status: "open"  # Risks stay open until resolved

  # Risk level to priority mapping
  risk_priority_map:
    "高|high|cao": "high"
    "中|medium|trung binh": "normal"
    "低|low|thap": "low"

  detection_keywords:
    ja: ["リスク", "懸念", "心配", "問題になりそう", "遅延の可能性"]
    vn: ["risk", "rui ro", "lo ngai", "co the cham tre"]
    en: ["risk", "concern", "might delay", "potential issue"]

  example:
    input: |
      リスク：外部API仕様が未確定で開発遅延の可能性
      影響: 2週間遅延
      確率: 60%
      対策: Mock APIで先行開発
    output:
      title: "[RISK] 外部API仕様未確定 -- API spec chua xac dinh"
      priority: "high"  # High probability + significant impact
      description: |
        ## リスク内容 / Noi dung rui ro
        外部APIの仕様が未確定のため、開発作業が遅延する可能性がある

        ## 影響 / Anh huong
        - 開発スケジュール: 2週間遅延の可能性
        - コスト: 追加工数発生

        ## 発生確率 / Xac suat xay ra
        60% (中～高)

        ## 対策 / Bien phap phong ngua
        - Mock APIを使用して先行開発を進める
        - 仕様確定後に結合テストを実施
```

---

### 5. User Feedback (ユーザーフィードバック/Phan hoi nguoi dung)

From end users - requires categorization and response tracking.

```yaml
user_feedback:
  type_id: "UserFeedback"
  title_format:
    internal: "[FB] {ja_summary} -- {vn_summary}"
    customer: "[フィードバック] {ja_summary}"

  description_structure:
    required:
      - feedback_content  # フィードバック内容 / Noi dung phan hoi
      - user_info        # ユーザー情報 / Thong tin nguoi dung
      - channel          # 受付経路 / Kenh tiep nhan
    optional:
      - sentiment        # 感情 / Cam xuc (positive/neutral/negative)
      - category         # 分類 / Phan loai (UX, performance, feature request)
      - priority_reason  # 優先理由 / Ly do uu tien
      - response         # 回答 / Tra loi

  required_fields:
    - summary
    - issue_type_id
    - priority_id
    - description

  optional_fields:
    - assignee_id
    - due_date          # Response deadline
    - custom_feedback_type

  auto_fill_logic:
    priority: "map_from_sentiment"
    category: "detect_from_content"

  # Feedback category detection
  feedback_categories:
    "使いにくい|UX|操作性": "UX"
    "遅い|パフォーマンス|重い": "Performance"
    "欲しい|追加してほしい|機能要望": "FeatureRequest"
    "良い|便利|助かる": "Positive"
    "不具合|バグ": "Bug"  # -> Convert to Bug type

  detection_keywords:
    ja: ["フィードバック", "ユーザーから", "お客様から", "要望", "ご意見"]
    vn: ["feedback", "phan hoi", "y kien", "yeu cau tu user"]
    en: ["feedback", "user request", "customer said", "suggestion"]

  example:
    input: |
      ユーザーフィードバック：
      お客様「検索結果が遅い。3秒以上かかる」
      経路: サポートチャット
    output:
      title: "[FB] 検索パフォーマンス改善要望 -- Yeu cau cai thien performance search"
      priority: "normal"
      category: "Performance"
      description: |
        ## フィードバック内容 / Noi dung phan hoi
        検索結果の表示が遅い（3秒以上かかる）

        ## ユーザー情報 / Thong tin nguoi dung
        - 匿名ユーザー

        ## 受付経路 / Kenh tiep nhan
        サポートチャット

        ## 分類 / Phan loai
        Performance (パフォーマンス)
```

---

### 6. Question (質問/Cau hoi)

Clarification needed - requires clear question and context.

```yaml
question:
  type_id: "Question"
  title_format:
    internal: "[Q] {ja_summary} -- {vn_summary}"
    customer: "[質問] {ja_summary}"

  description_structure:
    required:
      - question         # 質問内容 / Noi dung cau hoi
      - context          # 背景 / Boi canh
    optional:
      - options          # 選択肢 / Cac lua chon
      - deadline_reason  # 回答期限理由 / Ly do deadline
      - related_issues   # 関連課題 / Issue lien quan
      - answer           # 回答 / Tra loi (filled later)

  required_fields:
    - summary
    - issue_type_id
    - priority_id
    - description

  optional_fields:
    - assignee_id       # Who should answer
    - due_date          # Answer needed by

  auto_fill_logic:
    priority: "normal"  # Questions usually not urgent
    assignee: "detect_expert"  # Try to route to relevant expert

  # Question routing by topic
  routing_rules:
    "API|バックエンド|DB": "backend_lead"
    "UI|フロントエンド|画面": "frontend_lead"
    "仕様|要件": "pm"
    "デザイン": "designer"

  detection_keywords:
    ja: ["質問", "確認したい", "教えてください", "どうすれば", "？"]
    vn: ["cau hoi", "hoi", "xin hoi", "lam sao"]
    en: ["question", "how to", "what is", "?"]

  example:
    input: |
      質問：APIの認証方式はJWTでいいですか？
      背景：仕様書に明記されていない
      選択肢：JWT / OAuth2 / Session
    output:
      title: "[Q] API認証方式の確認 -- Xac nhan phuong thuc auth API"
      priority: "normal"
      description: |
        ## 質問内容 / Noi dung cau hoi
        APIの認証方式はJWTで進めて良いでしょうか？

        ## 背景 / Boi canh
        仕様書に認証方式が明記されていないため確認したい

        ## 選択肢 / Cac lua chon
        1. JWT (推奨)
        2. OAuth2
        3. Session-based

        ## 回答期限 / Deadline tra loi
        開発着手前（1/30まで）
```

---

### 7. Change Request (変更要求/Yeu cau thay doi)

Scope change - requires impact analysis and approval workflow.

```yaml
change_request:
  type_id: "ChangeRequest"
  title_format:
    internal: "[CR] {ja_summary} -- {vn_summary}"
    customer: "[変更要求] {ja_summary}"

  description_structure:
    required:
      - change_content   # 変更内容 / Noi dung thay doi
      - reason           # 変更理由 / Ly do thay doi
      - impact           # 影響範囲 / Pham vi anh huong
    optional:
      - cost_impact      # コスト影響 / Anh huong chi phi
      - schedule_impact  # スケジュール影響 / Anh huong lich trinh
      - approval_status  # 承認状況 / Trang thai phe duyet
      - alternatives     # 代替案 / Phuong an thay the

  required_fields:
    - summary
    - issue_type_id
    - priority_id
    - description

  optional_fields:
    - assignee_id       # Change owner
    - due_date          # Decision deadline
    - custom_approval_status

  auto_fill_logic:
    priority: "high"    # Changes need prompt attention
    status: "pending_approval"

  # Impact level detection
  impact_levels:
    "大きい|重大|major": "major"
    "中程度|moderate": "moderate"
    "軽微|minor|小さい": "minor"

  detection_keywords:
    ja: ["変更要求", "仕様変更", "追加要件", "変更したい", "変更依頼"]
    vn: ["change request", "thay doi", "yeu cau thay doi", "bo sung"]
    en: ["change request", "scope change", "modification", "CR"]

  example:
    input: |
      仕様変更依頼：
      ログイン画面にSNS認証（Google, Facebook）を追加したい
      理由：ユーザー利便性向上
      影響：+2週間、+40時間
    output:
      title: "[CR] SNS認証追加 -- Them chuc nang dang nhap SNS"
      priority: "high"
      description: |
        ## 変更内容 / Noi dung thay doi
        ログイン画面にSNS認証（Google, Facebook）を追加

        ## 変更理由 / Ly do thay doi
        ユーザー利便性向上のため

        ## 影響範囲 / Pham vi anh huong
        - 画面: ログイン画面
        - API: 認証API
        - DB: ユーザーテーブル

        ## コスト影響 / Anh huong chi phi
        +40時間（5人日）

        ## スケジュール影響 / Anh huong lich trinh
        +2週間

        ## 承認状況 / Trang thai phe duyet
        [ ] PM承認
        [ ] 顧客承認
```

---

### 8. Investigation (調査/Dieu tra)

Research/POC - requires clear scope and deliverables.

```yaml
investigation:
  type_id: "Investigation"
  title_format:
    internal: "[INV] {ja_summary} -- {vn_summary}"
    customer: "[調査] {ja_summary}"

  description_structure:
    required:
      - objective        # 調査目的 / Muc dich dieu tra
      - scope            # 調査範囲 / Pham vi dieu tra
      - deliverables     # 成果物 / San pham giao
    optional:
      - constraints      # 制約 / Rang buoc
      - assumptions      # 前提 / Gia dinh
      - findings         # 調査結果 / Ket qua (filled later)
      - recommendation   # 推奨 / De xuat (filled later)

  required_fields:
    - summary
    - issue_type_id
    - priority_id
    - estimated_hours   # Investigation must be time-boxed
    - description

  optional_fields:
    - assignee_id
    - due_date

  auto_fill_logic:
    priority: "normal"
    estimated_hours: "time_box_default"  # Default 4-8 hours

  # Investigation type detection
  investigation_types:
    "技術調査|technical": "technical_spike"
    "POC|プロトタイプ|proof": "poc"
    "パフォーマンス|性能": "performance_analysis"
    "セキュリティ|脆弱性": "security_audit"
    "競合|市場": "market_research"

  detection_keywords:
    ja: ["調査", "検証", "POC", "スパイク", "確認", "評価"]
    vn: ["dieu tra", "nghien cuu", "POC", "kiem tra", "danh gia"]
    en: ["investigation", "research", "POC", "spike", "evaluate", "analyze"]

  example:
    input: |
      技術調査：Redis vs Memcached のパフォーマンス比較
      目的：キャッシュ基盤選定
      期限：2日以内
      成果物：比較レポート
    output:
      title: "[INV] キャッシュ基盤選定調査 -- Nghien cuu lua chon cache"
      priority: "normal"
      estimated_hours: 8  # Time-boxed
      due_date: "2026-01-31"  # 2 days
      description: |
        ## 調査目的 / Muc dich dieu tra
        キャッシュ基盤（Redis vs Memcached）の選定

        ## 調査範囲 / Pham vi dieu tra
        - パフォーマンス比較
        - 運用コスト比較
        - 機能比較

        ## 成果物 / San pham giao
        - 比較レポート（Markdown）
        - 推奨案

        ## 制約 / Rang buoc
        - タイムボックス: 8時間
        - 本番環境での検証は不可
```

---

## Workflow Integration

### Waterfall Flow Templates

```yaml
waterfall_workflow:
  # When WBS or Spec is provided
  trigger: "WBS|仕様書|spec"

  flow:
    1_requirements:
      parent_task:
        type: "Task"
        title: "{feature}/要件定義 -- Requirements"
      subtasks:
        - "要件定義/ヒアリング -- Hearing"
        - "要件定義/要件定義書作成 -- Tao file spec"
        - "要件定義/要件定義書レビュー -- Review spec"

    2_development:
      parent_task:
        type: "Task"
        title: "{feature}/開発 -- Development"
      subtasks:
        - "開発/開発 -- Coding"
        - "開発/テストケース作成 -- Tao test case"
        - "開発/テスト -- Execute test"
        - "開発/テスト後の修正 -- Fix bug"
        - "開発/UAT -- UAT"

    3_release:
      parent_task:
        type: "Task"
        title: "{feature}/リリース -- Release"
      subtasks:
        - "リリース判定/マニュアル作成 -- User manual"
        - "リリース判定/リリース判定 -- Release approval"
```

### Ad-hoc Flow Templates

```yaml
adhoc_workflow:
  # When customer request or meeting minutes

  customer_request:
    trigger: "お客様から|customer|依頼"
    default_type: "Task"
    title_format: "{ja_summary} -- {vn_summary}"
    auto_fields:
      priority: "detect_from_urgency"
      due_date: "detect_from_text"

  meeting_minutes:
    trigger: "議事録|MTG|meeting|宿題"
    # Parse action items section
    action_item_pattern: "^[・•\-]\s*([^：:]+)[：:]\s*(.+)$"
    # Format: ・田中：ログイン機能の仕様書作成（1/30まで）
    extract:
      - assignee: "$1"
      - task: "$2"
      - deadline: "detect_from_parenthesis"
```

---

## Configuration Schema for project-master.yaml

```yaml
# Add to brsekit/master.yaml
issue_types:
  # Issue type definitions with Backlog IDs
  # These IDs must be fetched from Backlog API for each project
  definitions:
    - name: "Task"
      ja: "タスク"
      vn: "Cong viec"
      default: true
    - name: "Subtask"
      ja: "子課題"
      vn: "Subtask"
      requires_parent: true
    - name: "Bug"
      ja: "不具合"
      vn: "Loi"
      auto_priority: "high"
    - name: "Risk"
      ja: "リスク"
      vn: "Rui ro"
    - name: "UserFeedback"
      ja: "ユーザーフィードバック"
      vn: "Phan hoi nguoi dung"
    - name: "Question"
      ja: "質問"
      vn: "Cau hoi"
    - name: "ChangeRequest"
      ja: "変更要求"
      vn: "Yeu cau thay doi"
    - name: "Investigation"
      ja: "調査"
      vn: "Dieu tra"

  # Title format settings
  title_format:
    internal_separator: " -- "
    customer_format: "ja_only"
    max_length: 100

  # Description templates per type (file paths)
  templates:
    task: "templates/task.md"
    subtask: "templates/subtask.md"
    bug: "templates/bug.md"
    risk: "templates/risk.md"
    feedback: "templates/feedback.md"
    question: "templates/question.md"
    change_request: "templates/change_request.md"
    investigation: "templates/investigation.md"
```

---

## Detection Algorithm

```python
# Priority order for type detection
TYPE_DETECTION_ORDER = [
    "Bug",            # Check first - error keywords are critical
    "Risk",           # Risk keywords next
    "ChangeRequest",  # Change/scope keywords
    "Question",       # Question keywords
    "UserFeedback",   # Feedback keywords
    "Investigation",  # Research keywords
    "Subtask",        # Only if parent specified
    "Task",           # Default fallback
]

def detect_issue_type(text: str, has_parent: bool = False) -> str:
    """Detect issue type from text content."""
    text_lower = text.lower()

    # Check each type in priority order
    for type_name in TYPE_DETECTION_ORDER:
        template = TEMPLATES[type_name]
        for lang in ['ja', 'vn', 'en']:
            for keyword in template['detection_keywords'].get(lang, []):
                if keyword.lower() in text_lower:
                    # Special case: Subtask only if has_parent
                    if type_name == "Subtask" and not has_parent:
                        continue
                    return type_name

    return "Task"  # Default
```

---

## Implementation Considerations

1. **API Integration**: Issue type IDs vary by project. Must fetch from `/api/v2/projects/{projectKey}/issueTypes` on first use.

2. **Title Length**: Backlog has 100 char limit. Truncate VN portion if needed.

3. **Description Markdown**: Backlog supports limited markdown. Test rendering.

4. **Custom Fields**: Some types (Risk, Feedback) may use custom fields. Check project settings.

5. **Validation**: Before create, validate all required fields present.

---

## Success Metrics

- Parse accuracy > 90% on mixed VN-JA input
- Type detection accuracy > 85%
- User approval rate on first parse > 80%
- Time to create issue < 30 seconds

---

## Unresolved Questions

1. **Custom field mapping**: How to handle projects with different custom field configurations?
2. **Template versioning**: Should templates be versioned per project or global?
3. **Subtask auto-creation**: Should waterfall workflow auto-create all subtasks or prompt for each?
4. **Translation accuracy**: Use AI translation or predefined dictionary for JA-VN?
5. **Backlog issue type IDs**: Store in master.yaml or fetch dynamically?

---

## Sources

- [Nulab Backlog API - Get Issue Type List](https://developer.nulab.com/docs/backlog/api/2/get-issue-type-list/)
- [Nulab Backlog API - Add Issue](https://developer.nulab.com/docs/backlog/api/2/add-issue/)
- Existing `feature-dev.json` template structure
- Current `task_parser.py` implementation

---

## Next Steps

1. Review templates with team
2. Validate against real Backlog project issue types
3. Decide on unresolved questions
4. Create implementation plan if approved

**Create detailed implementation plan?** [Yes/No]
