
# FSD – FingerScan Biometrik

## Document Metadata

| Item | Value |
|------|-------|
| Module | FingerScan Biometrik – Otorisasi Transaksi |
| Parent PRD | PRD-BJBS-FingerScan-01 |
| Version | 1.0 |
| Date | 2025 |
| Status | Draft |
| Owner | IT / System Owner |
| Notes | Dokumen FSD untuk sistem otorisasi transaksi berbasis sidik jari |

---

## Daftar Isi

- [1. Overview & Scope](#1-overview--scope)
- [2. Actors & Roles](#2-actors--roles)
- [3. Shared Business Rules](#3-shared-business-rules)
- [4. Backend Functional Specification](#4-backend-functional-specification)
  - [4.1 Use Case: Enrollment Sidik Jari](#41-use-case-enrollment-sidik-jari)
  - [4.2 Use Case: Verifikasi Fingerprint](#42-use-case-verifikasi-fingerprint)
  - [4.3 Use Case: Lock/Unlock User Fingerprint](#43-use-case-lockunlock-user-fingerprint)
  - [4.4 Use Case: Aktivasi Fallback Password](#44-use-case-aktivasi-fallback-password)
  - [4.5 Use Case: Audit Trail Logging](#45-use-case-audit-trail-logging)
- [5. Frontend Functional Specification](#5-frontend-functional-specification)
  - [5.1 Screen: Enrollment Fingerprint](#51-screen-enrollment-fingerprint)
  - [5.2 Screen: Verifikasi Fingerprint](#52-screen-verifikasi-fingerprint)
  - [5.3 Screen: Fingerprint Management (Admin)](#53-screen-fingerprint-management-admin)
  - [5.4 UI Actions](#54-ui-actions)
- [6. Integration Notes](#6-integration-notes)
  - [6.1 Integrasi dengan Sistem Eksisting](#61-integrasi-dengan-sistem-eksisting)
  - [6.2 Service Integration untuk Surrounding Apps](#62-service-integration-untuk-surrounding-apps)
  - [6.3 Komunikasi Antar Komponen](#63-komunikasi-antar-komponen)
- [Appendix A – UI Field Specification](#appendix-a--ui-field-specification)
- [Appendix B – Backend Data Mapping](#appendix-b--backend-data-mapping)
- [Appendix C – Traceability Matrix](#appendix-c--traceability-matrix)
- [Appendix D – Security Requirements](#appendix-d--security-requirements)
- [Appendix E – Non-Functional Requirements](#appendix-e--non-functional-requirements)
- [Appendix F – Open Points](#appendix-f--open-points)
- [Change Log](#change-log)

---

## 1. Overview & Scope

Modul **FingerScan Biometrik** digunakan untuk menggantikan otorisasi berbasis password menjadi **sidik jari (finger scan biometrik)** di seluruh jaringan kantor Bank.

**Tujuan:**

- Mengganti otorisasi berbasis password menjadi sidik jari
- Meningkatkan keamanan dan mengurangi fraud internal
- Memastikan kehadiran fisik approval
- Mempercepat proses layanan transaksi

**Cakupan fungsi:**

- Enrollment sidik jari user (definitif dan alternate)
- Verifikasi sidik jari untuk approval transaksi
- Manajemen perangkat dan station
- Fallback mechanism ke password
- Audit trail dan logging

**Komponen Sistem:**

- **Hardware:** DigitalPersona 4500 Fingerprint Reader
- **Fingerprint Service & Fingerprint FE** untuk verifikasi
- **Enrollment Service** untuk pendaftaran awal user
- **Central Repository:** Database biometrik terenkripsi

---

## 2. Actors & Roles

| Actor | Description |
|-------|-------------|
| User (Maker) | Melakukan input transaksi yang memerlukan otorisasi |
| Approver | Melakukan verifikasi fingerprint untuk otorisasi transaksi |
| Administrator TI | Mengelola enrollment, device, dan parameter sistem |
| Auditor | Mengakses log dan laporan audit fingerprint |
| Admin Kantor Pusat (TI) | Memberikan persetujuan fallback password |

---

## 3. Shared Business Rules

| Rule ID | Description |
|---------|-------------|
| BR-FS-01 | Setiap user wajib melakukan enrollment minimal 2 sidik jari dari kedua tangan |
| BR-FS-02 | Approval tidak dapat dilakukan tanpa verifikasi fingerprint yang valid |
| BR-FS-03 | Sistem mengunci akun setelah 3 kali percobaan verifikasi gagal |
| BR-FS-04 | Fallback password hanya dapat diaktifkan dengan persetujuan Admin Kantor Pusat (TI) |
| BR-FS-05 | Fallback password memiliki durasi waktu tertentu dan akan kembali ke fingerprint setelah expired |
| BR-FS-06 | Hanya user aktif di HRMIS yang dapat diverifikasi |
| BR-FS-07 | Data biometrik harus dienkripsi at rest dan in transit |
| BR-FS-08 | Hanya template fingerprint yang disimpan (bukan gambar mentah) |
| BR-FS-09 | Verifikasi fingerprint maksimal 30 detik |
| BR-FS-10 | Akurasi verifikasi minimal 97% match |

---

## 4. Backend Functional Specification

### 4.1 Use Case: Enrollment Sidik Jari

**Purpose**
Mendaftarkan sidik jari user untuk pertama kali ke dalam sistem.

**Precondition**

- User terdaftar dan aktif di HRMIS
- User telah login via OIDC
- Perangkat fingerprint terhubung dan aktif

**Input**

- `user_id`
- `finger_templates[]` (minimal 2 jari dari kedua tangan)
- `station_id`

**Process**

1. Sistem memvalidasi status user di HRMIS
2. Sistem memvalidasi koneksi perangkat fingerprint
3. Sistem melakukan capture sidik jari melalui Fingerstation
4. Sistem mengenkripsi template sidik jari
5. Sistem menyimpan template ke database pusat

**Output**

- Status enrollment (sukses/gagal)
- `enrollment_id`

**Business Rules:** BR-FS-01, BR-FS-06, BR-FS-07, BR-FS-08

---

### 4.2 Use Case: Verifikasi Fingerprint

**Purpose**
Memverifikasi sidik jari user untuk proses approval transaksi.

**Precondition**

- User telah melakukan enrollment
- User tidak dalam status terkunci
- Perangkat fingerprint terhubung dan aktif

**Input**

- `user_id`
- `session_id`
- `station_id`
- `transaction_reference`

**Process**

1. Sistem membuat session verifikasi
2. Sistem mengirim perintah capture ke Fingerstation
3. Fingerstation melakukan capture sidik jari
4. Sistem menerima template hasil capture
5. Sistem melakukan matching dengan template tersimpan
6. Sistem mencatat hasil verifikasi ke audit log
7. Jika gagal, sistem increment counter kegagalan
8. Jika counter kegagalan >= 3, sistem mengunci user

**Output**

- Status verifikasi (sukses/gagal)
- `verification_id`
- Timestamp verifikasi

**Business Rules:** BR-FS-02, BR-FS-03, BR-FS-09, BR-FS-10

---

### 4.3 Use Case: Lock/Unlock User Fingerprint

**Purpose**
Mengunci atau membuka kunci akun user di level fingerprint.

**Input**

- `user_id`
- `action` (lock/unlock)
- `admin_user_id`
- `reason`

**Process**

1. Sistem memvalidasi authority admin
2. Sistem mengubah status lock user
3. Jika unlock, sistem reset counter kegagalan
4. Sistem mencatat aktivitas ke audit log

**Output**

- Status operasi (sukses/gagal)

**Business Rules:** BR-FS-03

---

### 4.4 Use Case: Aktivasi Fallback Password

**Purpose**
Mengaktifkan fallback password sementara untuk user.

**Precondition**

- Disetujui oleh Admin Kantor Pusat (TI)
- Ada alasan valid (perangkat rusak, kondisi darurat)

**Input**

- `user_id`
- `duration_days`
- `admin_user_id`
- `reason`

**Process**

1. Sistem memvalidasi authority Admin Kantor Pusat
2. Sistem mengaktifkan mode fallback password
3. Sistem set expiry date berdasarkan durasi
4. Sistem mencatat aktivitas ke audit log
5. Scheduler akan menonaktifkan fallback setelah expired

**Output**

- Status aktivasi (sukses/gagal)
- Tanggal expiry fallback

**Business Rules:** BR-FS-04, BR-FS-05

---

### 4.5 Use Case: Audit Trail Logging

**Purpose**
Mencatat semua aktivitas verifikasi dan approval.

**Data yang Dicatat**

| Field | Description |
|-------|-------------|
| application_code | Kode aplikasi yang memanggil verifikasi |
| transaction_type | Jenis transaksi |
| approval_time | Waktu approval |
| reference_number | Nomor referensi transaksi |
| ip_address | IP address station |
| input_authorization | Tipe otorisasi (fingerprint/fallback) |
| user_input | User yang menginput transaksi |
| user_author | User yang melakukan approval |
| timestamp | Timestamp lengkap |

**Business Rules:** BR-FS-07

---

## 5. Frontend Functional Specification

### 5.1 Screen: Enrollment Fingerprint

**Fungsi utama:**

- Menampilkan panduan enrollment
- Menampilkan status koneksi perangkat
- Capture sidik jari dengan feedback visual
- Menampilkan progress enrollment per jari

**UI Components:**

| Component | Description |
|-----------|-------------|
| Device Status Indicator | Menampilkan status koneksi perangkat |
| Finger Selector | Pemilihan jari yang akan di-capture |
| Capture Area | Area visual untuk panduan posisi jari |
| Progress Bar | Progress enrollment per jari |
| Submit Button | Mengirim data enrollment |

---

### 5.2 Screen: Verifikasi Fingerprint

**Fungsi utama:**

- Menampilkan prompt verifikasi
- Menampilkan countdown timer
- Feedback hasil verifikasi (sukses/gagal)
- Menampilkan sisa percobaan jika gagal

**UI Components:**

| Component | Description |
|-----------|-------------|
| Transaction Info | Informasi transaksi yang akan di-approve |
| Verification Prompt | Instruksi untuk scan sidik jari |
| Timer | Countdown waktu verifikasi (max 30 detik) |
| Result Indicator | Status hasil verifikasi |
| Retry Counter | Sisa percobaan (max 3x) |

---

### 5.3 Screen: Fingerprint Management (Admin)

**Fungsi utama:**

- Mengelola perangkat (station dan reader)
- Melakukan enrollment user baru
- Mengatur parameter sistem
- Memantau status station secara real-time
- Melihat audit log dan aktivitas

**UI Components:**

| Component | Description |
|-----------|-------------|
| Device List | Daftar perangkat dan status |
| User Enrollment Form | Form enrollment user baru |
| Parameter Settings | Pengaturan timeout, minimal jari, dll |
| Station Monitor | Dashboard monitoring station |
| Audit Log Viewer | Tampilan log aktivitas |

---

### 5.4 UI Actions

| Action | Description |
|--------|-------------|
| Start Enrollment | Memulai proses enrollment sidik jari |
| Capture Finger | Melakukan capture sidik jari |
| Verify Fingerprint | Memulai proses verifikasi |
| Retry Verification | Mencoba verifikasi ulang |
| Use Fallback | Menggunakan password sebagai fallback |
| Lock User | Mengunci user di level fingerprint |
| Unlock User | Membuka kunci user |
| Activate Fallback | Mengaktifkan mode fallback password |

---

## 6. Integration Notes

### 6.1 Integrasi dengan Sistem Eksisting

| System | Integration Point | Description |
|--------|------------------|-------------|
| DAF-Core | Otorisasi Entri Data | Produk Parameter, Layanan Counter, Treasury |
| DAF-Financing | Otorisasi & Override | Menu Financing |
| DAF-Treasury | Otorisasi & Override | Menu Treasury |
| DAF-Enterprise | Authorization List | Menu Enterprise |
| BDS-CS Teller | Otorisasi Entri Data | List Otorisasi Web BDS |
| OIDC | Autentikasi | SSO internal |
| HRMIS | User Validation | Data karyawan aktif |

### 6.2 Service Integration untuk Surrounding Apps

Fingerprint Service menyediakan API untuk integrasi dengan:

- CMS (Content Management System)
- APUPPT
- VA (Virtual Account)
- QRIS
- CAM
- VMS

### 6.3 Komunikasi Antar Komponen

| From | To | Protocol | Description |
|------|----|----------|-------------|
| Business App | Fingerscan Service | REST/HTTPS | Request verifikasi |
| Fingerscan Service | Fingerstation | WebSocket (secure) | Perintah capture |
| Fingerstation | Fingerscan Service | WebSocket (secure) | Hasil capture |
| Fingerscan Service | Database | Encrypted | Simpan/retrieve template |
| Fingerscan Service | Redis | Encrypted | Cache session verifikasi |
| All Components | All Components | HTTPS + mTLS | Komunikasi aman |

---

## Appendix A – UI Field Specification

### A.1 Form Enrollment

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| User ID | Text (Read-only) | Yes | Auto-populated from OIDC |
| Nama User | Text (Read-only) | Yes | Auto-populated from HRMIS |
| Cabang | Text (Read-only) | Yes | Auto-populated |
| Jari Terdaftar | Grid | Yes | Minimal 2 jari dari kedua tangan |

### A.2 Form Verifikasi

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| Transaction Ref | Text (Read-only) | Yes | Auto-populated |
| Transaction Type | Text (Read-only) | Yes | Auto-populated |
| Timeout | Timer | Yes | Max 30 detik |
| Retry Count | Counter | Yes | Max 3x |

### A.3 Form Fallback Activation

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| User ID | Text | Yes | Must exist in system |
| Duration (Days) | Number | Yes | Min 1, Max 30 |
| Reason | Text Area | Yes | Min 10 characters |
| Approval Admin | Text (Read-only) | Yes | Auto-populated from session |

---

## Appendix B – Backend Data Mapping

### B.1 Entity: User Fingerprint

| Attribute | Type | Description |
|-----------|------|-------------|
| user_id | String | ID user dari HRMIS |
| enrollment_id | UUID | ID enrollment |
| finger_templates | Encrypted Blob | Template sidik jari terenkripsi |
| finger_count | Integer | Jumlah jari terdaftar |
| status | Enum | ACTIVE, LOCKED, INACTIVE |
| lock_counter | Integer | Counter kegagalan verifikasi |
| fallback_enabled | Boolean | Status fallback password |
| fallback_expiry | DateTime | Tanggal expired fallback |
| created_at | DateTime | Waktu enrollment |
| updated_at | DateTime | Waktu update terakhir |

### B.2 Entity: Verification Session

| Attribute | Type | Description |
|-----------|------|-------------|
| session_id | UUID | ID session verifikasi |
| user_id | String | ID user yang verifikasi |
| station_id | String | ID station yang digunakan |
| transaction_ref | String | Referensi transaksi |
| status | Enum | PENDING, SUCCESS, FAILED, TIMEOUT |
| created_at | DateTime | Waktu mulai session |
| completed_at | DateTime | Waktu selesai session |

### B.3 Entity: Fingerstation

| Attribute | Type | Description |
|-----------|------|-------------|
| station_id | UUID | ID station |
| branch_code | String | Kode cabang |
| device_serial | String | Serial number device |
| status | Enum | ONLINE, OFFLINE, MAINTENANCE |
| last_heartbeat | DateTime | Waktu heartbeat terakhir |
| ip_address | String | IP address station |

### B.4 Entity: Audit Log

| Attribute | Type | Description |
|-----------|------|-------------|
| log_id | UUID | ID log |
| application_code | String | Kode aplikasi |
| transaction_type | String | Jenis transaksi |
| approval_time | DateTime | Waktu approval |
| reference_number | String | Nomor referensi |
| ip_address | String | IP address |
| input_authorization | String | Tipe otorisasi |
| user_input | String | User input transaksi |
| user_author | String | User approval |

---

## Appendix C – Traceability Matrix

| FR ID | Description | BE Use Case | UI Screen | Business Rule |
|-------|-------------|-------------|-----------|---------------|
| FR-FS-001 | Enrollment sidik jari | Enrollment Sidik Jari | Enrollment Fingerprint | BR-FS-01, BR-FS-06 |
| FR-FS-002 | Dual finger registration | Enrollment Sidik Jari | Enrollment Fingerprint | BR-FS-01 |
| FR-FS-003 | Central repository storage | Enrollment Sidik Jari | - | BR-FS-07, BR-FS-08 |
| FR-FS-004 | Verification process | Verifikasi Fingerprint | Verifikasi Fingerprint | BR-FS-02, BR-FS-09, BR-FS-10 |
| FR-FS-005 | Approval workflow | Verifikasi Fingerprint | Verifikasi Fingerprint | BR-FS-02 |
| FR-FS-006 | Lock mechanism | Lock/Unlock User | Fingerprint Management | BR-FS-03 |
| FR-FS-007 | Fallback password | Aktivasi Fallback Password | Fingerprint Management | BR-FS-04, BR-FS-05 |
| FR-FS-008 | Audit trail | Audit Trail Logging | Fingerprint Management | BR-FS-07 |

---

## Appendix D – Security Requirements

| Req ID | Requirement | Implementation |
|--------|-------------|----------------|
| S-01 | Encrypted Template | Template fingerprint dienkripsi sebelum disimpan |
| S-02 | Secure Channel | HTTPS + mTLS untuk semua komunikasi |
| S-03 | OIDC Integration | Autentikasi user via SSO internal |
| S-04 | Access Policy | Validasi status aktif user di HRMIS |
| S-05 | Redis Cache | Data sementara di Redis dengan TTL |

---

## Appendix E – Non-Functional Requirements

| Req ID | Requirement | Target |
|--------|-------------|--------|
| NF-01 | Response Time | < 5 detik per verifikasi |
| NF-02 | Verification Timeout | Max 30 detik |
| NF-03 | Accuracy | >= 97% match rate |
| NF-04 | Availability | Operasional selama jam kerja tanpa downtime |
| NF-05 | Concurrent Users | Mampu menangani concurrent verification requests |

---

## Appendix F – Open Points

| No | Description | Status |
|----|-------------|--------|
| 1 | Detail wireframe UI | TBD |
| 2 | Spesifikasi API endpoint | TBD |
| 3 | Detail error codes dan messages | TBD |
| 4 | Prosedur disaster recovery | TBD |

---

## Change Log

| Date | Version | Description |
|------|---------|-------------|
| 2025 | 1.0 | Initial draft FSD dari PRD-BJBS-FingerScan-01 |
