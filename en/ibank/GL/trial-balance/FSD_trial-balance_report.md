
# FSD – Laporan Trial Balance

## Document Metadata

| Item | Value |
|------|-------|
| Module | Laporan Trial Balance (General Ledger Reporting) |
| Parent FSD | FSD_trial-balance_report |
| Version | 1.0 |
| Date | 2026-01-28 |
| Status | Draft |
| Owner | IT / System Owner |
| Notes | Dokumen terpusat FSD (Backend + Frontend) dengan struktur berlapis |

---

## 1. Overview & Scope

Modul **Laporan Trial Balance** digunakan untuk menghasilkan laporan trial balance (neraca saldo) yang menampilkan saldo debit dan kredit seluruh rekening GL dalam periode tertentu.

**Cakupan fungsi:**
- Generate laporan Trial Balance untuk rentang tanggal tertentu (dari-sampai)
- Filter laporan berdasarkan valuta (currency)
- Filter laporan berdasarkan cabang (branch)
- Konsolidasi data berdasarkan valuta (multi-currency consolidation)
- Konsolidasi data berdasarkan cabang (multi-branch consolidation)
- Filter untuk menampilkan hanya rekening yang memiliki saldo
- Export laporan ke format Excel

---

## 2. Actors & Roles

| Actor | Description |
|------|------------|
| Operator Data | User yang dapat melihat dan generate laporan trial balance |
| Otorisator | User yang dapat melihat dan generate laporan trial balance |
| Supervisor / Manager | User yang dapat melihat dan generate laporan trial balance |

---

## 3. Business Rules

**BR-001: Periode Tanggal**
- Laporan Trial Balance menggunakan rentang tanggal (Mulai Tanggal - Hingga Tanggal)
- Format tanggal: DD/MM/YYYY
- "Mulai Tanggal" tidak boleh lebih besar dari "Hingga Tanggal"
- "Hingga Tanggal" tidak boleh melebihi tanggal hari ini
- Kedua field tanggal bersifat required

**BR-002: Konsolidasi Valuta**
- Jika checkbox "Konsolidasi Valuta" dicentang, sistem mengkonsolidasikan semua valuta ke dalam satu laporan
- Jika checkbox tidak dicentang, user harus memilih satu valuta spesifik
- Konversi valuta menggunakan kurs yang berlaku pada akhir periode (Hingga Tanggal)

**BR-003: Valuta**
- Sistem mendukung multi-currency: IDR, USD, EUR, SGD
- Default valuta adalah IDR (Rupiah)
- Field valuta menjadi disabled jika "Konsolidasi Valuta" dicentang
- Placeholder dropdown: "-- PILIH VALUTA --"

**BR-004: Konsolidasi Cabang**
- Jika checkbox "Konsolidasi Cabang" dicentang, sistem mengkonsolidasikan semua cabang
- Jika checkbox tidak dicentang, user dapat memilih cabang spesifik
- Field cabang menjadi disabled jika "Konsolidasi Cabang" dicentang
- Jika user hanya boleh akses ke satu cabang, maka field "Konsolidasi Cabang" menjadi disabled

**BR-005: Cabang**
- User dapat memilih satu atau semua cabang
- List Cabang yang tampil di dropdown sesuai tipe hak akses cabang yang diatur
- Default option adalah kode cabang sesuai user yang login
- Placeholder dropdown: "-- PILIH SEMUA --"
- Jika user hanya boleh akses ke satu cabang, maka field "Cabang" menjadi disabled

**BR-006: Filter Saldo**
- Checkbox "Tampilkan hanya yang memiliki saldo" bersifat optional
- Jika checked, laporan hanya menampilkan rekening yang memiliki saldo (debit > 0 atau kredit > 0)
- Jika unchecked, laporan menampilkan semua rekening termasuk yang saldo nol
- Default: unchecked

**BR-007: Output Format**
- Laporan dihasilkan dalam format Excel (.xlsx)
- File Excel harus dapat di-download langsung oleh user

---

## 4. Backend Functional Specification

### 4.1 Use Case: Generate Excel Laporan Trial Balance

**ID:** BE-TB-001  
**Nama:** Generate Laporan Trial Balance

**Deskripsi:**  
Backend service untuk menghasilkan laporan Trial Balance dalam format Excel berdasarkan parameter yang diberikan.

**Actor:** Operator Data, Otorisator, Supervisor/Manager

**Pre-conditions:**
- User sudah login ke sistem
- Data transaksi GL sudah tersedia untuk periode yang diminta

**Input Parameters:**
- `startDate`: Date (DD/MM/YYYY) - required
- `endDate`: Date (DD/MM/YYYY) - required
- `consolidateCurrency`: Boolean (default: false)
- `currencyCode`: String (IDR|USD|EUR|SGD) - optional jika consolidateCurrency = true
- `consolidateBranch`: Boolean (default: false)
- `branchCode`: String - optional jika consolidateBranch = true
- `showOnlyWithBalance`: Boolean (default: false)

**Main Flow:**
1. Validasi input parameters:
   - Validasi format tanggal
   - Validasi startDate <= endDate
   - Validasi endDate <= current date
   - Validasi valuta code (jika tidak konsolidasi)
   - Validasi branch code (jika tidak konsolidasi)
2. Query data GL transactions dalam rentang tanggal yang ditentukan
3. Calculate opening balance (saldo awal periode) untuk setiap account
4. Calculate movement (mutasi debit/kredit) selama periode
5. Calculate ending balance (saldo akhir periode)
6. Jika consolidateCurrency = true:
   - Konversi semua balance ke currency base (IDR) menggunakan exchange rate per endDate
7. Jika consolidateBranch = true:
   - Aggregate semua cabang
8. Jika showOnlyWithBalance = true:
   - Filter hanya account dengan ending balance != 0
9. Grouping dan sorting account berdasarkan account code
10. Calculate grand total debit dan kredit
11. Validasi balance equation (total debit = total kredit)
12. Format data ke struktur Excel dengan kolom:
    - Account Code
    - Account Name
    - Beginning Balance (Debit/Credit)
    - Movement (Debit/Credit)
    - Ending Balance (Debit/Credit)
13. Generate file Excel dengan template Trial Balance
14. Return file Excel sebagai binary stream

**Output:**
- File Excel (.xlsx) dengan laporan Trial Balance
- Kolom laporan:
  - Kode Rekening
  - Nama Rekening
  - Saldo Awal Debit
  - Saldo Awal Kredit
  - Mutasi Debit
  - Mutasi Kredit
  - Saldo Akhir Debit
  - Saldo Akhir Kredit

**Business Rules Applied:**
- BR-001, BR-002, BR-003, BR-004, BR-005, BR-006, BR-007

**Exception Handling:**
- Invalid date format → HTTP 400 "Format tanggal tidak valid"
- startDate > endDate → HTTP 400 "Mulai tanggal tidak boleh lebih besar dari hingga tanggal"
- endDate > current date → HTTP 400 "Hingga tanggal tidak boleh melebihi hari ini"
- Invalid currency → HTTP 400 "Kode valuta tidak valid"
- Invalid branch → HTTP 400 "Kode cabang tidak valid"
- No data found → HTTP 404 "Data tidak ditemukan untuk periode yang diminta"
- Balance not balanced → HTTP 500 "Total debit dan kredit tidak balance"
- System error → HTTP 500 "Gagal generate laporan"

---

### 4.2 API Endpoints

**POST /api/gl/reports/trial-balance/generate**

```json
Request:
{
  "startDate": "01/01/2026",
  "endDate": "28/01/2026",
  "consolidateCurrency": false,
  "currencyCode": "IDR",
  "consolidateBranch": false,
  "branchCode": "001",
  "showOnlyWithBalance": true
}

Response: Binary Excel file
```

**Example - With Consolidation:**
```json
Request:
{
  "startDate": "01/01/2026",
  "endDate": "31/01/2026",
  "consolidateCurrency": true,
  "consolidateBranch": true,
  "showOnlyWithBalance": false
}

Response: Binary Excel file
```

---

## 5. Frontend Functional Specification

### 5.1 Screen: Laporan Trial Balance

**Screen ID:** UI-TB-001  
**Nama Screen:** Generate Laporan Trial Balance

**Fungsi utama:**
- Menampilkan form input untuk parameter laporan trial balance
- Validasi input sebelum submit
- Trigger generate laporan ke backend
- Download file Excel hasil generate

**Layout:**
- Header dengan breadcrumb: "Laporan / Trial Balance"
- Header kanan: Module selector "Modul General Ledger" dan user info
- Main content: Form dengan title "Generate Laporan Trial Balance"
- Form fields (top to bottom):
  - **Form Row (2 kolom):**
    - Mulai Tanggal (required) - kolom kiri
    - Hingga Tanggal (required) - kolom kanan
  - Konsolidasi Valuta (checkbox)
  - Valuta (dropdown)
  - Konsolidasi Cabang (checkbox)
  - Cabang (dropdown)
  - Tampilkan hanya yang memiliki saldo (checkbox)
- Report section dengan gradient background dan button "Generate Excel"

**Field Behaviors:**
- Valuta field: disabled jika "Konsolidasi Valuta" checked
- Cabang field: disabled jika "Konsolidasi Cabang" checked
- Hingga Tanggal: must be >= Mulai Tanggal

---

### 5.2 UI Actions

| Action | Description |
|------|-------------|
| **ACT-001: Input Mulai Tanggal** | User input tanggal mulai periode dalam format DD/MM/YYYY. Dapat menggunakan date picker atau manual input. Field ini required |
| **ACT-002: Input Hingga Tanggal** | User input tanggal akhir periode dalam format DD/MM/YYYY. Harus >= Mulai Tanggal dan <= tanggal hari ini. Field ini required |
| **ACT-003: Toggle Konsolidasi Valuta** | User mencentang checkbox untuk konsolidasi valuta. Jika checked, field Valuta menjadi disabled |
| **ACT-004: Select Valuta** | User memilih valuta dari dropdown (IDR, USD, EUR, SGD). Hanya aktif jika Konsolidasi Valuta tidak checked. Default: Rupiah |
| **ACT-005: Toggle Konsolidasi Cabang** | User mencentang checkbox untuk konsolidasi cabang. Jika checked, field Cabang menjadi disabled |
| **ACT-006: Select Cabang** | User memilih cabang dari dropdown. Hanya aktif jika Konsolidasi Cabang tidak checked. Default: "-- PILIH SEMUA --" |
| **ACT-007: Toggle Filter Saldo** | User mencentang checkbox "Tampilkan hanya yang memiliki saldo" untuk filter rekening dengan saldo. Default: unchecked |
| **ACT-008: Generate Excel** | User klik button "Generate Excel" untuk trigger proses generate laporan. System validasi input, call backend API, dan auto-download file Excel |

---

### 5.3 Validation Rules

| Field | Validation |
|-------|------------|
| Mulai Tanggal | Required. Format DD/MM/YYYY. Must be valid date |
| Hingga Tanggal | Required. Format DD/MM/YYYY. Must be >= Mulai Tanggal. Must be <= today |
| Valuta | Conditional required (jika Konsolidasi Valuta tidak checked) |
| Cabang | Optional |

---

## 6. Integration Notes

- UI menggunakan BE service untuk generate laporan (`POST /api/gl/reports/trial-balance/generate`)
- Request dikirim dalam format JSON dengan semua parameter filter
- Response berupa binary file Excel yang langsung di-download oleh browser
- Error dikembalikan dalam format standar sistem dengan HTTP status code dan error message
- Loading indicator ditampilkan selama proses generate
- Success notification ditampilkan setelah file berhasil di-download
- Frontend validation dilakukan sebelum call backend API
- Backend melakukan final validation sebelum processing

---

## Appendix A – UI Field Specification

> Bagian ini mendefinisikan detail field UI, validasi, dan perilaku.

### A.1 Page Laporan Trial Balance

| Field Name | Label | Type | Required | Default Value | Options/Format | Behavior |
|------------|-------|------|----------|---------------|----------------|----------|
| startDate | Mulai Tanggal | Date Input | Yes | Current date | DD/MM/YYYY | Date picker atau manual input |
| endDate | Hingga Tanggal | Date Input | Yes | Current date | DD/MM/YYYY | Date picker atau manual input. Must be >= startDate |
| consolidateCurrency | Konsolidasi Valuta | Checkbox | No | Unchecked | - | Jika checked, disable field Valuta |
| currencyCode | Valuta | Dropdown | Conditional | IDR | IDR, USD, EUR, SGD | Disabled jika consolidateCurrency = true |
| consolidateBranch | Konsolidasi Cabang | Checkbox | No | Unchecked | - | Jika checked, disable field Cabang |
| branchCode | Cabang | Dropdown | No | "-- PILIH SEMUA --" | List of branches | Disabled jika consolidateBranch = true |
| showOnlyWithBalance | Tampilkan hanya yang memiliki saldo | Checkbox | No | Unchecked | - | Filter rekening dengan saldo |

**Field Details:**

**1. Mulai Tanggal**
- Type: Text input with date picker
- Label: "Mulai Tanggal"
- Format: DD/MM/YYYY
- Required: Yes
- Default: Current date (28/01/2026)
- Validation:
  - Valid date format
  - Must be a valid date
  - Show error message if invalid

**2. Hingga Tanggal**
- Type: Text input with date picker
- Label: "Hingga Tanggal"
- Format: DD/MM/YYYY
- Required: Yes
- Default: Current date (28/01/2026)
- Validation:
  - Valid date format
  - Must be >= Mulai Tanggal
  - Must be <= current date
  - Show error message if invalid

**3. Konsolidasi Valuta**
- Type: Checkbox
- Default: Unchecked
- Behavior: When checked, disable Valuta dropdown

**4. Valuta**
- Type: Select/Dropdown
- Placeholder: "-- PILIH VALUTA --"
- Default: "Rupiah" (IDR) when enabled
- Options:
  - Rupiah (IDR)
  - US Dollar (USD)
  - Euro (EUR)
  - Singapore Dollar (SGD)
- Disabled when: Konsolidasi Valuta is checked

**5. Konsolidasi Cabang**
- Type: Checkbox
- Default: Unchecked
- Behavior: When checked, disable Cabang dropdown

**6. Cabang**
- Type: Select/Dropdown
- Placeholder: "-- PILIH SEMUA --"
- Options: Loaded from backend (list of branches based on user access)
- Disabled when: Konsolidasi Cabang is checked

**7. Tampilkan hanya yang memiliki saldo**
- Type: Checkbox
- Default: Unchecked
- Behavior: When checked, backend will filter out accounts with zero balance

**8. Generate Excel Button**
- Type: Button
- Label: "Generate Excel"
- Icon: 📊
- Style: Green button with gradient background section
- Action: Submit form and download Excel file

---

## Appendix B – Backend Data Mapping

> Bagian ini mendefinisikan entitas dan atribut backend yang relevan.

### B.1 Entity: GeneralLedger / GLTransaction

**Table:** `gl_transaction`

| Attribute | Data Type | Description |
|-----------|-----------|-------------|
| transaction_id | VARCHAR(50) | ID transaksi |
| transaction_date | DATE | Tanggal transaksi |
| account_id | VARCHAR(20) | ID rekening GL |
| account_code | VARCHAR(20) | Kode rekening |
| currency_code | VARCHAR(3) | Kode valuta |
| branch_code | VARCHAR(10) | Kode cabang |
| debit_amount | DECIMAL(18,2) | Jumlah debit |
| credit_amount | DECIMAL(18,2) | Jumlah kredit |
| description | VARCHAR(500) | Deskripsi transaksi |

### B.2 Entity: Account

**Table:** `account`

| Attribute | Data Type | Description |
|-----------|-----------|-------------|
| account_id | VARCHAR(20) | ID rekening |
| account_code | VARCHAR(20) | Kode rekening |
| account_name | VARCHAR(255) | Nama rekening |
| account_type | VARCHAR(50) | Tipe rekening (Asset, Liability, Equity, Income, Expense) |
| normal_balance | VARCHAR(10) | Saldo normal (Debit/Credit) |
| is_active | BOOLEAN | Status aktif |

### B.3 Entity: Currency / ExchangeRate

**Table:** `currency_exchange_rate`

| Attribute | Data Type | Description |
|-----------|-----------|-------------|
| currency_code | VARCHAR(3) | Kode valuta |
| currency_name | VARCHAR(100) | Nama valuta |
| rate_date | DATE | Tanggal kurs |
| exchange_rate | DECIMAL(18,6) | Kurs terhadap IDR |

### B.4 Entity: Branch

**Table:** `branch`

| Attribute | Data Type | Description |
|-----------|-----------|-------------|
| branch_code | VARCHAR(10) | Kode cabang |
| branch_name | VARCHAR(255) | Nama cabang |
| is_active | BOOLEAN | Status aktif |

---

## Appendix C – Traceability Matrix

| FR ID | Description | BE Use Case | UI Screen | Business Rule |
|------|------------|------------|-----------|---------------|
| FR-TB-001 | Generate laporan Trial Balance dalam format Excel | BE-TB-001 | UI-TB-001 | BR-001, BR-007 |
| FR-TB-002 | Filter laporan berdasarkan periode tanggal | BE-TB-001 | UI-TB-001 | BR-001 |
| FR-TB-003 | Filter laporan berdasarkan valuta | BE-TB-001 | UI-TB-001 | BR-003 |
| FR-TB-004 | Konsolidasi multi-currency | BE-TB-001 | UI-TB-001 | BR-002 |
| FR-TB-005 | Filter laporan berdasarkan cabang | BE-TB-001 | UI-TB-001 | BR-005 |
| FR-TB-006 | Konsolidasi multi-branch | BE-TB-001 | UI-TB-001 | BR-004 |
| FR-TB-007 | Filter rekening dengan saldo | BE-TB-001 | UI-TB-001 | BR-006 |

---

## Appendix D – Open Points

| No | Description | Status | Owner |
|----|------------|--------|-------|
| 1 | Konfirmasi template Excel untuk laporan Trial Balance | Open | Business Analyst |
| 2 | Konfirmasi kolom-kolom yang perlu ditampilkan di Excel (apakah perlu kolom total running balance?) | Open | Business Analyst |
| 3 | Logic perhitungan konsolidasi valuta (kurs yang digunakan: closing rate atau average rate) | Open | Finance Team |
| 4 | Apakah perlu fitur export ke PDF selain Excel? | Open | Business Owner |
| 5 | Apakah perlu fitur print preview sebelum download? | Open | Business Owner |
| 6 | Apakah perlu pagination/grouping berdasarkan account type di Excel? | Open | Business Analyst |

---

## Change Log

| Date | Description | Author |
|------|-------------|--------|
| 2026-01-28 | Initial draft - completed all sections based on UI design | System Analyst |
