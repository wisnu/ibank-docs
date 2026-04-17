# Summary: Change Request Form — Penyesuaian Status dan Sistem Pengelolaan Rekening

## Informasi Umum

| Atribut | Detail |
|---|---|
| **No. Nota Dinas** | 2489/N-DDJ/2025 & 3051/N-DDK/DI/2025 |
| **Tanggal** | 19 Desember 2025 |
| **Diajukan Oleh** | Ardian Faturahman (Div. Dana Jasa Ritel) & Dara Fitri Januarti (Div. Dana Korporasi & Institusi) |
| **Ditujukan Kepada** | Divisi Teknologi Informasi |
| **Alasan Perubahan** | POJK Nomor 24 Tahun 2025 |
| **Deadline Implementasi** | **30 April 2026** (batas regulator OJK: 10 Mei 2026) |

---

## Latar Belakang

OJK menerbitkan POJK No. 24 Tahun 2025 tentang Standarisasi Pengelolaan Rekening pada Bank. Peraturan ini menggantikan kebijakan internal masing-masing bank agar terdapat keseragaman perlakuan, perlindungan nasabah, serta kepastian prosedur bagi seluruh stakeholder. Peraturan berlaku untuk **Rekening Giro dan Tabungan**.

---

## Klasifikasi Status Rekening (Ketentuan Baru)

### 1. Rekening Aktif
Rekening yang dalam **360 hari terakhir** memiliki salah satu aktivitas berikut:
- Aktivitas **pemasukan** (setoran tunai via Teller / Cash Deposit Machine)
- Aktivitas **penarikan** (tunai via Teller, ATM Bank, ATM Bank lain)
- **Pengecekan saldo** (via ATM, Mobile Banking, Cash Management System, Jaringan Kantor)

**Tidak dihitung sebagai aktivitas:** pembayaran bagi hasil, pemotongan pajak, biaya administrasi, auto debet standing instruction, serta pemindahbukuan/transfer antar rekening.

Rekening berikut **selalu berstatus Aktif** berdasarkan kode produk, antara lain:
- Giro: 0103, 0104, 0105, 0108, 0109, 0110, 0111, 0112, 0123, 0124, 0125
- Tabungan: 0207/0252 (Haji), 0210 (Pensiunan), 0260 (Simpanan Pelajar PIP), 0262–0269 (Tabungan Rencana)
- Rekening afiliasi pembiayaan & rekening jaminan pembiayaan

### 2. Rekening Tidak Aktif (Pasif)
- Tidak ada aktivitas selama **> 360 hari kalender** → berubah status pada **hari ke-361**
- Bank **menonaktifkan fitur penarikan** (Teller, ATM, cardless withdrawal)
- Rekening masih dapat menerima **transfer/pemindahbukuan**
- Sistem menampilkan peringatan: *"Rekening berstatus Tidak Aktif, mohon lakukan Pengajuan Pengaktifan Kembali ke Kantor Cabang terdekat"*
- Aktivasi kembali hanya setelah nasabah mengajukan permohonan ke Bank

### 3. Rekening Dormant
- Tidak ada aktivitas selama **> 1.800 hari kalender** → berubah pada **hari ke-1.801**
- Bank **menonaktifkan fitur penarikan DAN pemasukan** (Teller, ATM, Cash Deposit Machine)
- Rekening masih dapat menerima **transfer/pemindahbukuan**
- Bank wajib menyampaikan informasi ke nasabah dan melakukan upaya reaktivasi paling sedikit:
  - **1x per 5 tahun** untuk saldo ≤ Rp 100 juta
  - **1x per 3 tahun** untuk saldo Rp 100 juta – Rp 1 miliar
  - **1x per 1 tahun** untuk saldo > Rp 1 miliar
- Bank tetap memberikan **bagi hasil** dan **boleh mengenakan biaya administrasi** pada rekening dormant

---

## Implikasi Perubahan Sistem (Change Request)

### 1. Penyesuaian Biaya Administrasi
- Mencabut ketentuan *"Transaction/Tx Pending"* yang berlaku saat ini
- Biaya administrasi (bulanan, pasif, dormant) hanya dikenakan **sebesar saldo yang tersedia** — tidak boleh menyebabkan saldo negatif
- Jika saldo habis, biaya tidak dikenakan hingga ada dana masuk berikutnya

### 2. Penyesuaian Kode Produk
- Diperlukan penyesuaian kode produk untuk tujuan tertentu sesuai ketentuan OJK
- Akan diajukan pada **change request selanjutnya**

### 3. Parameter Baru Status Rekening
- Pembuatan parameter aktivitas sesuai definisi OJK (pemasukan, penarikan, cek saldo)
- Penambahan parameter **"Day Last Activity (DLA)"**: menghitung lama hari sejak aktivitas terakhir yang valid
- DLA untuk rekening Tidak Aktif/Dormant **tidak diperbarui** saat ada aktivitas selama status tersebut — DLA baru dihitung ulang setelah nasabah mengajukan pengaktifan kembali
- Jika tidak dapat diakomodasi dalam satu parameter, ditambahkan parameter terpisah: *"Tanggal Aktivitas Terakhir Rekening Tidak Aktif/Dormant"*

### 4. Penambahan Kolom DLA pada Laporan PSR
- Penambahan kolom **Day Last Activity** pada laporan PSR: **K008, K010, K012, dan K013**

### 5. Penambahan Laporan Rekening Dormant di SILAUK
Laporan nominatif rekening dormant per jaringan kantor, dengan segmentasi waktu:
- ≥ 5 tahun dormant → saldo ≤ Rp 100 juta
- ≥ 3 tahun dormant → saldo Rp 100 juta – Rp 1 miliar
- ≥ 1 tahun dormant → saldo > Rp 1 miliar
- ≥ 30 tahun dormant → semua nominal

### 6. Penyesuaian Menu Aktivasi pada Aplikasi BDS
- Menu diubah menjadi: **"Aktivasi Rekening Tidak Aktif/Dormant"**
- Nasabah wajib mengajukan permohonan aktivasi melalui Bank

### 7. Penutupan Otomatis Rekening Saldo Nihil
- Rekening saldo nihil selama **30 hari kalender** ditutup otomatis (sudah sesuai POJK ≤ 6 bulan)
- Berlaku untuk **semua jenis Rekening Giro dan Tabungan**, kecuali rekening afiliasi pembiayaan atau rekening jaminan pembiayaan

---

## Ketentuan Peralihan

Pada saat implementasi dilakukan, rekening existing disesuaikan sebagai berikut:

| Kondisi Existing | Status Baru |
|---|---|
| Rekening dormant/pasif dengan kode produk yang termasuk kategori Aktif (lihat daftar kode produk) | → **Rekening Aktif** |
| Rekening pasif/dormant yang **tidak** termasuk kategori kode produk Aktif | → **Rekening Tidak Aktif** (DLA di-setting 361 hari) |
| Rekening Tidak Aktif yang tidak mengajukan pengaktifan kembali hingga hari ke-1.440 | → **Rekening Dormant** (hari ke-1.801) |

---

## Persetujuan

| Peran | Nama | Tanggal |
|---|---|---|
| Change Initiator (DDJ) | Ardian Faturahman | 12 Des 2025 |
| Change Initiator (DDK) | Dara Fitri Januarti | 16 Des 2025 |
| Change Coordinator (DDJ) | Rois Muhammad Zaky | 12 Des 2025 |
| Change Coordinator (DDK) | Eva Arifah | 16 Des 2025 |
| Change Manager / Kadiv TI | *(belum diisi)* | — |

---

> **Catatan:** Dokumen ini merupakan ringkasan dari RFC No. D.2 v1.0 — Penyesuaian Status dan Sistem Pengelolaan Rekening, sebagai tindak lanjut POJK No. 24 Tahun 2025.