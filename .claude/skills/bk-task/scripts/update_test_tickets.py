"""Update BKT-1 to BKT-8 with new bilingual templates for testing."""

import sys
import io
import requests
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SPACE_URL = 'brsekit.backlog.com'
API_KEY = 'L0oxhoz3OjiGKmix9fcO5RgYwrnQLvRaCNd9X7IQJVkU0NK0SbebmHeb862UjgqP'
PROJECT_ID = 'BKT'

# Issue type IDs
ISSUE_TYPES = {
    'Task': 670845,
    'Bug': 670846,
    'SubTask': 671009,
    'Risk': 671006,
    'Issue': 671007,
    'UserFeedback': 671008,
}

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def load_template(name):
    """Load template from file."""
    path = TEMPLATES_DIR / f"{name}.md"
    if path.exists():
        return path.read_text(encoding='utf-8')
    return ""


def render_template(template_content, vars):
    """Replace placeholders with values."""
    result = template_content
    for key, value in vars.items():
        result = result.replace('{' + key + '}', str(value))
    return result


def update_issue(key, summary, issue_type_id, description):
    """Update issue via Backlog API."""
    url = f'https://{SPACE_URL}/api/v2/issues/{key}?apiKey={API_KEY}'
    data = {
        'summary': summary,
        'issueTypeId': issue_type_id,
        'description': description,
    }
    resp = requests.patch(url, data=data)
    return resp.status_code, resp.json() if resp.status_code == 200 else resp.text


# Update configurations for BKT-1 to BKT-8
UPDATES = [
    {
        'key': 'BKT-1',
        'summary': '[TASK] Triển khai chức năng phòng chờ -- 待合室機能を実装',
        'issueTypeId': ISSUE_TYPES['Task'],
        'template': 'task',
        'vars': {
            'description_vn': 'Triển khai chức năng phòng chờ cho ứng dụng.\nBao gồm: giao diện phòng chờ, real-time updates, notification khi được gọi.',
            'description_ja': '待合室機能をアプリに実装する。\n待合室UI、リアルタイム更新、呼び出し通知を含む。',
            'criterion_1_vn': 'Waiting room UI implemented',
            'criterion_2_vn': 'Real-time status updates',
            'criterion_1_ja': '待合室UI実装完了',
            'criterion_2_ja': 'リアルタイムステータス更新',
            'notes_vn': 'Tham khảo hệ thống xếp hàng hiện có\nXem xét khả năng tương thích với thiết bị di động',
            'notes_ja': '既存の待ち行列システムを参照\nモバイルデバイスの互換性を考慮する',
        }
    },
    {
        'key': 'BKT-2',
        'summary': '[SUBTASK] Thiết kế UI phòng chờ -- 待合室UIデザイン',
        'issueTypeId': ISSUE_TYPES['SubTask'],
        'template': 'subtask',
        'vars': {
            'parent_issue_key': 'BKT-1',
            'parent_issue_title': '[TASK] Triển khai chức năng phòng chờ',
            'description_vn': 'Thiết kế giao diện người dùng cho màn hình phòng chờ.',
            'description_ja': '待合室画面のユーザーインターフェースをデザインする。',
            'scope_item_1_vn': 'Mockup màn hình chính',
            'scope_item_2_vn': 'Responsive design cho mobile',
            'scope_item_1_ja': 'メイン画面のモックアップ',
            'scope_item_2_ja': 'モバイル向けレスポンシブデザイン',
            'criterion_1_vn': 'Figma mockup approved',
            'criterion_2_vn': 'Design specs documented',
            'criterion_1_ja': 'Figmaモックアップ承認済み',
            'criterion_2_ja': 'デザイン仕様書作成完了',
        }
    },
    {
        'key': 'BKT-3',
        'summary': '[BUG-INT] Nút đăng nhập không phản hồi -- ログインボタンが反応しない',
        'issueTypeId': ISSUE_TYPES['Bug'],
        'template': 'bug-internal',
        'vars': {
            'severity': 'High',
            'found_by': 'Dev Team',
            'found_date': '2026-01-28',
            'browser_device': 'Chrome 120',
            'os': 'Windows 11',
            'environment': 'Development',
            'version': 'v1.2.0-dev',
            'symptom_vn': 'Khi click vào nút đăng nhập, không có phản hồi. Console hiển thị lỗi TypeError.',
            'symptom_ja': 'ログインボタンをクリックしても反応がない。コンソールにTypeErrorが表示される。',
            'step_1_vn': 'Truy cập trang đăng nhập',
            'step_2_vn': 'Nhập email và mật khẩu',
            'step_3_vn': 'Click nút "Đăng nhập"',
            'step_1_ja': 'ログインページにアクセス',
            'step_2_ja': 'メールとパスワードを入力',
            'step_3_ja': '「ログイン」ボタンをクリック',
            'expected_result_vn': 'Chuyển hướng đến dashboard',
            'expected_result_ja': 'ダッシュボードにリダイレクト',
            'actual_result_vn': 'Không có phản hồi, console hiển thị lỗi',
            'actual_result_ja': '反応なし、コンソールにエラー表示',
            'screenshot_link': 'N/A',
            'log_link': 'logs/error-20260128.log',
            'root_cause_vn': '(Chưa điều tra)',
            'root_cause_ja': '（未調査）',
            'solution_vn': '(Chưa fix)',
            'solution_ja': '（未修正）',
        }
    },
    {
        'key': 'BKT-4',
        'summary': '[BUG-UAT] Hiển thị sai số tiền -- 金額表示が間違っている',
        'issueTypeId': ISSUE_TYPES['Bug'],
        'template': 'bug-uat',
        'vars': {
            'severity': 'Medium',
            'found_by': 'QA Team',
            'found_date': '2026-01-27',
            'uat_round': 'UAT Round 2',
            'browser_device': 'Safari 17',
            'os': 'macOS Sonoma',
            'environment': 'UAT',
            'version': 'v1.1.9',
            'symptom_vn': 'Số tiền hiển thị thiếu dấu phân cách hàng nghìn.',
            'symptom_ja': '金額表示に桁区切りがない。',
            'step_1_vn': 'Đăng nhập vào hệ thống',
            'step_2_vn': 'Vào trang thanh toán',
            'step_3_vn': 'Xem tổng tiền',
            'step_1_ja': 'システムにログイン',
            'step_2_ja': '決済ページに移動',
            'step_3_ja': '合計金額を確認',
            'expected_result_vn': '1,000,000 VND',
            'expected_result_ja': '1,000,000 VND',
            'actual_result_vn': '1000000 VND',
            'actual_result_ja': '1000000 VND',
            'screenshot_link': 'screenshots/uat-bug-amount.png',
            'log_link': 'N/A',
            'root_cause_vn': 'Thiếu format number trong component',
            'root_cause_ja': 'コンポーネントに数値フォーマットがない',
            'solution_vn': 'Thêm toLocaleString() cho số tiền',
            'solution_ja': '金額にtoLocaleString()を追加',
        }
    },
    {
        'key': 'BKT-5',
        'summary': '[BUG-PROD] API timeout khi load danh sách -- API読み込みタイムアウト',
        'issueTypeId': ISSUE_TYPES['Bug'],
        'template': 'bug-prod',
        'vars': {
            'severity': 'Critical',
            'found_by': 'User Report',
            'found_date': '2026-01-29',
            'affected_users': '~500 users',
            'environment': 'Production',
            'version': 'v1.1.8',
            'time_range': '14:00-14:30 JST',
            'symptom_vn': 'API /api/items timeout sau 30 giây, người dùng không thể load danh sách sản phẩm.',
            'symptom_ja': 'API /api/items が30秒後にタイムアウト、ユーザーが商品リストを読み込めない。',
            'step_1_vn': 'Đăng nhập production',
            'step_2_vn': 'Vào trang danh sách sản phẩm',
            'step_3_vn': 'Đợi load',
            'step_1_ja': '本番環境にログイン',
            'step_2_ja': '商品一覧ページに移動',
            'step_3_ja': '読み込みを待つ',
            'expected_result_vn': 'Danh sách load trong 2 giây',
            'expected_result_ja': 'リストが2秒以内に読み込まれる',
            'actual_result_vn': 'Timeout sau 30 giây',
            'actual_result_ja': '30秒後にタイムアウト',
            'log_link': 'cloudwatch/prod-api-errors',
            'error_message': 'ETIMEDOUT: connection timed out',
            'action_1_vn': 'Scale up database connection pool',
            'action_2_vn': 'Enable query caching',
            'action_3_vn': 'Monitor response times',
            'action_1_ja': 'データベース接続プールをスケールアップ',
            'action_2_ja': 'クエリキャッシュを有効化',
            'action_3_ja': 'レスポンス時間を監視',
            'root_cause_vn': 'Database connection pool exhausted',
            'root_cause_ja': 'データベース接続プール枯渇',
            'solution_vn': 'Increase pool size from 10 to 50',
            'solution_ja': 'プールサイズを10から50に増加',
        }
    },
    {
        'key': 'BKT-6',
        'summary': '[RISK] Dependency outdated có security vulnerability -- セキュリティ脆弱性のある古い依存関係',
        'issueTypeId': ISSUE_TYPES['Risk'],
        'template': 'risk',
        'vars': {
            'impact_level_vn': 'Cao',
            'impact_level_ja': '高',
            'probability_level_vn': 'Trung bình',
            'probability_level_ja': '中',
            'risk_score': '6/9',
            'description_vn': 'Package lodash version 4.17.15 có CVE-2021-23337 vulnerability. Cần upgrade lên version mới.',
            'description_ja': 'lodashパッケージ v4.17.15 にCVE-2021-23337の脆弱性あり。新バージョンへのアップグレードが必要。',
            'cause_1_vn': 'Không có automated dependency scanning',
            'cause_2_vn': 'Package lock file chưa được update định kỳ',
            'cause_1_ja': '自動依存関係スキャンがない',
            'cause_2_ja': 'パッケージロックファイルの定期更新がない',
            'impact_schedule_vn': 'Có thể delay release nếu phát hiện muộn',
            'impact_cost_vn': 'Chi phí fix tăng nếu bị exploit',
            'impact_quality_vn': 'Ảnh hưởng đến security audit',
            'impact_schedule_ja': '発見が遅れるとリリース遅延の可能性',
            'impact_cost_ja': '悪用された場合、修正コストが増加',
            'impact_quality_ja': 'セキュリティ監査に影響',
            'action_1_vn': 'Setup Dependabot alerts',
            'action_1_ja': 'Dependabotアラートを設定',
            'owner_1': 'DevOps',
            'deadline_1': '2026-02-05',
            'status_1_vn': 'Đang thực hiện',
            'status_1_ja': '進行中',
            'contingency_plan_vn': 'Nếu không thể upgrade, isolate package với wrapper function.',
            'contingency_plan_ja': 'アップグレードできない場合、ラッパー関数でパッケージを分離。',
            'next_review_date': '2026-02-10',
        }
    },
    {
        'key': 'BKT-7',
        'summary': '[ISSUE] Performance degradation sau deploy -- デプロイ後のパフォーマンス低下',
        'issueTypeId': ISSUE_TYPES['Issue'],
        'template': 'issue',
        'vars': {
            'category_vn': 'Hiệu năng',
            'category_ja': 'パフォーマンス',
            'severity_vn': 'Cao',
            'severity_ja': '高',
            'status_vn': 'Đang điều tra',
            'status_ja': '調査中',
            'description_vn': 'Sau khi deploy v1.2.0, response time tăng 300%. Cần investigate và fix.',
            'description_ja': 'v1.2.0デプロイ後、レスポンスタイムが300%増加。調査と修正が必要。',
            'impact_1_vn': 'User experience giảm',
            'impact_2_vn': 'Có thể mất khách hàng',
            'impact_1_ja': 'ユーザー体験が低下',
            'impact_2_ja': '顧客を失う可能性',
            'root_cause_vn': 'N+1 query trong feature mới',
            'root_cause_ja': '新機能でN+1クエリ発生',
            'option_a_vn': 'Rollback to v1.1.9',
            'pros_a_vn': 'Nhanh, ít risk',
            'cons_a_vn': 'Mất feature mới',
            'effort_a': '1h',
            'option_a_ja': 'v1.1.9にロールバック',
            'pros_a_ja': '速い、リスク低い',
            'cons_a_ja': '新機能が使えない',
            'option_b_vn': 'Hotfix N+1 query',
            'pros_b_vn': 'Giữ feature mới',
            'cons_b_vn': 'Cần test kỹ',
            'effort_b': '4h',
            'option_b_ja': 'N+1クエリをホットフィックス',
            'pros_b_ja': '新機能を維持',
            'cons_b_ja': '十分なテストが必要',
            'selected_solution_vn': 'Lựa chọn B - Hotfix N+1 query với eager loading',
            'selected_solution_ja': 'オプションB - Eager loadingでN+1クエリをホットフィックス',
            'action_1_vn': 'Triển khai eager loading',
            'action_1_ja': 'Eager loadingを実装',
            'owner_1': 'Backend Team',
            'deadline_1': '2026-01-30',
            'status_1_vn': 'Đang thực hiện',
            'status_1_ja': '進行中',
            'review_date': '2026-01-31',
            'success_criteria_vn': 'Response time < 200ms',
            'success_criteria_ja': 'レスポンスタイム < 200ms',
        }
    },
    {
        'key': 'BKT-8',
        'summary': '[FEEDBACK] Yêu cầu dark mode -- ダークモードのリクエスト',
        'issueTypeId': ISSUE_TYPES['UserFeedback'],
        'template': 'feedback',
        'vars': {
            'feedback_type': 'Feature Request',
            'feedback_type_ja': '機能リクエスト',
            'source': 'Customer Support',
            'source_ja': 'カスタマーサポート',
            'received_date': '2026-01-25',
            'channel': 'Email',
            'channel_ja': 'メール',
            'original_quote': '夜間に使用すると目が疲れます。ダークモードを追加してほしいです。',
            'summary_vn': 'Người dùng yêu cầu thêm chế độ tối để giảm mỏi mắt khi sử dụng ban đêm.',
            'summary_ja': 'ユーザーが夜間使用時の目の疲れを軽減するためにダークモードを要望。',
            'user_type': 'Premium User',
            'user_type_ja': 'プレミアムユーザー',
            'frequency': '5+ requests/month',
            'frequency_ja': '月5件以上',
            'impact_scope': 'All users',
            'impact_scope_ja': '全ユーザー',
            'related_feature': 'UI/UX',
            'related_feature_ja': 'UI/UX',
            'user_impact_score': '4',
            'user_impact_notes_vn': 'Ảnh hưởng trải nghiệm nhiều user',
            'user_impact_notes_ja': '多くのユーザーの体験に影響',
            'effort_score': '3',
            'effort_notes_vn': 'Cần refactor theme system',
            'effort_notes_ja': 'テーマシステムのリファクタリングが必要',
            'business_score': '4',
            'business_notes_vn': 'Tăng retention',
            'business_notes_ja': 'リテンション向上',
            'decision_vn': 'Approved - Add to Q2 roadmap',
            'decision_ja': '承認 - Q2ロードマップに追加',
            'reason_vn': 'High user demand, reasonable effort',
            'reason_ja': '高いユーザー需要、妥当な工数',
            'target_release': 'v1.4.0 (Q2 2026)',
            'user_response_vn': 'Cảm ơn phản hồi! Chúng tôi đã thêm Dark Mode vào roadmap Q2.',
            'user_response_ja': 'フィードバックありがとうございます！ダークモードをQ2ロードマップに追加しました。',
        }
    },
]


def main():
    """Update all test tickets."""
    print('=== Updating Issues BKT-1 to BKT-8 ===\n')

    for update in UPDATES:
        template_content = load_template(update['template'])
        description = render_template(template_content, update['vars'])

        status, result = update_issue(
            update['key'],
            update['summary'],
            update['issueTypeId'],
            description
        )

        if status == 200:
            print(f"OK  {update['key']}: {update['summary'][:50]}...")
        else:
            print(f"ERR {update['key']}: {str(result)[:80]}")

    print('\n=== Done! ===')
    print('Check: https://brsekit.backlog.com/find/BKT')


if __name__ == '__main__':
    main()
