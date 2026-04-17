
# FSD – Laporan Neraca dan Laba Rugi

## Document Metadata

| Item | Value |
|------|-------|
| Module | Laporan Neraca dan Laba Rugi (General Ledger Reporting) |
| Parent FSD | FSD_balance-sheet_report |
| Version | 1.0 |
| Date | 2026-01-28 |
| Status | Draft |
| Owner | IT / System Owner |
| Notes | Dokumen terpusat FSD (Backend + Frontend) dengan struktur berlapis |

---

## 1. Overview & Scope

Modul **Laporan Neraca dan Laba Rugi** digunakan untuk menghasilkan laporan keuangan berupa Neraca (Balance Sheet) dan Laba Rugi (Income Statement) dalam format Excel.

**Cakupan fungsi:**
- Generate laporan Neraca per tanggal tertentu
- Generate laporan Laba Rugi per tanggal tertentu
- Filter laporan berdasarkan valuta (currency)
- Filter laporan berdasarkan cabang (branch)
- Konsolidasi data berdasarkan valuta (multi-currency consolidation)
- Konsolidasi data berdasarkan cabang (multi-branch consolidation)
- Export laporan ke format Excel

---

## 2. Actors & Roles

| Actor | Description |
|------|------------|
| Operator Data | User yang dapat melihat dan generate laporan keuangan |
| Otorisator | User yang dapat melihat dan generate laporan keuangan |
| Supervisor / Manager | User yang dapat melihat dan generate laporan keuangan  |

---

## 3. Business Rules

**BR-001: Jenis Laporan**
- Sistem harus menyediakan dua jenis laporan: Neraca dan Laba Rugi
- User harus memilih salah satu jenis laporan sebelum generate

**BR-002: Per Tanggal**
- Laporan Neraca menampilkan posisi keuangan pada tanggal tertentu
- Laporan Laba Rugi menampilkan kinerja keuangan sampai dengan tanggal tertentu
- Format tanggal: DD/MM/YYYY
- Tanggal tidak boleh melebihi tanggal hari ini

**BR-003: Konsolidasi Valuta**
- Jika checkbox "Konsolidasi Valuta" dicentang, sistem mengkonsolidasikan semua valuta ke dalam satu laporan
- Jika checkbox tidak dicentang, user harus memilih satu valuta spesifik
- Konversi valuta menggunakan kurs yang berlaku pada tanggal laporan

**BR-004: Valuta**
- Sistem mendukung multi-currency: IDR, USD, EUR, SGD, JPY, CNY
- Default valuta adalah IDR (Rupiah)
- Field valuta menjadi disabled jika "Konsolidasi Valuta" dicentang

**BR-005: Konsolidasi Cabang**
- Jika checkbox "Konsolidasi Cabang" dicentang, sistem mengkonsolidasikan semua cabang
- Jika checkbox tidak dicentang, user dapat memilih cabang spesifik
- Field cabang menjadi disabled jika "Konsolidasi Cabang" dicentang
- Jika user hanya boleh akses ke satu cabang, maka field "Konsolidasi Cabang" menjadi disabled

**BR-006: Cabang**
- User dapat memilih satu atau semua cabang
- List Cabang yang tampil di dropdown sesuai tipe hak akses cabang yang diatur
- Default option adalah kode cabang sesuai user yang login
- Jika user hanya boleh akses ke satu cabang, maka field "Cabang" menjadi disabled

**BR-007: Output Format**
- Laporan dihasilkan dalam format Excel (.xlsx)
- File Excel harus dapat di-download langsung oleh user

---

## 4. Backend Functional Specification

### 4.1 Use Case: Generate Excel Laporan Neraca

**ID:** BE-RPT-001  
**Nama:** Generate Laporan Neraca

**Deskripsi:**  
Backend service untuk menghasilkan laporan Neraca dalam format Excel berdasarkan parameter yang diberikan.

**Actor:** Operator Data, Otorisator

**Pre-conditions:**
- User sudah login ke sistem
- Data transaksi GL sudah tersedia untuk periode yang diminta

**Input Parameters:**
- `reportType`: String = "neraca"
- `asOfDate`: Date (DD/MM/YYYY)
- `consolidateCurrency`: Boolean
- `currencyCode`: String (IDR|USD|EUR|SGD|JPY|CNY) - optional jika consolidateCurrency = true
- `consolidateBranch`: Boolean
- `branchCode`: String - optional jika consolidateBranch = true

**Main Flow:**
1. Validasi input parameters (tanggal, valuta, cabang)
2. Query data account balance per tanggal yang ditentukan
3. Jika consolidateCurrency = true, konversi semua balance ke currency base (IDR) menggunakan exchange rate per tanggal
4. Jika consolidateBranch = true, aggregate semua cabang
5. Grouping account berdasarkan klasifikasi Neraca (Aktiva, Pasiva, Modal)
6. Calculate subtotal dan grand total
7. Format data ke struktur Excel
8. Generate file Excel dengan template Neraca
9. Return file Excel sebagai binary stream

**Output:**
- File Excel (.xlsx) dengan laporan Neraca

**Business Rules Applied:**
- BR-001, BR-002, BR-003, BR-004, BR-005, BR-006, BR-007

**Exception Handling:**
- Invalid date format → HTTP 400 "Format tanggal tidak valid"
- Date > current date → HTTP 400 "Tanggal tidak boleh melebihi hari ini"
- Invalid currency → HTTP 400 "Kode valuta tidak valid"
- Invalid branch → HTTP 400 "Kode cabang tidak valid"
- No data found → HTTP 404 "Data tidak ditemukan untuk periode yang diminta"
- System error → HTTP 500 "Gagal generate laporan"

---

### 4.2 Use Case: Generate Excel Laporan Laba Rugi

**ID:** BE-RPT-002  
**Nama:** Generate Laporan Laba Rugi

**Deskripsi:**  
Backend service untuk menghasilkan laporan Laba Rugi dalam format Excel berdasarkan parameter yang diberikan.

**Actor:** Operator Data, Otorisator

**Pre-conditions:**
- User sudah login ke sistem
- Data transaksi GL sudah tersedia untuk periode yang diminta

**Input Parameters:**
- `reportType`: String = "laba-rugi"
- `asOfDate`: Date (DD/MM/YYYY)
- `consolidateCurrency`: Boolean
- `currencyCode`: String (IDR|USD|EUR|SGD|JPY|CNY) - optional jika consolidateCurrency = true
- `consolidateBranch`: Boolean
- `branchCode`: String - optional jika consolidateBranch = true

**Main Flow:**
1. Validasi input parameters (tanggal, valuta, cabang)
2. Query data account balance period-to-date (dari awal tahun buku sampai dengan tanggal yang ditentukan)
3. Jika consolidateCurrency = true, konversi semua balance ke currency base (IDR) menggunakan exchange rate per tanggal
4. Jika consolidateBranch = true, aggregate semua cabang
5. Grouping account berdasarkan klasifikasi Laba Rugi (Pendapatan, Beban)
6. Calculate subtotal, laba/rugi bersih
7. Format data ke struktur Excel
8. Generate file Excel dengan template Laba Rugi
9. Return file Excel sebagai binary stream

**Output:**
- File Excel (.xlsx) dengan laporan Laba Rugi

**Business Rules Applied:**
- BR-001, BR-002, BR-003, BR-004, BR-005, BR-006, BR-007

**Exception Handling:**
- Invalid date format → HTTP 400 "Format tanggal tidak valid"
- Date > current date → HTTP 400 "Tanggal tidak boleh melebihi hari ini"
- Invalid currency → HTTP 400 "Kode valuta tidak valid"
- Invalid branch → HTTP 400 "Kode cabang tidak valid"
- No data found → HTTP 404 "Data tidak ditemukan untuk periode yang diminta"
- System error → HTTP 500 "Gagal generate laporan"

---

### 4.3 API Endpoints

**POST /api/gl/reports/balance-sheet/generate**
```json
Request:
{
  "reportType": "neraca",
  "asOfDate": "31/12/2025",
  "consolidateCurrency": false,
  "currencyCode": "IDR",
  "consolidateBranch": false,
  "branchCode": "001"
}

Response: Binary Excel file
```

**POST /api/gl/reports/income-statement/generate**
```json
Request:
{
  "reportType": "laba-rugi",
  "asOfDate": "31/12/2025",
  "consolidateCurrency": true,
  "consolidateBranch": true
}

Response: Binary Excel file
```

---

## 5. Frontend Functional Specification

### 5.1 Screen: Laporan Neraca dan Laba Rugi

**Screen ID:** UI-RPT-001  
**Nama Screen:** Generate Laporan Neraca dan Laba / Rugi

**Fungsi utama:**
- Menampilkan form input untuk parameter laporan
- Validasi input sebelum submit
- Trigger generate laporan ke backend
- Download file Excel hasil generate

**Layout:**
- Header dengan breadcrumb: "Laporan / Neraca & Laba / Rugi"
- Header kanan: Module selector "Modul General Ledger" dan user info
- Main content: Form dengan title "Generate Laporan Neraca dan Laba / Rugi"
- Form fields (top to bottom):
  - Jenis Laporan (required)
  - Per Tanggal (required)
  - Konsolidasi Valuta (checkbox)
  - Valuta (dropdown)
  - Konsolidasi Cabang (checkbox)
  - Cabang (dropdown)
- Report section dengan gradient background dan button "Generate Excel"

**Field Behaviors:**
- Valuta field: disabled jika "Konsolidasi Valuta" checked
- Cabang field: disabled jika "Konsolidasi Cabang" checked

---

### 5.2 UI Actions

| Action | Description |
|------|-------------|
| **ACT-001: Select Jenis Laporan** | User memilih jenis laporan (Neraca / Laba Rugi) dari dropdown |
| **ACT-002: Input Per Tanggal** | User input tanggal laporan dalam format DD/MM/YYYY. Dapat menggunakan date picker atau manual input |
| **ACT-003: Toggle Konsolidasi Valuta** | User mencentang checkbox untuk konsolidasi valuta. Jika checked, field Valuta menjadi disabled |
| **ACT-004: Select Valuta** | User memilih valuta dari dropdown (IDR, USD, EUR, SGD, JPY, CNY). Hanya aktif jika Konsolidasi Valuta tidak checked |
| **ACT-005: Toggle Konsolidasi Cabang** | User mencentang checkbox untuk konsolidasi cabang. Jika checked, field Cabang menjadi disabled |
| **ACT-006: Select Cabang** | User memilih cabang dari dropdown. Option default "-- PILIH SEMUA --". Hanya aktif jika Konsolidasi Cabang tidak checked |
| **ACT-007: Generate Excel** | User klik button "Generate Excel" untuk trigger proses generate laporan. System validasi input, call backend API, dan auto-download file Excel |

---

### 5.3 Validation Rules

| Field | Validation |
|-------|------------|
| Jenis Laporan | Required. Harus dipilih salah satu |
| Per Tanggal | Required. Format DD/MM/YYYY. Tidak boleh > tanggal hari ini |
| Valuta | Conditional required (jika Konsolidasi Valuta tidak checked) |
| Cabang | Optional |

---

## 6. Integration Notes

- UI menggunakan BE service untuk generate laporan (`POST /api/gl/reports/balance-sheet/generate` atau `/income-statement/generate`)
- Request dikirim dalam format JSON dengan semua parameter filter
- Response berupa binary file Excel yang langsung di-download oleh browser
- Error dikembalikan dalam format standar sistem dengan HTTP status code dan error message
- Loading indicator ditampilkan selama proses generate
- Success notification ditampilkan setelah file berhasil di-download

---

## Appendix A – UI Field Specification

> Bagian ini mendefinisikan detail field UI, validasi, dan perilaku.

### A.1 Page Laporan Neraca dan Laba Rugi

| Field Name | Label | Type | Required | Default Value | Options/Format | Behavior |
|------------|-------|------|----------|---------------|----------------|----------|
| reportType | Jenis Laporan | Dropdown | Yes | - | "neraca", "laba-rugi" | User harus pilih salah satu |
| asOfDate | Per Tanggal | Date Input | Yes | - | DD/MM/YYYY | Date picker atau manual input. Max = today |
| consolidateCurrency | Konsolidasi Valuta | Checkbox | No | Unchecked | - | Jika checked, disable field Valuta |
| currencyCode | Valuta | Dropdown | Conditional | IDR | IDR, USD, EUR, SGD, JPY, CNY | Disabled jika consolidateCurrency = true |
| consolidateBranch | Konsolidasi Cabang | Checkbox | No | Unchecked | - | Jika checked, disable field Cabang |
| branchCode | Cabang | Dropdown | No | "-- PILIH SEMUA --" | List of branches | Disabled jika consolidateBranch = true |

**Field Details:**

**1. Jenis Laporan**
- Type: Select/Dropdown
- Placeholder: "-- PILIH SATU --"
- Options:
  - Neraca
  - Laba Rugi
- Required: Yes
- Validation: Must select one option

**2. Per Tanggal**
- Type: Text input with date picker
- Placeholder: "DD/MM/YYYY"
- Format: DD/MM/YYYY
- Required: Yes
- Validation:
  - Valid date format
  - Date <= current date
  - Show error message if invalid

**3. Konsolidasi Valuta**
- Type: Checkbox
- Default: Unchecked
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
- Disabled when: Konsolidasi Valuta is checked

**5. Konsolidasi Cabang**
- Type: Checkbox
- Default: Unchecked
- Behavior: When checked, disable Cabang dropdown

**6. Cabang**
- Type: Select/Dropdown
- Default: "-- PILIH SEMUA --"
- Options: Loaded from backend (list of branches)
- Disabled when: Konsolidasi Cabang is checked

**7. Generate Excel Button**
- Type: Button
- Label: "Generate Excel"
- Icon: 📊
- Style: Green button with gradient background section
- Action: Submit form and download Excel file

---

## Appendix B – Backend Data Mapping

> Bagian ini mendefinisikan entitas dan atribut backend yang relevan.

### B.1 Entity: GeneralLedger / AccountBalance

**Table:** `gl_account_balance`

| Attribute | Data Type | Description |
|-----------|-----------|-------------|
| account_id | VARCHAR(20) | ID rekening GL |
| account_code | VARCHAR(20) | Kode rekening |
| account_name | VARCHAR(255) | Nama rekening |
| account_type | VARCHAR(50) | Tipe rekening (Asset, Liability, Equity, Income, Expense) |
| currency_code | VARCHAR(3) | Kode valuta (IDR, USD, EUR, etc) |
| branch_code | VARCHAR(10) | Kode cabang |
| balance_date | DATE | Tanggal balance |
| debit_balance | DECIMAL(18,2) | Saldo debit |
| credit_balance | DECIMAL(18,2) | Saldo kredit |
| balance_amount | DECIMAL(18,2) | Saldo bersih |

### B.2 Entity: Currency / ExchangeRate

**Table:** `currency_exchange_rate`

| Attribute | Data Type | Description |
|-----------|-----------|-------------|
| currency_code | VARCHAR(3) | Kode valuta |
| currency_name | VARCHAR(100) | Nama valuta |
| rate_date | DATE | Tanggal kurs |
| exchange_rate | DECIMAL(18,6) | Kurs terhadap IDR |

### B.3 Entity: Branch

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
| FR-001 | Generate laporan Neraca dalam format Excel | BE-RPT-001 | UI-RPT-001 | BR-001, BR-002, BR-007 |
| FR-002 | Generate laporan Laba Rugi dalam format Excel | BE-RPT-002 | UI-RPT-001 | BR-001, BR-002, BR-007 |
| FR-003 | Filter laporan berdasarkan valuta | BE-RPT-001, BE-RPT-002 | UI-RPT-001 | BR-004 |
| FR-004 | Konsolidasi multi-currency | BE-RPT-001, BE-RPT-002 | UI-RPT-001 | BR-003 |
| FR-005 | Filter laporan berdasarkan cabang | BE-RPT-001, BE-RPT-002 | UI-RPT-001 | BR-006 |
| FR-006 | Konsolidasi multi-branch | BE-RPT-001, BE-RPT-002 | UI-RPT-001 | BR-005 |

---

## Appendix D – Open Points

| No | Description | Status | Owner |
|----|------------|--------|-------|
| 1 | Konfirmasi template Excel untuk laporan Neraca dan Laba Rugi | Open | Business Analyst |
| 2 | Definisi akun-akun yang masuk kategori Aktiva, Pasiva, Modal, Pendapatan, Beban | Open | Business Analyst |
| 3 | Logic perhitungan konsolidasi valuta (kurs yang digunakan: closing rate, average rate, atau historical rate) | Open | Finance Team |
| 4 | Apakah perlu fitur export ke PDF selain Excel? | Open | Business Owner |
| 5 | Apakah perlu print preview sebelum download? | Open | Business Owner |

---

## Change Log

| Date | Description | Author |
|------|-------------|--------|
| 2026-01-28 | Initial draft - completed all sections based on UI design | System Analyst |
