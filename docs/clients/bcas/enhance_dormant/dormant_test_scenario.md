# Test Scenarios — Enhancement Rekening Dormant BCAS

> Berdasarkan: `dormant_design_plan.md`
> Dibuat: 2026-03-29

---

## Konvensi

| Simbol | Arti |
|---|---|
| ✅ PASS | Hasil sesuai ekspektasi |
| ❌ FAIL | Hasil tidak sesuai |
| **Pre** | Precondition / setup data |
| **Act** | Aksi yang dilakukan |
| **Exp** | Expected result |

---

## GRUP 1 — Transisi Status (EOD Batch)

### TS-01 | AKTIF → TIDAK AKTIF (pakai default global)

**Pre:**
- `ParameterGlobal.TAKT_HARI = 360`
- Produk: `is_exc_tidakaktif = NULL`, `is_custom_tidak_aktif = NULL`
- Rekening A: `tgl_aktivitas_terakhir = SYSDATE - 361`, `status_rekening = 1 (AKTIF)`

**Act:** Jalankan EOD batch `update_dormant_account.py`

**Exp:**
- `status_rekening` rekening A berubah menjadi `7` (TIDAK AKTIF)
- Rekening masuk tabel `ibanktmp.rekening_tidak_aktif_candidate`
- Log di `ibankrep.rekening_tidak_aktif` terisi

---

### TS-02 | AKTIF tidak berubah jika tepat di batas threshold

**Pre:**
- `ParameterGlobal.TAKT_HARI = 360`
- Rekening A: `tgl_aktivitas_terakhir = SYSDATE - 360`, `status_rekening = 1`

**Act:** Jalankan EOD batch

**Exp:**
- `status_rekening` rekening A **tetap** `1` (AKTIF)
- Tidak masuk kandidat tidak aktif

---

### TS-03 | TIDAK AKTIF → DORMANT (pakai default global)

**Pre:**
- `ParameterGlobal.DORM_HARI = 1800`
- Produk: `is_tidak_dormant = NULL`, `is_custom_dormant = NULL`
- Rekening A: `tgl_aktivitas_terakhir = SYSDATE - 1801`, `status_rekening = 7 (TIDAK AKTIF)`

**Act:** Jalankan EOD batch

**Exp:**
- `status_rekening` berubah menjadi `2` (DORMANT)
- Rekening masuk tabel `ibanktmp.rekening_dorman_candidate`
- Log di `ibankrep.rekening_dorman` terisi dengan `tgl_aktivitas_terakhir`

---

### TS-04 | AKTIF → TIDAK AKTIF menggunakan override produk

**Pre:**
- `ParameterGlobal.TAKT_HARI = 360`
- Produk: `is_custom_tidak_aktif = 'T'`, `jumlah_hari_jadi_tidak_aktif = 180`
- Rekening A: `tgl_aktivitas_terakhir = SYSDATE - 181`, `status_rekening = 1`

**Act:** Jalankan EOD batch

**Exp:**
- `status_rekening` berubah menjadi `7` (TIDAK AKTIF) — threshold produk (180) dipakai, bukan global (360)

---

### TS-05 | AKTIF tidak berubah jika is_custom_tidak_aktif = T tapi threshold belum terlewati

**Pre:**
- `ParameterGlobal.TAKT_HARI = 360`
- Produk: `is_custom_tidak_aktif = 'T'`, `jumlah_hari_jadi_tidak_aktif = 180`
- Rekening A: `tgl_aktivitas_terakhir = SYSDATE - 361`, `status_rekening = 1`
  *(sudah lewat global 360, tapi belum lewat produk 180 — mustahil secara logika, ini edge case)*

> Kasus ini tidak mungkin terjadi: jika `is_custom_tidak_aktif = 'T'`, hanya threshold produk yang dipakai.
> Rekening dengan hari = 361 dan threshold produk = 180 → **TETAP jadi TIDAK AKTIF**.

---

### TS-06 | TIDAK AKTIF → DORMANT menggunakan override produk

**Pre:**
- `ParameterGlobal.DORM_HARI = 1800`
- Produk: `is_custom_dormant = 'T'`, `jumlah_hari_jadi_dormant = 730`
- Rekening A: `tgl_aktivitas_terakhir = SYSDATE - 731`, `status_rekening = 7`

**Act:** Jalankan EOD batch

**Exp:**
- `status_rekening` berubah menjadi `2` (DORMANT) — threshold produk (730) dipakai

---

## GRUP 2 — Pengecualian (Exclusion Flags)

### TS-07 | Rekening tidak masuk TIDAK AKTIF jika is_exc_tidakaktif = T

**Pre:**
- Produk: `is_exc_tidakaktif = 'T'`
- Rekening A: `tgl_aktivitas_terakhir = SYSDATE - 500`, `status_rekening = 1`

**Act:** Jalankan EOD batch

**Exp:**
- `status_rekening` rekening A **tetap** `1` (AKTIF)
- Tidak masuk kandidat tidak aktif

---

### TS-08 | Rekening tidak masuk DORMANT jika produk.is_tidak_dormant = T

**Pre:**
- Produk: `is_tidak_dormant = 'T'`
- Rekening A: `tgl_aktivitas_terakhir = SYSDATE - 2000`, `status_rekening = 7`

**Act:** Jalankan EOD batch

**Exp:**
- `status_rekening` rekening A **tetap** `7` (TIDAK AKTIF)
- Tidak masuk kandidat dormant

---

### TS-09 | Rekening tidak masuk DORMANT jika rekeningliabilitas.is_tidak_dormant = T

**Pre:**
- Produk: `is_tidak_dormant = NULL` (tidak ada pengecualian di level produk)
- `rekeningliabilitas.is_tidak_dormant = 'T'` (pengecualian di level rekening)
- Rekening A: `tgl_aktivitas_terakhir = SYSDATE - 2000`, `status_rekening = 7`

**Act:** Jalankan EOD batch

**Exp:**
- `status_rekening` rekening A **tetap** `7` (TIDAK AKTIF)
- Pengecualian per-rekening tetap dihormati

---

### TS-10 | is_exc_tidakaktif = T tidak memblokir fase DORMANT

**Pre:**
- Produk: `is_exc_tidakaktif = 'T'`, `is_tidak_dormant = NULL`
- Rekening A: `tgl_aktivitas_terakhir = SYSDATE - 2000`, `status_rekening = 7 (TIDAK AKTIF)`

> Rekening ini sudah masuk TIDAK AKTIF sebelum is_exc_tidakaktif diset.

**Act:** Jalankan EOD batch

**Exp:**
- `status_rekening` berubah menjadi `2` (DORMANT)
- `is_exc_tidakaktif` hanya memblokir transisi ke TIDAK AKTIF, bukan ke DORMANT

---

## GRUP 3 — Tutup Otomatis Saldo Nol

### TS-11 | Tutup otomatis dari AKTIF (saldo nol + threshold tercapai)

**Pre:**
- `ParameterGlobal.TUTUP_NOL_HARI = 730`
- Produk: `is_exc_tutupnol = NULL`, `is_custom_tutup_oto = NULL`
- Rekening A: `status_rekening = 1 (AKTIF)`, saldo = 0, `DailyBalanceRekening: last balance_date = SYSDATE - 731, balance = 0`

**Act:** Jalankan EOD batch `saving_auto_close.py`

**Exp:**
- `status_rekening` berubah menjadi `3` (TUTUP)
- Di `ibanktmp.autoclose_zerobalance_candidate`:
  - `tgl_saldo_nol` terisi = `SYSDATE - 731` (dari DailyBalanceRekening)
  - `param_hari_tutup_oto` terisi = `730` (dari ParameterGlobal)
- Di `ibankrep.rekening_tutupotomatis`:
  - `tgl_saldo_nol` dan `param_hari_tutup_oto` ikut tersalin dari staging

---

### TS-12 | Tutup otomatis dari TIDAK AKTIF

**Pre:**
- `ParameterGlobal.TUTUP_NOL_HARI = 730`
- Rekening A: `status_rekening = 7 (TIDAK AKTIF)`, saldo = 0, `DailyBalanceRekening: last balance_date = SYSDATE - 731, balance = 0`

**Act:** Jalankan EOD batch

**Exp:**
- `status_rekening` berubah menjadi `3` (TUTUP)
- Tutup otomatis tidak melihat status aktif/tidak aktif/dormant

---

### TS-13 | Tutup otomatis dari DORMANT

**Pre:**
- Rekening A: `status_rekening = 2 (DORMANT)`, saldo = 0, `DailyBalanceRekening: last balance_date = SYSDATE - 731, balance = 0`

**Act:** Jalankan EOD batch

**Exp:**
- `status_rekening` berubah menjadi `3` (TUTUP)

---

### TS-14 | Tutup otomatis tidak terjadi jika is_exc_tutupnol = T

**Pre:**
- Produk: `is_exc_tutupnol = 'T'`
- Rekening A: saldo = 0, DailyBalanceRekening: last balance_date = SYSDATE - 1000, balance = 0

**Act:** Jalankan EOD batch

**Exp:**
- `status_rekening` **tidak berubah**
- Rekening tidak masuk kandidat tutup otomatis

---

### TS-15 | Tutup otomatis menggunakan threshold override produk

**Pre:**
- `ParameterGlobal.TUTUP_NOL_HARI = 730`
- Produk: `is_custom_tutup_oto = 'T'`, `jumlah_hari_tutup_otomatis = 365`
- Rekening A: saldo = 0, DailyBalanceRekening: last balance_date = SYSDATE - 366, balance = 0

**Act:** Jalankan EOD batch

**Exp:**
- `status_rekening` berubah menjadi `3` (TUTUP) — threshold produk (365) dipakai

---

### TS-16 | Tutup otomatis tidak terjadi jika saldo belum nol cukup lama

**Pre:**
- `ParameterGlobal.TUTUP_NOL_HARI = 730`
- Rekening A: saldo = 0, DailyBalanceRekening: last balance_date = SYSDATE - 729, balance = 0

**Act:** Jalankan EOD batch

**Exp:**
- `status_rekening` **tidak berubah** — threshold belum terlewati

---

### TS-16b | param_hari_tutup_oto di report menggunakan override produk (bukan global)

**Pre:**
- `ParameterGlobal.TUTUP_NOL_HARI = 730`
- Produk: `is_custom_tutup_oto = 'T'`, `jumlah_hari_tutup_otomatis = 365`
- Rekening A: saldo = 0, DailyBalanceRekening: last balance_date = SYSDATE - 400, balance = 0

**Act:** Jalankan EOD batch

**Exp:**
- `status_rekening` berubah menjadi `3` (TUTUP)
- Di `rekening_tutupotomatis`: `param_hari_tutup_oto = 365` (bukan 730)
- Di `rekening_tutupotomatis`: `tgl_saldo_nol = SYSDATE - 400`

---

### TS-16c | tgl_saldo_nol di report mencatat tanggal saldo nol terbaru (bukan yang terlama)

**Pre:**
- Rekening A memiliki histori DailyBalanceRekening:
  - `SYSDATE - 800`: balance = 0
  - `SYSDATE - 600`: balance = 500 (sempat naik)
  - `SYSDATE - 400`: balance = 0 (nol lagi, tidak ada transaksi sejak itu)

**Act:** Jalankan EOD batch

**Exp:**
- `tgl_saldo_nol` di report = `SYSDATE - 400` (tanggal saldo nol yang paling baru)
- Bukan `SYSDATE - 800` (saldo nol yang lama sudah tidak relevan karena sempat naik)

---

## GRUP 4 — Aktivitas Non-Finansial

### TS-17 | Aktivitas non-fin (cek saldo) dicatat di rekeningaktivitasnonfin

**Pre:**
- Nasabah dengan rekening A melakukan cek saldo via Mobile Banking

**Act:** Request cek saldo diproses oleh sistem

**Exp:**
- Baris baru di `rekeningaktivitasnonfin`:
  - `nomor_rekening = rekening_A`
  - `kode_aktivitas = 'CEK_SALDO'`
  - `kode_channel = 'MOBILE'`
  - `tanggal_aktivitas` terisi dengan timestamp saat ini

---

### TS-18 | tgl_aktivitas_terakhir diupdate saat EOD (gabungan finansial + non-fin)

**Pre:**
- Rekening A: transaksi finansial terakhir = `SYSDATE - 100`
- Rekening A: cek saldo (non-fin) = `SYSDATE - 30`

**Act:** Jalankan EOD `update_account_lasttxdate.py`

**Exp:**
- `rekeningliabilitas.tgl_aktivitas_terakhir = SYSDATE - 30` (diambil yang terbaru)
- `rekeningliabilitas.tgl_transaksi_terakhir` **tidak berubah** (tetap `SYSDATE - 100`)

---

### TS-19 | tgl_aktivitas_terakhir menggunakan transaksi jika lebih baru dari non-fin

**Pre:**
- Rekening A: transaksi finansial = `SYSDATE - 5`
- Rekening A: cek saldo (non-fin) = `SYSDATE - 10`

**Act:** Jalankan EOD

**Exp:**
- `tgl_aktivitas_terakhir = SYSDATE - 5` (transaksi finansial lebih baru)

---

### TS-20 | Rekening tanpa aktivitas hari ini tidak diupdate tgl_aktivitas_terakhir

**Pre:**
- Rekening A tidak ada transaksi maupun non-fin hari ini

**Act:** Jalankan EOD

**Exp:**
- `tgl_aktivitas_terakhir` rekening A **tidak berubah** dari nilai sebelumnya

---

## GRUP 5 — Kode Transaksi Excluded

### TS-21 | Transaksi sistem (SD) tidak dihitung sebagai aktivitas nasabah

**Pre:**
- `parametertransaksiumum`: `kode_transaksi = 'SD'`, `is_exclude_aktivitas_nasabah = 'T'`
- Rekening A: `tgl_aktivitas_terakhir = SYSDATE - 400`
- Hari ini hanya ada transaksi bagi hasil (`kode_transaksi = 'SD'`) untuk rekening A

**Act:** Jalankan EOD `update_account_lasttxdate.py`

**Exp:**
- `tgl_aktivitas_terakhir` rekening A **tidak berubah** (tetap `SYSDATE - 400`)
- Transaksi SD tidak dianggap aktivitas nasabah

---

### TS-22 | Transaksi nasabah (TT = Tarik Tunai) dihitung sebagai aktivitas

**Pre:**
- Rekening A: `tgl_aktivitas_terakhir = SYSDATE - 400`
- Hari ini ada transaksi tarik tunai (`kode_transaksi = 'TT'`, tidak ada di exclude list)

**Act:** Jalankan EOD

**Exp:**
- `tgl_aktivitas_terakhir` rekening A diupdate ke tanggal hari ini

---

### TS-23 | Semua kode excluded (SD, PD, SC, SCD, SDP, SDZ, SI) tidak mengupdate aktivitas

**Pre:**
- Rekening A: `tgl_aktivitas_terakhir = SYSDATE - 400`
- Hari ini ada transaksi SD, PD, SC sekaligus (semua sistem)

**Act:** Jalankan EOD

**Exp:**
- `tgl_aktivitas_terakhir` **tidak berubah**

---

## GRUP 6 — Reaktivasi Manual (Menu Cabang)

### TS-24 | Happy path: user Cabang reaktivasi rekening TIDAK AKTIF, diapprove

**Pre:**
- Rekening A: `status_rekening = 7 (TIDAK AKTIF)`

**Act:**
1. User Cabang buka menu "Ubah Rekening Tidak Aktif/Dormant"
2. Pilih rekening A, isi alasan reaktivasi
3. Submit
4. Supervisor buka antrian approval, approve

**Exp:**
- Setelah submit: rekening A berstatus PENDING APPROVAL (belum AKTIF)
- Setelah approve:
  - `status_rekening = 1 (AKTIF)`
  - `tgl_aktivitas_terakhir = SYSDATE` (di-reset ke tanggal approval)
  - Log reaktivasi tersimpan (user input, user approval, tanggal, alasan)

---

### TS-25 | Supervisor reject reaktivasi

**Pre:**
- Rekening A: `status_rekening = 7`, permintaan reaktivasi sudah disubmit (PENDING)

**Act:** Supervisor reject dengan alasan

**Exp:**
- `status_rekening` rekening A **tetap** `7` (TIDAK AKTIF)
- Log reject tersimpan (alasan, user approval, tanggal)
- Notifikasi reject dikirim ke user Cabang

---

### TS-26 | Happy path: reaktivasi rekening DORMANT

**Pre:**
- Rekening A: `status_rekening = 2 (DORMANT)`

**Act:** Sama seperti TS-24

**Exp:**
- Sama seperti TS-24 — alur tidak berbeda antara TIDAK AKTIF dan DORMANT

---

### TS-27 | Aktivitas nasabah tidak mengubah status rekening TIDAK AKTIF menjadi AKTIF

**Pre:**
- Rekening A: `status_rekening = 7 (TIDAK AKTIF)`

**Act:** Nasabah melakukan cek saldo via Mobile Banking

**Exp:**
- `status_rekening` rekening A **tetap** `7` (TIDAK AKTIF)
- Aktivitas tercatat di `rekeningaktivitasnonfin`
- `tgl_aktivitas_terakhir` akan diupdate saat EOD, tapi **status tidak berubah**

---

### TS-28 | Aktivitas nasabah tidak mengubah status rekening DORMANT menjadi AKTIF

**Pre:**
- Rekening A: `status_rekening = 2 (DORMANT)`

**Act:** Nasabah melakukan transaksi kredit (transfer masuk)

**Exp:**
- `status_rekening` rekening A **tetap** `2` (DORMANT)
- Transaksi diproses, `tgl_aktivitas_terakhir` diupdate saat EOD, tapi **status tidak berubah**

---

## GRUP 7 — EOM Biaya Rekening

### TS-29 | Biaya rekening TIDAK AKTIF dikenakan menggunakan default global

**Pre:**
- `ParameterGlobal.TAKT_BIAYA = 5000`
- Produk: `is_custom_tidak_aktif = NULL` (ikut global)
- Rekening A: `status_rekening = 7`, saldo = 100.000

**Act:** Jalankan EOM batch `admcost_dormant_process.py`

**Exp:**
- Transaksi biaya rekening tidak aktif sebesar Rp 5.000 terbuat untuk rekening A
- Saldo rekening A berkurang Rp 5.000

---

### TS-30 | Biaya rekening TIDAK AKTIF = 0 jika TAKT_BIAYA = 0

**Pre:**
- `ParameterGlobal.TAKT_BIAYA = 0`
- Rekening A: `status_rekening = 7`

**Act:** Jalankan EOM batch

**Exp:**
- Tidak ada transaksi biaya untuk rekening A
- Saldo tidak berubah

---

### TS-31 | Biaya rekening DORMANT menggunakan default global

**Pre:**
- `ParameterGlobal.DORM_BIAYA = 10000`
- Produk: `is_custom_dormant = NULL`
- Rekening A: `status_rekening = 2`, saldo = 50.000

**Act:** Jalankan EOM batch

**Exp:**
- Transaksi biaya rekening dormant sebesar Rp 10.000 terbuat (kode transaksi: `SCD`)

---

### TS-32 | Biaya rekening DORMANT menggunakan override produk

**Pre:**
- `ParameterGlobal.DORM_BIAYA = 10000`
- Produk: `is_custom_dormant = 'T'`, `is_biaya_rekening_dormant = 'T'`, `biaya_rekening_dormant = 25000`
- Rekening A: `status_rekening = 2`

**Act:** Jalankan EOM batch

**Exp:**
- Biaya yang dikenakan adalah Rp 25.000 (override produk), bukan Rp 10.000 (global)

---

### TS-33 | Biaya tidak dikenakan jika is_biaya_rekening_dormant = F (override produk)

**Pre:**
- Produk: `is_custom_dormant = 'T'`, `is_biaya_rekening_dormant = 'F'`
- Rekening A: `status_rekening = 2`

**Act:** Jalankan EOM batch

**Exp:**
- Tidak ada transaksi biaya dormant untuk rekening A

---

## GRUP 8 — Backward Compatibility

### TS-34 | Rekening lama tanpa tgl_aktivitas_terakhir menggunakan tgl_transaksi_terakhir sebagai fallback (migrasi)

**Pre:**
- Migrasi one-time sudah dijalankan: `tgl_aktivitas_terakhir = tgl_transaksi_terakhir`
- Rekening lama yang tidak punya aktivitas non-fin tetap punya nilai `tgl_aktivitas_terakhir`

**Act:** Verifikasi data setelah migrasi

**Exp:**
- Semua rekening yang `tgl_transaksi_terakhir IS NOT NULL` → `tgl_aktivitas_terakhir` terisi
- Rekening dengan `tgl_transaksi_terakhir IS NULL` → `tgl_aktivitas_terakhir IS NULL`

---

### TS-35 | ParameterGlobal lama (tanpa kode_group) tidak terganggu

**Pre:**
- Ada data `parameterglobal` existing dengan `kode_group = NULL`

**Act:** Baca ParameterGlobal via aplikasi / query

**Exp:**
- Data lama tetap bisa dibaca normal
- Kolom `kode_group = NULL` tidak menyebabkan error

---

### TS-36 | Produk lama (semua flag baru = NULL) ikut ParameterGlobal

**Pre:**
- Produk lama: semua kolom baru (`is_custom_*`, `is_exc_*`) = NULL
- Rekening A dengan produk lama: `tgl_aktivitas_terakhir = SYSDATE - 400`

**Act:** Jalankan EOD batch

**Exp:**
- Rekening A diproses menggunakan nilai default ParameterGlobal
- `TAKT_HARI = 360` → rekening A masuk TIDAK AKTIF (400 > 360)

---

## GRUP 9 — Urutan EOD (Step 1 → 2 → 3)

### TS-37 | Step 2 menggunakan tgl_aktivitas_terakhir yang sudah diupdate Step 1

**Pre:**
- Rekening A: sebelum EOD `tgl_aktivitas_terakhir = SYSDATE - 400`, ada cek saldo (non-fin) hari ini

**Act:** Jalankan Step 1 lalu Step 2

**Exp:**
- Setelah Step 1: `tgl_aktivitas_terakhir = SYSDATE`
- Step 2 membaca nilai terbaru → rekening A **tidak** masuk TIDAK AKTIF (0 hari, bukan 400)

---

### TS-38 | Step 3 tidak menutup rekening yang baru saja direaktivasi hari ini

**Pre:**
- Rekening A: direaktivasi hari ini → `status_rekening = 1`, `tgl_aktivitas_terakhir = SYSDATE`, saldo = 0

**Act:** Jalankan Step 3 (tutup otomatis)

**Exp:**
- Rekening A **tidak ditutup** — saldo baru saja nol, belum melewati threshold `TUTUP_NOL_HARI`

---

*Dibuat: 2026-03-29. Update setiap ada perubahan signifikan pada Design Plan.*
