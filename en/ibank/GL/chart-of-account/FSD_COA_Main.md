# FSD: COA Management (Chart of Account)

| **Metadata** | |
|--------------|-------------|
| **Module** | COA Management |
| **Parent FSD** | FSD-Main.md |
| **Version** | 1.0 |
| **Date** | 2026-01-19 |
| **Status** | Final |
| **Owner** | IT / System Owner |

---

## Change Log

- 1.0 Initial FSD untuk modul COA Management.

---

## Module Overview

Modul **COA Management** mengelola master data rekening (COA) untuk kebutuhan akuntansi dan pelaporan.
Fitur utama mencakup daftar rekening, pembuatan rekening baru, perubahan data rekening, dan proses otorisasi perubahan.

Cakupan utama:

- Daftar & pencarian data rekening
- Pembuatan rekening baru
- Perubahan data rekening (ubah)
- Otorisasi pengajuan perubahan

---

## Actors & Roles

| Actor | Deskripsi |
| --- | --- |
| Operator Data | Mengelola data COA (list, create, edit, submit) |
| Otorisator | Approve/Reject pengajuan perubahan |

---

## 🖥️ Frontend Requirements (FE)

### FR-COA-MAIN-001 (FE): Akses Modul COA Management

**Deskripsi:**
Sistem menyediakan akses menu COA Management dari Data Master.

**Actor:** Operator Data

**Functional Acceptance Criteria:**

- Operator dapat membuka menu **Data Master -> Data Rekening (COA)**
- Sistem menampilkan halaman daftar rekening (list)
- Menu hanya terlihat untuk role yang berwenang

**Functional Flow:**

| Step | Actor | Action | System Response | Notes |
| --- | --- | --- | --- | --- |
| 1 | Operator | Login | Sistem validasi credential | |
| 2 | Operator | Buka Data Master -> Data Rekening (COA) | Sistem tampilkan halaman list | |

---

### FR-COA-MAIN-002 (FE): Navigasi ke Sub Modul

**Deskripsi:**
Sistem menyediakan navigasi dari halaman list ke fitur create dan edit.

**Actor:** Operator Data

**Functional Acceptance Criteria:**

- Dari list, Operator dapat klik **Tambah Rekening** untuk masuk ke halaman create
- Dari list, Operator dapat klik **Ubah Rekening** pada record untuk masuk ke halaman edit
- Navigasi membawa parameter `account_code` yang dipilih

---

## UI/UX Specification

#### Menu & Navigasi

- **Data Master -> Data Rekening (COA)**

#### Sub Modul & Dokumen Referensi

- List Rekening COA : `FSD_COA_List.md`
- Buat Rekening COA : `FSD_COA_Create.md`
- Ubah Rekening COA : `FSD_COA_Edit.md`

---

## 🛠️ Backend Requirements (BE)

### BE-COA-MAIN-001: Endpoint Utama

Sistem menyediakan endpoint untuk:

- List rekening (paging, filter)
- Get detail rekening (untuk edit)
- Submit create/edit sebagai pengajuan
- Pending list dan approve/reject

### BE-COA-MAIN-002: Audit & Otorisasi

- Seluruh perubahan data COA dicatat untuk audit.
- Pengajuan perubahan mengikuti proses otorisasi.

---

## 📌 Shared Business Rules

| Rule ID | Description |
| --- | --- |
| FR-COA-R01 | `account_code` bersifat unik dalam master COA |
| FR-COA-R02 | Semua perubahan data COA melalui otorisasi sebelum efektif |

---

## Open Questions

| # | Question | Status | Notes |
| --- | --- | --- | --- |
| 1 | Apakah pembuatan rekening baru memerlukan otorisasi? | Open | Defaultnya Ya|
| 2 | Apakah modul otorisasi menggunakan fitur existing atau khusus COA? | Open | Menggunakan fitur workflow |
