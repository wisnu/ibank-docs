# Aturan Update `tgl_aktivitas_terakhir`

> Dokumen ini menjelaskan **kapan dan bagaimana** field `tgl_aktivitas_terakhir` di tabel
> `rekeningliabilitas` boleh diupdate, beserta alasan dan implikasinya.

---

## 1. Aturan Utama

> **`tgl_aktivitas_terakhir` hanya boleh diupdate oleh proses EOD jika `status_rekening = 1` (Aktif).**

Rekening dengan status **Tidak Aktif (7)** atau **Dormant (2)** tidak mengalami perubahan
`tgl_aktivitas_terakhir` meskipun ada aktivitas nasabah (transaksi atau inquiry) yang terjadi.

---

## 2. Mengapa Demikian?

### Masalah jika aturan ini tidak diterapkan — "Silent Reactivation"

Jika `tgl_aktivitas_terakhir` tetap diupdate tanpa memandang status, maka:

```
Rekening TIDAK AKTIF
  → Nasabah melakukan inquiry CEK_SALDO via ATM
  → EOD: tgl_aktivitas_terakhir diupdate ke hari ini
  → Batch dormant: hari_tidak_aktif = 0 → rekening kembali dianggap AKTIF
  → status_rekening berubah ke 1 (Aktif) tanpa sepengetahuan siapapun
```

Ini melanggar prinsip desain: **reaktivasi rekening tidak aktif / dormant wajib melalui
persetujuan manual** oleh user Cabang + approval Supervisor.

### Prinsip yang dijaga

| Prinsip | Penjelasan |
|---|---|
| **Reaktivasi hanya manual** | Satu-satunya jalan rekening TIDAK_AKTIF/DORMANT kembali ke AKTIF adalah melalui menu Ubah Rekening Tidak Aktif/Dormant, bukan dari aktivitas otomatis |
| **Aktivitas tetap tercatat** | Transaksi dan inquiry pada rekening TIDAK_AKTIF/DORMANT tetap masuk ke tabel `rekeningaktivitasnonfin` dan `transaksi` — hanya tidak mempengaruhi `tgl_aktivitas_terakhir` |
| **Fail-safe EOD** | Batch dormant membaca `tgl_aktivitas_terakhir` untuk menentukan status → jika field tidak berubah meski ada aktivitas, rekening tetap pada statusnya |

---

## 3. Implementasi di SQL EOD (update_account_lasttxdate)

Filter `status_rekening = 1` **wajib ada** di klausa `ON` atau `WHERE` proses EOD update:

```sql
-- Step EOD — Update tgl_aktivitas_terakhir
-- Hanya rekening dengan status_rekening = 1 (Aktif) yang diupdate
MERGE INTO ibcore.rekeningliabilitas rl
USING (
    -- ... query gabungan transaksi + non-finansial ...
) sg_final
ON (
    rl.nomor_rekening = sg_final.nomor_rekening
    AND rl.status_rekening = 1   -- ← WAJIB: hanya rekening Aktif
)
WHEN MATCHED THEN
  UPDATE SET
      rl.tgl_aktivitas_terakhir  = sg_final.tgl_aktivitas_final,
      rl.kode_aktivitas_terakhir = sg_final.kode_aktivitas_final;
```

> **Catatan migrasi awal:** Query `MIGRASI 1/3` s.d. `MIGRASI 3/3` di `executed_update_pg.sql`
> **tidak** dibatasi `status_rekening = 1`, karena tujuannya adalah mengisi baseline historis
> `tgl_aktivitas_terakhir` dari seluruh data transaksi yang pernah ada, terlepas dari status
> rekening saat migrasi dijalankan.

---

## 4. Tabel Use Case — Perilaku Update per Skenario

| # | Status Rekening Awal | Aktivitas Terjadi | Sumber Aktivitas | `tgl_aktivitas_terakhir` Diupdate? | Status Rekening Setelah EOD | Keterangan |
|---|---|---|---|---|---|---|
| 1 | **1 — Aktif** | Ada transaksi nasabah (Setor/Tarik/Transfer) | `transaksi` + `detiltransaksi` | **Ya** | 1 — Aktif | Normal — rekening aktif, ada transaksi |
| 2 | **1 — Aktif** | Ada inquiry (cek saldo ATM) | `rekeningaktivitasnonfin` | **Ya** | 1 — Aktif | Normal — inquiry dihitung sebagai aktivitas |
| 3 | **1 — Aktif** | Tidak ada aktivitas, hari < threshold TAKT_HARI | — | Tidak berubah | 1 — Aktif | Masih dalam batas, status tidak berubah |
| 4 | **1 — Aktif** | Tidak ada aktivitas, hari ≥ threshold TAKT_HARI | — | Tidak berubah | **7 — Tidak Aktif** | Batch dormant mengubah status karena melewati threshold |
| 5 | **1 — Aktif** | Ada transaksi sistem EOD (bagi hasil, biaya SC) | `transaksi` + `detiltransaksi` | **Tidak** (di-exclude oleh `tipe_exclude_aktivitas_nasabah = 'DC'`) | 1 — Aktif | Transaksi sistem tidak dihitung aktivitas nasabah |
| 6 | **7 — Tidak Aktif** | Ada transaksi nasabah (mis. Transfer Masuk / kredit) | `transaksi` + `detiltransaksi` | **Tidak** (`status_rekening ≠ 1`) | 7 — Tidak Aktif | Aktivitas ada, tapi tidak memicu perubahan `tgl_aktivitas_terakhir` |
| 7 | **7 — Tidak Aktif** | Ada inquiry cek saldo via ATM | `rekeningaktivitasnonfin` | **Tidak** (`status_rekening ≠ 1`) | 7 — Tidak Aktif | Inquiry tercatat di log, tapi tidak mengubah status |
| 8 | **7 — Tidak Aktif** | Tidak ada aktivitas | — | Tidak berubah | **2 — Dormant** *(jika hari ≥ threshold DORM_HARI)* | Batch dormant menaikkan status ke Dormant |
| 9 | **7 — Tidak Aktif** | Reaktivasi manual diapprove | Menu Cabang + Supervisor | **Ya** (reset ke `SYSDATE` saat approve) | **1 — Aktif** | Satu-satunya cara rekening TIDAK_AKTIF kembali ke Aktif |
| 10 | **2 — Dormant** | Ada transaksi kredit (diizinkan via `allow_rekening_dormant = 'C'`) | `transaksi` + `detiltransaksi` | **Tidak** (`status_rekening ≠ 1`) | 2 — Dormant | Transaksi mungkin diizinkan oleh konfigurasi, tapi `tgl_aktivitas_terakhir` tidak berubah |
| 11 | **2 — Dormant** | Ada inquiry via Teller (cetak saldo) | `rekeningaktivitasnonfin` | **Tidak** (`status_rekening ≠ 1`) | 2 — Dormant | Log tercatat, status tetap |
| 12 | **2 — Dormant** | Reaktivasi manual diapprove | Menu Cabang + Supervisor | **Ya** (reset ke `SYSDATE` saat approve) | **1 — Aktif** | Satu-satunya cara rekening DORMANT kembali ke Aktif |
| 13 | **2 — Dormant** | Tidak ada aktivitas, saldo = 0 ≥ threshold TUTUP_NOL_HARI | — | Tidak berubah | **3 — Tutup** | Tutup otomatis saldo nol, tidak tergantung aktivitas |

---

## 5. Tabel — Field yang Diupdate EOD per Status Rekening

### 5.1 Ringkasan per Status

| `status_rekening` | Label | `tgl_transaksi_terakhir` | `tgl_aktivitas_nonfin_terakhir` | `tgl_aktivitas_terakhir` |
|---|---|---|---|---|
| **1** | Aktif | **Diupdate** — tgl sistem aktif jika ada transaksi baru di `transaksi` nasabah (`tipe_exclude ≠ 'DC'`) | **Diupdate** — berdasarkan `tanggal_aktivitas` dari `rekeningaktivitasnonfin` sesuai tgl aktif sistem | **Diupdate** — GREATEST dari `tgl_transaksi_terakhir` dan `tgl_aktivitas_nonfin_terakhir` |
| **7** | Tidak Aktif | **Diupdate** — sama seperti status_rekening 1 | **Diupdate** — sama seperti status_rekening 1 | Tidak diupdate |
| **2** | Dormant | **Diupdate** — sama seperti status_rekening 1 | **Diupdate** — sama seperti status_rekening 1 | Tidak diupdate |
| **3** | Tutup | Tidak diupdate | Tidak diupdate | Tidak diupdate |

> `tgl_aktivitas_terakhir` adalah satu-satunya field yang diblok untuk status 7 dan 2 — karena
> field inilah yang menjadi **acuan batch dormant**. Field lainnya tetap diupdate sebagai data
> mentah dan audit trail.

### 5.2 Kondisi Tambahan saat `status_rekening = 1`

| Kondisi Aktivitas | `tgl_aktivitas_terakhir` Diupdate? | Keterangan |
|---|---|---|
| Ada transaksi nasabah (Setor/Tarik/Transfer) | **Ya** | Sumber: `transaksi` + `detiltransaksi` |
| Ada inquiry nasabah (cek saldo, cetak passbook) | **Ya** | Sumber: `rekeningaktivitasnonfin` |
| Hanya transaksi sistem EOD (SD, PD, SC, SCD, SDP, SDZ, SI) | **Tidak** | Di-exclude — `tipe_exclude_aktivitas_nasabah = 'DC'` |
| Tidak ada aktivitas sama sekali | **Tidak** | Field tetap menyimpan nilai terakhir |

---

## 6. Diagram Alur — Keputusan Update `tgl_aktivitas_terakhir`

```
EOD berjalan
    │
    ▼
Ada aktivitas hari ini?
(transaksi nasabah atau inquiry di rekeningaktivitasnonfin)
    │
    ├── Tidak → skip rekening ini
    │
    └── Ya
          │
          ▼
       tipe_exclude_aktivitas_nasabah = 'DC' ?
          │
          ├── Ya → skip (transaksi sistem, bukan aktivitas nasabah)
          │
          └── Tidak
                │
                ▼
             status_rekening = 1 (Aktif)?
                │
                ├── Tidak (7 atau 2) → SKIP
                │     └── tgl_aktivitas_terakhir TIDAK diupdate
                │         Log aktivitas tetap tersimpan di rekeningaktivitasnonfin / transaksi
                │
                └── Ya
                      │
                      ▼
                   UPDATE tgl_aktivitas_terakhir = MAX(aktivitas hari ini)
```

---

## 7. Kapan `tgl_aktivitas_terakhir` Bisa Berubah di Luar EOD?

| Proses | Update? | Nilai Baru |
|---|---|---|
| EOD `update_account_lasttxdate` | Ya, jika `status_rekening = 1` | MAX aktivitas hari berjalan |
| Reaktivasi manual (Approve di menu Cabang) | **Ya selalu** | `SYSDATE` saat approval |
| Migrasi awal (one-time) | Ya, semua rekening | MAX dari data historis transaksi |
| Tutup rekening | Tidak | — |
| Pembukaan rekening baru | Ya | `SYSDATE` saat pembukaan |

---

## 8. Catatan Terkait Tabel `rekeningaktivitasnonfin`

Log aktivitas non-finansial **tetap di-INSERT** meskipun `status_rekening ≠ 1`.
Pemisahan ini penting: log berfungsi sebagai **audit trail** (rekaman bahwa nasabah
masih ada aktivitas), sedangkan `tgl_aktivitas_terakhir` adalah **acuan teknis** proses dormant.

```
status_rekening = 7 (Tidak Aktif)
  → Nasabah cek saldo via ATM
  → INSERT rekeningaktivitasnonfin  ← tetap terjadi (audit trail)
  → EOD: tgl_aktivitas_terakhir     ← TIDAK diupdate
  → Batch dormant: membaca tgl_aktivitas_terakhir yang lama → status tetap 7
```

Dengan demikian, data di `rekeningaktivitasnonfin` bisa digunakan oleh petugas Cabang
sebagai bahan pertimbangan saat memproses reaktivasi manual.

---

*File ini dibuat: 2026-04-10. Terkait: `dormant_design_plan.md`, `executed_update_pg.sql`.*
