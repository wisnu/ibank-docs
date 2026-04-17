# TSD – System Architecture

## 1. Purpose

Dokumen ini mendefinisikan arsitektur teknis global sistem,
yang menjadi acuan seluruh **TSD per-feature**.

---

## 2. High-Level Architecture

Komponen utama:
- Frontend (Web)
- Workflow Service
- Core Service
- Database

Alur umum:
User → Frontend → Workflow → Core → Database

---

## 3. Technology Stack

### 3.1 Frontend
- Framework: Next.js
- Responsibility:
  - UI rendering
  - Client-side validation
  - Orchestrating user interaction

### 3.2 Workflow Service
- Role: Orchestration & approval
- Responsibility:
  - Workflow state management
  - Approval logic
  - Validation layer sebelum Core

### 3.3 Core Service
- Language: Golang
- Responsibility:
  - Business logic utama
  - Data persistence
  - Final validation

### 3.4 Database
- RDBMS
- Menyimpan data master dan transaksi

---

## 4. Integration Principles

- FE tidak langsung mengakses Core.
- Semua perubahan data master wajib melalui Workflow.
- Core hanya menerima request dari Workflow.

---

## 5. Security & Access Control

- Authentication di FE.
- Authorization berbasis role (Maker / Approver).
- Workflow meng-enforce approval boundary.

---

## 6. Validation Strategy

| Layer     | Scope |
|----------|------|
| FE       | Format & mandatory |
| Workflow | Business rule & approval |
| Core     | Data integrity & persistence |

---

## 7. Error Handling Standard

- Error dikembalikan dengan code & message.
- Core error tidak diekspos langsung ke FE.
- Workflow menjadi boundary error.

---

## 8. Observability

- Logging per service.
- Correlation ID lintas FE–Workflow–Core.
- Audit log untuk approval.

---

## 9. Document Reference

- FSD per feature
- TSD per feature
- API Contract