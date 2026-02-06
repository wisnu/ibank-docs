# TSD: Laporan Neraca dan Laba Rugi

| **Metadata** | |
|--------------|-------------|
| **Module** | Laporan Neraca dan Laba Rugi (General Ledger Reporting) |
| **Parent FSD** | FSD_balance-sheet_report.md |
| **Version** | 1.0 |
| **Date** | 2026-02-05 |
| **Status** | Draft |
| **Owner** | IT / System Owner |

---

## 1. Tujuan & Ruang Lingkup

Dokumen ini menjabarkan spesifikasi teknis implementasi modul **Laporan Neraca dan Laba Rugi**, mencakup:

- Endpoint backend untuk generate laporan Neraca dan Laba Rugi dalam format Excel.
- Struktur payload dan mapping field ke schema database.
- Validasi, query data balance, dan konsolidasi multi-currency/multi-branch.
- Detail tabel database yang diakses.
- Mockup frontend dan mapping field UI ke database.

---

## 2. Asumsi & Ketergantungan

- Data balance GL sudah tersedia di `dailybalance` untuk periode yang diminta.
- Exchange rate tersedia di `kurshistory` untuk konversi valuta.
- Master cabang tersedia di `enterprise.cabang`.
- User sudah login dan memiliki hak akses sesuai role.
- File Excel template untuk Neraca dan Laba Rugi sudah tersedia.

---

## 3. Arsitektur Ringkas

- FE memanggil BE service `gl-reporting`.
- BE melakukan validasi parameter, query data balance, konsolidasi (jika diperlukan), format ke Excel.
- Excel file di-download langsung oleh FE.

---

## 4. Model Data & Mapping

### 4.1 Entity Utama

- `dailybalance` (Balance Rekening GL)
  - PK: `dailybalance_id`
  - Unique: (datevalue, accountinstance_id)
- `accountinstance` (Instance Account per Cabang)
  - PK: `accountinstance_id`
- `account` (Master Chart of Account)
  - PK: `account_id`
- `kurshistory` (History Kurs Valuta)
  - PK: `kurshistory_id`
- `enterprise.cabang` (Master Cabang)
  - PK: `kode_cabang`

---

## 5. 🖥️ Frontend Specification

### 5.1 Mockup

Link mockup UI: [neraca.html](./assets/neraca.html)

### 5.2 Frontend Field Mapping

#### Form Generate Laporan Neraca dan Laba / Rugi

| Field (UI) | Mandatory | DB Column / Parameter | DB Table | Rules |
|------------|-----------|----------------------|----------|--------|
| Jenis Laporan | M | `reportType` | - | Parameter API. Dropdown: {Neraca, Laba Rugi} |
| Per Tanggal | M | `asOfDate` | - | Parameter API. Format DD/MM/YYYY. Max = today |
| Konsolidasi Valuta | O | `consolidateCurrency` | - | Parameter API. Checkbox. Default unchecked |
| Valuta | C | `currencyCode` | `kurshistory` | Parameter API. Dropdown: {IDR, USD, EUR, SGD, JPY, CNY}. Conditional required (jika Konsolidasi Valuta tidak checked). Disabled jika Konsolidasi Valuta checked |
| Konsolidasi Cabang | O | `consolidateBranch` | - | Parameter API. Checkbox. Default unchecked |
| Cabang | O | `branchCode` | `enterprise.cabang` | Parameter API. Dropdown: list of branches. Default "-- PILIH SEMUA --". Disabled jika Konsolidasi Cabang checked |

**Field Details:**

**1. Jenis Laporan**
- Type: Select/Dropdown
- Placeholder: "-- PILIH SATU --"
- Options:
  - Neraca
  - Laba Rugi
- Required: Yes
- Mapping: `reportType` = "neraca" | "laba-rugi"

**2. Per Tanggal**
- Type: Text input with date picker
- Placeholder: "DD/MM/YYYY"
- Format: DD/MM/YYYY
- Required: Yes
- Validation:
  - Valid date format
  - Date <= current date
- Mapping: `asOfDate`

**3. Konsolidasi Valuta**
- Type: Checkbox
- Default: Unchecked
- Mapping: `consolidateCurrency` = true | false
- Behavior: When checked, disable Valuta dropdown

**4. Valuta**
- Type: Select/Dropdown
- Default: "Rupiah (IDR)"
- Options:
  - Rupiah (IDR)
  - US Dollar (USD)
  - Euro (EUR)
  - Singapore Dollar (SGD)
  - Japanese Yen (JPY)
  - Chinese Yuan (CNY)
- Mapping: `currencyCode`
- Disabled when: Konsolidasi Valuta is checked

**5. Konsolidasi Cabang**
- Type: Checkbox
- Default: Unchecked
- Mapping: `consolidateBranch` = true | false
- Behavior: When checked, disable Cabang dropdown

**6. Cabang**
- Type: Select/Dropdown
- Default: "-- PILIH SEMUA --"
- Options: Loaded from backend (list of branches)
- Mapping: `branchCode`
- Disabled when: Konsolidasi Cabang is checked

**7. Generate Excel Button**
- Type: Button
- Label: "Generate Excel"
- Icon: 📊
- Action: Submit form and download Excel file

---

## 6. 🛠️ Backend Specification

### 6.1 API Specification

Base path (contoh): `/api/gl/reports`

#### 6.1.1 Generate Laporan Neraca

**Endpoint:** `POST /api/gl/reports/balance-sheet/generate`

**Tabel yang Diakses (SELECT):**

| Tabel | Operasi | Kolom | Join/Lookup |
|-------|---------|-------|-------------|
| `dailybalance` | **SELECT** | dailybalance_id, datevalue, accountinstance_id, debit, credit, balance | WHERE datevalue = asOfDate |
| `accountinstance` | **SELECT** | accountinstance_id, account_id, kode_cabang, currency_code | JOIN dailybalance ON accountinstance_id. Filter by kode_cabang (jika consolidateBranch = false), currency_code (jika consolidateCurrency = false) |
| `account` | **SELECT** | account_id, account_code, account_name, account_type, normal_balance, is_active | JOIN accountinstance ON account_id. WHERE account_type IN ('Asset', 'Liability', 'Equity') |
| `kurshistory` | **SELECT** (conditional) | currency_code, history_date, kurs_tengah_bi | JOIN jika consolidateCurrency = true. WHERE history_date = asOfDate |
| `enterprise.cabang` | **SELECT** (lookup) | kode_cabang, nama_cabang, is_active | JOIN untuk nama cabang (optional) |

**Request**

```json
{
  "reportType": "neraca",
  "asOfDate": "31/12/2025",
  "consolidateCurrency": false,
  "currencyCode": "IDR",
  "consolidateBranch": false,
  "branchCode": "001"
}
```

**Response:** Binary Excel file (.xlsx)

**Proses Backend:**

1. Validasi input parameters:
   - `asOfDate`: format valid DD/MM/YYYY, tidak boleh > current date
   - `currencyCode`: valid jika consolidateCurrency = false
   - `branchCode`: valid jika consolidateBranch = false
2. **Query data balance**:
   - Query dari `dailybalance`  JOIN `accountinstance` JOIN `account` JOIN `enterprise.cabang`
   - Filter by `datevalue = asOfDate`
   - Filter by `account_type IN ('Asset', 'Liability', 'Equity')` (untuk Neraca)
   - Filter by `kode_cabang` via accountinstance (jika consolidateBranch = false)
   - Filter by `currency_code` via accountinstance (jika consolidateCurrency = false)
3. **Konsolidasi Valuta** (jika `consolidateCurrency = true`):
   - Query exchange rate dari `kurshistory` untuk `history_date = asOfDate`
   - Konversi semua balance ke IDR (base currency) menggunakan kurs_tengah_bi
   - Formula: `amount_idr = amount_foreign_currency × kurs_tengah_bi`
   - Aggregate balance per account per cabang (merge semua currency)
   - **Note:** Konsolidasi valuta dapat dilakukan dengan atau tanpa konsolidasi cabang
4. **Konsolidasi Cabang** (jika `consolidateBranch = true`):
   - Aggregate balance per account per currency (merge semua branch)
   - SUM(debit_balance) dan SUM(credit_balance) untuk setiap account
   - **Note:** Konsolidasi cabang dapat dilakukan dengan atau tanpa konsolidasi valuta
4a. **Konsolidasi Penuh** (jika `consolidateCurrency = true` DAN `consolidateBranch = true`):
   - Konversi semua valuta ke IDR
   - Aggregate semua branch
   - Hasil akhir: satu baris per account (total konsolidasi penuh dalam IDR)
4b. **Kombinasi Konsolidasi** - System mendukung 4 skenario:
   - **Skenario 1**: `consolidateCurrency=false`, `consolidateBranch=false` → Report per valuta per cabang (paling detail)
   - **Skenario 2**: `consolidateCurrency=true`, `consolidateBranch=false` → Report dalam IDR per cabang
   - **Skenario 3**: `consolidateCurrency=false`, `consolidateBranch=true` → Report per valuta untuk semua cabang
   - **Skenario 4**: `consolidateCurrency=true`, `consolidateBranch=true` → Report dalam IDR untuk semua cabang (fully consolidated)
5. Grouping account berdasarkan klasifikasi Neraca:
   - AKTIVA (Assets)
   - PASIVA (Liabilities)
   - MODAL (Equity)
6. Calculate subtotal dan grand total
7. Format data ke struktur Excel menggunakan template Neraca
8. Generate file Excel
9. Return file Excel sebagai binary stream dengan Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

**Validation:**

- `reportType` = "neraca" (required)
- `asOfDate` valid format DD/MM/YYYY dan <= current date
- **Currency Validation:**
  - Jika `consolidateCurrency = false`, maka `currencyCode` **REQUIRED** dan harus valid (IDR, USD, EUR, SGD, JPY, CNY)
  - Jika `consolidateCurrency = true`, maka `currencyCode` dapat kosong/diabaikan (system akan konsolidasi semua currency)
- **Branch Validation:**
  - Jika `consolidateBranch = false`, maka `branchCode` optional (kosong = semua cabang dengan access rights user)
  - Jika `consolidateBranch = true`, maka `branchCode` diabaikan (system akan konsolidasi semua cabang)
- **Consolidation Flags:**
  - `consolidateCurrency` dan `consolidateBranch` adalah **independent** (dapat digunakan bersamaan atau terpisah)
  - Default values: `consolidateCurrency = false`, `consolidateBranch = false`

**Exception Handling:**

| Code | Scenario | HTTP | Message |
|------|----------|------|---------|
| RPT-400-01 | Invalid date format | 400 | "Format tanggal tidak valid" |
| RPT-400-02 | Date > current date | 400 | "Tanggal tidak boleh melebihi hari ini" |
| RPT-400-03 | Invalid currency | 400 | "Kode valuta tidak valid" |
| RPT-400-04 | Invalid branch | 400 | "Kode cabang tidak valid" |
| RPT-400-05 | Missing currency when consolidateCurrency=false | 400 | "Parameter currencyCode wajib diisi ketika konsolidasi valuta tidak aktif" |
| RPT-404-01 | No data found | 404 | "Data tidak ditemukan untuk periode yang diminta" |
| RPT-404-02 | Exchange rate not found | 404 | "Kurs tidak tersedia untuk tanggal [date] dan valuta [currency]" |
| RPT-500-01 | System error | 500 | "Gagal generate laporan" |

---

#### 6.1.2 Generate Laporan Laba Rugi

**Endpoint:** `POST /api/gl/reports/income-statement/generate`

**Tabel yang Diakses (SELECT):**

| Tabel | Operasi | Kolom | Join/Lookup |
|-------|---------|-------|-------------|
| `dailybalance` | **SELECT** | dailybalance_id, datevalue, accountinstance_id, debit, credit, balance | WHERE datevalue <= asOfDate |
| `accountinstance` | **SELECT** | accountinstance_id, account_id, kode_cabang, currency_code | JOIN dailybalance ON accountinstance_id. Filter by kode_cabang (jika consolidateBranch = false), currency_code (jika consolidateCurrency = false) |
| `account` | **SELECT** | account_id, account_code, account_name, account_type, normal_balance, is_active | JOIN accountinstance ON account_id. WHERE account_type IN ('Income', 'Expense') |
| `kurshistory` | **SELECT** (conditional) | currency_code, history_date, kurs_tengah_bi | JOIN jika consolidateCurrency = true. WHERE history_date = asOfDate |
| `enterprise.cabang` | **SELECT** (lookup) | kode_cabang, nama_cabang, is_active | JOIN untuk nama cabang (optional) |

**Request**

```json
{
  "reportType": "laba-rugi",
  "asOfDate": "31/12/2025",
  "consolidateCurrency": true,
  "consolidateBranch": true
}
```

**Response:** Binary Excel file (.xlsx)

**Proses Backend:**

1. Validasi input parameters (sama seperti Neraca)
2. **Query data balance**:
   - Query dari `dailybalance` JOIN `accountinstance` JOIN `account` JOIN `enterprise.cabang`
   - Filter by `datevalue <= asOfDate` (period-to-date dari awal tahun buku)
   - Filter by `account_type IN ('Income', 'Expense')` (untuk Laba Rugi)
   - Filter by `kode_cabang` via accountinstance (jika consolidateBranch = false)
   - Filter by `currency_code` via accountinstance (jika consolidateCurrency = false)
3. **Konsolidasi Valuta** (jika `consolidateCurrency = true`):
   - Query exchange rate dari `kurshistory` untuk `history_date = asOfDate`
   - Konversi semua balance ke IDR (base currency)
   - Formula: `amount_idr = amount_foreign_currency × kurs_tengah_bi`
   - Aggregate balance per account per cabang (merge semua currency)
4. **Konsolidasi Cabang** (jika `consolidateBranch = true`):
   - Aggregate balance per account per currency (merge semua branch)
   - SUM(debit_balance) dan SUM(credit_balance) untuk setiap account
4a. **Konsolidasi Penuh** (jika keduanya `= true`):
   - Konversi semua valuta ke IDR + Aggregate semua branch
   - Hasil: satu baris per account (consolidated)
4b. **Kombinasi Konsolidasi**: System mendukung 4 skenario yang sama dengan Neraca (lihat section 6.1.1)
5. Grouping account berdasarkan klasifikasi Laba Rugi:
   - PENDAPATAN (Income/Revenue)
   - BEBAN (Expenses)
6. Calculate subtotal, laba/rugi bersih (net income/loss)
7. Format data ke struktur Excel menggunakan template Laba Rugi
8. Generate file Excel
9. Return file Excel sebagai binary stream

**Validation:**

- `reportType` = "laba-rugi" (required)
- `asOfDate` valid format DD/MM/YYYY dan <= current date
- **Currency Validation:**
  - Jika `consolidateCurrency = false`, maka `currencyCode` **REQUIRED** dan harus valid (IDR, USD, EUR, SGD, JPY, CNY)
  - Jika `consolidateCurrency = true`, maka `currencyCode` dapat kosong/diabaikan
- **Branch Validation:**
  - Jika `consolidateBranch = false`, maka `branchCode` optional
  - Jika `consolidateBranch = true`, maka `branchCode` diabaikan
- **Consolidation Flags:** Independent, dapat dikombinasikan

**Exception Handling:**

Same as Neraca (section 6.1.1)

---

#### 6.1.3 API Endpoint untuk Data Lookup (Dropdown)

> [!NOTE]
> Backend harus menyediakan endpoint untuk load data dropdown secara dynamic (Currency dan Cabang).

**Base Endpoint:** `/api/gl/reports/lookup`

##### Get Currency List

**Endpoint:** `GET /api/gl/reports/lookup/currencies` atau menggunakan GraphQL query `GetCurrencyList`

**Query Type:** `GetCurrencyList`

**Purpose:** Load daftar valuta untuk dropdown "Valuta"

**Request:**

```http
GET /api/gl/reports/lookup/currencies
```

Atau via GraphQL:
```graphql
query GetCurrencyList {
  GetCurrencyList {
    currency_code
    currency_name
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "currency_code": "IDR",
      "currency_name": "Rupiah"
    },
    {
      "currency_code": "USD",
      "currency_name": "US Dollar"
    },
    {
      "currency_code": "EUR",
      "currency_name": "Euro"
    },
    {
      "currency_code": "SGD",
      "currency_name": "Singapore Dollar"
    },
    {
      "currency_code": "JPY",
      "currency_name": "Japanese Yen"
    },
    {
      "currency_code": "CNY",
      "currency_name": "Chinese Yuan"
    }
  ]
}
```

**Business Logic:**
- Return list of supported currencies for balance sheet reporting
- Only return active currencies
- Sort by standard order: IDR first, then alphabetically

**Database Query:**

```sql
SELECT currency_code, currency_name
FROM kurshistory
WHERE currency_code IN ('IDR', 'USD', 'EUR', 'SGD', 'JPY', 'CNY')
  AND history_date = (SELECT MAX(history_date) FROM kurshistory)
  AND is_active = true
ORDER BY 
  CASE currency_code
    WHEN 'IDR' THEN 1
    WHEN 'USD' THEN 2
    WHEN 'EUR' THEN 3
    WHEN 'SGD' THEN 4
    WHEN 'JPY' THEN 5
    WHEN 'CNY' THEN 6
  END;
```

**Alternative: Static Dropdown (Recommended)**

Frontend dapat menggunakan static dropdown options karena daftar currency fixed:

```typescript
const CURRENCY_OPTIONS = [
  { value: 'IDR', label: 'Rupiah (IDR)' },
  { value: 'USD', label: 'US Dollar (USD)' },
  { value: 'EUR', label: 'Euro (EUR)' },
  { value: 'SGD', label: 'Singapore Dollar (SGD)' },
  { value: 'JPY', label: 'Japanese Yen (JPY)' },
  { value: 'CNY', label: 'Chinese Yuan (CNY)' },
];
```

---

##### Get Branch List

**Endpoint:** `GET /api/gl/reports/lookup/branches`

**Purpose:** Load daftar cabang untuk dropdown "Cabang" berdasarkan user access rights

**Request:**

```http
GET /api/gl/reports/lookup/branches
```

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "branch_code": "001",
      "branch_name": "Cabang Jakarta Pusat"
    },
    {
      "branch_code": "002",
      "branch_name": "Cabang Bandung"
    },
    {
      "branch_code": "003",
      "branch_name": "Cabang Surabaya"
    }
  ]
}
```

**Business Logic:**
- Return list of branches based on user's access rights (dari JWT token atau session)
- Only return active branches (`is_active = true`)
- Sort by `branch_code` ascending
- If user has access to all branches, return all active branches

**Database Query:**

```sql
SELECT kode_cabang, nama_cabang
FROM enterprise.cabang
WHERE is_active = true
  AND branch_code IN (
    SELECT kode_cabang 
    FROM user_branch_access 
    WHERE user_id = :user_id
  )
ORDER BY kode_cabang ASC;
```

**Error Handling:**

| Scenario | HTTP | Message |
|----------|------|---------|
| No branch access | 403 | "User tidak memiliki akses ke cabang manapun" |
| Database error | 500 | "Gagal mengambil data cabang" |

---

### 6.2 Backend Data Requirements

#### Entity: `dailybalance` (Daily Account Balance)

**Primary Key:** `dailybalance_id`

**Unique Constraint:** (datevalue, accountinstance_id)

**Kolom yang Relevan:**

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `dailybalance_id` | bigint | ID balance record (PK) |
| `datevalue` | date | Tanggal balance |
| `accountinstance_id` | bigint | ID instance account (FK ke accountinstance) |
| `debit` | decimal(18,2) | Saldo debit |
| `credit` | decimal(18,2) | Saldo kredit |
| `balance` | decimal(18,2) | Saldo bersih (debit - credit) |

**Join Relationships:**
- `accountinstance` → untuk mendapatkan account details dan cabang
- Filter by `datevalue = asOfDate` untuk Neraca
- Filter by `datevalue <= asOfDate` untuk Laba Rugi (period-to-date)

---

#### Entity: `accountinstance` (Account Instance per Cabang)

**Primary Key:** `accountinstance_id`

**Kolom yang Relevan:**

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `accountinstance_id` | bigint | ID instance (PK) |
| `account_id` | bigint | ID account (FK ke account) |
| `kode_cabang` | varchar(10) | Kode cabang (FK ke enterprise.cabang) |
| `currency_code` | varchar(3) | Kode valuta untuk instance ini |
| `is_active` | boolean | Status aktif |

**Purpose:**
- Memetakan account ke specific cabang dan currency
- Satu account bisa punya multiple instances (per cabang, per currency)

---

#### Entity: `account` (Master Chart of Account)

**Primary Key:** `account_id`

**Kolom yang Relevan:**

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `account_id` | bigint | ID account (PK) |
| `account_code` | varchar(20) | Kode rekening |
| `account_name` | varchar(255) | Nama rekening |
| `account_type` | varchar(50) | Tipe rekening (Asset, Liability, Equity, Income, Expense) |
| `normal_balance` | varchar(10) | Saldo normal (Debit/Credit) |
| `is_active` | boolean | Status aktif |

---

#### Entity: `kurshistory` (Exchange Rate History)

**Primary Key:** `kurshistory_id`

**Kolom yang Relevan:**

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `kurshistory_id` | bigint | ID kurs record (PK) |
| `currency_code` | varchar(3) | Kode valuta (USD, EUR, SGD, JPY, CNY) |
| `history_date` | date | Tanggal kurs |
| `kurs_tengah_bi` | decimal(18,6) | Kurs tengah BI terhadap IDR |

**Logic Konversi:**
- Balance dalam IDR = Balance dalam foreign currency × kurs_tengah_bi
- Contoh: 100 USD × 15,000 = 1,500,000 IDR
- Untuk konsolidasi valuta, query kurs pada `history_date = asOfDate`

---

#### Entity: `enterprise.cabang` (Master Cabang)

**Primary Key:** `kode_cabang`

**Kolom yang Relevan:**

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `kode_cabang` | varchar(10) | Kode cabang (PK) |
| `nama_cabang` | varchar(255) | Nama cabang |
| `is_active` | boolean | Status aktif |

**Access Control:**
- User hanya bisa akses cabang sesuai with user_branch_access mapping

---

## 7. Validation Rules

### 7.1 Input Validation

| Parameter | Rule |
|-----------|------|
| `reportType` | Required. Must be "neraca" or "laba-rugi" |
| `asOfDate` | Required. Format DD/MM/YYYY. Must be <= current date |
| `consolidateCurrency` | Boolean. Default false |
| `currencyCode` | Conditional required (if consolidateCurrency = false). Must be valid currency code: IDR, USD, EUR, SGD, JPY, CNY |
| `consolidateBranch` | Boolean. Default false |
| `branchCode` | Optional. Must be valid branch code if provided |

### 7.2 Business Logic Validation

**BR-001: Jenis Laporan**
- Sistem harus menyediakan dua jenis laporan: Neraca dan Laba Rugi
- User harus memilih salah satu jenis laporan sebelum generate

**BR-002: Per Tanggal**
- Neraca menampilkan posisi keuangan pada tanggal tertentu (as of date)
- Laba Rugi menampilkan kinerja keuangan period-to-date (dari awal tahun buku sampai tanggal laporan)
- Format tanggal: DD/MM/YYYY
- Tanggal tidak boleh melebihi tanggal hari ini

**BR-003: Konsolidasi Valuta**
- Jika "Konsolidasi Valuta" dicentang, sistem mengkonsolidasikan semua valuta ke dalam satu laporan (base currency = IDR)
- Jika tidak dicentang, user harus memilih valuta spesifik (field required)
- Konversi valuta menggunakan kurs yang berlaku pada tanggal laporan (closing rate)
- **Independent dari Konsolidasi Cabang**: dapat digunakan bersamaan atau terpisah

**BR-004: Valuta**
- Sistem mendukung multi-currency: IDR, USD, EUR, SGD, JPY, CNY
- Default currency adalah IDR (Rupiah)
- Field Valuta menjadi disabled jika "Konsolidasi Valuta" dicentang
- **Field required** jika Konsolidasi Valuta tidak dicentang

**BR-005: Konsolidasi Cabang**
- Jika "Konsolidasi Cabang" dicentang, sistem mengkonsolidasikan semua cabang
- Jika tidak dicentang, user dapat memilih cabang spesifik atau mengosongkan untuk semua cabang yang dapat diakses
- Field Cabang menjadi disabled jika "Konsolidasi Cabang" dicentang
- **Independent dari Konsolidasi Valuta**: dapat digunakan bersamaan atau terpisah

**BR-006: Cabang**
- User dapat memilih satu cabang atau semua cabang (via opsi "-- PILIH SEMUA --")
- List cabang di dropdown sesuai dengan hak akses cabang user
- Default option adalah "-- PILIH SEMUA --" (semua cabang yang dapat diakses)
- Field optional: tidak wajib dipilih

**BR-007: Output Format**
- Laporan di-generate dalam format Excel (.xlsx)
- File Excel harus dapat langsung di-download oleh user

**BR-008: Kombinasi Konsolidasi**
- Sistem mendukung 4 skenario konsolidasi:
  1. **Tidak ada konsolidasi** (`consolidateCurrency=false`, `consolidateBranch=false`): Laporan per valuta per cabang (paling detail)
  2. **Konsolidasi Valuta saja** (`consolidateCurrency=true`, `consolidateBranch=false`): Laporan dalam IDR per cabang
  3. **Konsolidasi Cabang saja** (`consolidateCurrency=false`, `consolidateBranch=true`): Laporan per valuta untuk semua cabang
  4. **Konsolidasi Penuh** (`consolidateCurrency=true`, `consolidateBranch=true`): Laporan dalam IDR untuk semua cabang (fully consolidated)

---

## 8. Excel Output Specification

### 8.1 Laporan Neraca

**Struktur:**

```
LAPORAN NERACA
PT. [NAMA BANK]
Per Tanggal: [DD/MM/YYYY]
Valuta: [Currency] / Konsolidasi
Cabang: [Branch] / Konsolidasi

I. AKTIVA
   1. Kas                           XXX,XXX.XX
   2. Bank                          XXX,XXX.XX
   ...
   TOTAL AKTIVA                     XXX,XXX.XX

II. PASIVA
   1. Hutang                        XXX,XXX.XX
   2. Lainnya                       XXX,XXX.XX
   ...
   TOTAL PASIVA                     XXX,XXX.XX

III. MODAL
   1. Modal Saham                   XXX,XXX.XX
   2. Laba Ditahan                  XXX,XXX.XX
   ...
   TOTAL MODAL                      XXX,XXX.XX

TOTAL PASIVA + MODAL                XXX,XXX.XX
```

**Format:**
- Font: Arial 10pt
- Header: Bold, center aligned
- Account names: Left aligned
- Amounts: Right aligned, number format with thousand separator
- Subtotals: Bold
- Grand totals: Bold, double underline

---

### 8.2 Laporan Laba Rugi

**Struktur:**

```
LAPORAN LABA RUGI
PT. [NAMA BANK]
Periode: 01/01/YYYY s/d [DD/MM/YYYY]
Valuta: [Currency] / Konsolidasi
Cabang: [Branch] / Konsolidasi

I. PENDAPATAN
   1. Bunga                         XXX,XXX.XX
   2. Provisi                       XXX,XXX.XX
   ...
   TOTAL PENDAPATAN                 XXX,XXX.XX

II. BEBAN
   1. Beban Bunga                   XXX,XXX.XX
   2. Beban Operasional             XXX,XXX.XX
   ...
   TOTAL BEBAN                      XXX,XXX.XX

LABA/RUGI BERSIH                    XXX,XXX.XX
```

**Format:**
- Same as Neraca

---

## 9. Error Handling

| Code | Scenario | HTTP | Message |
| ---- | -------- | ---- | ------- |
| RPT-400-01 | Invalid date format | 400 | "Format tanggal tidak valid" |
| RPT-400-02 | Date > current date | 400 | "Tanggal tidak boleh melebihi hari ini" |
| RPT-400-03 | Invalid currency code | 400 | "Kode valuta tidak valid" |
| RPT-400-04 | Invalid branch code | 400 | "Kode cabang tidak valid" |
| RPT-400-05 | Missing required parameter | 400 | "Parameter [nama] wajib diisi" |
| RPT-404-01 | No data found | 404 | "Data tidak ditemukan untuk periode yang diminta" |
| RPT-404-02 | Exchange rate not found | 404 | "Kurs tidak tersedia untuk tanggal [date]" |
| RPT-500-01 | Excel generation error | 500 | "Gagal generate file Excel" |
| RPT-500-02 | Database error | 500 | "Gagal mengambil data dari database" |

---

## 10. Logging & Audit

- Log setiap request generate laporan dengan detail:
  - User ID
  - Timestamp
  - Report type (Neraca / Laba Rugi)
  - Parameters (asOfDate, currency, branch, consolidation flags)
  - Result (success / error code)
- Log performance metrics:
  - Query execution time
  - Excel generation time
  - Total request processing time

---

## 11. Performance & Optimization

### 11.1 Query Optimization

- Index pada `dailybalance` untuk kolom: (datevalue, accountinstance_id)
- Index pada `accountinstance` untuk kolom: (account_id, kode_cabang, currency_code)
- Index pada `kurshistory` untuk kolom: (history_date, currency_code)
- Use prepared statements untuk query
- Limit result set jika data terlalu besar (warning ke user)

### 11.2 Excel Generation

- Use streaming untuk generate Excel (jangan load semua data ke memory)
- Set timeout untuk request (max 60 seconds)
- Implement caching untuk master data (branch, currency)

---

## 12. Security & Access Control

- **Role Operator Data**: akses generate laporan
- **Role Otorisator**: akses generate laporan
- **Role Supervisor / Manager**: akses generate laporan
- Endpoint harus validasi user dan role di middleware
- Validasi branch access: user hanya bisa generate laporan untuk branch yang diizinkan
- Logging untuk audit trail

---

## 13. 📌 Shared Business Rules

| Rule ID | Description |
|---------|-------------|
| FR-RPT-R01 | Semua laporan keuangan harus menggunakan **format Excel (.xlsx)** |
| FR-RPT-R02 | Tanggal laporan **tidak boleh melebihi tanggal hari ini** |
| FR-RPT-R03 | Konversi valuta menggunakan **kurs pada tanggal laporan** (closing rate) |
| FR-RPT-R04 | Laporan Neraca menampilkan **posisi keuangan pada tanggal tertentu** (as of date) |
| FR-RPT-R05 | Laporan Laba Rugi menampilkan **kinerja keuangan period-to-date** (dari awal tahun buku sampai tanggal laporan) |
| FR-RPT-R06 | Jika data tidak ditemukan, sistem harus memberikan **error message yang jelas** |
| FR-RPT-R07 | User hanya dapat generate laporan untuk **cabang yang diizinkan** sesuai access rights |

---

## 14. Open Questions

| # | Question | Status | Notes |
| --- | -------- | ------ | ----- |
| 1 | Konfirmasi template Excel untuk laporan Neraca dan Laba Rugi | Open | Business Analyst perlu provide template final |

---

## 15. Change Log

| Date | Description | Author |
|------|-------------|--------|
| 2026-02-05 | Initial TSD draft - converted from FSD_balance-sheet_report.md | System Analyst |

