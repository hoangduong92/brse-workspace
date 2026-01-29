# BK-Task Bilingual Templates Specification

**Report ID:** brainstormer-260129-1206-bk-task-bilingual-templates
**Date:** 2026-01-29
**Context:** VN-JA development team templates for bk-task skill

---

## Overview

Templates for 6 task types with bilingual (Vietnamese-Japanese) support:
1. Task (Standard work item)
2. Subtask (Child task with parent reference)
3. Bug (3 sub-types: Internal, UAT, PROD)
4. Risk (Project risk with mitigation)
5. Issue (Operational/Process problems)
6. User Feedback (Kaizen/improvement suggestions)

---

## 1. Task (タスク/Công việc)

### Title Format
```
[TASK] {Action} {Target} -- {Action_JA} {Target_JA}
```

### Detection Keywords
| Language | Keywords |
|----------|----------|
| JA | 作成, 実装, 対応, 開発, 設計, タスク, 機能 |
| VN | tạo, làm, phát triển, thiết kế, task, chức năng |
| EN | implement, create, develop, task, feature |

### Fields Mapping
| Field | Backlog Field | Type |
|-------|---------------|------|
| Summary | summary | Required |
| Assignee | assigneeId | Optional |
| Due Date | dueDate | Optional |
| Estimate | estimatedHours | Optional |
| Priority | priorityId | Default: Normal |
| Description | description | Optional |

### Template

```markdown
## [TASK] {Summary_VN} -- {Summary_JA}

### Mô tả (説明)
{Description in VN}

{Description in JA}

### Tiêu chí hoàn thành (完了基準)
- [ ] {Criterion 1}
- [ ] {Criterion 2}

### Ghi chú (備考)
- {Notes}
```

### Sample: API Integration Task

**Title:**
```
[TASK] Tích hợp API thanh toán VNPay -- VNPay決済API連携実装
```

**Description:**
```markdown
## [TASK] Tích hợp API thanh toán VNPay -- VNPay決済API連携実装

### Mô tả (説明)
Tích hợp VNPay payment gateway vào hệ thống e-commerce.
Bao gồm: sandbox testing, production setup, webhook handling.

VNPay決済ゲートウェイをeコマースシステムに連携する。
サンドボックステスト、本番設定、Webhook処理を含む。

### Tiêu chí hoàn thành (完了基準)
- [ ] Sandbox environment tested / サンドボックス環境テスト完了
- [ ] Webhook endpoint implemented / Webhookエンドポイント実装
- [ ] Error handling for failed payments / 決済失敗時のエラー処理
- [ ] Documentation updated / ドキュメント更新

### Ghi chú (備考)
- VNPay sandbox credentials in .env.example
- Reference: VNPay API docs v2.1
```

---

## 2. Subtask (子課題/Công việc con)

### Title Format
```
[SUBTASK] {Action} {Target} -- {Action_JA} {Target_JA}
```

### Detection Keywords
| Language | Keywords |
|----------|----------|
| JA | 子課題, サブタスク, 細分化, 分割 |
| VN | subtask, công việc con, task con |
| EN | subtask, child task, sub-task |

### Fields Mapping
| Field | Backlog Field | Type |
|-------|---------------|------|
| Summary | summary | Required |
| Parent Issue | parentIssueId | Required |
| Assignee | assigneeId | Optional |
| Due Date | dueDate | Optional |
| Estimate | estimatedHours | Optional |

### Template

```markdown
## [SUBTASK] {Summary_VN} -- {Summary_JA}

### Parent Issue (親課題)
- Key: {PROJ-XXX}
- Title: {Parent Title}

### Mô tả (説明)
{Description}

### Phạm vi công việc (作業範囲)
- {Scope item 1}
- {Scope item 2}
```

### Sample: Database Migration Subtask

**Title:**
```
[SUBTASK] Tạo migration cho bảng users -- usersテーブルのマイグレーション作成
```

**Description:**
```markdown
## [SUBTASK] Tạo migration cho bảng users -- usersテーブルのマイグレーション作成

### Parent Issue (親課題)
- Key: PROJ-142
- Title: [TASK] User Authentication Module -- ユーザー認証モジュール

### Mô tả (説明)
Tạo Prisma migration thêm các trường mới cho bảng users:
- phone_number (optional)
- last_login_at
- login_count

Prismaマイグレーションを作成し、usersテーブルに新フィールドを追加：
- phone_number（任意）
- last_login_at
- login_count

### Phạm vi công việc (作業範囲)
- Create migration file / マイグレーションファイル作成
- Update Prisma schema / Prismaスキーマ更新
- Run migration on dev environment / 開発環境でマイグレーション実行
```

---

## 3. Bug (不具合/Lỗi)

### Bug Sub-Types

| Sub-Type | Prefix | Japanese | Vietnamese | Found By |
|----------|--------|----------|------------|----------|
| Internal | [BUG-INT] | 内部不具合 | Lỗi nội bộ | Tester (QA team) |
| UAT | [BUG-UAT] | UAT不具合 | Lỗi UAT | Customer (during UAT) |
| PROD | [BUG-PROD] | 本番不具合 | Lỗi production | End-client (live system) |

### Title Format
```
[BUG-{TYPE}] {Symptom_VN} -- {Symptom_JA}
```

### Detection Keywords
| Language | Keywords |
|----------|----------|
| JA | 不具合, バグ, エラー, 障害, 動かない, 表示されない, 消失, 問題 |
| VN | lỗi, bug, error, không hoạt động, không hiển thị, mất dữ liệu |
| EN | bug, error, defect, not working, broken, crash |

### Bug Type Detection
| Keywords | Sub-Type |
|----------|----------|
| テスター, QA, 内部テスト, kiểm thử nội bộ | Internal |
| UAT, 顧客テスト, 受入テスト, khách hàng test | UAT |
| 本番, 本番環境, production, PROD, live | PROD |

### Priority Auto-Escalation
| Sub-Type | Default Priority |
|----------|------------------|
| Internal | Normal |
| UAT | High |
| PROD | High (Critical) |

### Fields Mapping
| Field | Backlog Field | Type |
|-------|---------------|------|
| Summary | summary | Required |
| Bug Type | category / customField | Required |
| Environment | customField_env | Required |
| Steps to Reproduce | description | Required |
| Priority | priorityId | Auto-set by type |
| Severity | customField_severity | Optional |

### Template

```markdown
## [BUG-{TYPE}] {Summary_VN} -- {Summary_JA}

### Phân loại (分類)
- Type: {Internal/UAT/PROD}
- Severity: {Critical/High/Medium/Low}
- Found by: {Name/Team}
- Found date: {YYYY-MM-DD}

### Môi trường (環境)
- Browser/Device: {Chrome 120 / iOS 17}
- OS: {Windows 11 / macOS}
- Environment: {dev/staging/production}
- Version: {v1.2.3}

### Hiện tượng (現象)
{VN: Mô tả hiện tượng}
{JA: 現象の説明}

### Các bước tái hiện (再現手順)
1. {Step 1}
2. {Step 2}
3. {Step 3}

### Kết quả mong đợi (期待結果)
{Expected behavior}

### Kết quả thực tế (実際の結果)
{Actual behavior}

### Evidence
- Screenshot: {link}
- Log: {link}
- Video: {link}

### Nguyên nhân (原因) -- After investigation
{Root cause analysis}

### Giải pháp (解決策) -- After fix
{Solution implemented}
```

### Sample A: Internal Bug (QA Found)

**Title:**
```
[BUG-INT] Form validation không hoạt động trên Safari -- Safariでフォームバリデーションが動作しない
```

**Description:**
```markdown
## [BUG-INT] Form validation không hoạt động trên Safari -- Safariでフォームバリデーションが動作しない

### Phân loại (分類)
- Type: Internal (内部不具合)
- Severity: Medium
- Found by: QA Team - Minh
- Found date: 2026-01-28

### Môi trường (環境)
- Browser: Safari 17.2
- OS: macOS Sonoma 14.2
- Environment: staging
- Version: v2.1.0-beta

### Hiện tượng (現象)
Form đăng ký user không hiển thị lỗi validation khi email format sai trên Safari.
Chrome và Firefox hoạt động bình thường.

ユーザー登録フォームで、メールフォーマットが間違っている場合、
Safariでバリデーションエラーが表示されない。
ChromeとFirefoxは正常に動作。

### Các bước tái hiện (再現手順)
1. Mở trang /register trên Safari / Safariで/registerページを開く
2. Nhập email sai format "test@" / 不正なフォーマット"test@"を入力
3. Click "Register" button / 「登録」ボタンをクリック
4. Không hiển thị error message / エラーメッセージが表示されない

### Kết quả mong đợi (期待結果)
Error message: "Please enter valid email" hiển thị dưới input field.
エラーメッセージ「有効なメールアドレスを入力してください」がinputの下に表示される。

### Kết quả thực tế (実際の結果)
Không có error message, form submit bình thường và API trả về 400.
エラーメッセージなし、フォーム送信され、APIが400を返す。

### Evidence
- Screenshot: /attachments/safari-validation-bug.png
- Console log: No JS errors
```

### Sample B: UAT Bug (Customer Found)

**Title:**
```
[BUG-UAT] Export CSV bị lỗi ký tự tiếng Nhật -- CSV出力で日本語が文字化け
```

**Description:**
```markdown
## [BUG-UAT] Export CSV bị lỗi ký tự tiếng Nhật -- CSV出力で日本語が文字化け

### Phân loại (分類)
- Type: UAT (UAT不具合)
- Severity: High
- Found by: Customer - Tanaka-san (田中様)
- Found date: 2026-01-27
- UAT Round: 2

### Môi trường (環境)
- Browser: Edge 120
- OS: Windows 11
- Environment: UAT (uat.example.com)
- Version: v2.0.0-rc1

### Hiện tượng (現象)
Khi export danh sách user ra CSV, các ký tự tiếng Nhật bị lỗi (mojibake).
Customer không thể đọc được file khi mở bằng Excel.

ユーザー一覧をCSVエクスポートすると、日本語が文字化けする。
お客様がExcelでファイルを開くと読めない状態。

### Các bước tái hiện (再現手順)
1. Login với account admin / 管理者アカウントでログイン
2. Vào trang /admin/users / /admin/usersページへ移動
3. Click "Export CSV" / 「CSVエクスポート」をクリック
4. Mở file bằng Excel / ファイルをExcelで開く
5. Ký tự Nhật bị lỗi / 日本語が文字化け

### Kết quả mong đợi (期待結果)
CSV file hiển thị đúng tiếng Nhật khi mở bằng Excel Windows.
CSVファイルをWindows Excelで開くと日本語が正しく表示される。

### Kết quả thực tế (実際の結果)
Ký tự tiếng Nhật bị chuyển thành "縺ゅ>縺・∴縺".
日本語が「縺ゅ>縺・∴縺」のように文字化け。

### Evidence
- Screenshot: /attachments/csv-mojibake.png
- Sample CSV: /attachments/export-sample.csv

### Nguyên nhân (原因)
CSV export đang sử dụng UTF-8 without BOM.
Excel Windows cần UTF-8 with BOM để đọc đúng tiếng Nhật.

CSVエクスポートがBOMなしUTF-8を使用。
Windows ExcelはBOM付きUTF-8が必要。

### Giải pháp (解決策)
Thêm BOM (0xEF, 0xBB, 0xBF) vào đầu file CSV.
CSVファイルの先頭にBOM（0xEF, 0xBB, 0xBF）を追加。
```

### Sample C: Production Bug (End-Client Found)

**Title:**
```
[BUG-PROD] KHẨN CẤP: Mất dữ liệu đơn hàng sau khi thanh toán -- 緊急：決済後に注文データが消失
```

**Description:**
```markdown
## [BUG-PROD] KHẨN CẤP: Mất dữ liệu đơn hàng sau khi thanh toán -- 緊急：決済後に注文データが消失

### Phân loại (分類)
- Type: PROD (本番不具合)
- Severity: CRITICAL
- Found by: End-client via Support Ticket #4521
- Found date: 2026-01-29 09:15 JST
- Affected users: ~15 orders (estimated)

### Môi trường (環境)
- Environment: Production (app.example.com)
- Version: v2.1.0
- Time range: 2026-01-29 08:00-09:30 JST

### Hiện tượng (現象)
Sau khi thanh toán thành công qua VNPay, một số đơn hàng không được lưu vào database.
Khách hàng bị trừ tiền nhưng không nhận được confirmation email.

VNPay決済成功後、一部の注文がデータベースに保存されない。
お客様は課金されたが、確認メールが届かない状態。

### Các bước tái hiện (再現手順)
1. User thanh toán đơn hàng / ユーザーが注文を決済
2. VNPay redirect về callback URL / VNPayがコールバックURLにリダイレクト
3. Callback timeout (>30s) / コールバックがタイムアウト（30秒超）
4. Order không được tạo / 注文が作成されない
5. VNPay đã trừ tiền thành công / VNPayは課金成功

### Kết quả mong đợi (期待結果)
Đơn hàng được tạo và confirmation email gửi cho khách hàng.
注文が作成され、確認メールがお客様に送信される。

### Kết quả thực tế (実際の結果)
Đơn hàng không tồn tại trong system nhưng tiền đã bị trừ.
注文がシステムに存在しないが、課金は完了している。

### Evidence
- VNPay transaction logs: /logs/vnpay-2026-01-29.log
- Error log: "Database connection timeout at order_service.create()"
- Affected order IDs: [Check VNPay dashboard]

### IMMEDIATE ACTIONS (即時対応)
1. [x] Notify affected customers / 影響を受けたお客様に通知
2. [x] Manual order creation for affected users / 影響ユーザーの注文を手動作成
3. [ ] Root cause investigation / 根本原因調査
4. [ ] Hotfix deployment / ホットフィックスデプロイ

### Nguyên nhân (原因)
Database connection pool exhausted do concurrent requests cao.
Connection pool max = 10, peak requests = 50/min.

同時リクエスト過多によりDBコネクションプールが枯渇。
コネクションプール上限=10、ピークリクエスト=50/分。

### Giải pháp (解決策)
1. Tăng connection pool lên 30 / コネクションプールを30に増加
2. Implement retry logic cho DB operations / DB操作にリトライロジック実装
3. Add VNPay webhook queue (Redis) / VNPay webhookキュー追加（Redis）
```

---

## 4. Risk (リスク/Rủi ro)

### Title Format
```
[RISK] {Risk_VN} -- {Risk_JA}
```

### Detection Keywords
| Language | Keywords |
|----------|----------|
| JA | リスク, 懸念, 可能性, 恐れ, 危険, 影響 |
| VN | rủi ro, nguy cơ, khả năng, ảnh hưởng, lo ngại |
| EN | risk, concern, possibility, potential issue |

### Impact Levels
| Level | Japanese | Vietnamese |
|-------|----------|------------|
| Critical | 致命的 | Nghiêm trọng |
| High | 高 | Cao |
| Medium | 中 | Trung bình |
| Low | 低 | Thấp |

### Probability Levels
| Level | Japanese | Vietnamese |
|-------|----------|------------|
| Very Likely | 非常に高い | Rất cao |
| Likely | 高い | Cao |
| Possible | 可能性あり | Có khả năng |
| Unlikely | 低い | Thấp |

### Fields Mapping
| Field | Backlog Field | Type |
|-------|---------------|------|
| Summary | summary | Required |
| Impact | customField_impact | Required |
| Probability | customField_probability | Required |
| Mitigation | description | Required |
| Owner | assigneeId | Required |
| Review Date | dueDate | Required |

### Template

```markdown
## [RISK] {Summary_VN} -- {Summary_JA}

### Đánh giá (評価)
| Factor | Level |
|--------|-------|
| Impact (影響度) | {Critical/High/Medium/Low} |
| Probability (発生確率) | {Very Likely/Likely/Possible/Unlikely} |
| Risk Score | {Impact x Probability} |

### Mô tả rủi ro (リスク説明)
{VN description}

{JA description}

### Nguyên nhân tiềm ẩn (潜在的な原因)
- {Cause 1}
- {Cause 2}

### Ảnh hưởng (影響)
- {Impact on schedule}
- {Impact on cost}
- {Impact on quality}

### Kế hoạch giảm thiểu (軽減策)
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| {Action 1} | {Name} | {Date} | {Pending/Done} |

### Kế hoạch dự phòng (コンティンジェンシープラン)
{If risk occurs, what actions will be taken}

### Ngày review tiếp theo (次回レビュー日)
{YYYY-MM-DD}
```

### Sample: Resource Risk

**Title:**
```
[RISK] 2 thành viên nghỉ phép cùng lúc tháng 2 -- 2月に2名が同時休暇によるリソース不足
```

**Description:**
```markdown
## [RISK] 2 thành viên nghỉ phép cùng lúc tháng 2 -- 2月に2名が同時休暇によるリソース不足

### Đánh giá (評価)
| Factor | Level |
|--------|-------|
| Impact (影響度) | High / 高 |
| Probability (発生確率) | Very Likely / 非常に高い (đã xác nhận nghỉ / 休暇確定済み) |
| Risk Score | High |

### Mô tả rủi ro (リスク説明)
Nguyên (Backend Lead) và Minh (Frontend) đã đăng ký nghỉ phép:
- Nguyên: 2026-02-10 ~ 2026-02-14 (Tết holiday)
- Minh: 2026-02-08 ~ 2026-02-12 (Personal)

Overlap 3 ngày (02/10-12) không có senior dev.
Sprint 5 deadline: 2026-02-15.

阮さん（バックエンドリード）と明さん（フロントエンド）が休暇申請済み：
- 阮さん：2026-02-10～2026-02-14（テト休暇）
- 明さん：2026-02-08～2026-02-12（私用）

3日間（02/10-12）シニア開発者不在。
スプリント5締切：2026-02-15。

### Nguyên nhân tiềm ẩn (潜在的な原因)
- Tết holiday period (peak leave season) / テト休暇期間（休暇集中時期）
- No leave coordination policy / 休暇調整ポリシーなし

### Ảnh hưởng (影響)
- Schedule: Sprint 5 có thể delay 3-5 ngày / スプリント5が3-5日遅延の可能性
- Quality: Code review bị delay, technical decisions bị pending / コードレビュー遅延、技術判断保留
- Cost: Overtime sau Tết để catch up / テト後の残業でキャッチアップ

### Kế hoạch giảm thiểu (軽減策)
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| Front-load critical tasks trước 02/08 | Nguyên | 02/05 | In Progress |
| Handover doc cho Tuấn (backup) | Nguyên | 02/07 | Pending |
| Pre-review code trước khi nghỉ | Minh | 02/07 | Pending |
| Shift Sprint 5 deadline to 02/18 | PM - Lan | 02/01 | Approved |

### Kế hoạch dự phòng (コンティンジェンシープラン)
Nếu có blocker critical trong 02/10-12:
- Nguyên có thể support remote 2h/ngày (đã đồng ý)
- Escalate lên Tech Lead Japan (Tanaka-san)

02/10-12にクリティカルブロッカーが発生した場合：
- 阮さんが1日2時間リモートサポート可能（同意済み）
- 日本側テックリード（田中さん）にエスカレーション

### Ngày review tiếp theo (次回レビュー日)
2026-02-07 (trước khi Minh nghỉ / 明さん休暇前)
```

---

## 5. Issue (問題/Vấn đề vận hành) - NEW

### Title Format
```
[ISSUE] {Issue_VN} -- {Issue_JA}
```

### Issue vs Bug Distinction
| Aspect | Bug | Issue |
|--------|-----|-------|
| Nature | App behavior != spec | Process/Operational problem |
| Examples | Login error, data loss | BA skill gap, effort shortage |
| Fix | Code change | Process change, training, hiring |
| Owner | Developer | PM, Team Lead |

### Detection Keywords
| Language | Keywords |
|----------|----------|
| JA | 問題, 課題, 障壁, 遅延, 不足, スキル不足, コミュニケーション問題 |
| VN | vấn đề, thiếu người, thiếu kỹ năng, chậm tiến độ, gặp khó khăn |
| EN | issue, problem, shortage, skill gap, delay, blocker, impediment |

### Issue Categories
| Category | Japanese | Vietnamese | Examples |
|----------|----------|------------|----------|
| Resource | リソース不足 | Thiếu nguồn lực | 2 people on leave, hiring delay |
| Skill | スキル不足 | Thiếu kỹ năng | BA cannot write specs, dev new to tech |
| Communication | コミュニケーション | Giao tiếp | Unclear requirements, timezone issues |
| Process | プロセス | Quy trình | No code review, no testing env |
| External | 外部依存 | Phụ thuộc bên ngoài | Client delay, 3rd party API down |

### Fields Mapping
| Field | Backlog Field | Type |
|-------|---------------|------|
| Summary | summary | Required |
| Category | customField_issue_category | Required |
| Impact | description | Required |
| Resolution | description | Required |
| Owner | assigneeId | Required |
| Status | statusId | Required |

### Template

```markdown
## [ISSUE] {Summary_VN} -- {Summary_JA}

### Phân loại vấn đề (問題分類)
- Category: {Resource/Skill/Communication/Process/External}
- Severity: {Critical/High/Medium/Low}
- Status: {Open/In Progress/Resolved/Closed}

### Mô tả vấn đề (問題説明)
{VN description}

{JA description}

### Ảnh hưởng hiện tại (現在の影響)
- {Impact 1}
- {Impact 2}

### Nguyên nhân gốc (根本原因)
{Root cause analysis}

### Giải pháp đề xuất (提案する解決策)
| Option | Pros | Cons | Effort |
|--------|------|------|--------|
| {Option A} | {Pros} | {Cons} | {Days/Cost} |
| {Option B} | {Pros} | {Cons} | {Days/Cost} |

### Giải pháp đã chọn (選択した解決策)
{Selected solution and rationale}

### Action Items
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| {Action 1} | {Name} | {Date} | {Status} |

### Follow-up
- Review date: {YYYY-MM-DD}
- Success criteria: {How to measure resolution}
```

### Sample A: BA Skill Gap Issue

**Title:**
```
[ISSUE] BA thiếu kỹ năng viết requirement cho RPA -- BAがRPA要件定義スキル不足
```

**Description:**
```markdown
## [ISSUE] BA thiếu kỹ năng viết requirement cho RPA -- BAがRPA要件定義スキル不足

### Phân loại vấn đề (問題分類)
- Category: Skill (スキル不足)
- Severity: High
- Status: In Progress
- Discovered: 2026-01-25

### Mô tả vấn đề (問題説明)
BA Linh chưa có kinh nghiệm viết requirement cho dự án RPA.
Spec document hiện tại thiếu:
- Chi tiết về exception handling
- Business rules cho edge cases
- Performance requirements

BA Linhさんは RPA プロジェクトの要件定義経験がない。
現在の仕様書に不足：
- 例外処理の詳細
- エッジケースのビジネスルール
- パフォーマンス要件

### Ảnh hưởng hiện tại (現在の影響)
- Dev team phải hỏi lại nhiều lần / 開発チームが何度も確認が必要
- RPA workflow delay 1 week / RPAワークフロー1週間遅延
- Quality concern for Phase 2 / フェーズ2の品質懸念

### Nguyên nhân gốc (根本原因)
- Linh mới chuyển từ Web project sang RPA / LinhさんがWebプロジェクトからRPAに異動
- Không có training trước khi bắt đầu dự án / プロジェクト開始前のトレーニングなし
- RPA spec template chưa có / RPAスペックテンプレートなし

### Giải pháp đề xuất (提案する解決策)
| Option | Pros | Cons | Effort |
|--------|------|------|--------|
| A: Pair với BA Japan 2 tuần | Fast knowledge transfer | Tanaka-san busy | 2 weeks |
| B: Hire contract BA có RPA exp | Expert quality | Cost, onboarding | 1 month |
| C: Internal RPA training course | Long-term benefit | Slow, delay current | 3 weeks |

### Giải pháp đã chọn (選択した解決策)
Option A: Pair Linh với Tanaka-san 2 tuần.
- Daily 1h sync call (10:00 VN / 12:00 JP)
- Tanaka-san review spec documents
- Create RPA spec template together

オプションA：Linhさんと田中さんのペアワーク2週間
- 毎日1時間の同期コール（VN 10:00 / JP 12:00）
- 田中さんが仕様書レビュー
- RPAスペックテンプレートを共同作成

### Action Items
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| Setup daily sync call schedule | PM Lan | 01/30 | Done |
| Share current spec docs | Linh | 01/30 | Done |
| First review session | Tanaka | 01/31 | Pending |
| Create RPA spec template v1 | Linh + Tanaka | 02/07 | Pending |
| Linh solo write Phase 2 spec | Linh | 02/14 | Pending |

### Follow-up
- Review date: 2026-02-07
- Success criteria:
  - Linh có thể viết RPA spec độc lập
  - Dev team hỏi lại < 2 lần/spec
  - 開発チームの質問が仕様書あたり2回未満
```

### Sample B: Resource Shortage Issue

**Title:**
```
[ISSUE] Thiếu effort do 2 người nghỉ ốm đột xuất -- 2名の急な病欠によるリソース不足
```

**Description:**
```markdown
## [ISSUE] Thiếu effort do 2 người nghỉ ốm đột xuất -- 2名の急な病欠によるリソース不足

### Phân loại vấn đề (問題分類)
- Category: Resource (リソース不足)
- Severity: Critical
- Status: Open
- Discovered: 2026-01-29 08:30

### Mô tả vấn đề (問題説明)
2 developer (Tuấn và Hoa) báo ốm sáng nay:
- Tuấn: Covid, dự kiến nghỉ 5-7 ngày
- Hoa: Sốt xuất huyết, dự kiến nghỉ 7-10 ngày

Team hiện tại còn 3 dev, Sprint deadline 02/05.

2名の開発者（TuanさんとHoaさん）が本日病欠：
- Tuanさん：コロナ、5-7日休みの見込み
- Hoaさん：デング熱、7-10日休みの見込み

現在チームは開発者3名、スプリント締切は02/05。

### Ảnh hưởng hiện tại (現在の影響)
- Capacity giảm 40% (2/5 dev) / キャパシティ40%減（5名中2名）
- 3 tasks đang assign cho Tuấn/Hoa / Tuan/Hoaに3タスクがアサイン済み
  - PROJ-201: API pagination (Tuấn, 8h remaining)
  - PROJ-205: Email template (Hoa, 4h remaining)
  - PROJ-208: Dashboard chart (Hoa, 6h remaining)
- Sprint 5 có nguy cơ fail / スプリント5が失敗のリスク

### Nguyên nhân gốc (根本原因)
- Mùa dịch bệnh (Covid + Dengue season) / 疫病シーズン
- Không có backup plan cho sudden absence / 急な欠勤のバックアッププランなし
- Tasks không có documentation để handover / タスクにハンドオーバー用ドキュメントなし

### Giải pháp đề xuất (提案する解決策)
| Option | Pros | Cons | Effort |
|--------|------|------|--------|
| A: Re-prioritize & cut scope | Fast, no extra cost | Features delay | 1 day |
| B: OT cho 3 dev còn lại | Keep deadline | Burnout risk, quality | - |
| C: Request support từ team khác | Extra capacity | Onboarding time | 2-3 days |
| D: Extend sprint deadline | Realistic | Client expectation | Need approval |

### Giải pháp đã chọn (選択した解決策)
Combination of A + D:
1. Cut PROJ-208 (Dashboard chart) - move to Sprint 6 / スプリント6に移動
2. Extend deadline 3 ngày (02/05 -> 02/08) / 締切を3日延長
3. Redistribute PROJ-201, PROJ-205 to remaining devs / 残りの開発者に再配分

A + D の組み合わせ:
1. PROJ-208をスプリント6に移動
2. 締切を3日延長（02/05 → 02/08）
3. PROJ-201、PROJ-205を残りの開発者に再配分

### Action Items
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| Inform client about delay | PM Lan | 01/29 12:00 | In Progress |
| Update sprint backlog | Scrum Master | 01/29 14:00 | Pending |
| Reassign PROJ-201 to Khánh | Tech Lead | 01/29 14:00 | Pending |
| Reassign PROJ-205 to Đức | Tech Lead | 01/29 14:00 | Pending |
| Daily health check-in with team | PM Lan | Daily | Ongoing |

### Follow-up
- Review date: 2026-01-31
- Success criteria:
  - Sprint complete by 02/08 with reduced scope
  - No additional sick leaves
  - Tuấn/Hoa recovery updates daily
```

---

## 6. User Feedback (ユーザーフィードバック/Phản hồi người dùng)

### Title Format
```
[FEEDBACK] {Feedback_VN} -- {Feedback_JA}
```

### Feedback Types
| Type | Japanese | Vietnamese | Action |
|------|----------|------------|--------|
| Kaizen | 改善提案 | Đề xuất cải tiến | Evaluate for backlog |
| Bug Report | 不具合報告 | Báo lỗi | Convert to Bug |
| Feature Request | 機能要望 | Yêu cầu tính năng | Evaluate for roadmap |
| Complaint | 苦情 | Khiếu nại | Investigate & respond |
| Praise | 称賛 | Khen ngợi | Share with team |

### Detection Keywords
| Language | Keywords |
|----------|----------|
| JA | フィードバック, 改善, 提案, 要望, ご意見, 使いにくい, 便利 |
| VN | phản hồi, góp ý, đề xuất, yêu cầu, ý kiến, khó sử dụng, tiện lợi |
| EN | feedback, suggestion, improvement, request, kaizen, UX |

### Fields Mapping
| Field | Backlog Field | Type |
|-------|---------------|------|
| Summary | summary | Required |
| Feedback Type | customField_feedback_type | Required |
| Source | customField_source | Required |
| Priority | priorityId | Auto (based on impact) |
| Action | description | Required |

### Template

```markdown
## [FEEDBACK] {Summary_VN} -- {Summary_JA}

### Thông tin nguồn (ソース情報)
- Feedback Type: {Kaizen/Bug Report/Feature Request/Complaint/Praise}
- Source: {User name/email/ticket}
- Received: {YYYY-MM-DD}
- Channel: {Support ticket/Survey/Interview/App review}

### Nội dung phản hồi (フィードバック内容)
**Original (nguyên văn):**
> {Quote from user}

**Summary (tóm tắt):**
{VN summary}
{JA summary}

### Phân tích (分析)
- User type: {Admin/Regular user/Guest}
- Frequency: {One-time/Recurring}
- Impact scope: {Single user/Multiple users/All users}
- Related feature: {Feature name}

### Đánh giá (評価)
| Criteria | Score (1-5) | Notes |
|----------|-------------|-------|
| User impact | {Score} | {Notes} |
| Implementation effort | {Score} | {Notes} |
| Business value | {Score} | {Notes} |
| **Priority Score** | {Total/15} | |

### Quyết định (決定)
- Decision: {Accept/Reject/Defer/Need more info}
- Reason: {Rationale}
- Target release: {Version/Sprint}

### Action Items
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| {Action 1} | {Name} | {Date} | {Status} |

### Phản hồi cho user (ユーザーへの回答)
{Response message to send back to user}
```

### Sample A: Kaizen - Performance Improvement

**Title:**
```
[FEEDBACK] Kaizen: Trang dashboard load chậm quá -- 改善提案：ダッシュボードの読み込みが遅すぎる
```

**Description:**
```markdown
## [FEEDBACK] Kaizen: Trang dashboard load chậm quá -- 改善提案：ダッシュボードの読み込みが遅すぎる

### Thông tin nguồn (ソース情報)
- Feedback Type: Kaizen (改善提案)
- Source: Yamamoto-san (山本様), Admin user
- Received: 2026-01-28
- Channel: Support ticket #4498

### Nội dung phản hồi (フィードバック内容)
**Original (nguyên văn):**
> ダッシュボードページを開くたびに10秒以上かかります。
> 毎朝チェックするので、もう少し早くなると嬉しいです。
> グラフは後から読み込んでも大丈夫なので、まずテーブルを表示してほしいです。

**Summary (tóm tắt):**
User Yamamoto-san (admin) phản hồi dashboard load chậm ~10s.
Gợi ý: Load table trước, chart load sau (lazy load).
Sử dụng mỗi sáng nên ảnh hưởng UX hàng ngày.

山本様（管理者）からダッシュボード読み込み約10秒との報告。
提案：テーブルを先に表示、グラフは後読み込み（遅延読み込み）。
毎朝使用するため、日々のUXに影響。

### Phân tích (分析)
- User type: Admin (power user, daily usage)
- Frequency: Recurring (reported by 3 other users before)
- Impact scope: All admin users (~20 users)
- Related feature: Dashboard, Analytics charts

**Technical investigation:**
- Current load time: 8-12s (measured)
- Bottleneck: 4 API calls run sequentially
- Chart data: 3 heavy queries (2-3s each)
- Table data: 1 light query (0.5s)

### Đánh giá (評価)
| Criteria | Score (1-5) | Notes |
|----------|-------------|-------|
| User impact | 5 | Daily usage, 20 users affected |
| Implementation effort | 2 | Refactor to parallel + lazy load |
| Business value | 4 | Admin efficiency, reduce complaints |
| **Priority Score** | 11/15 | High priority |

### Quyết định (決定)
- Decision: Accept (採用)
- Reason: High impact, low effort, recurring feedback
- Target release: v2.2.0 (Sprint 6)

### Action Items
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| Create PROJ-215 for dashboard optimization | PM Lan | 01/29 | Done |
| Implement parallel API calls | Khánh | 02/10 | Pending |
| Add lazy loading for charts | Đức | 02/12 | Pending |
| Performance test (target <3s) | QA Minh | 02/14 | Pending |
| Notify Yamamoto-san when released | Support | 02/15 | Pending |

### Phản hồi cho user (ユーザーへの回答)
**Japanese:**
```
山本様

いつもご利用いただきありがとうございます。
ダッシュボードの読み込み速度についてのフィードバックを頂き、ありがとうございます。

ご提案いただいた通り、テーブルを先に表示し、グラフは後から読み込む改善を
バージョン2.2.0（2月中旬リリース予定）で対応いたします。

改善完了次第、ご連絡いたします。

引き続きよろしくお願いいたします。
```

**Vietnamese (internal):**
```
Đã nhận feedback và lên kế hoạch fix trong Sprint 6.
Target release: v2.2.0 (mid-Feb).
```
```

### Sample B: Feature Request

**Title:**
```
[FEEDBACK] Yêu cầu: Export báo cáo ra PDF -- 機能要望：レポートのPDFエクスポート
```

**Description:**
```markdown
## [FEEDBACK] Yêu cầu: Export báo cáo ra PDF -- 機能要望：レポートのPDFエクスポート

### Thông tin nguồn (ソース情報)
- Feedback Type: Feature Request (機能要望)
- Source: Multiple users (5 requests in Jan 2026)
- Received: 2026-01-15 ~ 2026-01-28
- Channel: Support tickets #4401, #4423, #4456, #4478, #4495

### Nội dung phản hồi (フィードバック内容)
**Original (nguyên văn):**
> [#4401] CSVだけでなく、PDFでも出力できると上司への報告がしやすいです。
> [#4456] 印刷用にPDFが欲しいです。グラフも含めて。
> [#4495] クライアントに送るためにPDFでエクスポートしたい。

**Summary (tóm tắt):**
5 user yêu cầu chức năng export báo cáo ra PDF.
Use cases: báo cáo cho sếp, in ấn, gửi cho client.
Hiện tại chỉ có CSV export.

5名のユーザーがレポートのPDFエクスポート機能を要望。
ユースケース：上司への報告、印刷、クライアントへの送付。
現在はCSVエクスポートのみ。

### Phân tích (分析)
- User type: Mixed (Admin, Regular users)
- Frequency: Recurring (5 requests in 1 month)
- Impact scope: Estimated 50+ users would benefit
- Related feature: Reports, Analytics

**Technical consideration:**
- Options: puppeteer (server-side), jspdf (client-side), pdf-lib
- Include charts: Need canvas/SVG to PDF conversion
- Estimated effort: 3-5 days

### Đánh giá (評価)
| Criteria | Score (1-5) | Notes |
|----------|-------------|-------|
| User impact | 4 | Multiple users, business reporting need |
| Implementation effort | 3 | Medium complexity, 3-5 days |
| Business value | 4 | Competitive feature, B2B value |
| **Priority Score** | 11/15 | High priority |

### Quyết định (決定)
- Decision: Accept (採用)
- Reason: Multiple requests, clear business value, reasonable effort
- Target release: v2.3.0 (Q1 2026)

### Action Items
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| Add to Q1 roadmap | PM Lan | 01/30 | Done |
| Technical spike for PDF library | Khánh | 02/15 | Pending |
| Design PDF template | UI/UX | 02/20 | Pending |
| Implementation | TBD | Sprint 8 | Pending |
| Reply to all requesters | Support | 01/30 | Pending |

### Phản hồi cho user (ユーザーへの回答)
**Japanese:**
```
お客様各位

レポートのPDFエクスポート機能のご要望ありがとうございます。

多くのお客様からご要望いただいており、2026年Q1（3月頃）の
リリースを目指して開発を進めております。

グラフを含むレポートの PDF エクスポートに対応予定です。
リリース時にはメールでお知らせいたします。

貴重なフィードバックをありがとうございました。
```
```

---

## Detection Keywords Summary

### Task Type Detection Matrix

| Type | JA Keywords | VN Keywords | EN Keywords |
|------|-------------|-------------|-------------|
| Task | タスク, 作成, 実装, 対応, 開発 | task, tạo, làm, phát triển | task, create, implement |
| Subtask | 子課題, サブタスク | subtask, task con | subtask, child |
| Bug-INT | 内部テスト, QA, テスター | kiểm thử nội bộ, QA | internal test, QA |
| Bug-UAT | UAT, 受入テスト, 顧客テスト | UAT, khách hàng test | UAT, acceptance test |
| Bug-PROD | 本番, 本番環境, 障害 | production, PROD, live | production, PROD, live |
| Risk | リスク, 懸念, 可能性 | rủi ro, nguy cơ | risk, concern |
| Issue | 問題, 課題, 不足, 障壁 | vấn đề, thiếu, gặp khó | issue, problem, shortage |
| Feedback | フィードバック, 改善, 要望 | phản hồi, góp ý, đề xuất | feedback, suggestion |

### Priority Auto-Detection

| Keyword Pattern | Priority |
|-----------------|----------|
| 緊急, 至急, ASAP, khẩn cấp | High |
| 本番, PROD, production | High (Bug only) |
| UAT, 顧客テスト | High (Bug only) |
| 通常, 今週中 | Normal |
| 余裕あれば, 時間あれば | Low |

---

## Implementation Recommendations

### 1. TaskType Enum Extension
```python
class TaskType(Enum):
    TASK = "task"
    SUBTASK = "subtask"
    BUG_INTERNAL = "bug_internal"
    BUG_UAT = "bug_uat"
    BUG_PROD = "bug_prod"
    RISK = "risk"
    ISSUE = "issue"
    FEEDBACK = "feedback"
```

### 2. Detection Order (Priority)
1. Bug PROD (highest priority - production incidents)
2. Bug UAT
3. Bug Internal
4. Risk
5. Issue
6. Feedback
7. Subtask (requires parent reference)
8. Task (default)

### 3. Template Files Structure
```
.claude/skills/bk-task/templates/
├── task.md
├── subtask.md
├── bug-internal.md
├── bug-uat.md
├── bug-prod.md
├── risk.md
├── issue.md
└── feedback.md
```

### 4. Backlog Custom Fields Mapping
| Template Field | Backlog Custom Field | Type |
|----------------|---------------------|------|
| Bug Type | bug_type | List (Internal/UAT/PROD) |
| Issue Category | issue_category | List |
| Feedback Type | feedback_type | List |
| Impact | impact_level | List |
| Probability | probability_level | List |
| Severity | severity | List |

---

## Unresolved Questions

1. **Custom field IDs**: Need to verify actual Backlog project custom field IDs for:
   - bug_type
   - issue_category
   - feedback_type
   - impact_level
   - severity

2. **Translation consistency**: Should we standardize VN terms or allow variations?
   - "Cong viec" vs "Task" for task type
   - "Loi" vs "Bug" for bug type

3. **Parent issue detection for Subtask**: How to extract parent issue key from input?
   - Pattern: "PROJ-XXX" mention
   - Pattern: "parent: XXX"
   - Require explicit flag?

4. **Feedback workflow**: Should feedback auto-convert to other types?
   - Bug Report -> Bug
   - Feature Request -> Task

---

## Next Steps

1. Review templates with team for VN/JA terminology accuracy
2. Confirm Backlog custom field configuration
3. Create implementation plan for TaskParser extension
4. Add test fixtures for new task types
