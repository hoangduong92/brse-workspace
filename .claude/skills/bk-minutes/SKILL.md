# bk-minutes

Meeting minutes generator with PM mindset classification.

## Command

```
/bk-minutes <input>
```

## Input

| Type | Description |
|------|-------------|
| Video (mp4, webm) | Transcribe via ai-multimodal |
| Audio (mp3, wav) | Transcribe via ai-multimodal |
| Text (txt, md) | Direct parse |

## Output

- Full meeting minutes document (Markdown)
- Classified items: Tasks, Issues, Risks, Questions
- Preview before creating Backlog items

## Classification (PM Mindset)

| Category | Japanese Keywords | Vietnamese Keywords |
|----------|-------------------|---------------------|
| Task | 作成, 実装, 対応, 確認 | làm, tạo, implement |
| Issue/Bug | 不具合, エラー, 問題 | lỗi, bug, vấn đề |
| Risk | リスク, 心配, もしかして | rủi ro, nếu, có thể |
| Question | 確認したい, 質問, ? | cần confirm, chưa rõ |

## Usage

```bash
# From transcript file
python scripts/main.py --file transcript.txt

# From video (requires ai-multimodal)
python scripts/main.py --file meeting.mp4

# Dry run (preview only)
python scripts/main.py --file transcript.txt --dry-run

# Output as JSON
python scripts/main.py --file transcript.txt --json
```

## Dependencies

- ai-multimodal skill (for video/audio transcription)
- bk-task skill (for task creation)