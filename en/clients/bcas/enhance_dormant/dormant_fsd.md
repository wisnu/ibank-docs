# FUNCTIONAL SPECIFICATION DOCUMENT

**BCA SYARIAH (BCAS)**
**MODUL REKENING FUNDING**
**FITUR ENHANCE REKENING TIDAK AKTIF & DORMANT**

Dipersiapkan oleh
PT Ihsan Solusi Informatika
Jl. PHH Mustofa No. 39
Ruko Surapati Core C-7 Bandung

| **Nomor Dokumen** | **Halaman** |
|---|---|
| **FSD-BCAS-DORMANT-01** | 1 / N |
| **Versi** | 1.0.0 | {DD Bulan YYYY} |

---

## Author

| **Nama** | **Role** |
|---|---|
| {Nama Writer} | Technical Writer |
| {Nama Reviewer} | Reviewer |

---

## Detail Daftar Perubahan

| Versi | Tanggal Perubahan | Penulis | Deskripsi |
|---|---|---|---|
| 1.0.0 | {DD/MM/YYYY} | {Nama Penulis} | Initial release dokumen FSD Enhance Rekening Tidak Aktif & Dormant |

---

## Daftar Isi

1. Gambaran Umum
   - 1.1. Latar Belakang
   - 1.2. Tujuan
   - 1.3. Ruang Lingkup
   - 1.4. Definisi
   - 1.5. Objektif
   - 1.6. Pengguna
2. Arsitektur Sistem
   - 2.1. Arsitektur Sistem
3. Alur Status Rekening
   - 3.1. Diagram Transisi Status
   - 3.2. Ringkasan Status Rekening
   - 3.3. Matriks Transaksi Berdasarkan Status Rekening
4. Konfigurasi Parameter
   - 4.1. Parameter Global
   - 4.2. Parameter Transaksi
   - 4.3. Parameter Produk
5. Pencatatan Aktivitas Nasabah
   - 5.1. Aktivitas yang Dicatat
   - 5.2. Transaksi Finansial — Yang Dihitung dan Yang Dikecualikan
6. Proses EOD (End of Day)
   - 6.1. Alur Proses EOD
   - 6.2. Rekening Berubah Menjadi Tidak Aktif (UC-01)
   - 6.3. Rekening Berubah Menjadi Dormant (UC-02)
   - 6.4. Rekening Ditutup Otomatis Saldo Nol (UC-03)
7. Transaksi Berdasarkan Status Rekening
8. Reaktivasi Rekening (UC-05)
9. Pengenaan Biaya Rekening (UC-06)
10. Laporan
    - 10.1. Laporan Rekening Tidak Aktif (R041)
    - 10.2. Laporan Rekening Dormant (R029)
    - 10.3. Laporan Tutup Otomatis (R030)
11. Perubahan Database
    - 11.1. Ringkasan Perubahan
12. Pengaturan Umum
13. Lampiran
    - Lampiran A. Screenshot Konfigurasi Parameter
    - Lampiran B. Screenshot Informasi Rekening
    - Lampiran C. Screenshot Transaksi Berdasarkan Status Rekening
    - Lampiran D. Screenshot Reaktivasi Rekening
    - Lampiran E. Screenshot Laporan

---

# Persetujuan Dokumen BCA Syariah

**PT Bank BCA Syariah**

| | | |
|---|---|---|
| | | |
| {Diisi Nama} | {Diisi Nama} | {Diisi Nama} |
| {Role/Jabatan} | {Role/Jabatan} | {Role/Jabatan} |
| {DD/MM/YYYY} | {DD/MM/YYYY} | {DD/MM/YYYY} |

---

# Persetujuan Dokumen ISI

**PT Ihsan Solusi Informatika**

| | | |
|---|---|---|
| | | |
| {Diisi Nama} | {Diisi Nama} | {Diisi Nama} |
| {Role/Jabatan} | {Role/Jabatan} | {Role/Jabatan} |
| {DD/MM/YYYY} | {DD/MM/YYYY} | {DD/MM/YYYY} |

---

## 1. Gambaran Umum

### 1.1. Latar Belakang

OJK menerbitkan **POJK Nomor 24 Tahun 2025** tentang Pengelolaan Rekening Pada Bank Umum, yang mewajibkan seluruh bank umum — termasuk BCA Syariah — untuk menyesuaikan sistem pengelolaan rekening paling lambat **08 Mei 2026**. Peraturan ini memperkenalkan standar baru klasifikasi status rekening yang lebih terstruktur dan menggantikan kebijakan internal yang berlaku saat ini.

**Kondisi Sistem yang Ada (Sebelum Perubahan)**

Saat ini sistem BCA Syariah hanya mengenal dua klasifikasi rekening aktif-nonaktif: **Rekening Aktif** dan **Rekening Dormant**, dengan kondisi sebagai berikut:

- Threshold dormant: **180 hari** tanpa transaksi nasabah
- Tutup otomatis saldo nol: **48 bulan** berturut-turut
- Counter dormant dihitung dari transaksi nasabah (Counter/Delivery Channel); transaksi sistem (biaya admin, bagi hasil, pajak, zakat) tidak dihitung
- Belum ada status perantara antara Aktif dan Dormant
- Rekening dormant masih dapat bertransaksi melalui e-channel
- Aktivasi rekening dormant: nasabah datang langsung ke cabang

**Perubahan yang Diperlukan Berdasarkan POJK 24/2025**

Ketentuan baru mewajibkan penyesuaian pada tiga sistem yang saling terintegrasi:

1. **Core Banking System (DAF Legacy)** — penambahan status Tidak Aktif, perubahan threshold, logika counter aktivitas
2. **Branch Delivery System (BDS)** — menu aktivasi rekening Tidak Aktif/Dormant di kantor cabang
3. **E-Channel (Aplikasi BSya)** — aktivasi mandiri oleh nasabah dan notifikasi perubahan status

Poin utama penyesuaian:
- Penambahan status **Tidak Aktif** sebagai fase perantara antara Aktif dan Dormant (threshold: > 360 hari tanpa aktivitas)
- Perubahan threshold dormant dari **180 hari → 1.800 hari**
- Perubahan threshold tutup otomatis dari **48 bulan → 180 hari** saldo nol berturut-turut
- Perluasan definisi aktivitas yang mereset counter — mencakup **transaksi kredit, debet, dan cek saldo nasabah**
- Pembatasan biaya administrasi: tidak boleh menyebabkan saldo negatif

Dokumen sumber: *146/MO/STO/2026 — User Requirement DAF Legacy (5 Mar 2026)* dan *006/REQ/BDS/2026 — Catatan Requirement BDS (12 Jan 2026)*.

### 1.2. Tujuan

Berikut ini adalah tujuan pengembangan fitur Enhance Rekening Tidak Aktif & Dormant pada sistem BCAS:

- **Memenuhi ketentuan POJK Nomor 24 Tahun 2025** tentang Pengelolaan Rekening Pada Bank Umum, dengan tenggat implementasi 08 Mei 2026.
- Menambahkan status **Tidak Aktif** sebagai fase perantara antara Aktif dan Dormant, dengan threshold 360 hari sesuai ketentuan POJK.
- Mengubah threshold dormant dari 180 hari menjadi **1.800 hari** dan threshold tutup otomatis saldo nol dari 48 bulan menjadi **180 hari**, sesuai ketentuan POJK.
- Memperluas definisi aktivitas yang mereset counter keaktifan rekening, mencakup **transaksi kredit (pemasukan), debet (penarikan), dan pengecekan saldo** — termasuk aktivitas melalui ATM, Mobile Banking, dan kanal digital lainnya.
- Menyediakan **konfigurasi parameter yang fleksibel** — threshold hari dan biaya dapat dikonfigurasi secara global maupun di-override per produk.
- Memastikan **biaya administrasi tidak menyebabkan saldo negatif** — pendebetan biaya dilakukan hanya sebatas saldo yang tersedia (partial debet diperbolehkan).
- Menyediakan **proses reaktivasi** rekening Tidak Aktif dan Dormant melalui:
  - Menu di **Core Banking (DAF)**: input oleh petugas cabang dengan otorisasi supervisor.
  - Menu di **BDS (Branch Delivery System)**: pengajuan oleh operator dengan approve supervisor.
  - **E-Channel (BSya Mobile)**: aktivasi mandiri oleh nasabah.
- Menyediakan **notifikasi kepada nasabah** saat status rekening berubah dari Aktif ke Tidak Aktif atau Dormant.
- Mengotomatisasi **pengenaan biaya** rekening Tidak Aktif dan Dormant pada proses akhir bulan (EOM).
- Mengintegrasikan **audit trail** aktivasi dari seluruh channel (BDS, E-Channel, ATM) ke Core Banking System.

### 1.3. Ruang Lingkup

Ruang lingkup pengembangan fitur Enhance Rekening Tidak Aktif & Dormant pada sistem BCAS adalah sebagai berikut:

**Core Banking System (DAF Legacy)**

- **Status Rekening:** Penambahan status Tidak Aktif (status `7`) sebagai fase perantara antara Aktif (`1`) dan Dormant (`2`); perubahan threshold dormant dari 180 hari menjadi 1.800 hari.
- **Pencatatan Aktivitas:** Penambahan tabel `RekeningAktivitasNonfin` untuk mencatat aktivitas non-finansial nasabah secara real-time (cek saldo, cetak passbook, dll.). Counter aktivitas juga mencakup transaksi kredit dan debet oleh nasabah.
- **EOD — Update Aktivitas Terakhir:** Script baru `update_account_lasttxdate.py` untuk mengupdate `tgl_aktivitas_terakhir` di `RekeningLiabilitas` setiap EOD, menggabungkan transaksi finansial dan aktivitas non-finansial. Nilai efektif = nilai terbesar antara tanggal aktivitas, tanggal buka rekening, dan tanggal reaktivasi.
- **EOD — Batch Dormant:** Modifikasi script `update_dormant_account.py` untuk membaca `tgl_aktivitas_terakhir` (field baru) dan memproses dua fase: Tidak Aktif dan Dormant.
- **EOD — Tutup Otomatis:** Modifikasi script `saving_auto_close.py`; threshold tutup otomatis diubah dari 48 bulan menjadi 180 hari, dengan dukungan override per produk.
- **EOM — Biaya Rekening:** Modifikasi script `admcost_dormant_process.py` untuk mengenakan biaya rekening Tidak Aktif, di samping biaya Dormant yang sudah ada. Biaya tidak boleh melebihi saldo tersedia — partial debet diperbolehkan, saldo tidak boleh negatif.
- **Menu Reaktivasi (DAF):** Penambahan menu `Ubah Status Rekening` di modul Pemeliharaan Rekening untuk proses reaktivasi dengan mekanisme input oleh petugas dan otorisasi oleh supervisor.
- **Parameter Global:** Penambahan 5 parameter baru di `ParameterGlobal` (grup `REKENING_DORMANT`) untuk konfigurasi hari dan biaya secara terpusat.
- **Parameter Produk:** Penambahan kolom override per produk untuk threshold hari, biaya, dan pengecualian dari proses Tidak Aktif/Dormant/tutup otomatis.
- **Parameter Transaksi:** Penambahan field `tipe_exclude_aktivitas_nasabah`, `allow_rekening_tidak_aktif`, dan `allow_rekening_dormant` di `ParameterTransaksiUmum`.
- **Pengecualian Rekening:** Rekening dengan tujuan tertentu, fitur berjangka, atau dalam sengketa dikecualikan dari klasifikasi Tidak Aktif/Dormant.
- **Rekening Sub-Account / Valas:** Status Tidak Aktif/Dormant mengikuti rekening induk; transaksi saku valas dihitung sebagai aktivitas rekening induk; saldo saku valas diperhitungkan untuk tutup otomatis saldo nol.

**Branch Delivery System (BDS)**

- **Menu Aktivasi BDS:** Penambahan/modifikasi menu `Aktivasi Rekening Tidak Aktif/Dormant` di BDS cabang — operator input, supervisor otorisasi; status rekening efektif H+1 setelah EOD, sinkron dengan DAF.

**E-Channel (Aplikasi BSya)**

- **Aktivasi Mandiri Nasabah:** Fitur baru pada aplikasi BSya untuk nasabah mengaktifkan sendiri rekening Tidak Aktif atau Dormant tanpa harus datang ke cabang.
- **Notifikasi Nasabah:** Notifikasi otomatis kepada nasabah saat status rekening berubah dari Aktif menjadi Tidak Aktif atau Dormant. Detail pengembangan dituangkan dalam dokumen terpisah.

**Laporan**

- **DAF:** Penambahan laporan baru R041 (Rekening Aktif jadi Tidak Aktif); enhance R029 (Dormant) dan R030 (Tutup Otomatis Berhasil); tambah R031 (Tutup Otomatis Gagal) dan R032 (Kartu Tutup Otomatis) dengan kolom tambahan.
- **BDS:** R017 — Laporan Rekening Tidak Aktif dan Dormant; R029 — Laporan Perubahan Status Rekening.

**Integrasi & Audit Trail**

- **API Multi-Channel:** Seluruh aktivasi dari channel manapun (BDS, BSya, ATM) mencatat log ke Core Banking; update tabel data rekening dan tabel laporan perubahan status rekening.
- **Migrasi Data:** Rekening existing diklasifikasikan ulang saat implementasi: rekening dormant existing yang counter-nya < 360 hari → Aktif; counter 360–1800 hari → Tidak Aktif; counter > 1800 hari → tetap Dormant. Rekening saldo nol saat migrasi: counter tutup otomatis dimulai dari tanggal implementasi.

### 1.4. Definisi

Berikut adalah definisi dari beberapa istilah yang ada pada fitur Enhance Rekening Tidak Aktif & Dormant:

- **Rekening Aktif:** Rekening dengan status `1` — terdapat aktivitas nasabah dalam batas hari yang dikonfigurasi (default: 360 hari).
- **Rekening Tidak Aktif:** Status baru dengan kode `7` — rekening yang tidak memiliki aktivitas nasabah selama lebih dari batas hari tidak aktif (default: 360 hari), namun belum mencapai batas hari dormant.
- **Rekening Dormant:** Rekening dengan status `2` — tidak ada aktivitas nasabah lebih dari batas hari dormant (default: 1.800 hari / ± 5 tahun). Seluruh transaksi nasabah diblokir.
- **Rekening Tutup:** Rekening dengan status `3` — ditutup otomatis saat saldo Rp 0 secara terus-menerus melebihi batas hari tutup otomatis.
- **Tgl Aktivitas Terakhir (`tgl_aktivitas_terakhir`):** Field baru di `RekeningLiabilitas` — gabungan dari tanggal transaksi finansial nasabah dan tanggal aktivitas non-finansial terakhir. Merupakan acuan utama perhitungan status rekening pada proses EOD.
- **Aktivitas Non-Finansial:** Aktivitas yang tidak melibatkan pergerakan uang namun mencerminkan keaktifan nasabah, seperti cek saldo dan cetak buku tabungan. Dicatat di tabel `RekeningAktivitasNonfin`.
- **EOD (End of Day):** Proses harian otomatis yang berjalan setiap akhir hari kerja, termasuk update status rekening berdasarkan aktivitas terakhir.
- **EOM (End of Month):** Proses otomatis akhir bulan, termasuk pengenaan biaya rekening Tidak Aktif dan Dormant.
- **ParameterGlobal:** Tabel konfigurasi terpusat untuk threshold hari dan biaya — berlaku untuk semua produk kecuali produk yang memiliki konfigurasi override sendiri.
- **Override Produk:** Konfigurasi threshold dan biaya khusus per produk — digunakan jika produk mengaktifkan flag `is_custom_dormant = T`.
- **Reaktivasi:** Proses pengembalian status rekening Tidak Aktif atau Dormant menjadi Aktif — dapat dilakukan oleh petugas cabang (DAF/BDS) dengan persetujuan supervisor, atau mandiri oleh nasabah via BSya.
- **BDS (Branch Delivery System):** Aplikasi operasional cabang BCA Syariah yang digunakan petugas teller dan customer service.
- **BSya:** Aplikasi mobile banking BCA Syariah untuk nasabah.

### 1.5. Objektif

- Dokumen ini disusun agar setiap pengguna dan pihak yang terlibat dalam proyek dapat memahami secara menyeluruh detail terkait fitur Enhance Rekening Tidak Aktif & Dormant.
- Seluruh ilustrasi/gambar pada dokumen ini digunakan semata-mata sebagai alat bantu untuk memudahkan pemahaman terhadap deskripsi field maupun alur proses/event.
- Dokumen ini merupakan dokumen fungsional yang dihasilkan dari proses pengumpulan kebutuhan bisnis (business requirement gathering) antara tim vendor (ISI) dan tim BCAS.
- Dokumen ini akan terus diperbarui sesuai kebutuhan, dan setiap perubahan harus disetujui oleh setiap pihak (vendor dan BCAS) melalui tanda tangan perwakilan resmi dari masing-masing pihak.

### 1.6. Pengguna

Berikut adalah pengguna fitur Enhance Rekening Tidak Aktif & Dormant:

| **No** | **Role** | **Deskripsi** |
|---|---|---|
| 1 | Nasabah | Melakukan aktivasi mandiri rekening Tidak Aktif atau Dormant melalui aplikasi BSya (E-Channel), tanpa harus datang ke cabang. |
| 2 | Petugas Cabang / Operator BDS | Melakukan pengajuan reaktivasi rekening Tidak Aktif atau Dormant melalui menu di DAF atau BDS. |
| 3 | Supervisor / Pejabat Cabang | Menyetujui atau menolak pengajuan reaktivasi rekening dari petugas cabang, baik di DAF maupun BDS. |
| 4 | System Administrator | Mengelola konfigurasi Parameter Global (hari dan biaya), Parameter Transaksi (exclude aktivitas nasabah), dan Parameter Produk (override threshold). |
| 5 | Finance & Accounting Staff | Mengakses laporan rekening Tidak Aktif (R041), Dormant (R029), Tutup Otomatis (R030/R031/R032), dan Laporan Perubahan Status Rekening. |

---

## 2. Arsitektur Sistem

### 2.1. Arsitektur Sistem

Berikut ini adalah arsitektur sistem dari fitur Enhance Rekening Tidak Aktif & Dormant BCAS:

```mermaid
graph TB
    NASABAH(["Nasabah"])
    BDS(["BDS\n(Branch Delivery System)"])
    BSYA(["BSya Mobile\n(E-Channel)"])
    ATM(["ATM / CDM"])

    subgraph DAF["Core Banking BCAS (DAF Legacy)"]
        subgraph MENU["Menu Operasional"]
            MREK["Ubah Status Rekening\n(Reaktivasi)"]
            MPARAM["Parameter Global\nParameter Transaksi\nParameter Produk"]
            MINFO["Informasi Rekening"]
        end
        subgraph EOD_EOM["Proses Otomatis"]
            SCRIPT1["EOD: update_account_lasttxdate\n(Update Tgl Aktivitas Terakhir)"]
            SCRIPT2["EOD: update_dormant_account\n(Update Status Rekening)"]
            SCRIPT3["EOD: saving_auto_close\n(Tutup Otomatis Saldo Nol)"]
            SCRIPT4["EOM: admcost_dormant_process\n(Pengenaan Biaya)"]
        end
        DB[("Core DB\noracle")]
    end

    subgraph LAPORAN["Laporan"]
        R041["R041 — Rekening Tidak Aktif"]
        R029["R029 — Rekening Dormant"]
        R030["R030 — Tutup Otomatis"]
    end

    NASABAH -->|"Transaksi / Cek Saldo"| ATM
    NASABAH -->|"Transaksi / Cek Saldo"| BSYA
    NASABAH -->|"Transaksi / Cek Saldo"| BDS
    NASABAH -->|"Aktivasi Mandiri"| BSYA

    ATM -->|"Log Aktivitas"| DAF
    BSYA -->|"Log Aktivitas\n& Aktivasi"| DAF
    BDS -->|"Input Reaktivasi\n& Log Aktivitas"| DAF

    MENU --- DB
    EOD_EOM --- DB
    DB --- LAPORAN
```

**Keterangan:**

Fitur ini berdampak pada tiga sistem yang saling terintegrasi:

- **Core Banking BCAS (DAF Legacy)** — pusat logika bisnis. Menyimpan seluruh data rekening, parameter konfigurasi, log aktivitas, dan menjalankan proses batch EOD/EOM secara otomatis.
- **BDS (Branch Delivery System)** — digunakan oleh petugas dan supervisor cabang untuk melihat status rekening dan melakukan proses reaktivasi (input + otorisasi). Perubahan status di BDS disinkronkan dengan DAF secara H+1 setelah EOD.
- **E-Channel (BSya Mobile)** — digunakan langsung oleh nasabah untuk aktivasi mandiri rekening Tidak Aktif/Dormant dan menerima notifikasi perubahan status.

Seluruh channel (BDS, BSya, ATM/CDM) mengirimkan log aktivitas ke Core Banking. Proses EOD berjalan setiap akhir hari kerja untuk mengupdate `tgl_aktivitas_terakhir` dan menentukan perubahan status rekening. Proses EOM berjalan setiap akhir bulan untuk pengenaan biaya rekening Tidak Aktif dan Dormant.

---

## 3. Alur Status Rekening

### 3.1. Diagram Transisi Status

#### Diagram A — Transisi Status Tidak Aktif & Dormant

```mermaid
stateDiagram-v2
    [*] --> AKTIF : Rekening dibuka

    AKTIF --> TIDAK_AKTIF : Tidak ada aktivitas\n> 360 hari (± 1 tahun)
    TIDAK_AKTIF --> DORMANT : Tidak ada aktivitas\n> 1.800 hari (± 5 tahun)

    TIDAK_AKTIF --> AKTIF : Reaktivasi oleh Petugas Cabang / Mandiri via BSya
    DORMANT --> AKTIF : Reaktivasi oleh Petugas Cabang / Mandiri via BSya
```

> Perubahan status **Tidak Aktif** dan **Dormant** ditentukan berdasarkan lamanya waktu tanpa aktivitas nasabah — dihitung setiap hari oleh sistem pada proses EOD (efektif H+1 setelah threshold tercapai).

#### Diagram B — Tutup Otomatis Saldo Nol (Independen)

```mermaid
stateDiagram-v2
    AKTIF --> TUTUP : Saldo Rp 0 selama\n≥ 180 hari berturut-turut
    TIDAK_AKTIF --> TUTUP : Saldo Rp 0 selama\n≥ 180 hari berturut-turut
    DORMANT --> TUTUP : Saldo Rp 0 selama\n≥ 180 hari berturut-turut

    TUTUP --> [*]
```

> Tutup otomatis adalah proses **terpisah** dari alur tidak aktif/dormant. Rekening dalam status apapun — termasuk **Aktif** — dapat ditutup otomatis apabila saldonya Rp 0 secara terus-menerus melebihi batas hari yang dikonfigurasi. Rekening yang dikecualikan dari aturan ini tidak akan ditutup otomatis.

### 3.2. Ringkasan Status Rekening

| Status | Kode | Kondisi | Keterangan |
|---|:---:|---|---|
| **Aktif** | `1` | Ada aktivitas dalam batas hari yang dikonfigurasi (default: 360 hari) | Operasional normal |
| **Tidak Aktif** | `7` *(baru)* | Tidak ada aktivitas > batas hari tidak aktif s.d. ≤ batas hari dormant | Debet nasabah dibatasi — perlu reaktivasi |
| **Dormant** | `2` | Tidak ada aktivitas > batas hari dormant (default: 1.800 hari) | Debet & kredit nasabah diblokir — perlu reaktivasi |
| **Tutup** | `3` | Saldo Rp 0 melebihi batas hari tutup otomatis *(dari status apapun)* | Rekening ditutup permanen |

### 3.3. Matriks Transaksi Berdasarkan Status Rekening

| Jenis Transaksi | Aktif | Tidak Aktif | Dormant |
|---|:---:|:---:|:---:|
| Setor Tunai (Teller) | ✅ | ✅ | ❌ |
| Tarik Tunai (Teller) | ✅ | ❌ | ❌ |
| Transfer Masuk | ✅ | ✅ | ❌ |
| Transfer Keluar | ✅ | ❌ | ❌ |
| Autodebit / Standing Instruction nasabah | ✅ | ❌ | ❌ |
| Cek Saldo / Inquiry | ✅ | ✅ | ✅ |
| Tarik Tunai ATM | ✅ | ❌ | ❌ |
| Bagi Hasil / Pajak / Zakat / Biaya Admin *(sistem)* | ✅ | ✅ | ✅ |
| ATS / Standing Instruction *(sistem)* | ✅ | ✅ | ✅ |

| Simbol | Arti |
|:---:|---|
| ✅ | Diperbolehkan |
| ❌ | Tidak diperbolehkan |

> **Catatan:**
> - Matriks di atas merupakan konfigurasi default. Perilaku per kode transaksi dapat dikonfigurasi lebih lanjut melalui **Parameter Transaksi** (field `allow_rekening_tidak_aktif` dan `allow_rekening_dormant`).
> - Transaksi yang dihasilkan otomatis oleh sistem bank (bagi hasil, pajak, zakat, biaya admin, ATS) **tetap dapat dilakukan** pada rekening Tidak Aktif maupun Dormant — ketentuan Post No Debet/Kredit hanya berlaku untuk transaksi yang diprakarsai nasabah.
> - **Cek Saldo / Inquiry** tetap dapat dilakukan di semua status rekening, namun tidak mengubah status rekening yang sudah Tidak Aktif atau Dormant.

---

## 4. Konfigurasi Parameter

### 4.1. Parameter Global

Semua parameter hari dan biaya dapat dikonfigurasikan oleh administrator sistem melalui menu **Parameter → Parameter Global** (filter grup: `REKENING_DORMANT`), tanpa perlu mengubah konfigurasi di setiap produk satu per satu.

| Kode Parameter | Nilai Default | Keterangan |
|---|---|---|
| `TAKT_HARI` | 360 hari | Batas hari menjadi Tidak Aktif (± 1 tahun). Sesuai ketentuan OJK |
| `DORM_HARI` | 1.800 hari | Batas hari menjadi Dormant (± 5 tahun). Sesuai ketentuan OJK |
| `TUTUP_NOL_HARI` | 180 hari | Batas hari tutup otomatis saldo nol |
| `TAKT_BIAYA` | Rp 0 | Default biaya rekening Tidak Aktif |
| `DORM_BIAYA` | Rp 10.000 | Default biaya rekening Dormant |

### 4.2. Parameter Transaksi

Menu: **Parameter → Parameter Transaksi**

Field baru yang ditambahkan pada `ParameterTransaksiUmum`:

| Caption di Form | Field | Nilai | Fungsi |
|---|---|---|---|
| **Transaksi Sistem** | `is_transaksi_sistem` | `T` / `F` (default `F`) | Menandai transaksi yang berasal dari sistem (mis. posting bagi hasil) |
| **Kategori Aktivitas Nasabah** | `tipe_exclude_aktivitas_nasabah` | `F` / `DC` / `D` / `C` (default `F`) | `F` = hitung sebagai aktivitas nasabah; `DC` = exclude; `D` = exclude debit; `C` = exclude kredit |
| **Izinkan Rekening Tidak Aktif** | `allow_rekening_tidak_aktif` | `F` / `DC` / `D` / `C` (default `C`) | `F` = Tolak Debet/Kredit; `DC` = Izinkan Debet/Kredit; `D` = Hanya Debet; `C` = Hanya Kredit |
| **Izinkan Rekening Dormant** | `allow_rekening_dormant` | `F` / `DC` / `D` / `C` (default `F`) | `F` = Tolak Debet/Kredit; `DC` = Izinkan Debet/Kredit; `D` = Hanya Debet; `C` = Hanya Kredit |

> **Catatan:** Jika kode transaksi tidak terdapat di parameter ini, secara default dianggap sebagai aktivitas nasabah (`tipe_exclude_aktivitas_nasabah = 'F'`), dan tidak diizinkan untuk rekening Tidak Aktif maupun Dormant.

**Contoh kode transaksi yang dikecualikan dari aktivitas nasabah:**

| Kode Transaksi | Keterangan | tipe_exclude_aktivitas_nasabah |
|---|---|:---:|
| `SD` | Bagi Hasil Tabungan/Giro — dibuat sistem EOD | `DC` |
| `PD` | Bagi Hasil Deposito — dibuat sistem EOD | `DC` |
| `SC` | Biaya Administrasi Bulanan — dibuat sistem EOD | `DC` |
| `SCD` | Biaya Rekening Dormant — dibuat sistem EOD | `DC` |
| `SDP` | Pajak Bagi Hasil — dibuat sistem EOD | `DC` |
| `SDZ` | Zakat Bagi Hasil — dibuat sistem EOD | `DC` |
| `SI` | Auto Transfer Antar Rekening — dibuat sistem | `DC` |

### 4.3. Parameter Produk

Menu: **Parameter → List Produk Tabungan** (atau Giro)

Sistem menggunakan **3 layer** untuk menentukan threshold dan biaya setiap rekening:

> **Pengecualian → Override Produk → Default Global**

**Fase 1 — Tidak Aktif**

```mermaid
flowchart TD
    START([Rekening masuk proses EOD\nfase: Tidak Aktif]) --> CHK1

    CHK1{"Rekening / Produk\ndikecualikan dari Tidak Aktif?"}
    CHK1 -->|Ya| EXC["Fase Tidak Aktif tidak berlaku\n— rekening di-skip —"]
    CHK1 -->|Tidak| CHK2

    CHK2{"Produk punya\nkonfigurasi custom?"}
    CHK2 -->|Ya| OVR["Gunakan threshold & biaya\ndari konfigurasi produk"]
    CHK2 -->|Tidak| DEF["Gunakan default global\nTAKT_HARI (360 hari)\nTAKT_BIAYA"]

    EXC:::skip
    OVR:::produk
    DEF:::global

    classDef skip   fill:#fde8e8,stroke:#e53e3e,color:#742a2a
    classDef produk fill:#fefcbf,stroke:#d69e2e,color:#744210
    classDef global fill:#e6fffa,stroke:#38a169,color:#1c4532
```

**Fase 2 — Dormant**

```mermaid
flowchart TD
    START([Rekening masuk proses EOD\nfase: Dormant]) --> CHK1

    CHK1{"Rekening / Produk\ndikecualikan dari Dormant?"}
    CHK1 -->|Ya| EXC["Fase Dormant tidak berlaku\n— rekening di-skip —"]
    CHK1 -->|Tidak| CHK2

    CHK2{"Produk punya\nkonfigurasi custom?"}
    CHK2 -->|Ya| OVR["Gunakan threshold & biaya\ndari konfigurasi produk"]
    CHK2 -->|Tidak| DEF["Gunakan default global\nDORM_HARI (1800 hari)\nDORM_BIAYA"]

    EXC:::skip
    OVR:::produk
    DEF:::global

    classDef skip   fill:#fde8e8,stroke:#e53e3e,color:#742a2a
    classDef produk fill:#fefcbf,stroke:#d69e2e,color:#744210
    classDef global fill:#e6fffa,stroke:#38a169,color:#1c4532
```

**Fase 3 — Tutup Otomatis Saldo Nol**

```mermaid
flowchart TD
    START([Rekening masuk proses EOD\nfase: Tutup Otomatis]) --> CHK1

    CHK1{"Produk dikecualikan\ndari tutup otomatis?"}
    CHK1 -->|Ya| EXC["Tutup Otomatis tidak berlaku\n— rekening di-skip —"]
    CHK1 -->|Tidak| CHK2

    CHK2{"Produk punya\nkonfigurasi custom?"}
    CHK2 -->|Ya| OVR["Gunakan threshold\ndari konfigurasi produk"]
    CHK2 -->|Tidak| DEF["Gunakan default global\nTUTUP_NOL_HARI (180 hari)"]

    EXC:::skip
    OVR:::produk
    DEF:::global

    classDef skip   fill:#fde8e8,stroke:#e53e3e,color:#742a2a
    classDef produk fill:#fefcbf,stroke:#d69e2e,color:#744210
    classDef global fill:#e6fffa,stroke:#38a169,color:#1c4532
```

> `is_tidak_dormant` berlaku untuk **kedua fase** — jika `T` di level produk atau per rekening, rekening dikecualikan dari fase Tidak Aktif maupun Dormant.

**Ringkasan field produk yang terlibat:**

*Parameter Produk Dormant / Tidak Aktif:*

| Caption di Form | Field | Fungsi |
|---|---|---|
| **Boleh Tidak Dormant** | `is_tidak_dormant` | ☑ = rekening produk ini boleh berstatus Tidak Aktif maupun Dormant |
| **Custom Param Dormant** | `is_custom_dormant` | ☑ = gunakan threshold & biaya dari produk, bukan global |
| **Durasi Hari Tidak Aktif** | `jumlah_hari_jadi_tidak_aktif` | Override threshold hari tidak aktif *(aktif jika Custom Param dicentang)* |
| **Durasi Hari Dormant** | `jumlah_hari_jadi_dormant` | Override threshold hari dormant *(aktif jika Custom Param dicentang)* |
| **Biaya Tidak Aktif** | `biaya_rekening_tidak_aktif` | Override nominal biaya tidak aktif *(aktif jika Custom Param dicentang)* |
| **Biaya Dormant** | `biaya_rekening_dormant` | Override nominal biaya dormant *(aktif jika Custom Param dicentang)* |

*Parameter Produk Tutup Otomatis Saldo Nol:*

| Caption di Form | Field | Fungsi |
|---|---|---|
| **Pengecualian Tutup Saldo Nol** | `is_exc_tutupnol` | ☑ = rekening produk ini tidak akan ditutup otomatis saat saldo nol |
| **Custom Param Tutup Saldo Nol** | `is_custom_tutup_oto` | ☑ = gunakan threshold tutup otomatis dari produk, bukan global |
| **Durasi Hari Tutup Saldo Nol** | `jumlah_hari_tutup_otomatis` | Override threshold hari tutup otomatis *(aktif jika Custom Param dicentang)* |

---

## 5. Pencatatan Aktivitas Nasabah (UC-04)

**Aktor:** Nasabah (via ATM, Mobile Banking, Internet Banking, atau Teller)

Nasabah yang melakukan aktivitas apapun — baik transaksi finansial maupun non-finansial — akan dicatat oleh sistem sebagai bukti keaktifan rekening. Pencatatan berjalan di latar belakang dan **tidak memperlambat** layanan yang diterima nasabah.

### 5.1. Aktivitas yang Dicatat

Aktivitas berikut dicatat dan menghitung ulang counter keaktifan rekening:

| Kategori | Jenis Aktivitas | Kanal |
|---|---|---|
| **Kredit (Pemasukan)** | Setor tunai, setoran kliring, transfer masuk (oleh nasabah) | Teller, ATM/CDM, E-Channel |
| **Debet (Penarikan)** | Tarik tunai, transfer keluar, pembayaran | Teller, ATM, E-Channel |
| **Cek Saldo** | Pengecekan saldo rekening | ATM, Mobile Banking, Internet Banking, Teller |
| **Non-Finansial Lainnya** | Cetak buku tabungan, cetak saldo passbook, pembukaan rekening | Teller |

Aktivitas non-finansial (cek saldo, cetak passbook) dicatat ke tabel `RekeningAktivitasNonfin` secara real-time. Field `tgl_aktivitas_terakhir` di `RekeningLiabilitas` diupdate setiap EOD — kecuali saat inquiry di menu Informasi Rekening yang memicu update langsung.

### 5.2. Transaksi Finansial — Yang Dihitung dan Yang Dikecualikan

| Kategori | Contoh Transaksi | Dihitung sebagai Aktivitas? |
|---|---|:---:|
| Transaksi oleh nasabah | Setor tunai, tarik tunai, transfer | ✅ Ya |
| Bagi hasil / nisbah | Pembukuan bagi hasil tabungan, giro, deposito | ❌ Tidak |
| Pajak & zakat | Pemotongan pajak bagi hasil, zakat bagi hasil | ❌ Tidak |
| Biaya rekening | Biaya administrasi bulanan, biaya rekening dormant | ❌ Tidak |
| Transfer otomatis sistem | Auto transfer antar rekening yang dibuat oleh sistem | ❌ Tidak |

> Daftar transaksi yang dikecualikan dapat dikonfigurasi administrator melalui menu **Parameter Transaksi** (`tipe_exclude_aktivitas_nasabah`).

**Skenario Khusus — Aktivitas pada Rekening Tidak Aktif atau Dormant:**

> Aktivitas nasabah — baik transaksi finansial maupun non-finansial — **tidak** secara otomatis mengembalikan status rekening ke Aktif. Rekening yang sudah berstatus Tidak Aktif atau Dormant hanya bisa dikembalikan melalui proses **reaktivasi** (lihat Bab 8).

---

## 6. Proses EOD (End of Day)

### 6.1. Alur Proses EOD

Urutan proses EOD yang wajib dijaga:

```mermaid
flowchart LR
    S1["Step 1 — BARU\nUpdate Tgl Aktivitas Terakhir\nupdate_account_lasttxdate.py"]
    S2["Step 2 — DIMODIFIKASI\nBatch Dormant\nupdate_dormant_account.py"]
    S3["Step 3 — DIMODIFIKASI\nBatch Tutup Otomatis\nsaving_auto_close.py"]

    S1 --> S2 --> S3
```

| Step | Script | Fungsi |
|---|---|---|
| 1 *(baru)* | `update_account_lasttxdate.py` | Update `tgl_transaksi_terakhir`, `tgl_aktivitas_nonfin_terakhir`, dan `tgl_aktivitas_terakhir` (gabungan) di `RekeningLiabilitas` |
| 2 *(dimodifikasi)* | `update_dormant_account.py` | Baca `tgl_aktivitas_terakhir` → tentukan status Tidak Aktif atau Dormant berdasarkan threshold efektif |
| 3 *(dimodifikasi)* | `saving_auto_close.py` | Identifikasi rekening saldo nol melewati threshold → tutup otomatis |

> ⚠️ **Urutan Step 1 → 2 → 3 wajib dijaga.** Step 2 dan 3 harus berjalan setelah `tgl_aktivitas_terakhir` selesai diupdate oleh Step 1.

### 6.2. Rekening Berubah Menjadi Tidak Aktif (UC-01)

**Aktor:** Sistem (proses otomatis harian / EOD)

| | Keterangan |
|---|---|
| **Given** | Rekening nasabah berstatus **Aktif** dan tidak memiliki aktivitas apapun selama lebih dari batas hari yang dikonfigurasi (default: 360 hari / ± 1 tahun) |
| **When** | Proses harian (End of Day) berjalan |
| **Then** | Status rekening berubah menjadi **Tidak Aktif** (H+1); rekening dicatat dalam laporan R041 |

**Skenario Tambahan:**

| Skenario | Given | When | Then |
|---|---|---|---|
| **Produk dikecualikan** | Rekening menggunakan produk dengan `is_tidak_dormant = T` | Proses harian berjalan | Rekening **tidak** berubah status — tetap Aktif |
| **Produk dengan threshold custom** | Rekening menggunakan produk dengan `is_custom_dormant = T` | Proses harian berjalan | Sistem menggunakan batas hari dari konfigurasi produk |
| **Nasabah cek saldo melalui ATM** | Rekening hampir melewati batas hari tidak aktif, nasabah cek saldo via ATM | Proses harian berjalan | Cek saldo **dicatat** dan counter di-reset — rekening tetap Aktif |

### 6.3. Rekening Berubah Menjadi Dormant (UC-02)

**Aktor:** Sistem (proses otomatis harian / EOD)

| | Keterangan |
|---|---|
| **Given** | Rekening nasabah berstatus **Tidak Aktif** dan tidak ada aktivitas apapun hingga melewati batas hari dormant (default: 1.800 hari / ± 5 tahun sejak aktivitas terakhir) |
| **When** | Proses harian (End of Day) berjalan |
| **Then** | Status rekening berubah menjadi **Dormant** (H+1); rekening dicatat dalam laporan R029; seluruh transaksi nasabah diblokir |

**Skenario Tambahan:**

| Skenario | Given | When | Then |
|---|---|---|---|
| **Rekening dikecualikan** | Rekening/produk dengan `is_tidak_dormant = T` | Proses harian berjalan | Rekening **tidak** berubah ke status Dormant |
| **Produk dengan threshold dormant custom** | Produk memiliki `is_custom_dormant = T` | Proses harian berjalan | Sistem menggunakan batas hari dari konfigurasi produk |

### 6.4. Rekening Ditutup Otomatis Saldo Nol (UC-03)

**Aktor:** Sistem (proses otomatis harian / EOD)

| | Keterangan |
|---|---|
| **Given** | Rekening nasabah (dalam status apapun kecuali Tutup) memiliki **saldo Rp 0** secara terus-menerus selama lebih dari batas hari yang dikonfigurasi (default: 180 hari) |
| **When** | Proses harian (End of Day) berjalan |
| **Then** | Rekening ditutup otomatis; dicatat dalam laporan R030 |

**Skenario Tambahan:**

| Skenario | Given | When | Then |
|---|---|---|---|
| **Produk dikecualikan** | Rekening menggunakan produk dengan `is_exc_tutupnol = T` | Proses harian berjalan | Rekening **tidak** ditutup, meskipun saldo Rp 0 dalam waktu lama |
| **Saldo kembali ada sebelum batas** | Rekening saldo Rp 0, kemudian ada setoran sebelum melewati batas hari | Proses harian berjalan | Counter saldo nol di-reset, rekening tidak ditutup |

---

## 7. Transaksi Berdasarkan Status Rekening

Perilaku sistem saat transaksi dilakukan pada rekening dengan status berbeda ditentukan oleh konfigurasi `allow_rekening_tidak_aktif` dan `allow_rekening_dormant` di **Parameter Transaksi**. Nilai default:

| Kondisi | Default |
|---|---|
| Rekening Tidak Aktif | Hanya kredit yang diizinkan (`allow_rekening_tidak_aktif = C`) |
| Rekening Dormant | Seluruh transaksi nasabah ditolak (`allow_rekening_dormant = F`) |

**Tabel nilai `allow_rekening_*`:**

| Nilai | Arti |
|:---:|---|
| `DC` | Izinkan Debet dan Kredit |
| `C` | Tolak Debet, Kredit diizinkan |
| `D` | Tolak Kredit, Debet diizinkan |
| `F` | Tolak Debet dan Kredit |

Untuk kode transaksi yang **tidak terdaftar** di Parameter Transaksi, sistem menggunakan nilai default: `allow_rekening_tidak_aktif = C` dan `allow_rekening_dormant = F`.

Lihat **Lampiran C** untuk screenshot pesan penolakan transaksi pada rekening Tidak Aktif dan Dormant.

---

## 8. Reaktivasi Rekening (UC-05)

Rekening Tidak Aktif dan Dormant dapat diaktivasi melalui dua jalur:

| Channel | Aplikasi | Mekanisme |
|---|---|---|
| **Kantor Cabang** | DAF & BDS | Operator input → Supervisor otorisasi |
| **E-Channel** | BSya Mobile | Nasabah aktivasi mandiri |

### 8.1. Alur Reaktivasi via Cabang (DAF / BDS)

```mermaid
flowchart TD
    A([Petugas Cabang\nBuka Menu Reaktivasi]) --> B[Cari rekening\nTidak Aktif / Dormant]
    B --> D[Submit → status: Menunggu Persetujuan]
    D --> E([Supervisor membuka\nantrian persetujuan])
    E --> F{Keputusan}
    F -->|Setuju| G[Status rekening → AKTIF\nCounter aktivitas di-reset ke hari ini\nLog & notifikasi disimpan]
    F -->|Tolak| H[Status rekening tetap\nLog & notifikasi disimpan]
```

| | Keterangan |
|---|---|
| **Given** | Rekening nasabah berstatus **Tidak Aktif** atau **Dormant** |
| **When** | Petugas cabang mengajukan reaktivasi melalui menu DAF atau BDS |
| **Then** | Pengajuan masuk ke antrian Supervisor |

| Skenario | When | Then |
|---|---|---|
| **Disetujui** | Supervisor menyetujui pengajuan | Status → **Aktif**; counter aktivitas di-reset; log disimpan; notifikasi ke petugas |
| **Ditolak** | Supervisor menolak pengajuan | Status **tidak berubah**; log disimpan; notifikasi ke petugas |

> Tutup rekening dapat dilakukan langsung **tanpa reaktivasi** terlebih dahulu. Status Tidak Aktif/Dormant akan ditampilkan pada informasi override.

---

## 9. Pengenaan Biaya Rekening (UC-06)

**Aktor:** Sistem (proses otomatis bulanan / EOM)

| | Keterangan |
|---|---|
| **Given** | Rekening nasabah berstatus **Tidak Aktif** atau **Dormant** pada saat proses akhir bulan berjalan |
| **When** | Proses akhir bulan (End of Month) berjalan |
| **Then** | Biaya administrasi rekening dikenakan sesuai konfigurasi yang berlaku. Biaya tidak boleh melebihi saldo tersedia — partial debet diperbolehkan, saldo tidak boleh menjadi negatif |

**Skenario Tambahan:**

| Skenario | Given | When | Then |
|---|---|---|---|
| **Biaya dari konfigurasi produk** | Produk memiliki konfigurasi biaya sendiri (`is_custom_dormant = T`) | Proses akhir bulan berjalan | Sistem menggunakan nominal biaya dari konfigurasi produk |
| **Biaya dari konfigurasi global** | Produk tidak memiliki konfigurasi biaya khusus | Proses akhir bulan berjalan | Sistem menggunakan nominal biaya dari pengaturan global (`TAKT_BIAYA`, `DORM_BIAYA`) |
| **Saldo tidak mencukupi** | Saldo rekening lebih kecil dari biaya yang akan dikenakan | Proses akhir bulan berjalan | Biaya dikenakan sebesar saldo tersedia (partial); saldo tidak menjadi negatif |

---

## 10. Laporan

### 10.1. Laporan Rekening Tidak Aktif (R041)

- **Nama Laporan:** Rekening Aktif jadi Tidak Aktif
- **Sistem:** DAF
- **Menu:** Laporan → Rekening Aktif jadi Tidak Aktif
- **Trigger:** Dihasilkan setiap hari setelah proses EOD — rekening yang berubah dari Aktif ke Tidak Aktif pada hari tersebut
- **Kolom:** Nomor Rekening, Nama Nasabah, Tanggal Aktivitas Terakhir, Saldo, Parameter Hari Tidak Aktif, Tanggal Proses

### 10.2. Laporan Rekening Dormant (R029)

- **Nama Laporan:** Rekening Dormant
- **Sistem:** DAF (R029) dan BDS (R029 Perubahan Status)
- **Menu:** Laporan → Rekening Dormant
- **Trigger:** Dihasilkan setiap hari setelah proses EOD
- **Enhance:** Penambahan kolom `tgl_aktivitas_terakhir` (gabungan transaksi + non-finansial)

### 10.3. Laporan Tutup Otomatis (R030)

- **Nama Laporan:** Rekening Tutup Otomatis
- **Sistem:** DAF
- **Menu:** Laporan → Rekening Tutup Otomatis
- **Trigger:** Dihasilkan setiap hari setelah proses EOD
- **Enhance:** Penambahan kolom `tgl_saldo_nol` (tanggal saldo pertama kali menjadi nol) dan `param_hari_tutup_oto` (threshold hari efektif yang digunakan)

---

## 11. Perubahan Database

### 11.1. Ringkasan Perubahan

| Objek | Aksi | Keterangan |
|---|---|---|
| `parameterglobal` | ADD COLUMN `kode_group` | Pengelompokan parameter per fitur/modul |
| `parameterglobal` | INSERT 5 data | Parameter grup `REKENING_DORMANT`: `TAKT_HARI`, `DORM_HARI`, `TUTUP_NOL_HARI`, `TAKT_BIAYA`, `DORM_BIAYA` |
| `produk` | ADD COLUMN | `is_custom_dormant`, `is_custom_tutup_oto`, `is_exc_tutupnol`, `jumlah_hari_jadi_dormant`, `biaya_rekening_tidak_aktif`, `is_biaya_rekening_tidak_aktif` |
| `produk` | UBAH SEMANTIK | `is_tidak_dormant` diperluas ke fase Tidak Aktif; kolom override hanya dibaca jika flag custom aktif |
| `rekeningliabilitas` | ADD COLUMN | `tgl_aktivitas_terakhir`, `tgl_aktivitas_nonfin_terakhir` |
| `parametertransaksiumum` | ADD COLUMN | `tipe_exclude_aktivitas_nasabah`, `is_transaksi_sistem`, `allow_rekening_tidak_aktif`, `allow_rekening_dormant` |
| `rekeningaktivitasnonfin` | CREATE TABLE | Log aktivitas non-finansial nasabah |
| `ibankrep.rekening_tidak_aktif` | CREATE TABLE | Tabel report rekening yang berpindah status ke Tidak Aktif |
| `ibankrep.rekening_dorman` | ADD COLUMN | `tgl_aktivitas_terakhir` |
| `ibankrep.rekening_tutupotomatis` | ADD COLUMN | `tgl_saldo_nol`, `param_hari_tutup_oto` |
| `ibanktmp.*` | CREATE TABLE | Tabel staging EOD: kandidat tidak aktif, dormant, tutup otomatis, update aktivitas |
| `bpscript` / `bpstep` | INSERT | Registrasi script `update_account_lasttxdate` ke jadwal EOD |
| `report` | INSERT | Registrasi laporan R041 — Rekening Aktif jadi Tidak Aktif |

> DDL detail untuk setiap objek di atas dituangkan dalam dokumen TSD (Technical Specification Document).

---

## 12. Pengaturan Umum

- Seluruh konfigurasi parameter (hari dan biaya) dapat diubah oleh administrator sistem tanpa perlu deployment ulang aplikasi.
- Nilai parameter global berlaku untuk semua produk kecuali produk yang memiliki konfigurasi override sendiri (`is_custom_dormant = T` atau `is_custom_tutup_oto = T`).
- Perubahan threshold parameter global berlaku efektif pada proses EOD berikutnya setelah perubahan disimpan.
- Reaktivasi rekening hanya dapat dilakukan melalui menu yang tersedia, oleh petugas yang memiliki hak akses, dan memerlukan persetujuan supervisor — tidak ada reaktivasi otomatis berdasarkan aktivitas nasabah.
- Perubahan status rekening di seluruh channel (BDS, E-Channel) efektif H+1 setelah proses EOD, sinkron dengan Core Banking (DAF).
- Tabel `RekeningAktivitasNonfin` dapat di-purge secara berkala (retensi disarankan: 2 tahun) untuk mengendalikan pertumbuhan volume data.
- Biaya administrasi rekening Tidak Aktif dan Dormant tidak boleh menyebabkan saldo negatif — pendebetan dilakukan sebesar saldo tersedia (partial debet).

---

## 13. Lampiran

### Lampiran A. Screenshot Konfigurasi Parameter

**A.1 Parameter Global**

- Menu Parameter Global (filter grup: `REKENING_DORMANT`)

![Parameter Global - Menu](assets/dorman_parameterglobal_01.png)

- List parameter `REKENING_DORMANT`

![Parameter Global - List](assets/dorman_parameterglobal_02.png)

- Form edit parameter (contoh: `TAKT_HARI = 360`)

![Parameter Global - Form Edit](assets/dorman_parameterglobal_03.png)

**A.2 Parameter Transaksi**

- Menu Parameter Transaksi

![Menu Parameter Transaksi](assets/dorman_parametertransaksi_01.png)

- List daftar parameter transaksi

![Daftar Parameter Transaksi](assets/dorman_parametertransaksi_02.png)

- Form detail parameter transaksi

![Form Detail Parameter Transaksi](assets/dorman_parametertransaksi_03.png)

**A.3 Parameter Produk**

- Menu List Produk Tabungan / Giro

![Menu List Produk Tabungan](assets/dorman_produk_01.png)

- Form Ubah Produk — Parameter Tidak Aktif, Dormant, dan Tutup Otomatis

![Form Ubah Produk](assets/dorman_produk_02.png)

---

### Lampiran B. Screenshot Informasi Rekening

- Info Tanggal Aktivitas Terakhir

![Informasi Rekening - Tgl Aktivitas Terakhir](assets/dorman_inforekening_01.png)

- Info Histori Tanggal Aktivitas Nonfin Terakhir

![Informasi Rekening - Histori Nonfin](assets/dorman_inforekening_02.png)

- Info Saldo Nol

![Informasi Rekening - Saldo Nol](assets/dorman_inforekening_03.png)

---

### Lampiran C. Screenshot Transaksi Berdasarkan Status Rekening

- Transaksi pada rekening **Tidak Aktif** — debet ditolak

![Transaksi Rekening Tidak Aktif](assets/dorman_transaksi_02.png)

- Transaksi pada rekening **Dormant** — transaksi diblokir

![Transaksi Rekening Dormant](assets/dorman_transaksi_01.png)

---

### Lampiran D. Screenshot Reaktivasi Rekening

- Menu Ubah Rekening Tidak Aktif / Dormant

![Menu Reaktivasi Rekening](assets/dorman_reaktivasi_01.png)

- Form Ubah Rekening Tidak Aktif / Dormant

![Form Reaktivasi Rekening](assets/dorman_reaktivasi_02.png)

---

### Lampiran E. Screenshot Laporan

**E.1 Laporan Rekening Tidak Aktif (R041)**

- Menu Laporan Rekening Aktif jadi Tidak Aktif

![Laporan Tidak Aktif - Menu](assets/dorman_laporan_tidakaktif_01.png)

- Hasil laporan

![Laporan Tidak Aktif - Hasil](assets/dorman_laporan_tidakaktif_02.png)

**E.2 Laporan Rekening Dormant (R029)**

- Menu Laporan Rekening Dormant

![Laporan Dormant - Menu](assets/dorman_laporan_dormant_01.png)

- Hasil laporan

![Laporan Dormant - Hasil](assets/dorman_laporan_dormant_02.png)

**E.3 Laporan Tutup Otomatis (R030)**

- Menu Laporan Rekening Tutup Otomatis

![Laporan Tutup Otomatis - Menu](assets/dorman_laporan_tutup_01.png)

- Hasil laporan

![Laporan Tutup Otomatis - Hasil](assets/dorman_laporan_tutup_02.png)
