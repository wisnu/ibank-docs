# memory.md — Context & Notes: Enhancement Rekening Dormant BCAS

> **Tujuan:** Konteks cepat untuk AI assistant agar tidak perlu baca ulang Design Plan dari awal setiap sesi.
> **Design Plan lengkap:** `dormant_design_plan.md` di folder ini.

---

## 1. RINGKASAN USE CASE

Enhancement sistem rekening dormant pada aplikasi **ibank2 BCAS — Modul Funding**.

**Masalah existing:** Hanya ada dua status rekening (Aktif / Dormant). Tidak ada status antara, dan aturan dormant dikonfigurasi per produk tanpa terpusat.

**Solusi:**
- Tambah status baru **Tidak Aktif** (`T`) sebagai fase antara Aktif dan Dormant.
- Konfigurasi terpusat via `ParameterGlobal`, dengan override opsional di level produk.
- Aktivitas non-finansial (cek saldo, inquiry, login) ikut dihitung untuk menunda dormant.

---

## 2. ALUR STATUS REKENING

```
AKTIF → TIDAK_AKTIF → DORMANT → TUTUP_OTOMATIS
          ↑___↗  (reaktivasi HANYA via menu Ubah Rekening Tidak Aktif/Dormant oleh user Cabang + approval)
```

> ⚠️ Aktivitas nasabah (transaksi/inquiry) **TIDAK** mengubah status kembali ke AKTIF.
> Reaktivasi hanya bisa dilakukan manual oleh user Cabang melalui menu khusus dengan approval.

| Status | Kode DB | Enum `rekeningliabilitas` | Threshold (default global) |
|---|---|---|---|
| Aktif | `A` | `1` | — |
| Tidak Aktif | `T` *(baru)* | `7` *(baru)* | `TAKT_HARI` hari tanpa aktivitas (default 360) |
| Dormant | `D` | `2` | `DORM_HARI` hari tanpa aktivitas (default 1800) |
| Tutup Otomatis | `C` | `3` | `TUTUP_NOL_HARI` hari sejak dormant (default 730) |

---

## 3. PERUBAHAN DATABASE (RINGKASAN)

### Tabel `parameterglobal` — ADD COLUMN + INSERT DATA
- **ADD COLUMN** `kode_group varchar(30) NULL` → untuk mengelompokkan parameter per fitur/modul
- **INSERT** 5 data baru dengan `kode_group = 'REKENING_DORMANT'`:

| `kode_parameter` | `nilai_parameter` | Keterangan |
|---|---|---|
| `TAKT_HARI` | 360 | Hari jadi tidak aktif |
| `DORM_HARI` | 1800 | Hari jadi dormant |
| `TUTUP_NOL_HARI` | 730 | Hari tutup otomatis |
| `TAKT_BIAYA` | 0 | Biaya rekening tidak aktif |
| `DORM_BIAYA` | 10000 | Biaya rekening dormant |

> Semua `kode_parameter` ≤ 15 karakter (sesuai `varchar(15)` di tabel).
> Field `kode_group` juga perlu ditambahkan ke PClass `ParameterGlobal` di `core.mdt` via DAF IDE.

### Tabel `produk` — ADD COLUMN + UBAH SEMANTIK

**3 flag eksplisit baru** (kontrol apakah produk override ParameterGlobal per fase):

| Field baru | Keterangan |
|---|---|
| `is_custom_tidak_aktif` | `T` = pakai threshold & biaya tidak aktif dari field produk |
| `is_custom_dormant` | `T` = pakai threshold & biaya dormant dari field produk |
| `is_custom_tutup_oto` | `T` = pakai threshold tutup otomatis dari field produk |

**2 flag pengecualian baru** (rekening produk ini dikecualikan dari fase tertentu):

| Field baru | Keterangan |
|---|---|
| `is_exc_tidakaktif` | `T` = rekening produk ini tidak akan pernah jadi tidak aktif |
| `is_exc_tutupnol` | `T` = rekening produk ini tidak akan ditutup otomatis saat saldo nol |

**3 field nilai baru** (override, hanya dibaca jika flag aktif):
- `jumlah_hari_jadi_dormant` — dibaca jika `is_custom_dormant = 'T'`
- `biaya_rekening_tidak_aktif` — dibaca jika `is_custom_tidak_aktif = 'T'`
- `is_biaya_rekening_tidak_aktif` — dibaca jika `is_custom_tidak_aktif = 'T'`

**3 field existing ubah semantik** (hanya dibaca jika flag masing-masing aktif):
- `jumlah_hari_jadi_tidak_aktif` → jika `is_custom_tidak_aktif = 'T'`
- `biaya_rekening_dormant`, `is_biaya_rekening_dormant` → jika `is_custom_dormant = 'T'`
- `jumlah_hari_tutup_otomatis` → jika `is_custom_tutup_oto = 'T'`

### Tabel `rekeningliabilitas` — ADD COLUMN
- `tgl_aktivitas_terakhir` timestamp → gabungan transaksi finansial + non-finansial

### Tabel `parametertransaksiumum` — ADD COLUMN
- `is_exclude_aktivitas_nasabah varchar(1)` → `T` = transaksi sistem EOD, tidak dihitung sebagai aktivitas nasabah

### Tabel baru `rekening_aktivitas_nonfin`
Log aktivitas non-finansial: `nomor_rekening`, `tanggal_aktivitas`, `kode_aktivitas`, `kode_channel`, dll.

### Penyesuaian Tabel Staging & Laporan
- **Staging Tabel Kandidat**: Menggunakan dua tabel terpisah `rekening_dorman_candidate` dan `rekening_tidak_aktif_candidate`.
- **Tabel Autoclose**: `autoclose_zerobalance_candidate` ditambahkan kolom `param_hari_tutup_oto`, `tgl_saldo_nol` beserta index referensinya.
- **Report Dormant**: Kolom `kode_status` dihilangkan dari insert `report.rekening_dorman`.

---

## 4. LOGIKA PRIORITAS NILAI (GLOBAL vs PRODUK)

Dikontrol via **flag eksplisit** per fase di tabel `produk`:

```
if is_custom_tidak_aktif = 'T' → baca field produk (jumlah_hari_jadi_tidak_aktif, biaya_rekening_tidak_aktif, ...)
else                           → baca ParameterGlobal: TAKT_HARI, TAKT_BIAYA

if is_custom_dormant = 'T'     → baca field produk (jumlah_hari_jadi_dormant, biaya_rekening_dormant, ...)
else                           → baca ParameterGlobal: DORM_HARI, DORM_BIAYA

if is_custom_tutup_oto = 'T'   → baca field produk (jumlah_hari_tutup_otomatis)
else                           → baca ParameterGlobal: TUTUP_NOL_HARI
```

Di kode Python (batch EOD):
```python
helper.GetObject('ParameterGlobal', 'TAKT_HARI').GetInt()   # → 180
helper.GetObject('ParameterGlobal', 'DORM_HARI').GetInt()   # → 365
helper.GetObject('ParameterGlobal', 'TUTUP_NOL_HARI').GetInt()  # → 730
helper.GetObject('ParameterGlobal', 'TAKT_BIAYA').Nilai_Parameter  # → 0.0
helper.GetObject('ParameterGlobal', 'DORM_BIAYA').Nilai_Parameter  # → 10000.0
```

---

## 5. EOD BATCH — URUTAN WAJIB

```
Step 1 → [BARU] update_account_lasttxdate.py
          Update tgl_trans_terakhir + tgl_aktivitas_terakhir
          (gabung: transaksi nasabah + rekening_aktivitas_nonfin)

Step 2 → [EXISTING, DIMODIFIKASI] update_dormant_account.py
          Ganti: tgl_trans_terakhir → tgl_aktivitas_terakhir
          Tambah: resolusi threshold dari ParameterGlobal (TAKT_HARI, DORM_HARI) jika produk tidak custom

Step 3 → [EXISTING, DIMODIFIKASI] saving_auto_close.py
          Tambah: fallback ke ParameterGlobal TUTUP_NOL_HARI jika is_custom_tutup_oto ≠ 'T'
```

> ⚠️ Step 2 dan 3 WAJIB setelah Step 1 selesai.

## 5b. EOM BATCH (End of Month) — BIAYA REKENING

```
Step 1 → [EXISTING, DIMODIFIKASI] admcost_dormant_process.py
          Tambah: biaya rekening TIDAK AKTIF (saat ini hanya DORMANT)
          Tambah: fallback ke ParameterGlobal (DORM_BIAYA, TAKT_BIAYA) jika produk tidak custom
          Kode transaksi: SCD (dormant), perlu kode baru untuk biaya tidak aktif
```

### Transaksi Sistem yang Di-exclude (tidak dihitung aktivitas nasabah)
`SD`, `PD`, `SC`, `SCD`, `SDP`, `SDZ`, `SI` → `is_exclude_aktivitas_nasabah = 'T'`

---

## 6. KODE AKTIVITAS NON-FINANSIAL

| `kode_aktivitas` | Channel |
|---|---|
| `CEK_SALDO` | ATM, MOBILE, IB, TELLER |
| `CEK_MUTASI` | ATM, MOBILE, IB, TELLER |
| `LOGIN_MB` | MOBILE |
| `LOGIN_IB` | IB |
| `LOGIN_ATM` | ATM |
| `TRX` | Semua (transaksi finansial) |

---

## 7. KEPUTUSAN DESAIN PENTING

| Topik | Keputusan |
|---|---|
| `tgl_trans_terakhir` | **Tidak diubah** — field baru `tgl_aktivitas_terakhir` ditambahkan |
| Update aktivitas non-fin | **Async EOD**, bukan real-time di `rekeningliabilitas` |
| Fail-safe exclude transaksi | Default `NULL`/`F` = **dihitung** aktivitas (aman untuk kode baru) |
| Field `kode_group` | varchar(30), **nullable** agar backward compatible dengan parameter lama |
| Nama field grup | **`kode_group`** (bukan `tag`) — konsisten dengan konvensi `kode_*` di codebase |

---

*Dibuat: 2026-03-23. Update terakhir: 2026-03-29. Selalu sync dengan `dormant_design_plan.md`.*
