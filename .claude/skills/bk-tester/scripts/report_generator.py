"""
ReportGenerator: Generate test execution reports.
"""

from datetime import datetime


def build_report_prompt(
    requirements: str,
    test_results: str = None,
    project_name: str = "プロジェクト"
) -> str:
    """
    Build a prompt for generating a test report.

    Args:
        requirements: The requirement document content
        test_results: Optional test execution results
        project_name: Name of the project

    Returns:
        A prompt string for claude -p
    """
    results_section = ""
    if test_results:
        results_section = f"""
# テスト実施結果

{test_results}
"""

    now = datetime.now()
    today = f"{now.year}年{now.month:02d}月{now.day:02d}日"

    prompt = f"""以下の要件定義書とテスト結果を基に、テスト報告書を作成してください。

# 要件定義書

{requirements}
{results_section}
# 指示

プロジェクト名「{project_name}」のテスト報告書を以下の構成で作成してください：

## 出力形式

```markdown
# テスト報告書

**プロジェクト名**: {project_name}
**報告日**: {today}
**報告者**: [担当者名]

---

## 1. エグゼクティブサマリー
[テスト結果の概要を3-5行で記述]

## 2. テスト実施概要
### 2.1 テスト期間
- 開始日: YYYY/MM/DD
- 終了日: YYYY/MM/DD

### 2.2 テスト対象
[テスト対象のシステム・機能]

### 2.3 テスト環境
[使用したテスト環境]

## 3. テスト実施結果
### 3.1 テストケース実施状況
| 分類 | 計画数 | 実施数 | 合格数 | 不合格数 | 実施率 | 合格率 |
|------|--------|--------|--------|----------|--------|--------|
| 機能テスト | XX | XX | XX | XX | XX% | XX% |
| 境界値テスト | XX | XX | XX | XX | XX% | XX% |
| 異常系テスト | XX | XX | XX | XX | XX% | XX% |
| セキュリティテスト | XX | XX | XX | XX | XX% | XX% |
| **合計** | **XX** | **XX** | **XX** | **XX** | **XX%** | **XX%** |

### 3.2 不具合サマリー
| 優先度 | 未対応 | 対応中 | 修正完了 | 再テスト完了 | 合計 |
|--------|--------|--------|----------|--------------|------|
| 高 | XX | XX | XX | XX | XX |
| 中 | XX | XX | XX | XX | XX |
| 低 | XX | XX | XX | XX | XX |
| **合計** | **XX** | **XX** | **XX** | **XX** | **XX** |

## 4. 主要な不具合
### 4.1 重大な不具合（優先度：高）
| 不具合ID | 概要 | ステータス | 対応予定日 |
|----------|------|------------|------------|
| BUG-XXX | [不具合概要] | 対応中/完了 | YYYY/MM/DD |

### 4.2 その他の課題
[その他気になった点や改善提案]

## 5. テストカバレッジ
- コードカバレッジ: XX%
- 要件カバレッジ: XX%
- 機能カバレッジ: XX%

## 6. 品質評価
### 6.1 品質メトリクス
- 不具合密度: XX件/KLOC
- 不具合検出率: XX%
- 修正効率: XX%

### 6.2 総合評価
[品質状況の総合評価]

## 7. リスクと課題
| リスク/課題 | 影響度 | 対応策 | 担当者 | 期限 |
|-------------|--------|--------|--------|------|
| [リスク項目] | 高/中/低 | [対応策] | [担当者] | YYYY/MM/DD |

## 8. 結論と推奨事項
### 8.1 リリース判定
- [ ] リリース可
- [ ] 条件付きリリース可（条件: [記述]）
- [ ] リリース不可

### 8.2 推奨事項
1. [推奨事項1]
2. [推奨事項2]
3. [推奨事項3]

## 9. 次回テストに向けて
### 9.1 改善点
[今回のテストから得られた改善点]

### 9.2 アクションアイテム
| 項目 | 担当者 | 期限 | ステータス |
|------|--------|------|------------|
| [アイテム] | [担当者] | YYYY/MM/DD | 未着手/進行中/完了 |

---

**承認者署名**:
**承認日**: YYYY/MM/DD
```

要件定義とテスト結果を基に、具体的で正確なテスト報告書を作成してください。
数値は実際のテスト結果に基づいて記入してください（不明な場合はXXのままで構いません）。
"""
    return prompt


def generate_test_report(
    requirements: str,
    test_results: str = None,
    project_name: str = "プロジェクト"
) -> str:
    """
    Generate a prompt for creating a test report.

    Args:
        requirements: The requirement document content
        test_results: Optional test execution results
        project_name: Name of the project

    Returns:
        Prompt string ready for `claude -p`
    """
    return build_report_prompt(requirements, test_results, project_name)
