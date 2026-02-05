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

- Data transaksi GL sudah tersedia di `gl_account_balance` untuk periode yang diminta.
- Exchange rate tersedia di `currency_exchange_rate` untuk konversi valuta.
- Master branch tersedia di `branch`.
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

- `gl_account_balance` (Balance Rekening GL)
  - PK: composite (account_id, balance_date, currency_code, branch_code)
- `currency_exchange_rate` (Kurs Valuta)
  - PK: composite (currency_code, rate_date)
- `branch` (Master Cabang)
  - PK: `branch_code`

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
| Valuta | C | `currencyCode` | `currency_exchange_rate` | Parameter API. Dropdown: {IDR, USD, EUR, SGD, JPY, CNY}. Conditional required (jika Konsolidasi Valuta tidak checked). Disabled jika Konsolidasi Valuta checked |
| Konsolidasi Cabang | O | `consolidateBranch` | - | Parameter API. Checkbox. Default unchecked |
| Cabang | O | `branchCode` | `branch` | Parameter API. Dropdown: list of branches. Default "-- PILIH SEMUA --". Disabled jika Konsolidasi Cabang checked |

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
| `gl_account_balance` | **SELECT** | account_id, account_code, account_name, account_type, currency_code, branch_code, balance_date, debit_balance, credit_balance, balance_amount | WHERE balance_date = asOfDate AND (branch_code = branchCode OR consolidateBranch = true) AND (currency_code = currencyCode OR consolidateCurrency = true) AND account_type IN ('Asset', 'Liability', 'Equity') |
| `currency_exchange_rate` | **SELECT** (conditional) | currency_code, rate_date, exchange_rate | JOIN jika consolidateCurrency = true. WHERE rate_date = asOfDate |
| `branch` | **SELECT** (lookup) | branch_code, branch_name, is_active | JOIN untuk nama cabang (optional) |

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
2. Query data dari `gl_account_balance`:
   - Filter by `balance_date = asOfDate`
   - Filter by `account_type IN ('Asset', 'Liability', 'Equity')`
   - Filter by `branch_code` (jika consolidateBranch = false)
   - Filter by `currency_code` (jika consolidateCurrency = false)
3. Jika `consolidateCurrency = true`:
   - Query exchange rate dari `currency_exchange_rate` untuk `rate_date = asOfDate`
   - Konversi semua balance ke IDR (base currency) menggunakan exchange_rate
   - Aggregate balance per account
4. Jika `consolidateBranch = true`:
   - Aggregate balance per account across all branches
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
- Jika `consolidateCurrency = false`, maka `currencyCode` required dan valid
- Jika `consolidateBranch = false`, maka `branchCode` harus valid (optional)

**Exception Handling:**

| Code | Scenario | HTTP | Message |
|------|----------|------|---------|
| RPT-400-01 | Invalid date format | 400 | "Format tanggal tidak valid" |
| RPT-400-02 | Date > current date | 400 | "Tanggal tidak boleh melebihi hari ini" |
| RPT-400-03 | Invalid currency | 400 | "Kode valuta tidak valid" |
| RPT-400-04 | Invalid branch | 400 | "Kode cabang tidak valid" |
| RPT-404-01 | No data found | 404 | "Data tidak ditemukan untuk periode yang diminta" |
| RPT-500-01 | System error | 500 | "Gagal generate laporan" |

---

#### 6.1.2 Generate Laporan Laba Rugi

**Endpoint:** `POST /api/gl/reports/income-statement/generate`

**Tabel yang Diakses (SELECT):**

| Tabel | Operasi | Kolom | Join/Lookup |
|-------|---------|-------|-------------|
| `gl_account_balance` | **SELECT** | account_id, account_code, account_name, account_type, currency_code, branch_code, balance_date, debit_balance, credit_balance, balance_amount | WHERE balance_date <= asOfDate AND balance_date >= start_of_fiscal_year AND (branch_code = branchCode OR consolidateBranch = true) AND (currency_code = currencyCode OR consolidateCurrency = true) AND account_type IN ('Income', 'Expense') |
| `currency_exchange_rate` | **SELECT** (conditional) | currency_code, rate_date, exchange_rate | JOIN jika consolidateCurrency = true. WHERE rate_date = asOfDate |
| `branch` | **SELECT** (lookup) | branch_code, branch_name, is_active | JOIN untuk nama cabang (optional) |

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
2. Query data dari `gl_account_balance`:
   - Filter by `balance_date <= asOfDate` AND `balance_date >= start_of_fiscal_year` (period-to-date)
   - Filter by `account_type IN ('Income', 'Expense')`
   - Filter by `branch_code` (jika consolidateBranch = false)
   - Filter by `currency_code` (jika consolidateCurrency = false)
3. Jika `consolidateCurrency = true`:
   - Query exchange rate dari `currency_exchange_rate` untuk `rate_date = asOfDate`
   - Konversi semua balance ke IDR (base currency)
   - Aggregate balance per account
4. Jika `consolidateBranch = true`:
   - Aggregate balance per account across all branches
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
- Jika `consolidateCurrency = false`, maka `currencyCode` required dan valid
- Jika `consolidateBranch = false`, maka `branchCode` harus valid (optional)

**Exception Handling:**

Same as Neraca (section 6.1.1)

---

### 6.2 Backend Data Requirements

#### Entity: `gl_account_balance` (Account Balance)

**Primary Key:** Composite (account_id, balance_date, currency_code, branch_code)

**Kolom yang Relevan:**

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `account_id` | varchar(20) | ID rekening GL |
| `account_code` | varchar(20) | Kode rekening |
| `account_name` | varchar(255) | Nama rekening |
| `account_type` | varchar(50) | Tipe rekening (Asset, Liability, Equity, Income, Expense) |
| `currency_code` | varchar(3) | Kode valuta (IDR, USD, EUR, SGD, JPY, CNY) |
| `branch_code` | varchar(10) | Kode cabang |
| `balance_date` | date | Tanggal balance |
| `debit_balance` | decimal(18,2) | Saldo debit |
| `credit_balance` | decimal(18,2) | Saldo kredit |
| `balance_amount` | decimal(18,2) | Saldo bersih |

---

#### Entity: `currency_exchange_rate` (Exchange Rate)

**Primary Key:** Composite (currency_code, rate_date)

**Kolom yang Relevan:**

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `currency_code` | varchar(3) | Kode valuta (USD, EUR, SGD, JPY, CNY) |
| `currency_name` | varchar(100) | Nama valuta |
| `rate_date` | date | Tanggal kurs |
| `exchange_rate` | decimal(18,6) | Kurs terhadap IDR (1 foreign currency = X IDR) |

**Logic Konversi:**
- Balance dalam IDR = Balance dalam foreign currency × exchange_rate
- Contoh: 100 USD × 15,000 = 1,500,000 IDR

---

#### Entity: `branch` (Master Cabang)

**Primary Key:** `branch_code`

**Kolom yang Relevan:**

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `branch_code` | varchar(10) | Kode cabang (PK) |
| `branch_name` | varchar(255) | Nama cabang |
| `is_active` | boolean | Status aktif |

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
- System must provide two report types: Neraca and Laba Rugi
- User must select one report type before generate

**BR-002: Per Tanggal**
- Neraca displays financial position as of specific date
- Laba Rugi displays financial performance up to specific date (period-to-date from start of fiscal year)
- Date format: DD/MM/YYYY
- Date must not exceed current date

**BR-003: Konsolidasi Valuta**
- If "Konsolidasi Valuta" checked, system consolidates all currencies into one report (base currency = IDR)
- If not checked, user must select specific currency
- Currency conversion uses exchange rate valid on report date

**BR-004: Valuta**
- System supports multi-currency: IDR, USD, EUR, SGD, JPY, CNY
- Default currency is IDR (Rupiah)
- Valuta field becomes disabled if "Konsolidasi Valuta" is checked

**BR-005: Konsolidasi Cabang**
- If "Konsolidasi Cabang" checked, system consolidates all branches
- If not checked, user can select specific branch
- Cabang field becomes disabled if "Konsolidasi Cabang" is checked

**BR-006: Cabang**
- User can select one or all branches
- List of branches in dropdown according to user's branch access rights
- Default option is user's branch code
- If user only has access to one branch, "Konsolidasi Cabang" field becomes disabled

**BR-007: Output Format**
- Report generated in Excel format (.xlsx)
- Excel file must be directly downloadable by user

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

- Index pada `gl_account_balance` untuk kolom: (balance_date, account_type, branch_code, currency_code)
- Index pada `currency_exchange_rate` untuk kolom: (rate_date, currency_code)
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
| 2 | Definisi akun-akun yang masuk kategori Aktiva, Pasiva, Modal, Pendapatan, Beban | Open | Business Analyst perlu provide mapping `account_type` |
| 3 | Logic perhitungan konsolidasi valuta: kurs yang digunakan (closing rate, average rate, atau historical rate)? | Open | Finance Team perlu konfirmasi. Saat ini assume closing rate |
| 4 | Start of fiscal year (untuk Laba Rugi period-to-date): bagaimana cara determine? Apakah fixed 01 Januari atau configurable? | Open | Business Owner perlu konfirmasi |
| 5 | Apakah perlu fitur export ke PDF selain Excel? | Open | Business Owner |
| 6 | Apakah perlu print preview sebelum download? | Open | Business Owner |
| 7 | Maximum data size: berapa limit untuk warning jika data terlalu besar? | Open | Technical Team |

---

## 15. Change Log

| Date | Description | Author |
|------|-------------|--------|
| 2026-02-05 | Initial TSD draft - converted from FSD_balance-sheet_report.md | System Analyst |

