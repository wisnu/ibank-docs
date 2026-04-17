# Business Requirement Document (BRD)
## Penyesuaian Klasifikasi Status Rekening Tabungan dan Giro
### Rekening Tidak Aktif & Dormant – BCA Syariah

| Atribut | Detail |
|---|---|
| **Regulasi Acuan** | POJK Nomor 24 Tahun 2025 tentang Pengelolaan Rekening Pada Bank Umum |
| **Sistem Terdampak** | Core Banking System (DAF Legacy), Branch Delivery System (BDS), E-Channel (BSya) |
| **Target Implementasi** | 08 Mei 2026 |
| **Dokumen Sumber** | 146/MO/STO/2026 (UR – DAF, 5 Mar 2026) · 006/REQ/BDS/2026 (Catatan Req – BDS, 12 Jan 2026) |
| **Project Owner** | Aulia Reza |
| **Project Manager** | Eka Prasetyo Ariefin |

---

## 1. Latar Belakang

Saat ini sistem BCA Syariah hanya mengenal dua klasifikasi rekening aktif: **Rekening Aktif** dan **Rekening Dormant** (dengan threshold dormant = 180 hari tanpa transaksi). Ketentuan POJK Nomor 24 Tahun 2025 memperkenalkan klasifikasi baru **Rekening Tidak Aktif** dan memperbarui threshold dormant menjadi 1800 hari, sehingga diperlukan penyesuaian pada:

1. Core Banking System (DAF Legacy) dan integrasi ke Thought Machine (TM)
2. Branch Delivery System (BDS) di kantor cabang
3. E-Channel (aplikasi BSya dan kanal digital lainnya)

---

## 2. Definisi Klasifikasi Rekening

Berdasarkan POJK 24 Tahun 2025:

| Status | Definisi | Threshold |
|---|---|---|
| **Rekening Aktif** | Memiliki aktivitas Kredit, Debet, atau Pengecekan Saldo | — |
| **Rekening Tidak Aktif** | Tidak ada aktivitas Kredit, Debet, atau Cek Saldo | > **360 hari** |
| **Rekening Dormant** | Tidak ada aktivitas Kredit, Debet, atau Cek Saldo | > **1800 hari** |
| **Rekening Tutup** | Rekening yang ditutup (otomatis atau manual) | Saldo nol ≥ **180 hari** berturut-turut |

---

## 3. Kondisi Eksisting (Sebelum Perubahan)

- Klasifikasi rekening: Aktif, Dormant, Tutup (tidak ada kategori "Tidak Aktif")
- Threshold dormant = **180 hari** tanpa transaksi
- Counter dormant dihitung dari transaksi nasabah terakhir (Counter/Delivery Channel)
- Transaksi sistem (biaya admin, bagi hasil, pajak, zakat) **tidak** dihitung sebagai transaksi nasabah
- Rekening dormant masih bisa bertransaksi di e-channel
- Aktivasi rekening dormant: nasabah datang ke cabang
- Override transaksi dormant oleh Pejabat Cabang **tidak** mengubah status menjadi aktif
- Tutup otomatis: saldo Rp0 selama **48 bulan** berturut-turut (otomatis menghapus kartu ATM/CDM)

---

## 4. Ruang Lingkup Pengembangan

### 4.1 Kategori Rekening Baru

| # | Status Rekening | Keterangan |
|---|---|---|
| 1 | Rekening Aktif | Tetap ada, definisi diperluas |
| 2 | **Rekening Tidak Aktif** | **BARU** – threshold 360 hari |
| 3 | Rekening Dormant | Threshold diubah dari 180 → **1800 hari** |
| 4 | Rekening Tutup | Tetap ada, threshold diubah dari 48 bulan → **180 hari** saldo nol |

### 4.2 Indikator Aktivitas yang Mereset Counter

| Indikator | Channel | Keterangan |
|---|---|---|
| **Kredit (Pemasukan)** | Cabang, E-Channel, ATM/CDM | Setor tunai oleh nasabah |
| **Debet (Penarikan)** | Cabang, E-Channel, ATM/CDM | Tarik tunai, transfer, pembayaran, pemindahbukuan |
| **Cek Saldo (Balance Inquiry)** | Cabang, E-Channel, ATM/CDM | Cetak passbook, login aplikasi, cek saldo ATM |

> **Penting:** Balance Inquiry **tidak** mengubah status rekening yang sudah Tidak Aktif/Dormant — hanya mereset counter jika rekening masih Aktif.

### 4.3 Transaksi Sistem yang TIDAK Mereset Counter

Transaksi yang dihasilkan otomatis oleh sistem bank (tidak diperhitungkan sebagai aktivitas nasabah):
Zakat · Pajak · Bagi Hasil · Bonus · ATS (Auto Transfer System/Standing Instruction) · Biaya Administrasi · Denda · Pembayaran Angsuran · Autodebit TRiB · Incoming BI-FAST (sistem)

### 4.4 Rekening yang Dikecualikan dari Klasifikasi Tidak Aktif/Dormant

- Rekening untuk **tujuan tertentu**
- Rekening dengan **fitur berjangka**
- Rekening **dalam sengketa**

### 4.5 Aturan Biaya Administrasi

- Biaya administrasi dibatasi hingga saldo **Rp0 (nol)** — tidak boleh bersaldo negatif
- Tidak diperbolehkan *unpaid* biaya admin/biaya dormant
- Pendebetan biaya dapat dilakukan secara *partial*
- Biaya atas status Tidak Aktif/Dormant hanya sampai di level **produk**

---

## 5. Contoh Aktivitas Rekening per Status

### 5.1 Rekening Aktif

| Aktivitas | Status |
|---|---|
| Debet | Dapat dilakukan |
| Kredit | Dapat dilakukan |
| Cek Saldo | Dapat dilakukan |
| Pajak / Zakat / Bagi Hasil / Bonus | Dapat dilakukan |
| Standing Instruction / ATS | Dapat dilakukan |
| Biaya Administrasi | Dapat dilakukan |
| Denda | Dapat dilakukan |

### 5.2 Rekening Tidak Aktif

| Aktivitas | Status |
|---|---|
| **Debet** | **Tidak dapat dilakukan** (Post No Debet) |
| Kredit | Dapat dilakukan |
| Cek Saldo | Dapat dilakukan |
| Pajak / Zakat / Bagi Hasil / Bonus | Dapat dilakukan |
| Standing Instruction / ATS | Dapat dilakukan |
| Biaya Administrasi | Dapat dilakukan |
| Denda | Dapat dilakukan |

### 5.3 Rekening Dormant

| Aktivitas | Status |
|---|---|
| **Debet** | **Tidak dapat dilakukan** (Post No Debet) |
| **Kredit** | **Tidak dapat dilakukan** (Post No Kredit) |
| Cek Saldo | Dapat dilakukan |
| Pajak / Zakat / Bagi Hasil / Bonus | Dapat dilakukan |
| Standing Instruction / ATS | Dapat dilakukan |
| Biaya Administrasi | Dapat dilakukan |
| Denda | Dapat dilakukan |

> **Catatan:** Post No Debet dan Post No Kredit dikecualikan untuk transaksi yang dilakukan oleh sistem bank (zakat, pajak, bagi hasil, biaya admin, dll).

---

## 6. Konsep Backend System

| Parameter | Nilai | Keterangan |
|---|---|---|
| **Threshold Tidak Aktif** | 360 hari | Configurable via parameter |
| **Threshold Dormant** | 1800 hari | Configurable via parameter |
| **Tutup otomatis saldo nol** | 180 hari | Dihitung dari tanggal saldo nol pertama |
| **Status efektif** | H+1 | Status berubah pada H+1 setelah batas threshold tercapai (melalui proses EOD) |
| **Proses counter** | EOD | Reset counter dilakukan saat End Of Day |
| **Cek status flagging** | SOD | Start Of Day: cek flagging status tidak aktif/dormant |

### Tanggal Aktivitas Terakhir Nasabah

Sistem menggunakan nilai terbesar dari:
1. **Last Transaction/Cek Saldo** — tanggal aktivitas nasabah terakhir
2. **Tanggal Buka Rekening** — jika nasabah belum pernah bertransaksi sejak buka rekening
3. **Tanggal Reaktivasi** — jika nasabah tidak bertransaksi setelah reaktivasi

### Rekening Sub-Account / Valas

- Status Tidak Aktif/Dormant mengikuti **rekening induk**
- Transaksi jual beli saku valas dihitung sebagai aktivitas rekening induk
- Saldo saku valas termasuk saldo konsolidasi (diperhitungkan untuk tutup otomatis saldo nol)

---

## 7. Simulasi Sistem

### Perubahan Status: Aktif → Tidak Aktif

| Konstanta | Terakhir trx | Counter Start | Counter 360 | Status Berubah (H+1) |
|---|---|---|---|---|
| 360 hari | 2-Feb-26 | 3-Feb-26 | 28-Jan-27 | **29-Jan-27** |
| 360 hari | 3-Feb-26 | 4-Feb-26 | 29-Jan-27 | **30-Jan-27** |

### Perubahan Status: Tidak Aktif → Dormant

| Konstanta | Terakhir trx | Counter Start | Counter 1800 | Status Berubah (H+1) |
|---|---|---|---|---|
| 1800 hari | 2-Feb-26 | 3-Feb-26 | 7-Jan-31 | **8-Jan-31** |

### Tutup Otomatis (Saldo Nol)

| Konstanta | Tgl Saldo Nol | Counter Start | Counter 180 | Tanggal Tutup |
|---|---|---|---|---|
| 180 hari | 2-Feb-26 | 3-Feb-26 | 1-Aug-26 | **1-Aug-26** |

---

## 8. Aktivasi Rekening

### 8.1 Channel Aktivasi

Rekening Tidak Aktif dan/atau Dormant dapat diaktivasi melalui:

| Channel | Aplikasi | Keterangan |
|---|---|---|
| **Kantor Cabang** | BDS & DAF | Operator input, Supervisor otorisasi |
| **E-Channel** | BSya Mobile | Nasabah aktivasi mandiri |

> Tutup rekening dapat dilakukan langsung **tanpa aktivasi** terlebih dahulu. Status Tidak Aktif/Dormant akan ditampilkan pada informasi override reason.

### 8.2 Alur Aktivasi via BDS (Cabang)

1. Operator akses menu Tabungan/Giro → Ubah Data Rekening
2. Input nomor rekening → validasi
3. Pilih tab "Informasi Lainnya"
4. Klik toggle button → status berubah menjadi Aktif
5. Submit → pop-up konfirmasi otorisasi
6. Supervisor melakukan approve di menu Otorisasi

### 8.3 Alur Aktivasi via DAF (Core Banking)

1. Operator akses Menu Pemeliharaan Rekening → Tabungan & Giro → Ubah Status Rekening
2. Inquiry nomor rekening
3. Pilih rekening Tidak Aktif/Dormant → aktivasi
4. Data dikirim ke menu otorisasi Supervisor
5. Supervisor approve/reject di Menu Otorisasi → Otorisasi Entri Data

### 8.4 Pembatasan Transaksi per Status

**Rekening Tidak Aktif** – transaksi diblokir untuk rekening **sumber dana**:
Tarik Tunai · Pindah Buku · Transfer (SKN/RTGS/BI-FAST/Online) · Tarikan Kliring · Pembayaran & Pembelian · Pembayaran Virtual Account

**Rekening Dormant** – transaksi diblokir untuk rekening **sumber dana DAN tujuan**:
Tarik Tunai · Pindah Buku · Transfer (SKN/RTGS/BI-FAST/Online) · Tarikan Kliring · Pembayaran & Pembelian · Setoran Tunai · Setoran Kliring · Pembayaran Virtual Account

**Pop-up pesan kepada user:**
> *"Rekening Tidak Aktif/Dormant silahkan lakukan aktivasi melalui Customer Service/Aplikasi BSya"*

**Transaksi yang tetap boleh dilanjutkan (operasional bank):**
- Transaksi Umum (TU) – dengan informasi status di otorisasi
- Pendebetan/Pengkreditan Umum (DKU) – dengan informasi dan override
- Upload Transaksi Textfile (eksisting)

---

## 9. Migrasi Data

Saat implementasi sistem dilakukan:

| Kondisi Rekening Saat Ini | Perlakuan Saat Migrasi |
|---|---|
| Status **Aktif** | Tanggal aktivitas terakhir dipertahankan sesuai data historis |
| Status **Dormant** saat ini | Diklasifikasikan ulang menjadi **Aktif** atau **Tidak Aktif** tergantung counter hari |
| Status **Tidak Aktif** (post-migrasi) | Counter langsung dihitung dari 360 hari |
| Saldo nol saat migrasi | Tanggal mulai counter = tanggal implementasi (sesuai ketentuan internal) |

---

## 10. Pengembangan E-Channel

- Fitur aktivasi rekening Tidak Aktif/Dormant mandiri oleh nasabah
- Notifikasi kepada nasabah saat status rekening berubah dari Aktif → Tidak Aktif / Dormant
- Detail pengembangan dituangkan dalam dokumen terpisah

---

## 11. API dan Integrasi Multi-Channel

Alur log aktivasi dari seluruh channel ke Core Banking:

```
All Channel (BDS/BSya/ATM/dll)
  → Activation Success
  → Save account status changes
  → Send log & history to CBS (ISI/TM)

CBS (ISI/TM)
  → Update tabel data rekening
  → Update tabel Laporan Perubahan Status Rekening
  → Generate laporan (.xls)
```

Sistem mencatat audit trail: ID pengguna, username, tanggal/waktu aktivasi, dan informasi pendukung.

---

## 12. Laporan

| Sistem | Kode | Nama Laporan |
|---|---|---|
| **BDS** | R017 | Laporan Rekening Tidak Aktif dan Dormant |
| **BDS** | R029 | Laporan Perubahan Status Rekening |
| **DAF** | R027 | Laporan Perubahan Data Rekening |
| **DAF** | R030 | Laporan Rekening Tutup Otomatis (Berhasil) |
| **DAF** | R031 | Laporan Rekening Tutup Otomatis (Gagal) |
| **DAF** | R032 | Laporan Kartu Tutup Otomatis |

---

## 13. Unit Kerja yang Terlibat

| Unit Kerja | Peran |
|---|---|
| **PPA (Dept. Perencanaan & Kelayakan Sistem Aplikasi)** | Analisa, pembuatan UR, review, UAT, sertifikasi kelayakan |
| **ITB (Dept. Pengembangan IT Core & Back Office)** | Development, environment test |
| **PPO** | Komunikasi ketentuan/manual ke unit kerja dan cabang |
| **Tim ISI** | Pengembangan BDS & E-Channel |
| **Tim Soluix** | Pengembangan BDS |

---

## 14. Poin Kritis untuk Implementasi

1. **Sinkronisasi H+1**: Status rekening di BDS harus selaras dengan DAF — keduanya efektif H+1 setelah EOD
2. **CDM sebagai channel reset counter**: Transaksi via CDM harus diperhitungkan di BDS, sama seperti di DAF
3. **Biaya Administrasi rekening Tidak Aktif**: Tetap dapat dibebankan (konfirmasi dari UR sebagai dokumen yang lebih baru)
4. **Standing Instruction / ATS**: Perlu penegasan apakah keduanya identik atau berbeda dalam konteks core banking
5. **Rekening TRiB/Pembiayaan/Deposito**: Jika rekening sumber dana/tujuan berstatus Tidak Aktif/Dormant, **aktivasi harus dilakukan terlebih dahulu** sebelum pelunasan dipercepat/break

---

*Summary ini disusun berdasarkan dua dokumen sumber:*
- *146/MO/STO/2026 – User Requirement DAF Legacy (5 Maret 2026)*
- *006/REQ/BDS/2026 – Catatan Requirement BDS (12 Januari 2026, Approved 20 Februari 2026)*
