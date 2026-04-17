# Dasar Perhitungan Tanggal Aktivitas Nasabah
## Enhancement Rekening Dormant & Tidak Aktif

---

## Latar Belakang Masalah

Sistem saat ini menentukan status rekening (Aktif → Tidak Aktif → Dormant) berdasarkan **satu field**:

```
rekeningliabilitas.tgl_transaksi_terakhir
```

Field ini hanya mencatat tanggal transaksi finansial terakhir — yaitu mutasi yang mengubah saldo rekening.

---

## Apa yang Dimaksud "Transaksi" Saat Ini?

```mermaid
flowchart LR
    A([Nasabah]) --> B[Setor / Tarik Tunai]
    A --> C[Transfer]
    A --> D[Pembayaran Tagihan]
    A --> E[Autodebit]

    B --> F[(tgl_transaksi_terakhir\ndi-update)]
    C --> F
    D --> F
    E --> F

    style F fill:#d4edda,stroke:#28a745
```

> Hanya transaksi yang **mengubah saldo** yang tercatat.

---

## Yang Tidak Tercatat — Padahal Nasabah Aktif

```mermaid
flowchart LR
    A([Nasabah]) --> B[Cek Saldo via ATM]
    A --> C[Cek Mutasi via Mobile Banking]
    A --> D[Login Internet Banking]
    A --> E[Cetak Buku Tabungan]

    B --> F([❌ Tidak tercatat\nsebagai aktivitas])
    C --> F
    D --> F
    E --> F

    style F fill:#f8d7da,stroke:#dc3545
```

> Aktivitas-aktivitas ini **tidak mengubah saldo**, sehingga tidak masuk ke `tgl_transaksi_terakhir`.

---

## Dampak: Rekening Salah Masuk Dormant

```mermaid
sequenceDiagram
    participant N as Nasabah
    participant S as Sistem
    participant R as Rekening

    Note over R: Status: AKTIF
    Note over R: tgl_transaksi_terakhir: 1 Jan 2024

    N->>S: Cek saldo via ATM (Feb 2024)
    S-->>N: Tampilkan saldo
    Note over R: tgl_transaksi_terakhir: TIDAK berubah ❌

    N->>S: Cek mutasi via Mobile (Jun 2024)
    S-->>N: Tampilkan mutasi
    Note over R: tgl_transaksi_terakhir: TIDAK berubah ❌

    N->>S: Cetak buku tabungan (Nov 2024)
    S-->>N: Cetak selesai
    Note over R: tgl_transaksi_terakhir: TIDAK berubah ❌

    Note over S: EOD Jan 2025 — sudah 360 hari
    S->>R: ❌ Status → TIDAK AKTIF
    Note over R: Padahal nasabah rutin pakai rekening!
```

---

## Akar Masalah

| Aspek | Kondisi Saat Ini |
|---|---|
| **Yang dicatat** | Hanya transaksi finansial (debet/kredit) |
| **Yang tidak dicatat** | Cek saldo, cek mutasi, login, cetak buku |
| **Akibat** | Rekening bisa masuk status Tidak Aktif / Dormant meski nasabah masih aktif menggunakannya |
| **Potensi kerugian** | Nasabah komplain, biaya dormant dikenakan pada rekening yang sebenarnya aktif |

---

## Solusi: Perluas Definisi "Aktivitas"

Sistem tidak hanya mencatat transaksi finansial, tapi juga **aktivitas non-finansial** nasabah.

```mermaid
flowchart TD
    subgraph SEBELUM["❌ Sebelum — Hanya Finansial"]
        direction LR
        T1[Setor] --> D1[(tgl_transaksi_terakhir)]
        T2[Tarik] --> D1
        T3[Transfer] --> D1
    end

    subgraph SESUDAH["✅ Sesudah — Finansial + Non-Finansial"]
        direction LR
        T4[Setor] --> D2
        T5[Tarik] --> D2
        T6[Transfer] --> D2
        T7[Cek Saldo] --> D2
        T8[Cek Mutasi] --> D2
        T9[Cetak Buku] --> D2
        D2[(tgl_aktivitas_terakhir)]
    end

    style SEBELUM fill:#fff5f5,stroke:#dc3545
    style SESUDAH fill:#f0fff4,stroke:#28a745
```

---

## Dua Sumber Data Aktivitas

```mermaid
flowchart TD
    A([Rekening Nasabah]) --> B & C

    B["📊 Transaksi Finansial\n(existing)\n\ntabel: Transaksi + DetilTransaksi\nfield: tgl_transaksi_terakhir"]
    C["📋 Aktivitas Non-Finansial\n(baru)\n\ntabel: rekeningaktivitasnonfin\nkode: CEK_SALDO, CEK_MUTASI\n       CETAK_PASSBOOK, CETAK_SALDO"]

    B --> D["🔀 Gabungkan:\nambil yang paling baru"]
    C --> D

    D --> E[(tgl_aktivitas_terakhir\ndi rekeningliabilitas)]

    E --> F["🔍 Dasar Perhitungan\nStatus Rekening EOD"]

    style B fill:#fff3cd,stroke:#ffc107
    style C fill:#cce5ff,stroke:#004085
    style E fill:#d4edda,stroke:#28a745
    style F fill:#d1ecf1,stroke:#0c5460
```

---

## Mengapa Tidak Langsung Update `tgl_transaksi_terakhir`?

`tgl_transaksi_terakhir` adalah field **existing yang sudah banyak dipakai** oleh modul lain.

```mermaid
flowchart LR
    F[(tgl_transaksi_terakhir)]

    F --> A[Batch Dormant]
    F --> B[Laporan Rekening Dormant]
    F --> C[Modul Cabang - Info Rekening]
    F --> D[API Inquiry Rekening]
    F --> E[Laporan Audit]

    style F fill:#f8d7da,stroke:#dc3545
```

> Mengubah field ini berisiko **merusak modul lain** yang bergantung pada semantik lamanya.

---

## Solusi: Field Baru, Tidak Ubah yang Lama

| | `tgl_transaksi_terakhir` | `tgl_aktivitas_terakhir` |
|---|---|---|
| **Status** | Existing — tetap ada | Baru — ditambahkan |
| **Isi** | Hanya transaksi finansial | Finansial + Non-Finansial |
| **Diupdate oleh** | Proses posting transaksi | Proses EOD (batch harian) |
| **Dipakai untuk** | Modul-modul existing | Perhitungan status dormant/tidak aktif |
| **Risiko** | Tidak ada — tidak diubah | Tidak ada — field baru |

> **Prinsip:** *Minimal change* — tidak mengubah yang sudah berjalan, hanya menambahkan.

---

## Transaksi Sistem — Tidak Dihitung Sebagai Aktivitas Nasabah

Tidak semua transaksi finansial mencerminkan keaktifan nasabah. Transaksi otomatis oleh sistem **dikecualikan**:

```mermaid
flowchart TD
    T([Transaksi Masuk]) --> CHK{"Dibuat oleh\nnasabah sendiri?"}

    CHK -->|Ya| INC["✅ Dihitung sebagai\naktivitas nasabah\n\nContoh: setor, tarik, transfer"]
    CHK -->|Tidak| EXC["❌ Dikecualikan\n\nContoh:\nSD  — Bagi hasil tabungan\nPD  — Bagi hasil deposito\nSC  — Biaya administrasi\nSCD — Biaya rekening dormant\nSDP — Pajak bagi hasil\nSDZ — Zakat bagi hasil\nSI  — Auto transfer sistem"]

    style INC fill:#d4edda,stroke:#28a745
    style EXC fill:#f8d7da,stroke:#dc3545
```

> Dikonfigurasi via **Parameter Transaksi** — flag `is_exclude_aktivitas_nasabah = 'T'`

---

## Alur Lengkap — EOD Harian

```mermaid
sequenceDiagram
    participant TRX as Transaksi Nasabah
    participant NON as Aktivitas Non-Finansial
    participant EOD as Proses EOD
    participant DB as rekeningliabilitas

    Note over TRX,NON: Sepanjang hari H
    TRX->>DB: Transaksi diposting → catat di tabel Transaksi
    NON->>DB: Cek saldo/mutasi → INSERT rekeningaktivitasnonfin

    Note over EOD: EOD Step 1 — Update tgl_aktivitas_terakhir
    EOD->>DB: SELECT MAX(tanggal_transaksi) per rekening\n(filter: exclude transaksi sistem)
    EOD->>DB: SELECT MAX(tanggal_aktivitas) per rekening\nfrom rekeningaktivitasnonfin
    EOD->>DB: UPDATE tgl_aktivitas_terakhir =\nMAX(tgl_transaksi, tgl_nonfin)

    Note over EOD: EOD Step 2 — Batch Status Rekening
    EOD->>DB: Hitung hari = SYSDATE - tgl_aktivitas_terakhir
    EOD->>DB: Jika hari > threshold → update status rekening
```

---

## Mengapa Hanya Baca Transaksi Hari Ini (H)?

### Asumsi Dasar: EOD Berjalan Setiap Hari

Setiap EOD berjalan, sistem memperbarui `tgl_aktivitas_terakhir` di `rekeningliabilitas`. Nilai ini adalah **akumulasi yang sudah benar per akhir hari sebelumnya (H-1)**.

```mermaid
flowchart LR
    subgraph H1["EOD H-1 (kemarin)"]
        A1["Baca tabel Transaksi\n(H-1 masih ada sebelum WIPE)"] --> B1[(rekeningliabilitas\ntgl_aktivitas_terakhir\n= nilai terbaru s.d. H-1)]
    end

    subgraph H["EOD H (hari ini)"]
        A2["Baca tabel Transaksi\n(hari ini, sebelum WIPE)\n⚠️ HistTransaksi diabaikan"] --> B2{Lebih baru\ndari H-1?}
        B2 -->|Ya| C2[UPDATE\ntgl_aktivitas_terakhir]
        B2 -->|Tidak| D2[Biarkan —\nnilai H-1 tetap berlaku]
    end

    B1 -->|"nilai sudah tersimpan\ndi rekeningliabilitas"| H

    style H1 fill:#e8f4fd,stroke:#0c5460
    style H fill:#f0fff4,stroke:#28a745
```

> EOD hari ini membaca tabel **`Transaksi`** (transaksi hari berjalan yang belum di-WIPE) — bukan `HistTransaksi`. Transaksi lama sudah diwakili oleh nilai `tgl_aktivitas_terakhir` yang tersimpan dari EOD sebelumnya.

---

## Mengapa Ini Aman?

### Properti "Monotonically Non-Decreasing"

`tgl_aktivitas_terakhir` hanya bisa **sama atau lebih baru** — tidak pernah mundur.

```mermaid
flowchart LR
    A["tgl_aktivitas_terakhir\nH-1 = 15 Mar"] --> CHK{"Ada aktivitas\nhari ini?"}

    CHK -->|Ya, 10 Apr| UPDATE["UPDATE:\ntgl_aktivitas_terakhir = 10 Apr\n(lebih baru → pakai yang baru)"]
    CHK -->|Tidak ada| KEEP["KEEP:\ntgl_aktivitas_terakhir tetap 15 Mar\n(tidak ada yang lebih baru)"]

    style UPDATE fill:#d4edda,stroke:#28a745
    style KEEP fill:#fff3cd,stroke:#ffc107
```

| Kondisi | Aksi EOD | Hasil |
|---|---|---|
| Ada aktivitas hari ini | `UPDATE` jika lebih baru dari nilai tersimpan | `tgl_aktivitas_terakhir` = hari ini |
| Tidak ada aktivitas hari ini | Tidak ada `UPDATE` | `tgl_aktivitas_terakhir` tetap dari EOD sebelumnya |
| Nilai tersimpan sudah lebih baru | Tidak ada `UPDATE` | Nilai lama dipertahankan |

---

## Ilustrasi: 3 Hari Berturut-turut

```mermaid
sequenceDiagram
    participant EOD as EOD Harian
    participant TBL as rekeningliabilitas\n(tgl_aktivitas_terakhir)
    participant TRX as Transaksi\n(bukan HistTransaksi)
    participant HIS as HistTransaksi\n(diabaikan ❌)

    Note over TBL: Nilai awal: 1 Mar

    Note over EOD: EOD 10 Apr
    EOD->>TRX: SELECT MAX(tanggal_transaksi)\nWHERE tanggal_transaksi = 10 Apr
    TRX-->>EOD: 10 Apr (ada transaksi hari ini)
    Note over HIS: Tidak dibaca
    EOD->>TBL: 10 Apr > 1 Mar → UPDATE ke 10 Apr
    Note over TBL: Nilai: 10 Apr ✅

    Note over EOD: EOD 11 Apr
    EOD->>TRX: SELECT MAX(tanggal_transaksi)\nWHERE tanggal_transaksi = 11 Apr
    TRX-->>EOD: NULL (tidak ada aktivitas hari ini)
    Note over HIS: Tidak dibaca
    EOD->>TBL: Tidak ada yang lebih baru → SKIP
    Note over TBL: Nilai tetap: 10 Apr ✅

    Note over EOD: EOD 12 Apr
    EOD->>TRX: SELECT MAX(tanggal_transaksi)\nWHERE tanggal_transaksi = 12 Apr
    TRX-->>EOD: 12 Apr (ada transaksi hari ini)
    Note over HIS: Tidak dibaca
    EOD->>TBL: 12 Apr > 10 Apr → UPDATE ke 12 Apr
    Note over TBL: Nilai: 12 Apr ✅
```

> Meskipun 11 Apr tidak ada aktivitas, nilai 10 Apr tetap tersimpan dengan benar karena EOD H-1 sudah menjaganya. `HistTransaksi` **tidak perlu dibaca** — seluruh histori sudah terepresentasi oleh nilai `tgl_aktivitas_terakhir` yang tersimpan.

---

## Mengapa Tidak Scan Seluruh Histori Setiap Hari?

```mermaid
flowchart TD
    subgraph SALAH["❌ Pendekatan Recalculate — Scan Semua Histori"]
        S1["Scan tabel Transaksi +\ntabel HistTransaksi +\nrekeningaktivitasnonfin"] --> S2[MAX per rekening\ndari seluruh data]
        S2 --> S3[(Update tgl_aktivitas_terakhir)]
        S4["⚠️ Transaksi + HistTransaksi\nbisa ratusan juta baris\n→ performa sangat lambat\n→ EOD bisa timeout"]
    end

    subgraph BENAR["✅ Pendekatan Inkremental — Scan H Saja"]
        B1["Scan tabel Transaksi saja\nWHERE tanggal_transaksi = HARI INI\n(HistTransaksi diabaikan ✅)"] --> B2[MAX per rekening\nhanya dari data hari ini]
        B2 --> B3{Lebih baru\ndari tersimpan?}
        B3 -->|Ya| B4[(UPDATE\ntgl_aktivitas_terakhir)]
        B3 -->|Tidak| B5[Skip —\nnilai lama tetap valid]
        B6["✅ Query ringan\n→ EOD cepat\n→ Histori dijaga oleh\nnilai tersimpan di rekeningliabilitas"]
    end

    style SALAH fill:#fff5f5,stroke:#dc3545
    style BENAR fill:#f0fff4,stroke:#28a745
```

| | Scan Semua Histori | Scan H Saja (inkremental) |
|---|---|---|
| **Volume data dibaca** | Seluruh riwayat transaksi | Hanya transaksi hari ini |
| **Performa** | Lambat — tidak skalabel | Cepat — stabil meski data tumbuh |
| **Keakuratan** | Sama | Sama (karena nilai H-1 sudah benar) |
| **Ketergantungan** | Tidak ada | EOD wajib berjalan setiap hari |

---

## Syarat Agar Pendekatan Ini Valid

```mermaid
flowchart LR
    A["EOD berjalan\nsetiap hari\ntanpa skip"] --> B["tgl_aktivitas_terakhir\nselalu akurat\nper akhir hari"]
    B --> C["EOD hari ini\ncukup baca H saja"]

    A2["⚠️ Jika EOD skip\n1 hari"] --> B2["Aktivitas hari skip\ntidak tercatat"]
    B2 --> C2["tgl_aktivitas_terakhir\nmundur 1 hari"]

    style A fill:#d4edda,stroke:#28a745
    style B fill:#d4edda,stroke:#28a745
    style C fill:#d4edda,stroke:#28a745
    style A2 fill:#f8d7da,stroke:#dc3545
    style B2 fill:#f8d7da,stroke:#dc3545
    style C2 fill:#f8d7da,stroke:#dc3545
```

> **Kesimpulan:** Pendekatan inkremental benar selama EOD **tidak pernah dilewati**. Jika EOD pernah skip, perlu mekanisme koreksi (scan N hari ke belakang).

---

## Perbandingan Skenario: Sebelum vs Sesudah

### Skenario: Nasabah hanya cek saldo, tidak ada transaksi selama 2 tahun

```mermaid
gantt
    title Timeline Rekening Nasabah
    dateFormat YYYY-MM-DD
    axisFormat %b %Y

    section Aktivitas Nasabah
    Transaksi terakhir          :milestone, 2022-01-01, 0d
    Cek saldo rutin tiap bulan  :active, 2022-02-01, 2024-01-01

    section Sistem Lama
    Hitung dari tgl_transaksi_terakhir : crit, 2022-01-01, 2023-01-01
    ❌ Rekening → TIDAK AKTIF  :milestone, crit, 2023-01-01, 0d

    section Sistem Baru
    Hitung dari tgl_aktivitas_terakhir : done, 2023-12-01, 2024-01-01
    ✅ Rekening tetap AKTIF     :milestone, done, 2024-01-01, 0d
```

| | Sistem Lama | Sistem Baru |
|---|---|---|
| **Dasar hitung** | `tgl_transaksi_terakhir` = 1 Jan 2022 | `tgl_aktivitas_terakhir` = Des 2023 |
| **Hari dihitung** | 730 hari (> 360) | 30 hari (< 360) |
| **Status rekening** | ❌ TIDAK AKTIF (salah) | ✅ AKTIF (benar) |

---

## Ringkasan

| Poin | Penjelasan |
|---|---|
| **Masalah** | `tgl_transaksi_terakhir` hanya mencatat mutasi saldo — aktivitas non-finansial tidak terhitung |
| **Dampak** | Rekening bisa masuk Tidak Aktif / Dormant meski nasabah masih aktif menggunakan |
| **Solusi** | Tambah field baru `tgl_aktivitas_terakhir` yang menggabungkan transaksi nasabah + aktivitas non-finansial |
| **Mengapa field baru** | Menghindari perubahan pada field existing yang banyak dipakai modul lain |
| **Pengecualian** | Transaksi sistem otomatis (bagi hasil, biaya admin, dll.) tetap dikecualikan dari hitungan aktivitas |
| **Konfigurasi** | Daftar transaksi yang dikecualikan dapat dikelola via **Parameter Transaksi** — fleksibel |

---

## Posisi Update Ketiga Field

### Mekanisme Update (Kapan & Siapa)

| | `tgl_transaksi_terakhir` | `tgl_aktivitas_nonfin_terakhir` | `tgl_aktivitas_terakhir` |
|---|---|---|---|
| **Diupdate oleh** | Proses posting transaksi (real-time) | Insert ke `rekeningaktivitasnonfin` (real-time) | Proses EOD (batch harian) |
| **Waktu update** | Saat transaksi diposting | Saat nasabah melakukan aktivitas non-fin | Satu kali per hari, saat EOD |
| **Sumber nilai** | `tanggal_transaksi` dari tabel Transaksi | `tanggal_aktivitas` dari `rekeningaktivitasnonfin` | `MAX(tgl_transaksi_terakhir, tgl_aktivitas_nonfin_terakhir)` |

---

### Kondisi Update per Skenario EOD

| Kondisi | `tgl_transaksi_terakhir` | `tgl_aktivitas_nonfin_terakhir` | `tgl_aktivitas_terakhir` |
|---|---|---|---|
| Ada transaksi finansial nasabah hari ini | Sudah ter-`UPDATE` saat posting | Tidak berubah | `UPDATE` ke tanggal hari ini |
| Ada aktivitas non-finansial hari ini (cek saldo, cetak buku, dll.) | Tidak berubah | Sudah ter-`INSERT` saat aktivitas terjadi | `UPDATE` ke tanggal hari ini |
| Keduanya ada hari ini | Sudah ter-`UPDATE` saat posting | Sudah ter-`INSERT` | `UPDATE` ke yang paling baru |
| Tidak ada aktivitas apapun hari ini | Tidak ada `UPDATE` | Tidak ada `UPDATE` | Tidak ada `UPDATE` — nilai dari EOD sebelumnya dipertahankan |
| Hanya transaksi sistem hari ini (bagi hasil, biaya admin, dll.) | Tidak ada `UPDATE` *(dikecualikan)* | Tidak ada `UPDATE` | Tidak ada `UPDATE` — transaksi sistem tidak dihitung |

---

### Ringkasan Peran Masing-masing Field

| | `tgl_transaksi_terakhir` | `tgl_aktivitas_nonfin_terakhir` | `tgl_aktivitas_terakhir` |
|---|---|---|---|
| **Mencatat** | Transaksi finansial nasabah saja | Aktivitas non-finansial saja | Gabungan — ambil yang paling baru |
| **Acuan perhitungan status rekening** | Jika ada data di tabel transaksi dan parametertransaksi tiak exclude maka tgl_transaksi_terakhir di update  | Jika ada data di tabel rekeningaktivitasnonfin yang sama dengang tgl sistem update tgl_aktivitas_nonfin_terakhir | Jika Rekening tidak dalam posisi dormant / non aktif lihat tanggal yang paling besar antara tgl_transaksi_terakhir dan tgl_aktivitas_nonfin_terakhir  |
| **Given** | Ada baris di `DetilTransaksi` JOIN `Transaksi` untuk rekening ini dengan `status_otorisasi = 1` | Ada baris di `rekeningaktivitasnonfin` dengan `tanggal_aktivitas` = hari ini | `RekeningTransaksi.status_rekening = 1` (rekening aktif) dan salah satu dari `tgl_transaksi_terakhir` / `tgl_aktivitas_nonfin_terakhir` tidak NULL |
| **When** | `tipe_exclude_aktivitas_nasabah` di `parametertransaksiumum`: NULL atau tidak ada = ✅ hitung \| `'F'` = ✅ hitung \| `'D'` + `jenis_mutasi='C'` = ✅ kredit dihitung \| `'C'` + `jenis_mutasi='D'` = ✅ debit dihitung \| `'DC'` = ❌ exclude semua | `tanggal_aktivitas >= Today AND tanggal_aktivitas < Today + 1` | — (langsung kalkulasi setelah step 1 & 2 selesai) |
| **Then** | `tgl_transaksi_terakhir = Today` | `tgl_aktivitas_nonfin_terakhir = Today` | `tgl_aktivitas_terakhir = GREATEST(NVL(tgl_transaksi_terakhir, tgl_aktivitas_nonfin_terakhir), NVL(tgl_aktivitas_nonfin_terakhir, tgl_transaksi_terakhir))` — handles NULL di salah satu sisi |

---

### Kondisi Update — Bahasa Bisnis

| | `tgl_transaksi_terakhir` | `tgl_aktivitas_nonfin_terakhir` | `tgl_aktivitas_terakhir` |
|---|---|---|---|
| **Situasi awal** | Nasabah melakukan transaksi finansial hari ini (setor, tarik, transfer, bayar tagihan) dan transaksi sudah diotorisasi | Nasabah melakukan aktivitas non-finansial hari ini (cek saldo, cek mutasi, cetak buku tabungan) | Proses akhir hari (EOD) sedang berjalan dan rekening masih berstatus aktif |
| **Syarat berlaku** | Jenis transaksi tersebut tidak dikecualikan oleh pengaturan parameter — atau jika dikecualikan sebagian, setidaknya ada sisi (debit/kredit) yang tetap dihitung | Aktivitas tercatat pada tanggal yang sama dengan tanggal sistem hari ini | Minimal salah satu dari tanggal transaksi atau tanggal aktivitas non-finansial sudah terisi |
| **Hasilnya** | Tanggal transaksi terakhir rekening diperbarui menjadi hari ini | Tanggal aktivitas non-finansial terakhir rekening diperbarui menjadi hari ini | Tanggal aktivitas terakhir rekening diisi dengan tanggal yang paling baru di antara keduanya — jika salah satu kosong, dipakai yang ada |

---

### Detail per Field

#### `tgl_transaksi_terakhir`

**Situasi:** Nasabah melakukan transaksi finansial hari ini (setor, tarik, transfer, bayar tagihan) dan transaksi sudah diotorisasi.

**Data yang dilihat:**
- **Transaksi** — header transaksi, difilter yang sudah diotorisasi (`status_otorisasi = 1`)
- **DetilTransaksi** — detail mutasi per rekening, untuk melihat arah mutasi (debit/kredit)
- **Parametertransaksiumum** — pengaturan per kode transaksi (`tipe_exclude_aktivitas_nasabah`):
  - Tidak terdaftar / kosong → dihitung sebagai aktivitas nasabah
  - `F` → dihitung sebagai aktivitas nasabah
  - `D` → sisi debit dikecualikan, sisi kredit tetap dihitung
  - `C` → sisi kredit dikecualikan, sisi debit tetap dihitung
  - `DC` → seluruh transaksi dikecualikan

**Syarat:** Jenis transaksi tersebut tidak dikecualikan oleh pengaturan parameter — atau jika dikecualikan sebagian, setidaknya ada sisi (debit/kredit) yang tetap dihitung.

**Hasil:** Tanggal transaksi terakhir rekening diperbarui menjadi hari ini.

**Contoh kasus:**

> Rekening 001-123456 memiliki `tgl_transaksi_terakhir` = 1 Maret 2025. Pada 10 April 2025, nasabah melakukan transfer keluar (debit) sebesar Rp 500.000. Kode transaksi `TF` terdaftar di parameter dengan `tipe_exclude_aktivitas_nasabah = NULL`. Karena tidak dikecualikan, EOD 10 April memperbarui `tgl_transaksi_terakhir` menjadi **10 April 2025**.

> Rekening 001-654321 menerima bagi hasil (kode `SD`) pada 10 April 2025. Kode `SD` terdaftar dengan `tipe_exclude_aktivitas_nasabah = 'DC'`. Karena seluruh transaksi dikecualikan, `tgl_transaksi_terakhir` **tidak berubah**.

---

#### `tgl_aktivitas_nonfin_terakhir`

**Situasi:** Nasabah melakukan aktivitas non-finansial hari ini (cek saldo, cek mutasi, cetak buku tabungan).

**Data yang dilihat:**
- **RekeningAktivitasNonfin** — log aktivitas non-finansial per rekening, difilter `tanggal_aktivitas` yang jatuh pada hari ini

**Syarat:** Aktivitas tercatat pada tanggal yang sama dengan tanggal sistem hari ini.

**Hasil:** Tanggal aktivitas non-finansial terakhir rekening diperbarui menjadi hari ini.

**Contoh kasus:**

> Rekening 001-123456 memiliki `tgl_aktivitas_nonfin_terakhir` = 5 Januari 2025. Pada 10 April 2025, nasabah mengecek saldo via ATM — sistem mencatat satu baris di `RekeningAktivitasNonfin` dengan `tanggal_aktivitas = 10 April 2025`. EOD 10 April memperbarui `tgl_aktivitas_nonfin_terakhir` menjadi **10 April 2025**.

> Rekening 001-654321 tidak ada aktivitas non-finansial sama sekali pada 10 April 2025. Tidak ada baris baru di `RekeningAktivitasNonfin`, sehingga `tgl_aktivitas_nonfin_terakhir` **tidak berubah**.

---

#### `tgl_aktivitas_terakhir`

**Situasi:** Proses akhir hari (EOD) sedang berjalan dan rekening masih berstatus aktif.

**Data yang dilihat:**
- **RekeningTransaksi** — status rekening, difilter `status_rekening = 1` (rekening aktif)
- **rekeningliabilitas** — nilai `tgl_transaksi_terakhir` dan `tgl_aktivitas_nonfin_terakhir` yang sudah diperbarui di dua langkah sebelumnya

**Syarat:** Minimal salah satu dari tanggal transaksi atau tanggal aktivitas non-finansial sudah terisi.

**Hasil:** Tanggal aktivitas terakhir rekening diisi dengan tanggal yang paling baru di antara keduanya — jika salah satu kosong, dipakai yang ada.

**Contoh kasus:**

> Setelah EOD 10 April 2025: `tgl_transaksi_terakhir` = 10 April (ada transfer), `tgl_aktivitas_nonfin_terakhir` = 5 Januari (tidak ada aktivitas non-fin hari ini). Sistem mengambil yang paling baru → `tgl_aktivitas_terakhir` = **10 April 2025**.

> Setelah EOD 11 April 2025: tidak ada transaksi finansial maupun non-finansial. `tgl_transaksi_terakhir` tetap 10 April, `tgl_aktivitas_nonfin_terakhir` tetap 5 Januari. Tidak ada yang lebih baru → `tgl_aktivitas_terakhir` tetap **10 April 2025**.

> Rekening yang `tgl_transaksi_terakhir` kosong (belum pernah bertransaksi), namun `tgl_aktivitas_nonfin_terakhir` = 10 April (pernah cek saldo). Sistem memakai yang ada → `tgl_aktivitas_terakhir` = **10 April 2025**.

---

### Tabel Contoh Kasus Gabungan

`Tanggal Sistem` : 2 April 2026

`tgl_transaksi_terakhir` = 15 Jan 2026

`tgl_aktivitas_nonfin_terakhir` = 20 Feb 2026

`tgl_aktivitas_terakhir` = 20 Feb 2026

| # | Skenario hari ini (2 Apr 2026) | `tgl_transaksi_terakhir` | `tgl_aktivitas_nonfin_terakhir` | `tgl_aktivitas_terakhir` |
|---|---|---|---|---|
| 1 | Nasabah transfer (kode `TF`, tidak dikecualikan) | ~~15 Jan~~ → **02 Apr 2026** | 20 Feb 2026 | ~~20 Feb~~ → **02 Apr 2026** |
| 2 | Nasabah cek saldo via ATM | 15 Jan 2026 | ~~20 Feb~~ → **02 Apr 2026** | ~~20 Feb~~ → **02 Apr 2026** |
| 3 | Nasabah transfer sekaligus cek mutasi | ~~15 Jan~~ → **02 Apr 2026** | ~~20 Feb~~ → **02 Apr 2026** | ~~20 Feb~~ → **02 Apr 2026** |
| 4 | Hanya terima bagi hasil (kode `SD`, `tipe = DC`) | 15 Jan 2026 *(dikecualikan)* | 20 Feb 2026 | 20 Feb 2026 |
| 5 | Tidak ada aktivitas apapun | 15 Jan 2026 | 20 Feb 2026 | 20 Feb 2026 |
| 6 | Rekening baru — belum pernah bertransaksi, baru pertama cek saldo | *(NULL)* | NULL → **02 Apr 2026** | NULL → **02 Apr 2026** *(diambil dari nonfin)* |
| 7 | Terima autodebit (kode `AD`, `tipe = D`) + nasabah juga setor tunai (kredit) | ~~15 Jan~~ → **02 Apr 2026** *(kredit setor dihitung)* | 20 Feb 2026 | ~~20 Feb~~ → **02 Apr 2026** |
| 8a | Pindah Buku masuk — rekening **menerima** dana (kredit, kode `PB`, `tipe = DC`) | 15 Jan 2026 *(PB dikecualikan penuh, tidak berubah)* | 20 Feb 2026 | 20 Feb 2026 |
| 8b | Pindah Buku keluar — rekening **mengirim** dana (debit, kode `PB`, `tipe = DC`) | 15 Jan 2026 *(PB dikecualikan penuh, tidak berubah)* | 20 Feb 2026 | 20 Feb 2026 |


