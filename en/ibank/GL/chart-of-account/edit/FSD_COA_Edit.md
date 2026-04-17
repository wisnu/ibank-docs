
# FSD – COA Maintenance: Ubah Rekening

## Document Metadata

| Item | Value |
|------|-------|
| Module | COA Management – Ubah Rekening |
| Parent FSD | FSD_COA_Main |
| Version | 1.2 |
| Date | 2026-01-19 |
| Status | Draft |
| Owner | IT / System Owner |
| Notes | Dokumen terpusat FSD (Backend + Frontend) dengan struktur berlapis |

---

## 1. Overview & Scope

Modul **Ubah Rekening (Chart of Account / COA)** digunakan untuk melakukan perubahan data rekening,
baik pada level **master rekening** maupun **instance rekening per cabang & valuta**.

Seluruh perubahan **tidak langsung efektif**, namun harus melalui proses **otorisasi (maker–checker)**.

**Cakupan fungsi:**
- Perubahan atribut master COA
- Perubahan parameter saldo & transaksi (default dan per instance)
- Pengajuan perubahan untuk otorisasi
- Proses approve / reject

---

## 2. Actors & Roles

| Actor | Description |
|------|------------|
| Operator Data | Mengajukan perubahan COA |
| Otorisator | Melakukan approve / reject perubahan |

---

## 3. Shared Business Rules

| Rule ID | Description |
|--------|------------|
| BR-COA-01 | `account_code` bersifat read-only |
| BR-COA-02 | Semua perubahan wajib melalui proses otorisasi |
| BR-COA-03 | Jika Reject, data aktif tidak berubah |
| BR-COA-04 | Parameter default dapat dipropagasikan ke seluruh instance |
| BR-COA-05 | Nilai tarif pajak tidak boleh negatif |
| BR-COA-06 | Field read-only tidak dapat dimodifikasi dari UI |

---

## 4. Backend Functional Specification

### 4.1 Use Case: Get Data COA

**Purpose**  
Mengambil data COA untuk keperluan tampilan dan pengolahan perubahan.

**Input**
- `account_code`

**Process**
1. Sistem mengambil data master rekening
2. Sistem mengambil seluruh instance rekening
3. Sistem melakukan lookup data referensi

**Output**
- Data master rekening
- Daftar instance rekening

---



### 4.2 Use Case: Submit Perubahan COA

**Process**
1. Sistem melakukan validasi
2. Sistem menyimpan perubahan sebagai pengajuan
3. Status pengajuan: *Pending Approval*

---

### 4.3 Use Case: Approval / Rejection

| Action | Result |
|------|--------|
| Approve | Perubahan diterapkan ke data aktif |
| Reject | Pengajuan dibatalkan |

---

## 5. Frontend Functional Specification

### 5.1 Screen: Form Ubah Rekening

**Fungsi utama:**
- Menampilkan data COA existing
- Mengatur field read-only & editable
- Mengirim pengajuan perubahan

---

### 5.2 UI Actions

| Action | Description |
|------|-------------|
| Submit | Mengirim pengajuan perubahan |
| Set Semua Parameter | Sinkronisasi parameter default ke seluruh instance |
| Approve / Reject | Dilakukan oleh Otorisator |

---

## 6. Integration Notes

- UI menggunakan BE service untuk retrieve dan submit data
- Validasi dilakukan di FE dan BE
- Error dikembalikan dalam format standar sistem

---

## Appendix A – UI Field Specification

> Bagian ini mendefinisikan detail field UI, validasi, dan perilaku.

### A.1 Form Ubah Rekening – Master

- Field read-only: kode rekening, rekening induk, flag sistem
- Field editable: nama rekening, deskripsi, klasifikasi, pajak

### A.2 Parameter Saldo & Transaksi

- Default saldo normal
- Default saldo harus nihil
- Default status transaksi

### A.3 Grid Account Instance

- Parameter saldo & transaksi per cabang dan valuta

---

## Appendix B – Backend Data Mapping

> Bagian ini mendefinisikan entitas dan atribut backend yang relevan.

### B.1 Entity: Account (Master)

- Identitas & hirarki
- Klasifikasi & pelaporan
- Parameter default
- Parameter pajak
- Audit

### B.2 Entity: Account Instance

- Relasi cabang & valuta
- Parameter saldo & transaksi per instance

---

## Appendix C – Traceability Matrix

| FR ID | Description | BE Use Case | UI Screen | Business Rule |
|------|------------|------------|-----------|---------------|
| FR-COA-001 | Akses Ubah Rekening | Get Data COA | Form Ubah Rekening | BR-COA-01 |
| FR-COA-002 | Submit Perubahan | Submit Perubahan COA | Form Ubah Rekening | BR-COA-02 |
| FR-COA-003 | Approval COA | Approval / Rejection | Approval Screen | BR-COA-03 |
| FR-COA-004 | Set Semua Parameter | Submit Perubahan COA | Form Ubah Rekening | BR-COA-04 |

---

## Appendix D – Open Points

| No | Description | Status |
|----|------------|--------|

---

## Change Log

| Date | Description |
|------|-------------|
| 2026-01-19 | Restrukturisasi FSD berlapis + traceability |
