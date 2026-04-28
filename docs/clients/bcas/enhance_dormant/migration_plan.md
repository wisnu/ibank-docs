# Migration Plan — Enhance Dormant BCAS

**Tanggal referensi go-live :** 15 November 2024
**Tanggal eksekusi migrasi  :** 8 April 2025
**Threshold tidak aktif     :** 360 hari
**Scope rekening            :** Tabungan (T) dan Giro (G), status bukan TUTUP (≠ 3)

---

## Ringkasan Fase

| Fase | Nama | Aksi Utama | Output |
|------|------|------------|--------|
| 1 | Inisialisasi Baseline Aktivitas | Insert aktivitas historis, update `tgl_aktivitas_terakhir` & `tgl_transaksi_terakhir` | Data aktivitas rekening siap dihitung |
| 2 | Sinkronisasi Transaksi Pasca Go-Live | Update `tgl_transaksi_terakhir` dari histori trx > 15 Nov 2024 | Rekening aktif tetap AKTIF dengan tanggal akurat |
| 3 | Inisiasi Saldo Nol sesuai tgl implementasi | Insert transaksi mutasi 0 untuk rekening saldo < 0.01 | Data dasar tutup otomatis tersedia |
| 4 | Penandaan Rekening TIDAK AKTIF | Update status = 7, insert laporan & audit trail | Rekening ≥ 360 hari tidak aktif berubah ke TIDAK AKTIF dan masuk ke laporan sesuai kalkulasi 361 hari dari tgl aktivitas terakhir |
| 5 | Reaktivasi Rekening | Update status = 1, insert laporan & audit trail | Rekening DORMANT dengan aktivitas baru kembali AKTIF |

---

## Fase 1 — Inisialisasi Baseline Aktivitas

Tujuan: mengisi data aktivitas historis agar sistem dapat menghitung status dormant secara konsisten sejak go-live.

| # | Aksi | Target | Keterangan |
|---|------|--------|------------|
| 1.1 | INSERT `rekeningaktivitasnonfin` | Semua rekening aktif T/G | Kode aktivitas `REGISTER_REKENING` pada `tanggal_buka` |
| 1.2 | INSERT `rekeningaktivitasnonfin` | Rekening dibuka ≤ 15 Nov 2024 | Kode aktivitas `INIT_AKTIVITAS` pada 15 Nov 2024 |
| 1.3 | UPDATE `rekeningliabilitas.tgl_aktivitas_nonfin_terakhir` | Semua rekening T/G aktif | MAX dari data `rekeningaktivitasnonfin` |
| 1.4 | CREATE TABLE `ibanktmp.rekeningaktivitasfin_maxdate` | — | Max `tanggal_transaksi` dari `histdetiltransaksi`, exclude transaksi non-aktivitas nasabah |
| 1.5 | MERGE → UPDATE `rekeningliabilitas.tgl_transaksi_terakhir` | Rekening T/G aktif | Dari tabel temp di 1.4 |
| 1.6 | UPDATE `rekeningliabilitas.tgl_aktivitas_terakhir` | Semua rekening T/G aktif | `GREATEST(tgl_transaksi_terakhir, tgl_aktivitas_nonfin_terakhir)` |
| 1.7 | UPDATE `rekeningliabilitas.tgl_aktivitas_terakhir` → 15 Nov 2024 | Rekening dibuka < 15 Nov 2024, keduanya < 15 Nov 2024 | Normalisasi baseline untuk rekening lama tanpa aktivitas baru |

---

## Fase 2 — Sinkronisasi Rekening dengan Transaksi Pasca Go-Live

Tujuan: memastikan rekening yang bertransaksi setelah 15 Nov 2024 memiliki `tgl_transaksi_terakhir` yang akurat. Status tidak diubah (tetap AKTIF).

| # | Aksi | Target | Keterangan |
|---|------|--------|------------|
| 2.1 | UPDATE `rekeningliabilitas.tgl_transaksi_terakhir` | Rekening dengan trx > 15 Nov 2024 | Dari `histtransaksi`/`histdetiltransaksi`, exclude transaksi non-aktivitas nasabah |

---

## Fase 3 — Migrasi Saldo Nol

Tujuan: mencatat mutasi saldo nol (nilai 0) untuk rekening dengan saldo < 0.01 per 8 April 2025 sebagai dasar proses tutup otomatis.

| # | Aksi | Target | Keterangan |
|---|------|--------|------------|
| 3.1 | Generate `id_transaksi` | — | `seq_transaksi.NEXTVAL` (hasil: `70526498`) |
| 3.2 | CREATE TABLE `ibanktmp.mig_saldo_nol_candidate` | Rekening T/G, saldo < 0.01 dan > -1, belum tutup | Termasuk `tgl_saldo_nol` dari `DailyBalanceRekening` |
| 3.3 | INSERT `ibankcore.transaksi` | 1 header transaksi | Kode `MIGSN`, tanggal 8 Apr 2025 |
| 3.4 | INSERT `ibankcore.detiltransaksi` | Satu baris per rekening candidate | Nilai mutasi 0, keterangan `Migrasi Saldo Nol` |

---

## Fase 4 — Penandaan Rekening TIDAK AKTIF

Tujuan: mengidentifikasi dan mengubah status rekening yang tidak aktif selama ≥ 360 hari menjadi TIDAK AKTIF (status 7).

| # | Aksi | Target | Keterangan |
|---|------|--------|------------|
| 4.1 | CREATE TABLE `ibanktmp.mig_tidak_aktif_candidate` | Rekening T/G aktif dengan `tgl_aktivitas_terakhir` < 13 Apr 2024 | Snapshot sebelum update, termasuk `jumlah_hari_tidak_aktif` dan `tgl_mulai_tidak_aktif` |
| 4.2 | UPDATE `rekeningtransaksi.status_rekening` = 7 | Rekening di candidate table | Perubahan status ke TIDAK AKTIF |
| 4.3 | INSERT `ibankrep.rekening_tidak_aktif` | Semua rekening candidate | Laporan rekening tidak aktif hasil migrasi |
| 4.4 | INSERT `ibankcore.custchangehistori` | Semua rekening candidate | Audit trail perubahan status → TIDAK AKTIF |

---

## Fase 5 — Reaktivasi Rekening (Dormant/Tidak Aktif → Aktif)

Tujuan: mengaktifkan kembali rekening dormant atau tidak aktif yang memiliki aktivitas terbaru sejak 13 April 2025.

| # | Aksi | Target | Keterangan |
|---|------|--------|------------|
| 5.1 | CREATE TABLE `ibanktmp.mig_aktivasi_candidate` | Rekening status 2 (DORMANT) atau 7 (TIDAK AKTIF) dengan `tgl_aktivitas_terakhir` ≥ 13 Apr 2025 | — |
| 5.2 | UPDATE `rekeningtransaksi.status_rekening` = 1 | Rekening di candidate table | Perubahan status ke AKTIF |
| 5.3 | INSERT `ibankcore.custchangehistori` | Semua rekening candidate | Audit trail perubahan status → AKTIF |
| 5.4 | INSERT `ibankrep.rekening_aktivasi` | Semua rekening candidate | Laporan rekening yang diaktivasi kembali |

---

## Tabel Temporary yang Dibuat

| Tabel | Fase | Dapat di-drop setelah |
|-------|------|-----------------------|
| `ibanktmp.rekeningaktivitasfin_maxdate` | 1 | Selesai Fase 1 |
| `ibanktmp.mig_saldo_nol_candidate` | 3 | Selesai Fase 3 |
| `ibanktmp.mig_tidak_aktif_candidate` | 4 | Selesai Fase 4 |
| `ibanktmp.mig_aktivasi_candidate` | 5 | Selesai Fase 5 |

---

## Skenario Variasi Rekening (Validasi)

| nomor_rekening | tgl_buka | tgl_aktivitas_terakhir | status_rekening | Keterangan |
|---|---|---|---|---|
| 001-001 | 2020-01-01 | 2024-05-01 | 7 (TIDAK AKTIF) | [Fase 1+4] Tidak ada trx sejak sebelum Nov 2024 |
| 001-002 | 2023-06-15 | 2024-11-15 * | 7 (TIDAK AKTIF) | [Fase 1+4] tgl_akt di-set ke 15 Nov via INIT_AKTIVITAS |
| 001-003 | 2021-03-10 | 2025-01-15 | 1 (AKTIF) | [Fase 2] Ada trx setelah Nov 2024, tetap aktif |
| 001-004 | 2019-08-20 | 2025-03-20 | 1 (AKTIF) | [Fase 2] Trx terakhir < 360 hari, tetap aktif |
| 001-005 | 2022-11-01 | 2024-03-01 | 7 (TIDAK AKTIF) | [Fase 4] tgl_akt > 360 hari dari 8 Apr 2025 |
| 001-006 | 2024-11-20 | 2025-02-10 | 1 (AKTIF) | tgl_buka > 15 Nov 2024, tidak masuk Fase 1 |

\* `tgl_aktivitas_terakhir` di-set oleh proses INIT_AKTIVITAS (Fase 1.2)
