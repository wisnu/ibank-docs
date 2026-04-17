# FSD: Daftar Rekening (Chart of Account)

| **Metadata** | |
|--------------|-------------|
| **Module** | COA Management - Daftar Rekening |
| **Parent FSD** | FSD_COA_Main.md |
| **Version** | 1.0 |
| **Date** | 2026-01-19 |
| **Status** | Draft |
| **Owner** | IT / System Owner |

---

## Change Log

### 2026-01-19
- Inisialisasi 
- 
---

## Module Overview

Modul **Daftar Rekening (COA)** menyediakan daftar data rekening beserta fitur
pencarian, filter, sorting, dan navigasi ke create/edit.

Cakupan utama:

- Tampilkan list rekening (paging)
- Filter dan pencarian data
- Akses ke fitur create dan edit

---

## Actors & Roles

| Actor | Deskripsi |
| --- | --- |
| Operator Data | Mengelola data COA (list, create, edit) |
| Otorisator | Melihat daftar untuk review pengajuan |

---

## 🖥️ Frontend Requirements (FE)

### FR-COA-LIST-001 (FE): Akses Halaman Daftar COA

**Deskripsi:**
Sistem menyediakan halaman daftar rekening COA.

**Actor:** Operator Data

**Functional Acceptance Criteria:**

- Operator dapat membuka menu **Data Master -> Data Rekening (COA)**
- Sistem menampilkan tabel list rekening
- Default paging aktif

---

### FR-COA-LIST-002 (FE): Pencarian & Filter

**Deskripsi:**
Sistem menyediakan pencarian dan filter pada daftar COA.

**Actor:** Operator Data

**Functional Acceptance Criteria:**

- Operator dapat mencari berdasarkan kode atau nama rekening
- Operator dapat filter berdasarkan grup/tipe rekening
- Operator dapat reset filter

---

### FR-COA-LIST-003 (FE): Sorting & Pagination

**Deskripsi:**
Sistem menyediakan sorting dan pagination.

**Actor:** Operator Data

**Functional Acceptance Criteria:**

- Operator dapat sorting minimal pada kolom Kode Rekening dan Nama Rekening
- Operator dapat pindah halaman dan memilih jumlah data per halaman

---

### FR-COA-LIST-004 (FE): Aksi pada List

**Deskripsi:**
Sistem menyediakan aksi pada list untuk create dan edit.

**Actor:** Operator Data

**Functional Acceptance Criteria:**

- Tombol **Tambah Rekening** membuka halaman create
- Tombol **Ubah Rekening** membuka halaman edit untuk record terpilih
- Sistem membawa `account_code` sebagai parameter ke halaman edit

---

## UI/UX Specification

#### Menu & Navigasi

- **Data Master -> Data Rekening (COA)**

#### Struktur Tabel List

| Kolom (UI) | DB Column | Notes |
| --- | --- | --- |
| Kode Rekening | `account_code` | Unik |
| Nama Rekening | `account_name` | - |
| Grup Rekening | `account_group_code` / `account_type` | Sesuaikan implementasi |
| Rekening Induk | `fl_parent_account` | Jika ada |
| Detail | `is_detail` | Posting account indicator |

#### Filter

- Kode Rekening
- Nama Rekening
- Grup/Tipe Rekening
- Detail (Ya/Tidak)

---

## 🛠️ Backend Requirements (BE)

### BE-COA-LIST-001: List COA

**Output minimal:**

- `account_code`
- `account_name`
- `account_group_code` / `account_type`
- `fl_parent_account`
- `is_detail`

**Fitur:**

- Pagination (page, size)
- Sorting (account_code, account_name)
- Filter (account_code, account_name, account_group_code/account_type, is_detail)

---

## 📌 Shared Business Rules

| Rule ID | Description |
| --- | --- |
| FR-COA-R01 | Data list hanya menampilkan rekening aktif (jika ada flag status) |
| FR-COA-R02 | `account_code` bersifat read-only di list |

---

## Open Questions

| # | Question | Status | Notes |
| --- | --- | --- | --- |
| 1 | Apakah ada status aktif/inaktif untuk rekening? | Open | Menentukan filter dan tampilan |
| 2 | Apakah kolom tambahan perlu ditampilkan di list? | Open | Konfirmasi kebutuhan bisnis |
