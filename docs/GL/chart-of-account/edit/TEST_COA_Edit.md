# Dokumen Testing: Ubah Rekening (COA)

> Sumber: [FSD_COA_Edit.md](FSD_COA_Edit.md)
> Versi: 1.0
> Tanggal: 2026-01-19
> Status: Draft

---

## 1. Tujuan

Memastikan fitur Ubah Rekening (COA) berjalan sesuai kebutuhan FE dan BE, termasuk validasi, alur otorisasi, serta penyimpanan perubahan pada `ibcore.account` dan `ibcore.accountinstance`.

---

## 2. Ruang Lingkup

- Akses halaman Ubah Rekening
- Edit field yang diizinkan pada master COA
- Edit parameter saldo/transaksi pada account instance
- Submit pengajuan perubahan (pending approval)
- Otorisasi approve/reject dan penerapan perubahan
- Validasi field dan aturan bisnis utama

Di luar lingkup:
- Master data pembuatan COA baru
- Perubahan struktur data di luar field yang disebutkan di FSD

---

## 3. Peran Penguji

- Operator Data
- Otorisator

---

## 4. Prasyarat & Data Uji

- Minimal 1 data COA aktif dengan `account_code` valid.
- Memiliki account instance untuk beberapa kombinasi `branch_code` dan `currency_code`.
- User Operator dan Otorisator aktif.
- Data master referensi yang dibutuhkan: CPA, pajak, cabang, valuta.

Contoh data uji:
- `account_code`: COA-1001 (is_detail = T)
- `branch_code`: 001, 002
- `currency_code`: IDR, USD

---

## 5. Kriteria Penerimaan

- Semua field read-only tidak bisa diubah.
- Field wajib tidak boleh kosong.
- Perubahan masuk ke daftar otorisasi dengan status Pending Approval.
- Approve menerapkan perubahan ke tabel terkait.
- Reject tidak mengubah data aktif.
- Audit `userid_last_modified` dan `time_last_modified` terisi saat approve.

---

## 6. Test Scenarios & Test Cases

### 6.1 Akses Halaman Ubah Rekening

| ID | Skenario | Langkah Uji | Hasil yang Diharapkan |
| --- | --- | --- | --- |
| FE-01 | Akses menu Ubah Rekening | Login sebagai Operator -> Buka Data Master -> Data Rekening (COA) -> Pilih rekening -> Klik Ubah Rekening | Halaman edit tampil, data terisi sesuai DB |
| FE-02 | Field read-only tidak dapat diubah | Coba edit `account_code`, `account_group_code`, `fl_parent_account` | Field tidak bisa diubah |

### 6.2 Validasi Form Master COA

| ID | Skenario | Langkah Uji | Hasil yang Diharapkan |
| --- | --- | --- | --- |
| FE-03 | Nama Rekening wajib | Kosongkan `account_name`, lalu submit | Validasi error muncul |
| FE-04 | Batas panjang Nama Rekening | Isi `account_name` > 200 char | Validasi error muncul |
| FE-05 | Batas panjang Deskripsi Rekening | Isi `account_desc` > 400 char | Validasi error muncul |
| FE-06 | Sandi BI max 10 char | Isi `sandi_bi` > 10 char | Validasi error muncul |
| FE-07 | Kode Pajak max 20 char | Isi `tax_code` > 20 char | Validasi error muncul |
| FE-08 | Tarif pajak tidak negatif | Isi `tax_rate_npwp` < 0 | Validasi error muncul |
| FE-09 | Default tarif pajak | Kosongkan `tax_rate_npwp` dan `tax_rate_non_npwp` | Default 0.00 tersimpan |

### 6.3 Parameter Saldo & Transaksi (Default)

| ID | Skenario | Langkah Uji | Hasil yang Diharapkan |
| --- | --- | --- | --- |
| FE-10 | Dropdown saldo normal default | Pilih Debet/Kredit/Netral | Nilai tersimpan sesuai mapping internal |
| FE-11 | Dropdown saldo harus nihil | Pilih Boleh Tidak Nihil/Harus Nihil | Nilai tersimpan sesuai mapping internal |
| FE-12 | Dropdown status transaksi | Pilih status transaksi yang tersedia | Nilai tersimpan sesuai mapping internal |

### 6.4 Button Propagasi ke Account Instance

| ID | Skenario | Langkah Uji | Hasil yang Diharapkan |
| --- | --- | --- | --- |
| FE-13 | Set Semua Status Saldo Normal | Pilih default -> klik Set Semua Status Saldo Normal | `accountinstance.normal_balance_type` ter-update semua instance |
| FE-14 | Set Semua Status Saldo Nihil | Pilih default -> klik Set Semua Status Saldo Nihil | `accountinstance.is_zero_balance` ter-update semua instance |
| FE-15 | Set Semua Status Transaksi | Pilih default -> klik Set Semua Status Transaksi | `accountinstance.trx_permit_type` ter-update semua instance |

### 6.5 Grid Account Instance

| ID | Skenario | Langkah Uji | Hasil yang Diharapkan |
| --- | --- | --- | --- |
| FE-16 | Field read-only pada grid | Coba edit `branch_code`, `currency_code` | Tidak bisa diubah |
| FE-17 | Edit parameter instance | Ubah saldo normal/saldo nihil/tipe transaksi | Nilai berubah pada baris terkait |

### 6.6 Submit Pengajuan Perubahan

| ID | Skenario | Langkah Uji | Hasil yang Diharapkan |
| --- | --- | --- | --- |
| BE-01 | Submit perubahan valid | Ubah beberapa field -> klik Submit | Pengajuan tersimpan, status Pending Approval |
| BE-02 | Submit tanpa `account_code` | Hapus/invalid `account_code` -> Submit | Error: account_code harus exist |
| BE-03 | Field di luar whitelist | Kirim payload dengan field non-editable | Error validasi |
| BE-04 | Perubahan instance tidak ada | Ubah instance yang tidak exist | Error validasi |

### 6.7 Otorisasi Approve/Reject

| ID | Skenario | Langkah Uji | Hasil yang Diharapkan |
| --- | --- | --- | --- |
| OA-01 | Approve pengajuan | Login Otorisator -> pilih pending -> Approve | Data `ibcore.account` dan `ibcore.accountinstance` ter-update |
| OA-02 | Reject pengajuan | Login Otorisator -> pilih pending -> Reject | Tidak ada perubahan pada data aktif |
| OA-03 | Audit field terisi | Approve pengajuan | `userid_last_modified` dan `time_last_modified` terisi |

---

## 7. Uji Negatif & Batasan

- Coba submit tanpa perubahan apa pun -> sistem menolak atau memberi peringatan.
- Coba input karakter khusus di field yang memiliki batas panjang.
- Coba user non-otorisator melakukan approve/reject -> akses ditolak.

---

## 8. Catatan

- Mapping dropdown ke kode internal harus dikonfirmasi di implementasi.
- Jika `alasan` wajib, tambahkan validasi di skenario submit.

