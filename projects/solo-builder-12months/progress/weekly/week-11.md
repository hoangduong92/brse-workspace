# Week 11: Schema Design

> Phase 2: Backend + Database | Focus: Database Design Principles

---

## 🎯 Week Goals

| Goal | Status |
|------|--------|
| Learn database design principles | ✅ |
| Design schema for Backlog Clone MVP | ✅ |
| Create implementation plan | ✅ |

---

## 📚 Topics Learned

- [x] Entity vs Column distinction
- [x] 1:N (One-to-Many) relationships
- [x] N:M (Many-to-Many) relationships
- [x] Junction tables pattern
- [x] Lookup tables vs Entity tables
- [x] `allow_multiple` setting pattern
- [x] "Schema không đổi runtime" principle
- [x] First Normal Form (1NF) - no multiple values in column

---

## 🗃️ Backlog Clone Schema (13 tables)

**Entity Tables (6):**
- organizations
- profiles (users)
- projects
- issues
- documents
- comments

**Junction Tables (2):**
- project_members (Users ↔ Projects)
- issue_categories (Issues ↔ Categories)

**Lookup Tables (4):**
- roles
- statuses
- issue_types
- categories

---

## 📋 Implementation Plan Created

Plan: `plans/260125-1822-backlog-clone-mvp/`

| Phase | Description |
|-------|-------------|
| 1 | Database Schema Setup |
| 2 | Organizations & Users CRUD |
| 3 | Projects & Members CRUD |
| 4 | Issues & Comments CRUD |
| 5 | Lookup Tables Management |
| 6 | Row Level Security (RLS) |
| 7 | UI Components & Polish |

---

## ✅ Session Summary

**Duration:** ~45 minutes
**Key Insights:**
- Pivot from 3 separate product schemas → 1 comprehensive Backlog Clone
- Learning schema design thru building real product
- Junction tables for N:M, FK for 1:N
- UI setting (single/multi select) is app logic, not schema change

---

_Created: 2026-01-25_
