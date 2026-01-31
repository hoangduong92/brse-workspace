# BrseKit Update Flow Investigation Report

**Date:** 2026-01-31
**Purpose:** Điều tra `bk update` command và tạo guideline cho release workflow

---

## 1. Tình Hình Hiện Tại

### 1.1 Flow của `bk update`

```
bk update
    ↓
updateCommand() [src/commands/update.ts]
    ↓
initCommand() với release="latest" [src/commands/init/init-command.ts]
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase 1: resolveOptions() - Parse CLI options                  │
│ Phase 2: handleAuth() - Xác thực GitHub (gh CLI token)         │
│ Phase 3: handleSelection() - Lấy releases từ GitHub API        │
│ Phase 4: handleDownload() - Download zipball từ release tag    │
│ Phase 5: handleMerge() - Merge files vào target directory      │
│ Phase 6: handlePostInstall() - Run install.sh/install.ps1      │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Source Repository

| Constant | Value |
|----------|-------|
| GITHUB_ORG | `brsekit` |
| STARTER_REPO | `brsekit-starter` |
| Download URL | `repos/brsekit/brsekit-starter/zipball/{tag}` |

### 1.3 Releases vs Main Branch

| Branch/Tag | `projects/` folder | `knowledge/` folder | Deprecated skills |
|------------|-------------------|---------------------|-------------------|
| **v1.1.0** (latest release) | ❌ Không có | ❌ Không có | ✅ Vẫn còn |
| **v1.0.0** | ❌ Không có | ❌ Không có | ✅ Vẫn còn |
| **main** | ✅ Có | ✅ Có | ❌ Đã xóa |

**→ Main branch đang ahead v1.1.0 2 commits**

---

## 2. Vấn Đề

**User muốn:** Push code lên main → `bk update` pull được code mới

**Hiện trạng:**
- `bk update` chỉ pull từ **GitHub Releases** (tagged versions)
- **Không** pull từ main branch
- Code mới push lên main **không** được pull về nếu chưa có release mới

**Kết luận:** File `projects/README.md` hiện chỉ có trên main branch, chưa có trong release nào.

---

## 3. Giải Pháp

### Option A: Tạo Release Mới (Recommended - Simple)

**Pros:** Không cần thay đổi code CLI, workflow chuẩn
**Cons:** Cần tạo release thủ công mỗi lần

**Steps:**
1. Commit changes lên main branch của `brsekit/brsekit-starter`
2. Tạo release mới với tag (e.g., `v1.2.0`)
3. Users chạy `bk update` để pull version mới

```bash
# Tại brsekit-starter repo
git tag v1.2.0
git push origin v1.2.0

# Tạo GitHub Release
gh release create v1.2.0 --title "v1.2.0" --notes "Release notes here"
```

### Option B: Thêm Option Pull từ Main Branch

**Pros:** Có thể pull latest changes ngay
**Cons:** Cần modify brsekit-cli code, users có thể pull unstable code

**Implementation:**
- Thêm option `--main` hoặc `--branch <name>` cho `bk update`
- Modify `handleSelection()` và `handleDownload()` để support branch download

---

## 4. Guideline cho Agents

### 4.1 Release Workflow (Khi muốn publish version mới)

```bash
# 1. Ở brsekit-starter repo
cd /path/to/brsekit-starter

# 2. Commit changes
git add .
git commit -m "feat: add projects support"
git push origin main

# 3. Tạo tag
git tag v1.X.0
git push origin v1.X.0

# 4. Tạo GitHub Release
gh release create v1.X.0 \
  --title "v1.X.0 - Feature Name" \
  --notes "$(cat <<'EOF'
## What's New
- Added projects folder support
- Added knowledge folder

## Breaking Changes
- None
EOF
)"

# 5. Verify
gh api repos/brsekit/brsekit-starter/releases --jq '.[0] | "\(.tag_name) - \(.published_at)"'
```

### 4.2 Verify Update Works

```bash
# Sau khi tạo release
bk update --verbose

# Check version
bk version
```

### 4.3 File Structure của brsekit-starter

```
brsekit-starter/
├── README.md
├── metadata.json          # Version info, dependencies
├── install.sh             # Linux/Mac post-install script
├── install.ps1            # Windows post-install script
├── bk-capture/            # Skill: Task/meeting capture
├── bk-convert/            # Skill: JA↔VI translation
├── bk-init/               # Skill: Project initialization
├── bk-morning/            # Skill: Morning brief
├── bk-recall/             # Skill: Memory layer
├── bk-spec/               # Skill: Requirement analysis
├── bk-track/              # Skill: Project tracking
├── bk-write/              # Skill: Japanese writing
├── brsekit/               # Core skill: Help & docs
├── common/                # Shared utilities
├── lib/                   # Python libraries
├── knowledge/             # Knowledge base (NEW)
└── projects/              # Per-project configs (NEW)
    └── README.md
```

---

## 5. Tóm Tắt Findings

| Item | Status |
|------|--------|
| `bk update` hoạt động? | ✅ Có, nhưng chỉ pull từ releases |
| Pull từ main branch? | ❌ Không support |
| `projects/README.md` có trong release? | ❌ Chưa (chỉ có trên main) |
| Giải pháp đề xuất | Tạo release v1.2.0 |

---

## 6. Next Actions

1. ✅ **Done:** Tạo release `v1.2.0` từ main branch của brsekit-starter
2. ✅ **Done:** Fix merge logic để install `projects/` và `knowledge/` ra workspace root
3. ✅ **Done:** Publish brsekit-cli v1.0.4 lên npm

---

## 8. Fix Applied (2026-01-31 18:30)

### Problem
`bk update` copy TẤT CẢ folders vào `.claude/skills/`, bao gồm cả `projects/` và `knowledge/`

### Solution
Update [merge-handler.ts](experiments/brsekit-cli/src/commands/init/phases/merge-handler.ts) để:

1. Thêm constant `WORKSPACE_FOLDERS = ["projects", "knowledge"]`
2. Khi merge:
   - DATA folders (`projects/`, `knowledge/`) → copy ra `<workspace>/`
   - CODE folders (skills) → copy vào `.claude/skills/`

### Changes

| File | Change |
|------|--------|
| [constants.ts](experiments/brsekit-cli/src/shared/constants.ts) | Add `WORKSPACE_FOLDERS` |
| [merge-handler.ts](experiments/brsekit-cli/src/commands/init/phases/merge-handler.ts) | Separate DATA vs CODE handling |
| package.json | Version bump to 1.0.4 |

### Result Structure After Fix

```
<workspace>/
├── .claude/skills/           # CODE - Skills code
│   ├── bk-track/
│   ├── bk-capture/
│   └── ...
├── projects/                 # DATA - Per-project configs
│   └── README.md
├── knowledge/                # DATA - Shared knowledge
│   └── ...
└── CLAUDE.md
```

---

## 7. Code References

| File | Purpose |
|------|---------|
| [update.ts](experiments/brsekit-cli/src/commands/update.ts) | Update command handler |
| [init-command.ts](experiments/brsekit-cli/src/commands/init/init-command.ts) | Main init orchestrator |
| [selection-handler.ts](experiments/brsekit-cli/src/commands/init/phases/selection-handler.ts) | Fetch releases from GitHub |
| [download-handler.ts](experiments/brsekit-cli/src/commands/init/phases/download-handler.ts) | Download zipball from release |
| [constants.ts](experiments/brsekit-cli/src/shared/constants.ts) | GitHub org/repo constants |
