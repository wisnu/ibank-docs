# iBank Documentation

Repositori dokumentasi untuk aplikasi core banking iBank.

## Deskripsi

Repositori ini berisi dokumentasi lengkap untuk sistem core banking iBank, termasuk panduan pengguna, dokumentasi API, arsitektur sistem, dan dokumentasi teknis lainnya.

## Struktur Repositori

```
ibank-docs/
├── docs/           # Direktori dokumentasi utama
├── mkdocs.yml      # Konfigurasi MkDocs
└── README.md       # File ini
```

## Teknologi

Dokumentasi ini dibangun menggunakan [MkDocs](https://www.mkdocs.org/), sebuah static site generator yang dirancang untuk dokumentasi proyek.

## Instalasi

### Prasyarat

- Python 3.7+
- pip

### Setup Lokal

1. Clone repositori ini:
   ```bash
   git clone <repository-url>
   cd ibank-docs
   ```

2. Install dependencies:
   ```bash
   pip install mkdocs
   ```

3. Jalankan development server:
   ```bash
   mkdocs serve
   ```

4. Buka browser dan akses `http://localhost:8000`

## Penggunaan

### Menjalankan Server Lokal

```bash
mkdocs serve
```

### Build Dokumentasi

```bash
mkdocs build
```

File hasil build akan tersimpan di direktori `site/`.

### Deploy

Dokumentasi dapat di-deploy menggunakan:

```bash
mkdocs gh-deploy
```

## Kontribusi

Untuk berkontribusi pada dokumentasi ini:

1. Fork repositori
2. Buat branch baru untuk perubahan Anda
3. Commit perubahan Anda
4. Push ke branch
5. Buat Pull Request

## Lisensi

[Sesuaikan dengan lisensi proyek Anda]

## Kontak

[Tambahkan informasi kontak atau link ke tim yang bertanggung jawab]
