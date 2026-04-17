# TSD: Ubah Rekening (Chart of Account)

| **Metadata** | |
|--------------|-------------|
| **Module** | COA Management – Ubah Rekening |
| **Parent FSD** | FSD_COA_Edit.md |
| **Version** | 2.0 |
| **Date** | 2026-01-28 |
| **Status** | Draft |
| **Owner** | IT / System Owner |

---

## 1. Tujuan & Ruang Lingkup

Dokumen ini menjabarkan spesifikasi teknis implementasi modul **Ubah Rekening (COA)**, mencakup:

- Endpoint backend untuk pengambilan data, submit, dan otorisasi.
- Struktur payload dan mapping field ke schema database.
- Validasi, transaksi, audit, dan logging.
- Perilaku propagasi parameter default ke seluruh `accountinstance`.
- Detail tabel database yang diakses dan dimodifikasi.
- Mockup frontend dan mapping field UI ke database.

---

## 2. Asumsi & Ketergantungan

- Modul otorisasi tersedia (pending list, detail before/after, approve/reject).
- Akses menu mengikuti role (Operator Data vs Otorisator).
- Referensi master seperti CPA, Pajak, Branch, Currency tersedia via layanan referensi.
- Audit user tersedia di header (mis. `X-UserId`) atau token.

---

## 3. Arsitektur Ringkas

- FE memanggil BE service `coa-management`.
- BE melakukan validasi, menyimpan pengajuan ke tabel pengajuan, dan menampilkan pending list.
- Approve/Reject dijalankan oleh Otorisator dengan transaksi atomik.

---

## 4. Model Data & Mapping

### 4.1 Entity Utama

- `ibcore.account` (Master COA)
  - PK: `account_code`
- `ibcore.accountinstance` (COA per Branch & Currency)
  - PK: `accountinstance_id`

### 4.2 Field Editable (Whitelist)

#### Master `ibcore.account`

Editable:

- `account_name`
- `account_desc`
- `account_type` atau `account_group_code` (pilih salah satu sesuai keputusan bisnis)
- `fl_cpa_accountcode`
- `lbus_code`, `lbus_type`, `lsmk_code`, `lsmk_type`, `lbbu_code`, `intern_code`, `pub_code`
- `sandi_bi`
- `tax_type`, `tax_code`, `tax_account_code`, `tax_rate_npwp`, `tax_rate_non_npwp`, `tax_flag_pph21`, `tax_flag_expert`
- `normal_balance_type_def`, `is_zero_balance_def`, `trx_permit_type_def`
- `isrpvrakreportshow`, `is_hidden_offbalancesheet`, `israkaccount`

Read-only:

- `account_code`, `time_create`, `isactivaoffbalancesheet`, `isrpvaccount`, `fl_parent_account`, `is_detail`

#### Instance `ibcore.accountinstance`

Editable:

- `normal_balance_type`
- `is_zero_balance`
- `trx_permit_type`

Read-only:

- `branch_code`, `currency_code`, seluruh kolom saldo

---

## 5. 🖥️ Frontend Specification

### 5.1 Mockup

Link mockup UI: [FSD_COA_Edit.html](../assets/FSD_COA_Edit.html)

Screenshot Tab `Konfigurasi Pelaporan`

![COA Ubah Rekening 1](../assets/FSD_COA_Edit_ss1.png)

Screenshot Tab `Konfigurasi Saldo & Transaksi`

![COA Ubah Rekening 2](../assets/FSD_COA_Edit_ss2.png)

### 5.2 Frontend Field Mapping

> Catatan: Beberapa label field UI dipetakan ke kolom DB berikut.

#### Form Ubah Rekening (Master `ibcore.account`)

| Field (UI) | Mandatory | DB Column | DB Table | Rules |
|------------|-----------|-----------|----------|--------|
| Kelompok Rekening | M | `account_group_code` | `ibcore.account` | Read-only dari DB |
| Tanggal Pembuatan | M | `time_create` | `ibcore.account` | Read-only dari DB |
| Rekening Administratif Aktiva | O | `isactivaoffbalancesheet` | `ibcore.account` | Read-only dari DB |
| Account RPV | O | `isrpvaccount` | `ibcore.account` | Read-only dari DB |
| Rekening Induk | M | `fl_parent_account` | `ibcore.account` | Read-only. Parent rekening |
| Nama Rekening Induk | M | `account_name` (lookup) | `ibcore.account` | Read-only. Lookup dari `account.account_name` parent |
| Kode Rekening | M | `account_code` | `ibcore.account` | Read-only (PK) |
| Nama Rekening | M | `account_name` | `ibcore.account` | **Editable**. Tidak boleh kosong. Max 200 char |
| Deskripsi Rekening | O | `account_desc` | `ibcore.account` | **Editable**. Max 400 char |
| Grup Rekening | M | `account_type` / `account_group_code`* | `ibcore.account` | **Editable**. Dropdown: reference data dengan kode |
| Detail | O | `is_detail` | `ibcore.account` | Read-only. Posting account indicator |
| Keterhubungan CPA | O | `fl_cpa_accountcode` | `ibcore.account` | **Editable**. Pilih dari referensi CPA |
| LBUS Code | O | `lbus_code` | `ibcore.account` | **Editable**. Pelaporan regulator |
| LBUS Type | O | `lbus_type` | `ibcore.account` | **Editable**. Pelaporan regulator |
| LSMK Code | O | `lsmk_code` | `ibcore.account` | **Editable**. Pelaporan regulator |
| LSMK Type | O | `lsmk_type` | `ibcore.account` | **Editable**. Pelaporan regulator |
| LBBU Code | O | `lbbu_code` | `ibcore.account` | **Editable**. Laporan internal |
| Intern Code | O | `intern_code` | `ibcore.account` | **Editable**. Klasifikasi internal |
| PUB Code | O | `pub_code` | `ibcore.account` | **Editable**. Publikasi/laporan tertentu |
| Sandi BI | O | `sandi_bi` | `ibcore.account` | **Editable**. Max 10 char |
| Tipe Pajak | O | `tax_type` | `ibcore.account` | **Editable**. Dari master pajak |
| Tenaga Ahli | O | `tax_flag_expert` | `ibcore.account` | **Editable**. Default uncheck |
| Kode Pajak | O | `tax_code` | `ibcore.account` | **Editable**. Max 20 char |
| Nomor Akun Pajak | O | `tax_account_code` | `ibcore.account` | **Editable**. Refer ke `account.account_code` dengan `is_detail='T'` |
| Tarif Pajak NPWP | O | `tax_rate_npwp` | `ibcore.account` | **Editable**. Numerik >= 0, default 0.00 |
| Tarif Pajak Non NPWP | O | `tax_rate_non_npwp` | `ibcore.account` | **Editable**. Numerik >= 0, default 0.00 |
| Flag PPh21 | O | `tax_flag_pph21` | `ibcore.account` | **Editable**. Opsional, flag |
| RPV RAK Report Show | O | `isrpvrakreportshow` | `ibcore.account` | **Editable**. Flag tampil report |
| Hidden Offbalance Sheet | O | `is_hidden_offbalancesheet` | `ibcore.account` | **Editable**. Flag |
| RAK Account | O | `israkaccount` | `ibcore.account` | **Editable**. Flag |

\*Catatan: pada dokumen lama ada "Grup Rekening" sebagai klasifikasi laporan (misal ASET). Di schema tersedia `account_group_code` dan `account_type`. Implementasi final perlu konsisten (pilih salah satu atau gabungkan aturan).

---

#### Tab: Parameter Saldo dan Transaksi (Default di `ibcore.account`)

| Field (UI) | Mandatory | DB Column | DB Table | Rules |
|------------|-----------|-----------|----------|--------|
| Saldo Normal (Default) | M | `normal_balance_type_def` | `ibcore.account` | **Editable**. Dropdown: {Debet, Kredit, Netral} (mapping ke kode internal `varchar(1)`) |
| Saldo Harus Nihil (Default) | M | `is_zero_balance_def` | `ibcore.account` | **Editable**. Dropdown: {Boleh Tidak Nihil, Harus Nihil} (mapping `varchar(1)`) |
| Status Transaksi (Default) | M | `trx_permit_type_def` | `ibcore.account` | **Editable**. Dropdown status transaksi (mapping `varchar(1)`) |

##### Button Rules

| Button | Aksi |
|--------|------|
| Set Semua Status Saldo Normal | Update `accountinstance.normal_balance_type` untuk seluruh instance sesuai default yang dipilih |
| Set Semua Status Saldo Nihil | Update `accountinstance.is_zero_balance` untuk seluruh instance sesuai default yang dipilih |
| Set Semua Status Transaksi | Update `accountinstance.trx_permit_type` untuk seluruh instance sesuai default yang dipilih |

---

#### Grid: List Account Instance (`ibcore.accountinstance`)

| Field (UI) | Mandatory | DB Column | DB Table | Lookup Table | Rules |
|------------|-----------|-----------|----------|--------------|--------|
| Kode Kantor | M | `branch_code` | `ibcore.accountinstance` | - | Read-only |
| Nama Kantor | M | `branch_name` (lookup) | `ibent.cabang` | `ibent.cabang` | Read-only, lookup master branch |
| Kode Valuta | M | `currency_code` | `ibcore.accountinstance` | - | Read-only |
| Saldo Normal | M | `normal_balance_type` | `ibcore.accountinstance` | - | **Editable** |
| Saldo Harus Nihil | M | `is_zero_balance` | `ibcore.accountinstance` | - | **Editable** |
| Tipe Bertransaksi | M | `trx_permit_type` | `ibcore.accountinstance` | - | **Editable** |

---

## 6. 🛠️ Backend Specification

### 6.1 API Specification

Base path (contoh): `/api/coa`

#### 6.1.1 Get Detail Rekening (Form Ubah)

**Endpoint:** `GET /api/coa/accounts/{account_code}`

**Tabel yang Diakses (SELECT):**

| Tabel | Operasi | Kolom | Joinlookup |
|-------|---------|-------|----------|
| `ibcore.account` | **SELECT** | Semua kolom (account_code, account_name, account_desc, fl_parent_account, account_group_code, account_type, account_level, is_detail, normal_balance_type_def, is_zero_balance_def, trx_permit_type_def, fl_cpa_accountcode, lbus_code, lbus_type, lsmk_code, lsmk_type, lbbu_code, intern_code, pub_code, sandi_bi, tax_type, tax_code, tax_account_code, tax_rate_npwp, tax_rate_non_npwp, tax_flag_pph21, tax_flag_expert, isactivaoffbalancesheet, isrpvaccount, isrpvrakreportshow, is_hidden_offbalancesheet, israkaccount, userid_create, time_create, userid_last_modified, time_last_modified) | Self-JOIN untuk mendapatkan `parent_account_name` dari `fl_parent_account` |
| `ibcore.accountinstance` | **SELECT** | accountinstance_id, account_code, branch_code, currency_code, normal_balance_type, is_zero_balance, trx_permit_type, isbolehinput, balance_sign | - |
| `ibent.cabang` | **SELECT** (lookup) | branch_code, branch_name | JOIN dengan `accountinstance.branch_code` |
| Master Currency | **SELECT** (lookup) | currency_code, currency_name | JOIN dengan `accountinstance.currency_code` (optional) |

**Response 200**

```json
{
  "account": {
    "account_code": "100100",
    "account_name": "Kas",
    "account_desc": "Kas besar",
    "account_group_code": "ASET",
    "account_type": "A",
    "fl_parent_account": "100000",
    "parent_account_name": "Aktiva",
    "is_detail": "T",
    "time_create": "2026-01-10T08:10:00Z",
    "isactivaoffbalancesheet": "F",
    "isrpvaccount": "F",
    "fl_cpa_accountcode": "CPA001",
    "lbus_code": "LB01",
    "lbus_type": "1",
    "lsmk_code": "LK01",
    "lsmk_type": "1",
    "lbbu_code": "LBBU01",
    "intern_code": "INT01",
    "pub_code": "PUB01",
    "sandi_bi": "1234567890",
    "tax_type": "PPh",
    "tax_code": "TAX01",
    "tax_account_code": "200100",
    "tax_rate_npwp": 0.00,
    "tax_rate_non_npwp": 0.00,
    "tax_flag_pph21": "F",
    "tax_flag_expert": "F",
    "normal_balance_type_def": "D",
    "is_zero_balance_def": "F",
    "trx_permit_type_def": "A",
    "isrpvrakreportshow": "F",
    "is_hidden_offbalancesheet": "F",
    "israkaccount": "F",
    "userid_create": "admin",
    "userid_last_modified": "admin",
    "time_last_modified": "2026-01-15T10:30:00Z"
  },
  "instances": [
    {
      "accountinstance_id": "AI001",
      "branch_code": "001",
      "branch_name": "Kantor Pusat",
      "currency_code": "IDR",
      "normal_balance_type": "D",
      "is_zero_balance": "F",
      "trx_permit_type": "A"
    }
  ]
}
```

**Validasi:**

- `account_code` harus exist di `ibcore.account`
- Jika tidak ditemukan, return error 404 (data not found)

---

#### 6.1.2 Submit Pengajuan Ubah Rekening

**Endpoint:** `POST /api/coa/accounts/{account_code}/change-requests`

**Tabel yang Diakses/Dimodifikasi:**

| Tabel | Operasi | Kolom | Keterangan |
|-------|---------|-------|------------|
| `ibcore.account` | **SELECT** | Semua kolom | Ambil data sebelum perubahan (before) untuk audit |
| `ibcore.accountinstance` | **SELECT** | Semua kolom terkait | Ambil data instance sebelum perubahan (before) |

**Request**

```json
{
  "reason": "Perubahan klasifikasi",
  "changes": {
    "account": {
      "account_name": "Kas Besar",
      "account_desc": "Kas besar utama",
      "account_type": "A",
      "tax_rate_npwp": 1.00,
      "tax_rate_non_npwp": 2.00,
      "normal_balance_type_def": "D",
      "is_zero_balance_def": "F",
      "trx_permit_type_def": "A"
    },
    "account_instances": [
      {
        "accountinstance_id": "AI001",
        "normal_balance_type": "D",
        "is_zero_balance": "F",
        "trx_permit_type": "A"
      }
    ],
    "apply_defaults": {
      "normal_balance_type": false,
      "is_zero_balance": false,
      "trx_permit_type": false
    }
  }
}
```

**Response 201**

```json
{
  "request_id": "CR-COA-20260119-0001",
  "status": "PENDING_APPROVAL"
}
```

**Proses Backend:**

1. Validasi input (field mandatory, format, dll)
2. **SELECT** data existing dari `ibcore.account` dan `ibcore.accountinstance` (before)
3. Commit transaksi

---

#### 6.1.3 Pending List Otorisasi

**Endpoint:** `GET /api/coa/change-requests?status=PENDING_APPROVAL`

**Tabel yang Diakses (SELECT):**



**Response 200**

```json
{
  "items": [
    {
      "request_id": "CR-COA-20260119-0001",
      "account_code": "100100",
      "requested_by": "operator01",
      "requested_at": "2026-01-19T09:00:00Z",
      "status": "PENDING_APPROVAL"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 10,
    "total": 1
  }
}
```

---

#### 6.1.4 Detail Pengajuan (Before/After)

**Endpoint:** `GET /api/coa/change-requests/{request_id}`

**Tabel yang Diakses (SELECT):**



**Response 200**

```json
{
  "request_id": "CR-COA-20260119-0001",
  "account_code": "100100",
  "requested_by": "operator01",
  "requested_at": "2026-01-19T09:00:00Z",
  "status": "PENDING_APPROVAL",
  "reason": "Perubahan klasifikasi",
  "before": { 
    "account": { 
      "account_name": "Kas",
      "account_desc": "Kas besar",
      "tax_rate_npwp": 0.00
    },
    "account_instances": [
      {
        "accountinstance_id": "AI001",
        "normal_balance_type": "D",
        "is_zero_balance": "F",
        "trx_permit_type": "A"
      }
    ]
  },
  "after": { 
    "account": {
      "account_name": "Kas Besar",
      "account_desc": "Kas besar utama",
      "tax_rate_npwp": 1.00
    },
    "account_instances": [
      {
        "accountinstance_id": "AI001",
        "normal_balance_type": "D",
        "is_zero_balance": "F",
        "trx_permit_type": "A"
      }
    ]
  }
}
```

---

#### 6.1.5 Approve Pengajuan

**Endpoint:** `POST /api/coa/change-requests/{request_id}/approve`

**Tabel yang Diakses/Dimodifikasi:**

| Tabel | Operasi | Kolom | Keterangan |
|-------|---------|-------|------------|
| `ibcore.account` | **UPDATE** | Kolom sesuai perubahan (account_name, account_desc, tax_rate_npwp, normal_balance_type_def, dll), userid_last_modified, time_last_modified | Apply perubahan ke master COA |
| `ibcore.accountinstance` | **UPDATE** | normal_balance_type, is_zero_balance, trx_permit_type (per instance yang berubah) | Apply perubahan ke instance COA |

**Request**

```json
{
  "comment": "Data sudah sesuai"
}
```

**Response 200**

```json
{
  "request_id": "CR-COA-20260119-0001",
  "status": "APPROVED"
}
```

**Proses Backend (dalam transaksi atomik):**

1. Validasi input
2. **UPDATE** ibcore.account dengan data perubahan
3. **UPDATE** userid_last_modified, time_last_modified pada ibcore.account
4. **UPDATE** ibcore.accountinstance dengan data perubahan
5. Commit transaksi

---

#### 6.1.6 Reject Pengajuan

**Endpoint:** `POST /api/coa/change-requests/{request_id}/reject`

**Tabel yang Diakses/Dimodifikasi:**



**Request**

```json
{
  "reason": "Data tidak sesuai"
}
```

**Response 200**

```json
{
  "request_id": "CR-COA-20260119-0001",
  "status": "REJECTED"
}
```



---

### 6.2 Backend Data Requirements

#### Entity: `ibcore.account` (Master COA)

**Primary Key:** `account_code`

**Kolom yang Relevan untuk Modul Ubah Rekening:**

| Kolom | Tipe | Editable | Keterangan |
|-------|------|----------|------------|
| `account_code` | varchar | No | Primary Key |
| `account_name` | varchar(200) | Yes | Nama rekening |
| `account_desc` | varchar(400) | Yes | Deskripsi rekening |
| `account_group_code` | varchar | Yes* | Grup rekening |
| `account_type` | varchar(1) | Yes* | Tipe rekening |
| `account_level` | integer | No | Level hirarki |
| `fl_parent_account` | varchar | No | FK ke account_code (parent) |
| `is_detail` | varchar(1) | No | Posting account indicator (T/F) |
| `normal_balance_type_def` | varchar(1) | Yes | Saldo normal default (D/K/N) |
| `is_zero_balance_def` | varchar(1) | Yes | Saldo harus nihil default (T/F) |
| `trx_permit_type_def` | varchar(1) | Yes | Status transaksi default |
| `fl_cpa_accountcode` | varchar | Yes | Keterhubungan CPA |
| `lbus_code` | varchar | Yes | Kode LBUS (pelaporan regulator) |
| `lbus_type` | varchar | Yes | Tipe LBUS |
| `lsmk_code` | varchar | Yes | Kode LSMK (pelaporan regulator) |
| `lsmk_type` | varchar | Yes | Tipe LSMK |
| `lbbu_code` | varchar | Yes | Kode LBBU (laporan internal) |
| `intern_code` | varchar | Yes | Kode internal |
| `pub_code` | varchar | Yes | Kode publikasi |
| `sandi_bi` | varchar(10) | Yes | Sandi BI |
| `tax_type` | varchar | Yes | Tipe pajak |
| `tax_code` | varchar(20) | Yes | Kode pajak |
| `tax_account_code` | varchar | Yes | Nomor akun pajak (FK ke account_code) |
| `tax_rate_npwp` | decimal | Yes | Tarif pajak NPWP (>= 0) |
| `tax_rate_non_npwp` | decimal | Yes | Tarif pajak non-NPWP (>= 0) |
| `tax_flag_pph21` | varchar(1) | Yes | Flag PPh21 (T/F) |
| `tax_flag_expert` | varchar(1) | Yes | Flag tenaga ahli (T/F) |
| `isactivaoffbalancesheet` | varchar(1) | No | Rekening adm. aktiva (T/F) |
| `isrpvaccount` | varchar(1) | No | Account RPV (T/F) |
| `isrpvrakreportshow` | varchar(1) | Yes | RPV RAK report show (T/F) |
| `is_hidden_offbalancesheet` | varchar(1) | Yes | Hidden offbalance sheet (T/F) |
| `israkaccount` | varchar(1) | Yes | RAK account (T/F) |
| `userid_create` | varchar | No | User pembuat (audit) |
| `time_create` | timestamp | No | Waktu pembuatan (audit) |
| `userid_last_modified` | varchar | Auto | User terakhir ubah (audit) |
| `time_last_modified` | timestamp | Auto | Waktu terakhir ubah (audit) |

\*Pilih salah satu antara `account_group_code` atau `account_type` sesuai keputusan bisnis

---

#### Entity: `ibcore.accountinstance` (COA per Branch & Currency)

**Primary Key:** `accountinstance_id`

**Kolom yang Relevan untuk Modul Ubah Rekening:**

| Kolom | Tipe | Editable | Keterangan |
|-------|------|----------|------------|
| `accountinstance_id` | varchar | No | Primary Key |
| `account_code` | varchar | No | FK ke ibcore.account |
| `branch_code` | varchar | No | FK ke master branch |
| `currency_code` | varchar | No | FK ke master currency |
| `normal_balance_type` | varchar(1) | Yes | Saldo normal per instance (D/K/N) |
| `is_zero_balance` | varchar(1) | Yes | Saldo harus nihil per instance (T/F) |
| `trx_permit_type` | varchar(1) | Yes | Status transaksi per instance |
| `isbolehinput` | varchar(1) | No | Boleh input manual (T/F) |
| `balance_sign` | varchar(1) | No | Tanda saldo (+/-) |
| `balance` | decimal | No | Saldo (read-only untuk edit COA) |
| `trial_balance` | decimal | No | Trial balance (read-only) |



---

## 7. Validation Rules

### 7.1 Umum

- `account_code` harus exist di `ibcore.account`.
- Field berubah hanya dari whitelist editable.
- `tax_rate_npwp`, `tax_rate_non_npwp` >= 0.00; jika null -> set 0.00.
- Default parameter harus valid: `normal_balance_type_def`, `is_zero_balance_def`, `trx_permit_type_def`.
- Untuk perubahan instance: `accountinstance_id` harus exist dan terkait `account_code`.

### 7.2 Mapping Dropdown

- `normal_balance_type(_def)`: {Debet -> `D`, Kredit -> `K`, Netral -> `N`}
- `is_zero_balance(_def)`: {Boleh Tidak Nihil -> `F`, Harus Nihil -> `T`}
- `trx_permit_type(_def)`: mapping sesuai master (mis. `A`=All, `D`=Debet only, `K`=Kredit only)

---

## 8. Perilaku Tombol "Set Semua"

Ketika user menekan tombol:

- **Set Semua Status Saldo Normal**: `accountinstance.normal_balance_type` diset ke `normal_balance_type_def` untuk seluruh instance.
- **Set Semua Status Saldo Nihil**: `accountinstance.is_zero_balance` diset ke `is_zero_balance_def` untuk seluruh instance.
- **Set Semua Status Transaksi**: `accountinstance.trx_permit_type` diset ke `trx_permit_type_def` untuk seluruh instance.

Implementasi pada submit:

- FE mengisi `apply_defaults` agar BE melakukan override untuk semua instance.
- BE mengisi perubahan per instance (before/after) sebagai bagian pengajuan.

---



---

## 10. Proses Approval

### 10.1 Approve

1. Validasi status masih `PENDING_APPROVAL`.
2. Apply perubahan ke `ibcore.account` (UPDATE field sesuai after_json).
3. Apply perubahan ke `ibcore.accountinstance` (UPDATE field sesuai after_json).
4. Update audit: `userid_last_modified`, `time_last_modified` pada `ibcore.account`.
5. Update status pengajuan ke `APPROVED` dengan `approved_by` dan `approved_at`.

### 10.2 Reject

1. Validasi status masih `PENDING_APPROVAL`.
2. Simpan alasan reject ke `reject_reason`.
3. Update status pengajuan ke `REJECTED` dengan `rejected_by` dan `rejected_at`.
4. **Tidak ada** perubahan ke data aktif (`ibcore.account` dan `ibcore.accountinstance`).

---

## 11. Error Handling

| Code | Scenario | HTTP |
| ---- | -------- | ---- |
| COA-400-01 | Validation error (field invalid) | 400 |
| COA-404-01 | Account not found | 404 |
| COA-404-02 | Accountinstance not found | 404 |
| COA-409-01 | Request status not pending | 409 |
| COA-403-01 | Unauthorized role | 403 |

---

## 12. Logging & Audit

- Log audit untuk submit/approve/reject (user, timestamp, account_code, request_id).
- Simpan before/after dalam bentuk JSON untuk keperluan review otorisasi.
- Update `userid_last_modified` dan `time_last_modified` pada `ibcore.account` saat approve.

---

## 13. Performance & Pagination

- Pending list gunakan pagination default (mis. `page`, `size`).
- Detail pengajuan menampilkan before/after sesuai kebutuhan UI.

---

## 14. Security & Access Control

- **Role Operator Data**: akses GET detail, submit change.
- **Role Otorisator**: akses pending list, detail, approve/reject.
- Endpoint harus validasi user dan role di middleware.

---

## 15. 📌 Shared Business Rules

| Rule ID | Description |
|---------|-------------|
| FR-COA-R01 | `account_code` bersifat **read-only** dan tidak boleh diubah |
| FR-COA-R02 | `fl_parent_account` (rekening induk) bersifat **read-only** pada proses ubah rekening |
| FR-COA-R03 | Semua perubahan wajib melalui **otorisasi** sebelum efektif |
| FR-COA-R04 | Jika pengajuan **Reject**, data aktif pada `account`/`accountinstance` tidak berubah |
| FR-COA-R05 | Perubahan parameter default (di `account`) dapat dipropagasikan ke seluruh `accountinstance` melalui tombol "Set Semua..." |
| FR-COA-R06 | Field tarif pajak (`tax_rate_npwp`, `tax_rate_non_npwp`) tidak boleh negatif dan default 0.00 jika kosong |

---

## 16. Open Questions

| # | Question | Status | Notes |
| --- | -------- | ------ | ----- |
| 1 | | Open | |

---

## 17. Change Log

### v2.0 (2026-01-28)
- Migrasi dan penyesuaian dari FSD_COA_Edit.md (referensi).
- Menambahkan spesifikasi detail tabel database (SELECT/INSERT/UPDATE).
- Menambahkan link mockup dan mapping field UI ke database.
- Sinkronisasi business rules, validation rules, dan scope.
- Penambahan detail operasi database untuk setiap endpoint API.
- Penambahan struktur tabel pengajuan (coa_change_request, coa_change_request_detail).

### v1.0 (2026-01-19)
- Inisialisasi dokumen TSD awal.
