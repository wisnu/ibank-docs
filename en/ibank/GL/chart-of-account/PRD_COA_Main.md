# PRD: COA Maintenance

> **Module**: COA Maintenance - General Ledger
> **Version**: 1.0
> **Date**: 2026-01-01
> **Status**: Draft
> **Owner**: Accounting

---

## Module Overview

Modul COA Maintenance mengelola data Chart of Account (COA) yang digunakan sebagai dasar pencatatan transaksi akuntansi. Modul ini mencakup pembuatan akun, pengelompokan/hirarki akun, perubahan status akun, dan inquiry data COA.

---

## User Stories

---

### US-COA-001: Membuat Akun COA Baru

**As a** Accounting Officer,
**I want** menambahkan akun COA baru,
**So that** transaksi dapat diposting ke akun yang sesuai.

**Acceptance Criteria:**
- [ ] AC-001.1: User dapat input kode akun, nama akun, tipe akun, dan normal balance
- [ ] AC-001.2: Kode akun harus unik dan sesuai format
- [ ] AC-001.3: User dapat memilih parent account (optional)
- [ ] AC-001.4: Akun baru berstatus Pending Approval

**User Flow:**

| Step | Actor | Action | System Response | Condition/Notes |
|------|-------|--------|-----------------|-----------------|
| 1 | User | Navigasi ke COA → Input Baru | Form COA baru | |
| 2 | User | Mengisi data akun dan klik [Simpan] | Sistem validasi | |
| 3 | System | Validasi unik dan format | **IF** valid **THEN** simpan Pending Approval **ELSE** error | |
| 4 | Approver | Review dan approve | Status menjadi Active | |

**Ref:** -

---

### US-COA-002: Ubah/Nonaktifkan Akun COA

**As a** Accounting Supervisor,
**I want** mengubah atau menonaktifkan akun COA,
**So that** data COA tetap akurat dan terkendali.

**Acceptance Criteria:**
- [ ] AC-002.1: User dapat mengubah nama akun dan parent account
- [ ] AC-002.2: Kode akun bersifat read-only
- [ ] AC-002.3: Akun dengan saldo atau transaksi aktif tidak bisa dinonaktifkan
- [ ] AC-002.4: Perubahan memerlukan approval dan tercatat di audit trail

**User Flow:**

| Step | Actor | Action | System Response | Condition/Notes |
|------|-------|--------|-----------------|-----------------|
| 1 | User | Inquiry COA dan pilih akun | Detail akun tampil | |
| 2 | User | Klik [Ubah] atau [Nonaktifkan] | Form edit/status | |
| 3 | User | Simpan perubahan | Sistem validasi | |
| 4 | System | Simpan sebagai Pending Approval | Notifikasi sukses | |
| 5 | Approver | Review dan approve | Status diperbarui | |

**Ref:** -

---

### US-COA-003: Inquiry & Export COA

**As a** User dengan akses,
**I want** melihat daftar COA dan export data,
**So that** saya dapat melakukan review struktur akun.

**Acceptance Criteria:**
- [ ] AC-003.1: Mendukung filter berdasarkan tipe akun dan status
- [ ] AC-003.2: Menampilkan hirarki akun
- [ ] AC-003.3: Dapat export ke Excel

**User Flow:**

| Step | Actor | Action | System Response | Condition/Notes |
|------|-------|--------|-----------------|-----------------|
| 1 | User | Navigasi ke COA → Inquiry | Form filter | |
| 2 | User | Isi filter dan klik [Cari] | Tabel hasil tampil | |
| 3 | User | (Optional) Klik [Export] | File Excel terunduh | |

**Ref:** -

---

## Data Requirements

### Entity: COA_ACCOUNT

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| account_code | VARCHAR(20) | Yes | Kode akun unik |
| account_name | VARCHAR(100) | Yes | Nama akun |
| account_type | ENUM | Yes | Asset, Liability, Equity, Income, Expense |
| normal_balance | ENUM | Yes | Debit, Credit |
| parent_code | VARCHAR(20) | No | Parent account |
| status | ENUM | Yes | Active, Inactive, Pending |
| created_by | VARCHAR(20) | Yes | User create |
| created_date | DATETIME | Yes | Tanggal create |
| modified_by | VARCHAR(20) | No | User modify |
| modified_date | DATETIME | No | Tanggal modify |

---

## Business Rules

| Rule ID | Description |
|---------|-------------|
| BR-COA-001 | Kode akun harus unik dan mengikuti format standar bank |
| BR-COA-002 | Akun parent harus berada di level di atasnya |
| BR-COA-003 | Akun yang memiliki saldo tidak dapat dinonaktifkan |
| BR-COA-004 | Perubahan COA memerlukan approval |

---

## Validation Rules

| Field | Rule | Error Message |
|------|------|---------------|
| account_code | Required, length 4-20 | Kode akun wajib diisi (4-20 karakter) |
| account_name | Required | Nama akun wajib diisi |
| account_type | Required | Tipe akun wajib dipilih |

---

## Test Scenarios

| Scenario ID | Description | Precondition | Steps | Expected Result |
|-------------|-------------|--------------|-------|-----------------|
| TC-COA-001 | Create COA valid | User login | Input akun valid, simpan | Status Pending Approval |
| TC-COA-002 | Duplicate account code | COA exists | Input kode sama | Error duplikasi |
| TC-COA-003 | Deactivate with balance | Akun memiliki saldo | Nonaktifkan | Ditolak dengan pesan |

---

## Open Questions

| # | Question | Status | Answer |
|---|----------|--------|--------|
| 1 | Apakah COA memakai segmentasi multi-dimensi? | Open | |

---

*Part of General Ledger Module*
