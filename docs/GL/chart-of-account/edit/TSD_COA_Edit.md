# TSD: Ubah Rekening (Chart of Account)

| **Metadata** | |
|--------------|-------------|
| **Module** | COA Management – Ubah Rekening |
| **Parent FSD** | FSD_COA_Edit_v2.md |
| **Version** | 2.0 |
| **Date** | 2026-01-19 |
| **Status** | Draft |
| **Owner** | IT / System Owner |

---

## Change Log (v2.0)

- Migrasi dan penyesuaian dari FSD_COA_Edit_v2.md.
- Sinkronisasi business rules, validation rules, dan scope.

---

## 1. Tujuan & Ruang Lingkup

Dokumen ini menjabarkan spesifikasi teknis implementasi modul **Ubah Rekening (COA)**, mencakup:

- Endpoint backend untuk pengambilan data, submit, dan otorisasi.
- Struktur payload dan mapping field ke schema database.
- Validasi, transaksi, audit, dan logging.
- Perilaku propagasi parameter default ke seluruh `accountinstance`.

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

## 5. API Specification

Base path (contoh): `/api/coa`

### 5.1 Get Detail Rekening (Form Ubah)

`GET /api/coa/accounts/{account_code}`

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
    "israkaccount": "F"
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

### 5.2 Submit Pengajuan Ubah Rekening

`POST /api/coa/accounts/{account_code}/change-requests`

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

### 5.3 Pending List Otorisasi

`GET /api/coa/change-requests?status=PENDING_APPROVAL`

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
  ]
}
```

### 5.4 Detail Pengajuan (Before/After)

`GET /api/coa/change-requests/{request_id}`

**Response 200**

```json
{
  "request_id": "CR-COA-20260119-0001",
  "account_code": "100100",
  "requested_by": "operator01",
  "requested_at": "2026-01-19T09:00:00Z",
  "status": "PENDING_APPROVAL",
  "before": { "account": { }, "account_instances": [ ] },
  "after": { "account": { }, "account_instances": [ ] }
}
```

### 5.5 Approve / Reject

`POST /api/coa/change-requests/{request_id}/approve`

`POST /api/coa/change-requests/{request_id}/reject`

**Request (reject)**

```json
{
  "reason": "Data tidak sesuai"
}
```

**Response 200**

```json
{
  "request_id": "CR-COA-20260119-0001",
  "status": "APPROVED"
}
```

---

## 6. Validation Rules

### 6.1 Umum

- `account_code` harus exist di `ibcore.account`.
- Field berubah hanya dari whitelist editable.
- `tax_rate_npwp`, `tax_rate_non_npwp` >= 0.00; jika null -> set 0.00.
- Default parameter harus valid: `normal_balance_type_def`, `is_zero_balance_def`, `trx_permit_type_def`.
- Untuk perubahan instance: `accountinstance_id` harus exist dan terkait `account_code`.

### 6.2 Mapping Dropdown

- `normal_balance_type(_def)`: {Debet -> `D`, Kredit -> `K`, Netral -> `N`}
- `is_zero_balance(_def)`: {Boleh Tidak Nihil -> `F`, Harus Nihil -> `T`}
- `trx_permit_type(_def)`: mapping sesuai master (mis. `A`=All, `D`=Debet only, `K`=Kredit only)

---

## 7. Perilaku Tombol "Set Semua"

Ketika user menekan tombol:

- **Set Semua Status Saldo Normal**: `accountinstance.normal_balance_type` diset ke `normal_balance_type_def` untuk seluruh instance.
- **Set Semua Status Saldo Nihil**: `accountinstance.is_zero_balance` diset ke `is_zero_balance_def` untuk seluruh instance.
- **Set Semua Status Transaksi**: `accountinstance.trx_permit_type` diset ke `trx_permit_type_def` untuk seluruh instance.

Implementasi pada submit:

- FE mengisi `apply_defaults` agar BE melakukan override untuk semua instance.
- BE mengisi perubahan per instance (before/after) sebagai bagian pengajuan.

---

## 8. Persistensi Pengajuan

### 8.1 Struktur Tabel Pengajuan (konseptual)

Jika modul otorisasi sudah ada, gunakan struktur existing. Jika belum, gunakan tabel konseptual:

- `coa_change_request`
  - `request_id` (PK)
  - `account_code`
  - `status` (PENDING_APPROVAL / APPROVED / REJECTED)
  - `requested_by`, `requested_at`, `approved_by`, `approved_at`, `rejected_by`, `rejected_at`
  - `reason`

- `coa_change_request_detail`
  - `request_id` (FK)
  - `entity_type` (ACCOUNT / ACCOUNT_INSTANCE)
  - `entity_id` (account_code / accountinstance_id)
  - `before_json`
  - `after_json`

### 8.2 Atomicity

- Submit dan Approve harus berjalan dalam transaksi DB.
- Approve meng-update `ibcore.account` dan `ibcore.accountinstance` dalam satu transaksi.

---

## 9. Proses Approval

### 9.1 Approve

- Validasi status masih `PENDING_APPROVAL`.
- Apply perubahan ke `ibcore.account` dan `ibcore.accountinstance`.
- Update audit: `userid_last_modified`, `time_last_modified`.
- Update status pengajuan ke `APPROVED`.

### 9.2 Reject

- Validasi status masih `PENDING_APPROVAL`.
- Simpan alasan reject.
- Update status pengajuan ke `REJECTED`.
- Tidak ada perubahan ke data aktif.

---

## 10. Error Handling

| Code | Scenario | HTTP |
| ---- | -------- | ---- |
| COA-400-01 | Validation error (field invalid) | 400 |
| COA-404-01 | Account not found | 404 |
| COA-404-02 | Accountinstance not found | 404 |
| COA-409-01 | Request status not pending | 409 |
| COA-403-01 | Unauthorized role | 403 |

---

## 11. Logging & Audit

- Log audit untuk submit/approve/reject (user, timestamp, account_code, request_id).
- Simpan before/after dalam bentuk JSON untuk keperluan review otorisasi.

---

## 12. Performance & Pagination

- Pending list gunakan pagination default (mis. `page`, `size`).
- Detail pengajuan menampilkan before/after sesuai kebutuhan UI.

---

## 13. Security & Access Control

- Role Operator Data: akses GET detail, submit change.
- Role Otorisator: akses pending list, detail, approve/reject.
- Endpoint harus validasi user dan role di middleware.

---

## 14. Open Questions

| # | Question | Status | Notes |
| --- | -------- | ------ | ----- |
| 1 | Apakah "Grup Rekening" UI dipetakan ke `account_group_code` atau `account_type`? | Open | Perlu diputuskan agar konsisten |
| 2 | Apakah `reason` wajib untuk setiap submit? | Open | Tergantung policy otorisasi |
| 3 | Menu/layar daftar otorisasi menggunakan modul otorisasi existing atau khusus COA? | Open | Menentukan integrasi flow otorisasi |
