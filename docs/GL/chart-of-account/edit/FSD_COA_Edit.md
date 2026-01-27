# FSD: Ubah Rekening (Chart of Account)

| **Metadata** | |
|--------------|-------------|
| **Module** | COA Management – Ubah Rekening |
| **Parent FSD** | FSD_COA_Main.md |
| **Version** | 1.0 |
| **Date** | 2026-01-19 |
| **Status** | Draft |
| **Owner** | IT / System Owner |

---

## Module Overview

Modul **Ubah Rekening (COA)** menyediakan fungsi untuk melakukan perubahan data master rekening (COA) beserta parameter pendukungnya.
Perubahan **tidak langsung efektif**, melainkan masuk ke **daftar otorisasi** untuk kemudian di-*approve* / di-*reject* oleh user berwenang.

Cakupan utama:

- Edit atribut COA pada level master (`ibcore.account`)
- Edit atribut COA per kantor & valuta (`ibcore.accountinstance`)
- Submit perubahan untuk proses otorisasi

---

## Actors & Roles


| Actor         | Deskripsi                                        |
| --------------- | -------------------------------------------------- |
| Operator Data | Mengajukan perubahan COA                         |
| Otorisator    | Melakukan approve/reject pengajuan perubahan COA |

---

## Data Flow Diagram

```mermaid
flowchart TB
    E1([E1: Operator Data]) -->|Request Ubah COA| P1[P1: Tampilkan Form Edit COA]
    P1 -->|Query COA| D1[(D1: ibcore.account)]
    P1 -->|Query Instance| D2[(D2: ibcore.accountinstance)]
    D1 -->|Data COA Existing| P1
    D2 -->|Data Instance| P1
    P1 -->|Form dengan Data| E1
    
    E1 -->|Data Perubahan COA| P2[P2: Validasi Data Perubahan]
    P2 -->|Data Valid| P3[P3: Simpan Pengajuan]
    P2 -->|Error Message| E1
    
    P3 -->|Data Pengajuan| D3[(D3: Approval Queue)]
    P3 -->|Notifikasi Pengajuan Baru| E2([E2: Otorisator])
    
    E2 -->|Request Daftar Pengajuan| P4[P4: Tampilkan Daftar Pengajuan]
    D3 -->|Data Pengajuan Pending| P4
    P4 -->|List Pengajuan| E2
    
    E2 -->|Request Detail Pengajuan| P5[P5: Tampilkan Detail Perubahan]
    D3 -->|Data Before/After| P5
    P5 -->|Detail Perubahan| E2
    
    E2 -->|Keputusan: Approve| P6[P6: Proses Approval]
    E2 -->|Keputusan: Reject| P7[P7: Proses Rejection]
    
    P6 -->|Update COA| D1
    P6 -->|Update Instance| D2
    P6 -->|Update Status| D3
    P6 -->|Notifikasi Approved| E1
    
    P7 -->|Update Status| D3
    P7 -->|Notifikasi Rejected| E1
    
    style E1 fill:#e1f5ff
    style E2 fill:#fff9c4
    style D1 fill:#f0f0f0
    style D2 fill:#f0f0f0
    style D3 fill:#f0f0f0
    style P2 fill:#fff3e0
    style P6 fill:#c8e6c9
    style P7 fill:#ffcdd2
```

### Penjelasan Diagram:

**External Entities:**
- **E1 (Operator Data)**: User yang mengajukan perubahan COA
- **E2 (Otorisator)**: User yang meng-approve/reject pengajuan perubahan

**Processes:**
- **P1 (Tampilkan Form Edit COA)**: Load data COA dan instance dari database, tampilkan form edit ke operator
- **P2 (Validasi Data Perubahan)**: Validasi data perubahan (mandatory fields, business rules, format)
- **P3 (Simpan Pengajuan)**: Simpan data perubahan sebagai pengajuan pending approval
- **P4 (Tampilkan Daftar Pengajuan)**: Tampilkan daftar pengajuan pending ke otorisator
- **P5 (Tampilkan Detail Perubahan)**: Tampilkan detail before/after perubahan
- **P6 (Proses Approval)**: Approve pengajuan dan update data aktif di database
- **P7 (Proses Rejection)**: Reject pengajuan tanpa mengubah data aktif

**Data Stores:**
- **D1 (ibcore.account)**: Tabel master COA
- **D2 (ibcore.accountinstance)**: Tabel COA per branch & currency
- **D3 (Approval Queue)**: Tabel penyimpanan pengajuan perubahan

**Data Flows:**
1. Operator request form edit → sistem load data dari D1 & D2 → tampilkan form
2. Operator submit perubahan → validasi → simpan ke D3 (approval queue)
3. Otorisator akses daftar pengajuan → sistem load dari D3 → tampilkan list
4. Otorisator pilih pengajuan → sistem load detail → tampilkan before/after
5. Otorisator approve → update D1 & D2 → notifikasi ke operator
6. Otorisator reject → update status di D3 → notifikasi ke operator

**Urutan Proses (Process Sequence):**

**Skenario 1: Pengajuan Perubahan COA (oleh Operator)**
1. **P1**: Operator request ubah COA → sistem query D1 & D2 → tampilkan form edit dengan data existing
2. **P2**: Operator submit data perubahan → sistem validasi data (mandatory, format, business rules)
   - Jika validasi gagal → tampilkan error message ke operator (kembali ke P1)
   - Jika validasi berhasil → lanjut ke P3
3. **P3**: Sistem simpan pengajuan ke D3 (Approval Queue) dengan status "Pending" → kirim notifikasi ke otorisator

**Skenario 2: Approval Perubahan COA (oleh Otorisator)**
4. **P4**: Otorisator request daftar pengajuan → sistem query D3 untuk data pending → tampilkan list pengajuan
5. **P5**: Otorisator pilih pengajuan → sistem query D3 untuk detail → tampilkan before/after perubahan
6. **P6** (jika Approve): 
   - Sistem update data di D1 (ibcore.account)
   - Sistem update data di D2 (ibcore.accountinstance) 
   - Sistem update status pengajuan di D3 menjadi "Approved"
   - Sistem kirim notifikasi approval ke operator (E1)
7. **P7** (jika Reject):
   - Sistem update status pengajuan di D3 menjadi "Rejected"
   - Sistem kirim notifikasi rejection ke operator (E1)
   - Data di D1 & D2 tidak berubah

---

## C4 Component Diagram

Diagram berikut menunjukkan arsitektur komponen sistem menggunakan notasi C4 Model sebagai perbandingan dengan DFD di atas.

```mermaid
C4Component
    title Component Diagram - COA Edit Module

    Person(operator, "Operator Data", "User yang mengajukan perubahan COA")
    Person(otorisator, "Otorisator", "User yang meng-approve/reject perubahan")

    Container_Boundary(fe, "Frontend Application") {
        Component(coaEditUI, "COA Edit UI", "React/Vue Component", "Form edit COA dengan validasi frontend")
        Component(coaListUI, "COA List UI", "React/Vue Component", "Daftar COA")
        Component(authListUI, "Authorization List UI", "React/Vue Component", "Daftar pengajuan untuk otorisasi")
        Component(authDetailUI, "Authorization Detail UI", "React/Vue Component", "Detail perubahan before/after")
    }

    Container_Boundary(be, "Backend Services") {
        Component(coaController, "COA Controller", "REST API", "Endpoint untuk operasi COA")
        Component(validationService, "Validation Service", "Service Layer", "Validasi business rules & data integrity")
        Component(approvalService, "Approval Service", "Service Layer", "Proses approval/rejection")
        Component(notificationService, "Notification Service", "Service Layer", "Kirim notifikasi ke user")
    }

    ContainerDb(accountDB, "Account Database", "PostgreSQL/Oracle", "Menyimpan data COA master (ibcore.account)")
    ContainerDb(instanceDB, "Account Instance Database", "PostgreSQL/Oracle", "Menyimpan data COA per branch & currency (ibcore.accountinstance)")
    ContainerDb(approvalDB, "Approval Queue Database", "PostgreSQL/Oracle", "Menyimpan pengajuan perubahan")

    Rel(operator, coaListUI, "1. Akses menu COA", "HTTPS")
    Rel(operator, coaEditUI, "2. Edit data COA", "HTTPS")
    Rel(coaListUI, coaController, "3. Get list COA", "JSON/HTTPS")
    Rel(coaEditUI, coaController, "4. Get COA data", "JSON/HTTPS")
    
    Rel(coaController, accountDB, "5. Read COA master", "SQL")
    Rel(coaController, instanceDB, "6. Read COA instance", "SQL")
    
    Rel(operator, coaEditUI, "7. Submit changes", "HTTPS")
    Rel(coaEditUI, coaController, "8. Submit changes", "JSON/HTTPS")
    Rel(coaController, validationService, "9. Validate data", "Internal call")
    Rel(coaController, approvalService, "10. Save approval", "Internal call")
    Rel(approvalService, approvalDB, "11. Write approval data", "SQL")
    Rel(approvalService, notificationService, "12. Send notification", "Internal call")
    
    Rel(otorisator, authListUI, "13. Lihat daftar pengajuan", "HTTPS")
    Rel(authListUI, coaController, "14. Get pending approvals", "JSON/HTTPS")
    Rel(coaController, approvalDB, "15. Read approval data", "SQL")
    
    Rel(otorisator, authDetailUI, "16. Review detail", "HTTPS")
    Rel(authDetailUI, coaController, "17. Get approval detail", "JSON/HTTPS")
    Rel(authDetailUI, coaController, "18. Approve/Reject", "JSON/HTTPS")
    
    Rel(coaController, approvalService, "19. Process approval/rejection", "Internal call")
    Rel(approvalService, accountDB, "20. Update on approve", "SQL")
    Rel(approvalService, instanceDB, "21. Update on approve", "SQL")
    Rel(approvalService, approvalDB, "22. Update status", "SQL")
    Rel(approvalService, notificationService, "23. Send notification", "Internal call")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Penjelasan C4 Component Diagram:

**People (Actors):**
- **Operator Data**: User yang mengajukan perubahan COA
- **Otorisator**: User yang melakukan approve/reject pengajuan

**Frontend Components:**
- **COA List UI**: Menampilkan daftar COA yang tersedia
- **COA Edit UI**: Form untuk edit data COA dengan validasi client-side
- **Authorization List UI**: Menampilkan daftar pengajuan yang pending
- **Authorization Detail UI**: Menampilkan detail perubahan (before/after) dan tombol approve/reject

**Backend Components:**
- **COA Controller**: REST API endpoints untuk semua operasi terkait COA dan approval
- **Validation Service**: Business logic untuk validasi data (mandatory fields, format, business rules)
- **Approval Service**: Orchestration logic untuk proses approval/rejection dan update database
- **Notification Service**: Service untuk mengirim notifikasi ke operator atau otorisator

**Databases:**
- **Account Database (D1)**: Database untuk tabel `ibcore.account` (master COA)
- **Account Instance Database (D2)**: Database untuk tabel `ibcore.accountinstance` (COA per branch & currency)
- **Approval Queue Database (D3)**: Database untuk menyimpan pengajuan perubahan pending

**Urutan Interaksi (Sequence):**

*Flow 1: Load dan Edit COA (Step 1-6)*
1. Operator akses menu COA via browser
2. Operator buka form edit COA
3. UI request list COA ke controller
4. UI request data COA detail ke controller
5. Controller query data master dari Account DB
6. Controller query data instance dari Account Instance DB

*Flow 2: Submit Perubahan (Step 7-12)*
7. Operator submit perubahan via form
8. UI kirim data perubahan ke controller
9. Controller panggil Validation Service untuk validasi
10. Controller panggil Approval Service untuk simpan pengajuan
11. Approval Service write data ke Approval Queue DB
12. Approval Service trigger notifikasi ke otorisator

*Flow 3: Review dan Approval (Step 13-23)*
13. Otorisator akses menu otorisasi
14. UI request daftar pending approvals
15. Controller read data dari Approval Queue DB
16. Otorisator pilih dan review detail pengajuan
17. UI request detail perubahan (before/after)
18. Otorisator klik approve/reject
19. Controller panggil Approval Service untuk process keputusan
20-21. (Jika approve) Approval Service update Account DB & Instance DB
22. Approval Service update status di Approval Queue DB
23. Approval Service trigger notifikasi ke operator

**Perbedaan DFD vs C4:**
- **DFD** fokus pada aliran data antar proses, data store, dan external entity (lebih cocok untuk analisis business process)
- **C4 Component** fokus pada arsitektur teknologi, komponen software, dan interaksi antar komponen (lebih cocok untuk desain teknis sistem)
- **Nomor di C4** menunjukkan urutan interaksi (sequence), sedangkan DFD lebih menekankan pada transformasi data

---

## 🖥️ Frontend Requirements (FE)

### FR-COA-001 (FE): Akses Halaman Ubah Rekening (COA)

**Deskripsi:**
Sistem harus menyediakan akses halaman untuk mengubah data rekening COA dari menu COA.

**Actor:** Operator Data

**Functional Acceptance Criteria:**

- Operator dapat membuka menu **Data Master → Data Rekening (COA)**
- Operator dapat memilih salah satu rekening dan klik **Ubah Rekening**
- Sistem menampilkan form edit dengan data existing
- Field **read-only** tetap tidak bisa diubah

**Functional Flow:**


| Step | Actor    | Action                                  | System Response               | Notes                 |
| ------ | ---------- | ----------------------------------------- | ------------------------------- | ----------------------- |
| 1    | Operator | Login                                   | Sistem validasi credential    |                       |
| 2    | Operator | Buka Data Master → Data Rekening (COA) | Sistem tampilkan daftar COA   |                       |
| 3    | Operator | Pilih COA, klik Ubah Rekening           | Sistem tampilkan halaman edit | Pre-fill data dari DB |

---

### FR-COA-002 (FE): Submit Perubahan COA untuk Otorisasi

**Deskripsi:**
Sistem harus menerima perubahan COA dan menyimpannya sebagai pengajuan yang memerlukan otorisasi.

**Actor:** Operator Data

**Functional Acceptance Criteria:**

- Sistem memvalidasi field mandatory & rule FE/BE
- Sistem menyimpan perubahan sebagai **pengajuan** dengan status **Pending Approval**
- Pengajuan muncul di daftar otorisasi untuk Otorisator

**Functional Flow:**


| Step | Actor    | Action                    | System Response                                                 | Notes                    |
| ------ | ---------- | --------------------------- | ----------------------------------------------------------------- | -------------------------- |
| 1    | Operator | Ubah field yang diizinkan | Sistem menerima input                                           |                          |
| 2    | Operator | Klik Submit               | Sistem validasi data                                            |                          |
| 3    | System   | Validasi                  | **IF** valid **THEN** simpan pengajuan **ELSE** tampilkan error |                          |
| 4    | System   | Simpan pengajuan          | Pengajuan masuk daftar otorisasi                                | Status: Pending Approval |

---

### FR-COA-003 (FE): Otorisasi Perubahan COA (Approve/Reject)

**Deskripsi:**
Sistem harus menyediakan daftar pengajuan perubahan COA dan memungkinkan Otorisator melakukan approve/reject.

**Actor:** Otorisator

**Functional Acceptance Criteria:**

- Otorisator dapat membuka daftar otorisasi (pending list)
- Otorisator dapat melihat detail perubahan (before/after)
- Otorisator dapat **Approve** atau **Reject**
- Jika Approve → perubahan diterapkan ke data aktif
- Jika Reject → perubahan dibatalkan, data aktif tidak berubah

**Functional Flow:**


| Step | Actor      | Action                | System Response                   | Notes                   |
| ------ | ------------ | ----------------------- | ----------------------------------- | ------------------------- |
| 1    | Otorisator | Login                 | Sistem validasi                   |                         |
| 2    | Otorisator | Buka daftar otorisasi | Sistem tampilkan data pending     |                         |
| 3    | Otorisator | Pilih pengajuan       | Sistem tampilkan detail perubahan | before/after            |
| 4    | Otorisator | Klik Approve/Reject   | Sistem proses keputusan           |                         |
| 5a   | System     | Approve               | Terapkan perubahan ke data aktif  | Update tabel terkait    |
| 5b   | System     | Reject                | Tandai pengajuan rejected         | Tidak update data aktif |

---

### UI/UX Specification

#### Menu & Navigasi

- **Data Master → Data Rekening (COA) → Ubah Rekening**

#### Proses Utama (UI)

1. Operator pilih rekening → buka form ubah
2. Operator edit field yang diizinkan
3. Operator submit → masuk otorisasi
4. Otorisator approve/reject

---

#### Mockup

- [FSD_COA_Edit.html](../assets/FSD_COA_Edit.html)

#### Screenshot

Screenshot Tab `Konfigurasi Pelaporan`

![COA Ubah Rekening 1](../assets/FSD_COA_Edit_ss1.png)

Screenshot Tab `Konfigurasi Saldo & Transaksi`

![COA Ubah Rekening 2](../assets/FSD_COA_Edit_ss2.png) |

---

### Frontend Field Specification & Validation

> Catatan: Beberapa label field UI dipetakan ke kolom DB berikut.

#### Form Ubah Rekening (Master `ibcore.account`)


| Field (UI)                    | Mandatory | DB Column                                   | Rules                                                 |
| ------------------------------- | ----------- | --------------------------------------------- | ------------------------------------------------------- |
| Kelompok Rekening             | M         | `account_group_code`                        | Read-only dari DB                                     |
| Tanggal Pembuatan             | M         | `time_create`                               | Read-only dari DB                                     |
| Rekening Administratif Aktiva | O         | `isactivaoffbalancesheet`                   | Read-only dari DB                                     |
| Account RPV                   | O         | `isrpvaccount`                              | Read-only dari DB                                     |
| Rekening Induk                | M         | `fl_parent_account`                         | Read-only. Parent rekening                            |
| Nama Rekening Induk           | M         | (lookup)                                    | Read-only. Lookup dari`account.account_name` parent   |
| Kode Rekening                 | M         | `account_code`                              | Read-only                                             |
| Nama Rekening                 | M         | `account_name`                              | Tidak boleh kosong. Max 200 char                      |
| Deskripsi Rekening            | O         | `account_desc`                              | Max 400 char                                          |
| Grup Rekening                 | M         | `account_type` / atau `account_group_code`* | Sesuaikan implementasi sistem: klasifikasi laporan    |
| Detail                        | O         | `is_detail`                                 | Read-only. Posting account indicator                  |
| Keterhubungan CPA             | O         | `fl_cpa_accountcode`                        | Pilih dari referensi CPA                              |
| LBUS Code                     | O         | `lbus_code`                                 | Pelaporan regulator                                   |
| LBUS Type                     | O         | `lbus_type`                                 | Pelaporan regulator                                   |
| LSMK Code                     | O         | `lsmk_code`                                 | Pelaporan regulator                                   |
| LSMK Type                     | O         | `lsmk_type`                                 | Pelaporan regulator                                   |
| LBBU Code                     | O         | `lbbu_code`                                 | Laporan internal                                      |
| Intern Code                   | O         | `intern_code`                               | Klasifikasi internal                                  |
| PUB Code                      | O         | `pub_code`                                  | Publikasi/laporan tertentu                            |
| Sandi BI                      | O         | `sandi_bi`                                  | Max 10 char                                           |
| Tipe Pajak                    | O         | `tax_type`                                  | Dari master pajak                                     |
| Tenaga Ahli                   | O         | `tax_flag_expert`                           | Default uncheck                                       |
| Kode Pajak                    | O         | `tax_code`                                  | Max 20 char                                           |
| Nomor Akun Pajak              | O         | `tax_account_code`                          | Refer ke`account.account_code` dengan `is_detail='T'` |
| Tarif Pajak NPWP              | O         | `tax_rate_npwp`                             | Numerik >= 0, default 0.00                            |
| Tarif Pajak Non NPWP          | O         | `tax_rate_non_npwp`                         | Numerik >= 0, default 0.00                            |
| Flag PPh21                    | O         | `tax_flag_pph21`                            | Opsional, flag                                        |
| RPV RAK Report Show           | O         | `isrpvrakreportshow`                        | Flag tampil report                                    |
| Hidden Offbalance Sheet       | O         | `is_hidden_offbalancesheet`                 | Flag                                                  |
| RAK Account                   | O         | `israkaccount`                              | Flag                                                  |

\*Catatan: pada dokumen lama ada "Grup Rekening" sebagai klasifikasi laporan (misal ASET). Di schema tersedia `account_group_code` dan `account_type`. Implementasi final perlu konsisten (pilih salah satu atau gabungkan aturan).

---

#### Tab: Parameter Saldo dan Transaksi (Default di `ibcore.account`)


| Field (UI)                  | Mandatory | DB Column                 | Rules                                                                    |
| ----------------------------- | ----------- | --------------------------- | -------------------------------------------------------------------------- |
| Saldo Normal (Default)      | M         | `normal_balance_type_def` | Dropdown: {Debet, Kredit, Netral} (mapping ke kode internal`varchar(1)`) |
| Saldo Harus Nihil (Default) | M         | `is_zero_balance_def`     | Dropdown: {Boleh Tidak Nihil, Harus Nihil} (mapping`varchar(1)`)         |
| Status Transaksi (Default)  | M         | `trx_permit_type_def`     | Dropdown status transaksi (mapping`varchar(1)`)                          |

##### Button Rules


| Button                        | Aksi                                                                                           |
| ------------------------------- | ------------------------------------------------------------------------------------------------ |
| Set Semua Status Saldo Normal | Update`accountinstance.normal_balance_type` untuk seluruh instance sesuai default yang dipilih |
| Set Semua Status Saldo Nihil  | Update`accountinstance.is_zero_balance` untuk seluruh instance sesuai default yang dipilih     |
| Set Semua Status Transaksi    | Update`accountinstance.trx_permit_type` untuk seluruh instance sesuai default yang dipilih     |

---

#### Grid: List Account Instance (`ibcore.accountinstance`)


| Field (UI)        | Mandatory | DB Column             | Rules                           |
| ------------------- | ----------- | ----------------------- | --------------------------------- |
| Kode Kantor       | M         | `branch_code`         | Read-only                       |
| Nama Kantor       | M         | (lookup)              | Read-only, lookup master branch |
| Kode Valuta       | M         | `currency_code`       | Read-only                       |
| Saldo Normal      | M         | `normal_balance_type` | Editable                        |
| Saldo Harus Nihil | M         | `is_zero_balance`     | Editable                        |
| Tipe Bertransaksi | M         | `trx_permit_type`     | Editable                        |

---

## 🛠️ Backend Requirements (BE)

### Backend Data Requirements

#### Entity: `ibcore.account` (Master COA)

Primary Key: `account_code`

Kolom penting yang relevan untuk modul Ubah Rekening:

- Identitas & hirarki: `account_code`, `account_name`, `account_level`, `fl_parent_account`, `is_detail`
- Klasifikasi & pelaporan: `account_group_code`, `account_type`, `lbus_code`, `lbus_type`, `lsmk_code`, `lsmk_type`, `lbbu_code`, `intern_code`, `pub_code`, `sandi_bi`
- Parameter saldo & transaksi (default): `normal_balance_type_def`, `is_zero_balance_def`, `trx_permit_type_def`
- Parameter pajak: `tax_type`, `tax_code`, `tax_account_code`, `tax_rate_npwp`, `tax_rate_non_npwp`, `tax_flag_pph21`, `tax_flag_expert`
- Flag lain: `isactivaoffbalancesheet`, `isrpvrakreportshow`, `isrpvaccount`, `is_hidden_offbalancesheet`, `israkaccount`
- Audit: `userid_create`, `time_create`, `userid_last_modified`, `time_last_modified`

#### Entity: `ibcore.accountinstance` (COA per Branch & Currency)

Primary Key: `accountinstance_id`

Kolom penting yang relevan untuk modul Ubah Rekening:

- Identitas & relasi: `accountinstance_id`, `account_code`, `branch_code`, `currency_code`
- Parameter saldo & transaksi (per instance): `normal_balance_type`, `is_zero_balance`, `trx_permit_type`, `isbolehinput`, `balance_sign`
- (Read-only untuk konteks perubahan COA): berbagai kolom saldo seperti `balance`, `trial_balance`, dll.

---

### BE-COA-001: Validasi Submit Pengajuan

**Input minimal yang harus ada:**

- `account_code`
- `changes` (daftar field yang berubah)
- `alasan` (reason) jika diwajibkan oleh kebijakan otorisasi
- `user_input` (userid operator)

**Validasi:**

- `account_code` harus exist di `ibcore.account`
- Field perubahan hanya boleh pada whitelist field editable
- Numeric (tarif pajak) tidak boleh negatif
- Default parameter (saldo/transaksi) harus punya nilai yang valid
- Jika ada perubahan ke accountinstance, pastikan baris instance target exist

---

### BE-COA-002: Persist & Approval Apply

**Saat submit:**

- Simpan pengajuan perubahan + detail before/after (untuk audit & review otorisasi)
- Status pengajuan: Pending Approval

**Saat approve:**

- Update `ibcore.account` sesuai perubahan master
- Update `ibcore.accountinstance` sesuai perubahan per instance
- Update audit field `userid_last_modified`, `time_last_modified` pada `ibcore.account`
- Status pengajuan: Approved

**Saat reject:**

- Status pengajuan: Rejected
- Tidak ada perubahan ke data aktif

---

## 📌 Shared Business Rules


| Rule ID    | Description                                                                                                               |
| ------------ | --------------------------------------------------------------------------------------------------------------------------- |
| FR-COA-R01 | `account_code` bersifat **read-only** dan tidak boleh diubah                                                              |
| FR-COA-R02 | `fl_parent_account` (rekening induk) bersifat **read-only** pada proses ubah rekening (sesuai dokumen awal)               |
| FR-COA-R03 | Semua perubahan wajib melalui**otorisasi** sebelum efektif                                                                |
| FR-COA-R04 | Jika pengajuan**Reject**, data aktif pada `account`/`accountinstance` tidak berubah                                       |
| FR-COA-R05 | Perubahan parameter default (di`account`) dapat dipropagasikan ke seluruh `accountinstance` melalui tombol "Set Semua..." |
| FR-COA-R06 | Field tarif pajak (`tax_rate_npwp`, `tax_rate_non_npwp`) tidak boleh negatif dan default 0.00 jika kosong                 |

---

## Open Questions (untuk finalisasi implementasi)


| # | Question                                                                          | Status | Notes                               |
| --- | ----------------------------------------------------------------------------------- | -------- | ------------------------------------- |



---

## Change Log

### 2026-01-19
- Inisialisasi 
- Menyesuaikan **Data Model** dan seluruh mapping field ke schema:
  - `ibcore.account`
  - `ibcore.accountinstance`
