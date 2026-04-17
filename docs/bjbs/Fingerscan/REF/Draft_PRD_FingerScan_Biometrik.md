# **PRODUCT REQUIREMENT DOCUMENTS

FingerScan Biometric**




Dipersiapkan oleh


PT Ihsan Solusi Informatika
Jl. PHH Mustofa No. 39
Ruko Surapati Core C-7 Bandung




# AUTHOR


# DAFTAR PERUBAHAN


# DAFTAR ISI


# Tujuan
Menetapkan spesifikasi produk untuk pengembangan **fitur otorisasi transaksi berbasis sidik jari (finger scan biometrik)** di seluruh jaringan kantor Bank.
Mengganti otorisasi berbasis password menjadi sidik jari.
Meningkatkan keamanan dan mengurangi fraud internal.
Memastikan kehadiran fisik approval.
Mempercepat proses layanan transaksi.
# Ringkasan Sistem
Komponen Sistem
Hardware: DigitalPersona 4500 Fingerprint Reader.
Fingerprint Service & Fingerprint FE untuk verifikasi 
Enrollment Service untuk pendaftaran awal user.
Central Repository: Database biometrik terenkripsi.
# Ruang Lingkup
In Scope:
Enrollment biometrik
Device yang digunakan DigitalPersona 4500 Fingerprint Reader
Integrasi dengan aplikasi berikut : DAF , BDS CS Teller
Menyediakan service integrasi dengan surrounding apps via Fingerprint Service 
Penyimpanan template terenkripsi

Out of Scope:
Biometrik selain sidik jari
Login sistem 
Proses integrasi dengan surrounding apps tidak termasuk dalam timeline utama
# List Requirement

## A. Fungsional (Functional Requirements)

## B. Non-Fungsional (Non-Functional Requirements)

## C. Integrasi (Integration Requirements)

## D. Keamanan (Security Requirements)

## E. Operasional (Operational Requirements)

## F. Risiko & Mitigasi (Risk Control Requirements)

## G. Audit & Logging

## H. Acceptance Criteria

# Activity Diagram


# Wireframe


# Arsitektur Sistem

Diagram di atas memperlihatkan integrasi antara sistem baru (berwarna biru) dengan sistem eksisting (berwarna hijau).

**Penjelasan Layer: **
a.  Layer Atas
Fingerprint Service, REDIS dan DB Fingerprint: modul middleware yang memverifikasi template terhadap database biometrik dan mengelola cache melalui Redis.
OIDC: menangani autentikasi user berbasis SSO.
HRMIS: sumber data karyawan aktif.
   
b. Layer Tengah – Integrasi Sistem Eksisting Front-End & Integrasi Sistem Eksisting Service
Fingerprint Management : antarmuka yang menghubungkan device dengan layanan Fingerprint Service.
DAF dan BDS: aplikasi core banking yang memanfaatkan Fingerprint Service untuk approval transaksi
Surrounding Apps: sistem pendukung (CMS, APUPPT, VA, QRIS, dll.) yang juga dapat terhubung dengan Fingerprint Service.

c. Layer Bawah – Fingerstation & Device
Fingerprint Device: perangkat DigitalPersona 4500 yang menangkap data biometrik
Fingerstation: aplikasi lokal untuk konversi hasil scan ke template digital.

**Komponen Utama :**
**Fingerstation
Peran utama:**
Menjadi penghubung antara perangkat fingerprint fisik (scanner) dan sistem backend.
Melakukan proses perekaman (capture) dan pengiriman hasil fingerprint ke layanan pusat.

**Interaksi**:
Menerima perintah capture dari Fingerscan Service melalui koneksi aman.
Mengirim hasil tangkapan sidik jari (template) kembali ke Fingerscan Service.
Beroperasi pada perangkat di teller, counter cabang, atau terminal yang memiliki device reader fingerscan.
**Catatan**: 
Station tidak menyimpan data biometrik permanen. Semua hasil dikirim ke server pusat untuk diproses lebih lanjut.
**Fingercan Service**
**Peran utama:**
Mengatur seluruh siklus hidup proses verifikasi sidik jari — mulai dari pembuatan sesi, pemilihan station, hingga pencocokan hasil.
Menjadi pusat komunikasi antara aplikasi bisnis dan station.
Membuat dan mengelola session verifikasi.
Mengirim perintah capture ke station yang aktif di cabang terkait.
Melakukan matching antara hasil fingerprint dengan template yang tersimpan.
Mengirim hasil akhir (sukses/gagal) ke sistem aplikasi bisnis.
Melakukan counter kegagalan,  jika melebihi batas maksimal gagal akan blokir user fingerscan.
**Interaksi:**
Berkomunikasi dua arah dengan Station melalui WebSocket aman.
Menerima permintaan capture dari Business App melalui API REST/HTTPS.
Menyampaikan hasil ke Business App (Core Banking / Authorization Service)  melalui API REST/HTTPS.
Database fingerscan dan REDIS

**Fingercan Management**
**Peran utama:**
**Portal web administratif** yang digunakan oleh petugas operasional dan administrator untuk:
**Mengelola perangkat** (station dan reader) yang terhubung ke sistem biometrik.
**Melakukan enrollment** pengguna baru (pegawai atau nasabah) dengan sidik jari.
**Mengatur kebijakan & parameter sistem** seperti batas waktu (timeout), minimal jari terdaftar.
**Memantau kesehatan dan status station** di seluruh cabang secara real-time.
**Melihat audit log dan aktivitas sistem** terkait verifikasi serta enrollment.

Portal ini menjadi **antarmuka visual utama** dari sistem Fingerscan yang menghubungkan pengguna non-teknis dengan layanan backend **Fingerscan Service**.
**Interaksi:**
Berkomunikasi dengan **Fingerscan Service ** melalui REST/HTTPS untuk semua operasi CRUD dan konfigurasi.
Menerima data status dan hasil enrollment real-time dari **Fingerscan Service**.
Menggunakan **OIDC / Identity Provider** untuk autentikasi pengguna.
Mengakses database audit dan registry perangkat melalui **Fingerscan Service**


**Business Applications (DAF, BDS, and Surrounding Apps)**
**Peran utama:**
Berfungsi sebagai aplikasi bisnis yang memanfaatkan layanan Fingerscan service untuk otorisasi transaksi dan autentikasi pengguna.
Menjadi titik awal interaksi pengguna terhadap proses verifikasi sidik jari di sistem perbankan atau layanan internal.
Melanjutkan proses approval  ke  alur transaksi atau penyimpanan data , jika otentikasi biometrik berhasil .
**Interaksi:**
Berkomunikasi langsung dengan **Fingerscan Service** melalui API REST untuk membuat dan memantau sesi verifikasi.
Melanjutkan proses data setelah hasil verifikasi diterima.**
**
**Catatan:**
Business Applications hanya memicu dan mengonsumsi hasil verifikasi — tidak menangani proses capture atau matching sidik jari. Semua logika biometrik berada di sisi** Fingerscan Service** dan **Fingerstation.**

| Nomor Dokumen | Nomor Dokumen | Halaman |
| --- | --- | --- |
| PRD-BJBS-FingerScan-01 | PRD-BJBS-FingerScan-01 |  |
| Versi | 1.0.0 | 2025 |


| Nama | Role |
| --- | --- |
| Aulia Riefqi Ardana |  |


| Versi | Tanggal | Direview oleh | Disetujui oleh | Ringkasan Perubahan |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |


| ID | Nama Requirement | Deskripsi |
| --- | --- | --- |
| 01 | Enrollment | Sistem menyediakan modul pendaftaran sidik jari untuk user definitif dan alternate. |
| 02 | Dual Finger | Sistem dapat merekam minimal dua sidik jari kedua tangan dengan parameterize. |
| 03 | Central Repository | Data template sidik jari disimpan secara terpusat di database fingerprint. |
| 04 | Verification Process | Sistem melakukan verifikasi fingerprint setiap kali approval dilakukan. |
| 05 | Approval Workflow | Approval tidak dapat dilakukan tanpa verifikasi fingerprint yang valid. |
| 06 | Lock Mechanism | Sistem harus mengunci akun setelah 3 kali percobaan verifikasi gagal. 
Skemanya seperti buka blokir, yang di lock user nya di level fingerprint |
| 07 | Fallback Password | Fallback password dapat dilakukan dengan persetujuan user kantor pusat (TI). Fallback password hanya dapat ditentukan berapa hari atau ada durasi tertentu. Dan setelah lewat durasi akan kembali menggunakan fingerprint. |
| 08 | Audit Trail | Semua aktivitas verifikasi dan approval dicatat secara lengkap dengan event (kode aplikasi, jenis transaksi, waktu approval,  Reference number,  IP,  input authorization, user input, user author, jam, hari) |


| ID | Nama Requirement | Deskripsi |
| --- | --- | --- |
| NF-01 | Encryption | Data biometrik harus dienkripsi at rest dan in transit. |
| NF-02 | Response Time | Verifikasi fingerprint maksimal 30 detik. |
| NF-03 | Availability | Sistem beroperasi selama jam kerja tanpa downtime. |
| NF-04 | Performance | Menangani concurrent verification requests. |


| ID | Nama Requirement | Deskripsi |
| --- | --- | --- |
| I-01 | [DAF-Core] Produk Parameter > Otorisasi Entri Data | Terhubung dengan proses otorisasi menu produk dan parameter modul daf-core. |
| I-02 | [DAF-Core] Layanan dan Transaksi Counter  > Otorisasi Entri Data | Terhubung dengan proses otorisasi menu layanan dan transaksi counter pada modul daf-core |
| I-03 | [DAF-Core] Layanan dan Transaksi Counter  > Otorisasi Transaksi Teller dan Back Office | Terhubung dengan proses otorisasi menu layanan dan transaksi counter - otorisasi transaksi teller dan back office  pada modul daf-core |
| I-04 | [DAF-Core] Treasury  > Otorisasi Entri Data | Terhubung dengan proses otorisasi menu Treasury  pada modul daf-core |
| I-05 | [DAF-Financing] Financing > Otorisasi Entri Data | Terhubung dengan proses otorisasi menu Financing  pada modul daf-financing |
| I-06 | [DAF-Financing] Financing > Override Entri Data | Terhubung dengan proses override menu Financing  pada modul daf-financing |
| I-07 | [DAF-Treasury] Treasury > Otorisasi Entri Data | Terhubung dengan proses otorisasi menu Tresuary  pada modul daf-treasury |
| I-08 | [DAF-Treasury] Treasury > Override Entri Data | Terhubung dengan proses override menu Treasury  pada modul daf-treasury |
| I-09 | [DAF-Enterprise] Enterprise > Authorization List | Terhubung dengan proses otorisasi menu Enterprise  pada modul daf-enterprise |
| I-10 | [BDS-CS Teller] Otorisasi Entri Data | Terhubung dengan proses otorisa di List Otorisasi Entri Data Web BDS untuk teller & CS. |
| I-11 | [BDS-CS Teller] Otorisasi Entri Data | Terhubung dengan proses otorisa di List Otorisasi Entri Data Web BDS untuk teller & CS. |
| I-12 | Service Fingerprint | Menyediakan service untuk mendukung verifikasi dari surrounding apps misalnya : CMS, VA, QRIS, CAM, VMS |


| ID | Nama Requirement | Deskripsi |
| --- | --- | --- |
| S-01 | Encrypted Template | Hanya template fingerprint yang disimpan (bukan gambar mentah). |
| S-02 | Secure Channel | Komunikasi antar komponen wajib HTTPS + mTLS. |
| S-03 | OIDC Integration | Autentikasi user menggunakan OIDC (SSO internal). |
| S-04 | Access Policy | Hanya user aktif HRMIS yang dapat diverifikasi. |
| S-05 | Redis Cache | Redis hanya menyimpan data verifikasi sementara. |


| ID | Nama Requirement | Deskripsi |
| --- | --- | --- |
| O-01 | Deployment | Enrollment definitif di Kantor Pusat, alternate di Cabang. |
| O-02 | Device Distribution | Perangkat tersedia di meja maker/approval. |
| O-03 | Device Type | Menggunakan DigitalPersona 4500 Fingerprint Reader. |
| O-04 | Training | User wajib mengikuti pelatihan penggunaan perangkat. |


| ID | Nama Requirement | Deskripsi |
| --- | --- | --- |
| R-01 | Perangkat rusak | Gunakan fallback password sementara. |
| R-02 | User tidak bisa scan | Gunakan jari cadangan saat enrollment. |
| R-03 | Fraud approval alternate | Wajib SK penugasan alternate. |
| R-04 | Keterlambatan approval | Distribusi device di meja maker. |


| ID | Nama Requirement | Deskripsi |
| --- | --- | --- |
| A-01 | Log Completeness | Log mencatat semua aktivitas verifikasi dan transaksi. |
| A-02 | Log Accessibility | Log hanya diakses auditor & TI pusat. |
| A-03 | Log Retention | Log disimpan minimal 2 tahun. |
| A-04 | Audit Report | Sistem menyediakan laporan audit fingerprint usage. |


| ID | Nama Requirement | Deskripsi |
| --- | --- | --- |
| AC-01 | Kecepatan Verifikasi | < 5 detik per scan. |
| AC-02 | Akurasi | ≥ 97% match. |
| AC-03 | Lock Mechanism | 3x gagal → user terkunci. |
| AC-04 | Audit Trail | Semua log tercatat lengkap. |
| AC-05 | Fallback Password | Status user dapat diubah menggunakan password . |
