# Checklist Aksi: Refactoring Struktur `docs/`

> Berdasarkan: [refactor_plan.md](refactor_plan.md)
>
> Status: **BELUM DIEKSEKUSI**

## Kondisi Saat Ini

```
docs/
├── bcas/
├── bjbs/
├── ibank/
│   ├── Financing/
│   ├── Funding/
│   └── GL/
├── index.md
└── robots.txt
```

## Target Struktur

```
docs/
├── public/
│   └── index.md
├── private/
├── clients/
│   ├── bjbs/
│   └── bcas/
├── ihsansolusi/
│   └── ibank/
│       ├── Financing/
│       ├── Funding/
│       └── GL/
├── index.md
└── robots.txt
```

---

## Step 1 — Persiapan

- [ ] **1.1** Backup state saat ini (commit git / backup folder)
- [ ] **1.2** Catat semua relative link di dalam markdown files yang perlu diupdate
  - [ ] Scan `docs/bjbs/` untuk internal links
  - [ ] Scan `docs/bcas/` untuk internal links
  - [ ] Scan `docs/ibank/` untuk internal links
  - [ ] Scan `docs/index.md` untuk internal links
- [ ] **1.3** Install plugin `mkdocs-redirects`
  ```bash
  pip install mkdocs-redirects
  ```

---

## Step 2 — Pindahkan Folder (Fisik)

- [ ] **2.1** Buat direktori baru
  - [ ] `mkdir -p docs/public`
  - [ ] `mkdir -p docs/private`
  - [ ] `mkdir -p docs/clients`
  - [ ] `mkdir -p docs/ihsansolusi`
- [ ] **2.2** Pindahkan folder client
  - [ ] `mv docs/bjbs docs/clients/bjbs`
  - [ ] `mv docs/bcas docs/clients/bcas`
- [ ] **2.3** Pindahkan folder iBank ke ihsansolusi
  - [ ] `mv docs/ibank docs/ihsansolusi/ibank`
- [ ] **2.4** Setup folder public
  - [ ] Buat `docs/public/index.md` (halaman utama publik)
- [ ] **2.5** Setup folder private
  - [ ] Buat `docs/private/index.md` (dokumentasi pribadi)
- [ ] **2.6** Verifikasi struktur baru sudah sesuai target
  ```bash
  tree docs/ -L 3
  ```

---

## Step 3 — Update `mkdocs.yml`

- [ ] **3.1** Update `nav` section dengan path baru
  - [ ] `ibank/` → `ihsansolusi/ibank/`
  - [ ] `bjbs/` → `clients/bjbs/`
  - [ ] `bcas/` → `clients/bcas/`
- [ ] **3.2** Tambahkan section `Public` dan `Private` di nav
- [ ] **3.3** Tambahkan legacy nav entries untuk backward compatibility
  ```yaml
  # BACKWARD COMPATIBILITY (URL LAMA)
  - BJBS (Legacy):
      - Home: clients/bjbs/index.md
  - BCAS (Legacy):
      - Home: clients/bcas/index.md
  ```
- [ ] **3.4** Tambahkan plugin `redirects` di `mkdocs.yml`
  ```yaml
  plugins:
    - redirects:
        redirect_maps:
          'bjbs/index.md': 'clients/bjbs/index.md'
          'bcas/index.md': 'clients/bcas/index.md'
          'ibank/index.md': 'ihsansolusi/ibank/index.md'
  ```

---

## Step 4 — Fix Relative Links di Markdown

- [ ] **4.1** Update semua relative links di `docs/clients/bjbs/`
- [ ] **4.2** Update semua relative links di `docs/clients/bcas/`
- [ ] **4.3** Update semua relative links di `docs/ihsansolusi/ibank/`
- [ ] **4.4** Update links di `docs/index.md` (root)
- [ ] **4.5** Update links di `docs/public/index.md`

---

## Step 5 — Persiapan Wiki.js

- [ ] **5.1** Dokumentasikan mapping permission Wiki.js

  | Path | Permission |
  |------|-----------|
  | `/public/*` | anonymous |
  | `/clients/bjbs/*` | group bjbs |
  | `/clients/bcas/*` | group bcas |
  | `/private/*` | personal / owner only |
  | `/ihsansolusi/*` | internal |

- [ ] **5.2** Pastikan struktur folder compatible dengan Wiki.js path-based permissions

---

## Step 6 — Verifikasi & Testing

- [ ] **6.1** Jalankan `mkdocs serve` dan cek halaman bisa diakses
  ```bash
  mkdocs serve
  ```
- [ ] **6.2** Test URL baru
  - [ ] `/clients/bjbs/` accessible
  - [ ] `/clients/bcas/` accessible
  - [ ] `/ihsansolusi/ibank/` accessible
  - [ ] `/public/` accessible
  - [ ] `/private/` accessible
- [ ] **6.3** Test URL lama (redirect)
  - [ ] `/bjbs/` → redirect ke `/clients/bjbs/`
  - [ ] `/bcas/` → redirect ke `/clients/bcas/`
  - [ ] `/ibank/` → redirect ke `/ihsansolusi/ibank/`
- [ ] **6.4** Cek semua internal links tidak broken
- [ ] **6.5** Cek images/assets masih ter-load dengan benar
- [ ] **6.6** Build final untuk validasi
  ```bash
  mkdocs build --strict
  ```

---

## Step 7 — Finalisasi

- [ ] **7.1** Commit perubahan ke git
- [ ] **7.2** Update `README.md` jika perlu
- [ ] **7.3** Update CI/CD pipeline (`.gitlab-ci.yml`) jika ada path-dependent config
- [ ] **7.4** Hapus legacy nav entries setelah periode transisi (optional, schedule)

---

## Catatan Penting

> ⚠️ **Relative Links**: Ini adalah bagian paling rawan error. Setelah memindahkan folder,
> kedalaman path berubah sehingga link relatif seperti `../guide.md` bisa rusak.
> Perlu di-scan dan di-fix satu per satu.

> ⚠️ **Assets/Images**: Jika ada gambar yang di-reference secara relatif,
> path-nya juga perlu diupdate sesuai lokasi baru.

> 💡 **Pembagian folder**:
> - `public/` → dokumentasi publik, bisa diakses siapa saja
> - `private/` → dokumentasi pribadi, hanya untuk pemilik
> - `clients/` → dokumentasi per klien (bjbs, bcas, dll)
> - `ihsansolusi/` → proyek internal perusahaan (ibank, core7, daf, dll)
> ✅ Sudah dikonfirmasi.
