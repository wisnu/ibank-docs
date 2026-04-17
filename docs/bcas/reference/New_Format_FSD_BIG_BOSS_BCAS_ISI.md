# FUNCTIONAL SPECIFICATION DOCUMENT
## BCA SYARIAH (BCAS)

**MODUL TAHAPAN RENCANA iB (TRiB)**

**FITUR REGISTRASI REKENING**

---

Dipersiapkan oleh:

**PT Ihsan Solusi Informatika**
Jl. PHH Mustofa No. 39, Ruko Surapati Core C-7 Bandung

| | | |
|---|---|---|
| **Nomor Dokumen** | **FSD-BCAS-TRIB-02** | **Halaman: 1 / 23** |
| **Versi** | 1.1.0 | 12 Januari 2025 |

---

## Author

| **Nama** | **Role** |
|---|---|
| {Nama writer} | Technical Writer |
| {Nama Reviewer} | Reviewer |

---

## Detail Daftar Perubahan

| Versi | Tanggal Perubahan | Penulis | Deskripsi |
|---|---|---|---|
| {diisi nomor versi} | {diisi tanggal ketika perubahan mulai dilakukan} | {nama penulis} | {poin – poin perubahan} |
| {diisi nomor versi} | {diisi tanggal ketika perubahan mulai dilakukan} | {nama penulis} | {poin – poin perubahan} |

---

## Daftar Isi

1. [Gambaran Umum](#1-gambaran-umum)
   - 1.1. Latar Belakang
   - 1.2. Tujuan
   - 1.3. Ruang Lingkup
   - 1.4. Definisi
   - 1.5. Objektif
   - 1.6. Pengguna
2. [Arsitektur Sistem](#2-arsitektur-sistem)
   - 2.1. Arsitektur Sistem
3. [Registrasi](#3-registrasi)
   - 3.1. Alur Proses
   - 3.2. Keterangan Alur Proses
   - 3.3. Use Case
   - 3.4. Mockup {judul mockup}
     - 3.4.1. Mockup {judul mockup 1}
     - 3.4.2. Mockup {judul mockup 2}
   - 3.5. *Field Description* {nama fitur/halaman}
     - 3.5.1. *Field Description* {sesuai mockup}
   - 3.6. *Action*
   - 3.7. Tabel Validasi {nama fitur}
4. [Pengaturan Umum](#4-pengaturan-umum)
   - 4.1. Pengaturan
5. [Persetujuan Dokumen BCA Syariah](#persetujuan-dokumen-bca-syariah)
6. [Persetujuan Dokumen ISI](#persetujuan-dokumen-isi)

---

# 1. Gambaran Umum

## 1.1. Latar Belakang

{berisikan mengapa perlu dilakukan pengembangan aplikasi}

## 1.2. Tujuan

Berikut ini adalah tujuan pengembangan fitur pada Aplikasi xxxxxxxxxxxxxxx:

- {poin poin yang diharapkan}
- {poin poin yang diharapkan}

## 1.3. Ruang Lingkup

Ruang lingkup pengembangan fitur pada aplikasi xxxxxxxxxxx adalah sebagai berikut:

- {Fitur yang akan dikembangkan}
- {Fitur yang akan dikembangkan}

## 1.4. Definisi

Berikut adalah definisi dari beberapa istilah yang ada pada proses {fitur}:

- {"Istilah": "definisi"}
  > *Contoh: Cetak Validasi: Cetak validasi adalah proses yang dilakukan pada saat akhir registrasi xxxxxxx*
- {berisi poin poin istilah penting/specialized process}

## 1.5. Objektif

- Dokumen ini disusun agar setiap pengguna dan pihak yang terlibat dalam proyek dapat memahami secara menyeluruh detail terkait aplikasi.
- Seluruh ilustrasi/gambar pada dokumen ini digunakan semata-mata sebagai alat bantu untuk memudahkan pemahaman terhadap deskripsi *field* maupun alur proses/*event*.
- Aplikasi ini ditujukan untuk mendukung operasional cabang, digunakan oleh petugas bank dalam melakukan transaksi dan aktivitas terkait, dengan pendekatan yang sederhana, efektif, dan mendukung implementasi cepat (*quick win*).
- Dokumen ini merupakan dokumen fungsional yang dihasilkan dari proses pengumpulan kebutuhan bisnis (*business requirement gathering*) antara tim vendor dan tim BCAS.
- Dokumen ini akan terus diperbarui sesuai kebutuhan, dan setiap perubahan harus disetujui oleh setiap pihak (vendor dan BCAS) melalui tanda tangan perwakilan resmi dari masing-masing pihak.

## 1.6. Pengguna

Berikut adalah pengguna {aplikasi/fitur}:

| **No** | ***Role*** | **Deskripsi** |
|---|---|---|
| 1 | {diisi role} | {penjelasan atas role termasuk fungsi dan menu yang dapat diakses} |
| | | *Contoh: Role operator pada fitur ini diberikan kepada petugas customer service BCA Syariah. Operator memiliki kewenangan untuk melakukan: penginputan data nasabah, melakukan proses setoran awal, dll (spesifik pada proses per fitur).* |
| 2 | {diisi role} | {penjelasan atas role termasuk fungsi} |

---

# 2. Arsitektur Sistem

## 2.1. Arsitektur Sistem

Berikut ini adalah arsitektur sistem dari xxxx.

{alur ini menggambarkan aplikasi terkoneksi dengan server aplikasi mana saja}

> {Lampirkan diagram arsitektur sistem di sini}

**Keterangan**

{Penjelasan secara high level dari konektivitas antar sistem. Jelaskan juga secara fungsi nya}

---

# 3. Registrasi

> *Catatan: Judul disesuaikan dengan setiap aktivitas yang dapat dilakukan pada fitur yang dikembangkan. Contoh untuk registrasi dapat dipecah menjadi beberapa aktivitas/judul: Registrasi (main flow saat operator melakukan registrasi seperti input data, dll), Otorisasi supervisor, Cetak ulang validasi, dll.*

## 3.1. Alur Proses

Alur Proses *xxxxxxx*.

{Penjelasan alur proses}

> {Lampirkan diagram alur proses di sini}

## 3.2. Keterangan Alur Proses

Berikut keterangan alur proses xxxx:

| | | |
|---|---|---|
| **Deskripsi** | **:** | Deskripsi terkait flow |
| ***User*** | **:** | {role} |
| **Pre kondisi** | **:** | {kondisi-kondisi sebelum proses dimulai} |
| | | *Misalnya: user telah login ke aplikasi BIG BOSS; Dana tersedia di SoF; dll* |
| **Alur** | **:** | 1. {langkah pertama} |
| | | 2. {langkah berikutnya} |
| | | {menerangkan detail dari flow di atas} |
| ***Error Handling*** | **:** | Sistem menampilkan pesan error sesuai dengan tabel validasi {nama fitur} |
| ***Post* kondisi** | **:** | {menerangkan kondisi yang terjadi setelah proses dijalankan} |

## 3.3. *Use Case*

Berikut *use case* proses xxxx:

| | | |
|---|---|---|
| ***Given*** | **:** | {kondisi awal / state yang sudah ada} |
| | | *Contoh: Nasabah sudah berada pada halaman **Pembayaran Zakat Fitrah*** |
| ***When*** | **:** | - {aksi yang dilakukan pengguna} |
| | | - {aksi berikutnya} |
| | | *Contoh: Nasabah menekan tombol "+" untuk menambah jumlah orang yang akan dibayarkan; Nasabah menekan tombol "-" untuk mengurangi jumlah orang yang akan dibayarkan.* |
| ***Then*** | **:** | - {hasil/output yang diharapkan dari sistem} |
| | | *Contoh: Detail pembayaran Zakat Fitrah akan bertambah **1 orang** setiap kali tombol "+" ditekan. Jika jumlah sudah mencapai **10 orang**, maka tombol "+" akan menjadi tidak aktif (berwarna abu-abu) dan tidak dapat ditekan. Detail pembayaran Zakat Fitrah akan berkurang **1 orang** setiap kali tombol "-" ditekan. Jika jumlah sudah mencapai **1 orang**, maka tombol "-" akan menjadi tidak aktif (berwarna abu-abu) dan tidak dapat ditekan.* |

## 3.4. *Mockup* {judul mockup}

> *Catatan: Masukkan seluruh mockup yang ada pada proses satu flow. Misal flow registrasi, mockup yang dimasukkan: Form registrasi, Pop up pencarian data CIF, dll.*

### 3.4.1. *Mockup* {judul mockup 1}

{Lampirkan UI detail Mockup1 dengan judul1}

{Keterangan1 dan/atau additional information dari mockup}

### 3.4.2. *Mockup* {judul mockup 2}

{Lampirkan UI detail Mockup2 dengan judul2}

{Keterangan2 dan/atau additional information dari mockup}

## 3.5. *Field Description* {nama fitur/halaman}

### 3.5.1. *Field Description* {sesuai mockup}

Berikut adalah tabel *field description* ketika sistem menampilkan informasi pada halaman {nama fitur sesuai *mockup*}:

| **Nama *Field*** | **Deskripsi** | ***Mandatory* (M/O/C)** | **Sumber Data** |
|---|---|---|---|
| Nomor Nasabah | Nomor CIF nasabah *join account* deposito yang bersumber dari *Core*. Tipe data: *Numeric* | - | *Core* |
| Nama nasabah | Nama nasabah *join account* deposito. Tipe data: *alphanumeric* | - | *Core* |

Berikut adalah tabel *field description* ketika user akan melakukan *inquiry* pada halaman {nama fitur}:

| **Nama *Field*** | **Deskripsi** | ***Data Type*** | ***Length*** | ***Mandatory* (M/O/C)** | **Sumber Data** |
|---|---|---|---|---|---|
| Kode Program | Kode Program pembukaan rekening deposito | *Varchar* | 20 | O | Manual Input |
| Status Kelengkapan | Kode dan Nama Marketing | *String* | - | M | *Dropdown* |

Keterangan pilihan pada *field dropdown* {digunakan jika field bersifat dropdown}:

| ***Field*** | ***Option Dropdown*** |
|---|---|
| {nama field} | - Pilihan 1 |
| | - Pilihan 2 |
| | - Pilihan 3 |

## 3.6. *Action*

Berikut adalah *action* yang dapat dilakukan oleh pengguna pada halaman {sesuai dengan mockup}:

| ***Action*** | ***Output*** | **Keterangan** |
|---|---|---|
| {Nama Button} | {Response sistem setelah button diklik} | {additional info/deskripsi fungsional dari button tsb} |
| *Contoh: Eye Button pada Field Input Password* | *Contoh: Sistem mengubah visibilitas teks pada field input password dari tersembunyi (masking) menjadi terlihat, dan sebaliknya. Ikon mata juga akan berubah (misal: dari mata tertutup menjadi mata terbuka).* | *Contoh: Memungkinkan pengguna untuk melihat/menyembunyikan karakter password yang diinput.* |

## 3.7. Tabel Validasi {nama fitur}

Berikut adalah tabel validasi yang menjadi acuan *error handling* pada proses xxxx:

| ***Case*** | ***Result*** |
|---|---|
| {Berisi validasi/case jika ada error system & human error dalam menggunakan aplikasi} | {error message yang tampil pada aplikasi} |
| *Contoh 1: Case bisa berupa validasi pada field input di setiap form, misal: field bersifat mandatory namun user tidak mengisi form tersebut → notifikasi: Mohon lengkapi semua field. (Field yang kosong dapat ditandai dengan highlight warna merah).* | |
| *Contoh 2: Case bisa berupa error system, misal: system gagal generate dokumen → Notifikasi: Terjadi kesalahan pada sistem. Gagal memproses data. Silakan coba kembali.* | |

---

# 4. Pengaturan Umum

## 4.1. Pengaturan

Pengaturan umum pada aplikasi sebagai berikut:

{penambahan pengaturan yang berlaku global}

| **Konfigurasi** | **Keterangan** |
|---|---|
| *Single Session* | Jika ada *user* yang sedang *login* kemudian ada user lain yang menggunakan credential yang sama dengan user yang saat ini sedang login, maka user lama tersebut akan dikeluarkan dari sesi aktifnya. |
| *Idle Time out* | Sistem akan logout secara otomatis apabila tidak ada interaksi atau proses selama 10 menit. |
| *Audit Trail* | xxxxxx |

---

# Persetujuan Dokumen BCA Syariah

**PT Bank BCA Syariah**

| | | |
|---|---|---|
| | | |
| {Diisi Nama} | {Diisi Nama} | {Diisi Nama} |
| {Role/Jabatan} | {Role/Jabatan} | {Role/Jabatan} |
| {DD/MM/YYYY} | {DD/MM/YYYY} | {DD/MM/YYYY} |

| | | |
|---|---|---|
| | | |
| {Diisi Nama} | {Diisi Nama} | {Diisi Nama} |
| {Role/Jabatan} | {Role/Jabatan} | {Role/Jabatan} |
| {DD/MM/YYYY} | {DD/MM/YYYY} | {DD/MM/YYYY} |

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

| | | |
|---|---|---|
| | | |
| {Diisi Nama} | {Diisi Nama} | {Diisi Nama} |
| {Role/Jabatan} | {Role/Jabatan} | {Role/Jabatan} |
| {DD/MM/YYYY} | {DD/MM/YYYY} | {DD/MM/YYYY} |
