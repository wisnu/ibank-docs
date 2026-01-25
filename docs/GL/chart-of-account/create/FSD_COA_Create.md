# FSD: Buat Rekening (Chart of Account)

> Module: COA Management - Buat Rekening
> Parent FSD: FSD_COA_Main.md
> Version: 1.0
> Date: 2026-01-19
> Status: Draft
> Owner: IT / System Owner

---

## Change Log (v1.0)

- Initial FSD untuk fitur Buat Rekening.

---

## Module Overview

Modul **Buat Rekening (COA)** menyediakan fungsi untuk membuat rekening baru beserta parameter
saldo, transaksi, dan atribut pelaporan.

Cakupan utama:

- Input data master rekening (`ibcore.account`)
- Input parameter default saldo/transaksi
- (Opsional) pembentukan data `accountinstance` sesuai kebijakan
- Submit pengajuan untuk proses otorisasi

---

## Actors & Roles

| Actor | Deskripsi |
| --- | --- |
| Operator Data | Mengajukan pembuatan rekening COA |
| Otorisator | Approve/Reject pengajuan pembuatan COA |

---

## 🖥️ Frontend Requirements (FE)

### FR-COA-CRT-001 (FE): Akses Halaman Buat Rekening

**Deskripsi:**
Sistem menyediakan halaman untuk membuat rekening COA baru.

**Actor:** Operator Data

**Functional Acceptance Criteria:**

- Operator dapat klik **Tambah Rekening** dari halaman list
- Sistem menampilkan form create dengan field input
- Field yang bersifat sistem (audit) tidak ditampilkan

**Functional Flow:**

| Step | Actor | Action | System Response | Notes |
| --- | --- | --- | --- | --- |
| 1 | Operator | Buka daftar COA | Sistem tampilkan list COA | |
| 2 | Operator | Klik Tambah Rekening | Sistem tampilkan form create | |

---

### FR-COA-CRT-002 (FE): Submit Pembuatan Rekening

**Deskripsi:**
Sistem menerima data rekening baru dan menyimpannya sebagai pengajuan.

**Actor:** Operator Data

**Functional Acceptance Criteria:**

- Sistem memvalidasi field mandatory & rule FE/BE
- Sistem menyimpan pengajuan dengan status **Pending Approval**
- Pengajuan muncul di daftar otorisasi untuk Otorisator

**Functional Flow:**

| Step | Actor | Action | System Response | Notes |
| --- | --- | --- | --- | --- |
| 1 | Operator | Isi field create | Sistem menerima input | |
| 2 | Operator | Klik Submit | Sistem validasi data | |
| 3 | System | Validasi | **IF** valid **THEN** simpan pengajuan **ELSE** tampilkan error | |
| 4 | System | Simpan pengajuan | Muncul di daftar otorisasi | Status: Pending Approval |

---

### FR-COA-CRT-003 (FE): Otorisasi Pembuatan COA

**Deskripsi:**
Sistem menyediakan proses approve/reject untuk pengajuan pembuatan rekening.

**Actor:** Otorisator

**Functional Acceptance Criteria:**

- Otorisator dapat melihat daftar pending
- Otorisator dapat Approve atau Reject
- Jika Approve -> data rekening dibuat aktif
- Jika Reject -> data tidak dibuat

---

## 🧭 UI/UX Specification

#### Menu & Navigasi

- **Data Master -> Data Rekening (COA) -> Tambah Rekening**

#### Mockup

- (to be provided)

#### Screenshot

- (to be provided)

---

## Frontend Field Specification & Validation

#### Form Buat Rekening (Master `ibcore.account`)

| Field (UI) | Mandatory | DB Column | Rules |
| --- | --- | --- | --- |
| Kode Rekening | M | `account_code` | Unik, format sesuai kebijakan |
| Nama Rekening | M | `account_name` | Tidak boleh kosong, max 200 char |
| Deskripsi Rekening | O | `account_desc` | Max 400 char |
| Rekening Induk | O | `fl_parent_account` | Jika diisi, harus exist |
| Grup Rekening | M | `account_type` / `account_group_code`* | Sesuaikan implementasi |
| Detail | M | `is_detail` | Indicator posting |
| Keterhubungan CPA | O | `fl_cpa_accountcode` | Pilih dari referensi CPA |
| LBUS Code | O | `lbus_code` | Pelaporan regulator |
| LBUS Type | O | `lbus_type` | Pelaporan regulator |
| LSMK Code | O | `lsmk_code` | Pelaporan regulator |
| LSMK Type | O | `lsmk_type` | Pelaporan regulator |
| LBBU Code | O | `lbbu_code` | Laporan internal |
| Intern Code | O | `intern_code` | Klasifikasi internal |
| PUB Code | O | `pub_code` | Publikasi/laporan tertentu |
| Sandi BI | O | `sandi_bi` | Max 10 char |
| Tipe Pajak | O | `tax_type` | Dari master pajak |
| Kode Pajak | O | `tax_code` | Max 20 char |
| Nomor Akun Pajak | O | `tax_account_code` | Refer ke `account.account_code` dengan `is_detail='T'` |
| Tarif Pajak NPWP | O | `tax_rate_npwp` | Numerik >= 0, default 0.00 |
| Tarif Pajak Non NPWP | O | `tax_rate_non_npwp` | Numerik >= 0, default 0.00 |
| Flag PPh21 | O | `tax_flag_pph21` | Flag |
| Tenaga Ahli | O | `tax_flag_expert` | Default uncheck |
| RPV RAK Report Show | O | `isrpvrakreportshow` | Flag tampil report |
| Hidden Offbalance Sheet | O | `is_hidden_offbalancesheet` | Flag |
| RAK Account | O | `israkaccount` | Flag |

\*Catatan: pada dokumen lama ada "Grup Rekening" sebagai klasifikasi laporan (misal ASET). Di schema tersedia `account_group_code` dan `account_type`. Implementasi final perlu konsisten (pilih salah satu atau gabungkan aturan).

---

#### Tab: Parameter Saldo dan Transaksi (Default di `ibcore.account`)

| Field (UI) | Mandatory | DB Column | Rules |
| --- | --- | --- | --- |
| Saldo Normal (Default) | M | `normal_balance_type_def` | Dropdown: {Debet, Kredit, Netral} |
| Saldo Harus Nihil (Default) | M | `is_zero_balance_def` | Dropdown: {Boleh Tidak Nihil, Harus Nihil} |
| Status Transaksi (Default) | M | `trx_permit_type_def` | Dropdown status transaksi |

---

## 🛠️ Backend Requirements (BE)

### BE-COA-CRT-001: Validasi Submit Pengajuan

**Input minimal:**

- `account_code`
- `account_name`
- `account_type` / `account_group_code`
- `normal_balance_type_def`, `is_zero_balance_def`, `trx_permit_type_def`
- `user_input` (userid operator)

**Validasi:**

- `account_code` harus unik
- `account_name` tidak boleh kosong
- Field perubahan hanya pada whitelist field create
- Numeric (tarif pajak) tidak boleh negatif
- Jika `fl_parent_account` diisi, parent harus exist

---

### BE-COA-CRT-002: Persist & Approval Apply

**Saat submit:**

- Simpan pengajuan pembuatan rekening + detail before/after
- Status pengajuan: Pending Approval

**Saat approve:**

- Insert ke `ibcore.account`
- (Opsional) Insert ke `ibcore.accountinstance` sesuai kebijakan
- Set audit `userid_create`, `time_create`
- Status pengajuan: Approved

**Saat reject:**

- Status pengajuan: Rejected
- Tidak ada insert ke data aktif

---

## 📌 Shared Business Rules

| Rule ID | Description |
| --- | --- |
| FR-COA-R01 | `account_code` bersifat unik |
| FR-COA-R02 | Field tarif pajak tidak boleh negatif dan default 0.00 jika kosong |
| FR-COA-R03 | Semua pembuatan COA mengikuti otorisasi sebelum efektif |

---

## Open Questions

| # | Question | Status | Notes |
| --- | --- | --- | --- |
| 1 | Apakah `fl_parent_account` wajib untuk rekening non-root? | Open | Aturan hierarki |
| 2 | Apakah `accountinstance` dibuat otomatis untuk semua branch/currency? | Open | Menentukan flow create |
| 3 | Apakah `reason` wajib saat submit create? | Open | Policy otorisasi |
