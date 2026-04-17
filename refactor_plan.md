This repo is about documentation using mkdocs as tools. root document is directory `docs/` .  I want to enhance using `wiki.js` but still backward compatible with mkdocs. I want to reorganize docs/ directory so it will be more clear and easy to maintain. I want to refactor docs/ directory to have the following structure:

```docs/
├── public/
├── private/
├── clients/
│   ├── bjbs/
│   ├── bcas/
│   ├── ...
├── ihsansolusi/
│   ├── core7
│   ├── daf 
│   ├── ...
```

- `public/` directory will contain all the public documentation that can be accessed by anyone. This will include general information about the project, how to get started, and any other information that is relevant to the public.
- `private/` directory will contain all the private documentation that can only be accessed by authorized personnel. This will include sensitive information about the project, such as internal processes, confidential data, and any other information that should not be shared with the public.
- `clients/` directory will contain documentation specific to each client. Each client will have its own subdirectory where all the relevant documentation for that client will be stored. This will make it easier to manage and maintain documentation for each client separately.
- `ihsansolusi/` directory will contain documentation specific to the internal projects of IHSAN SOLUSI. Each project will have its own subdirectory where all the relevant documentation for that project will be stored. This will make it easier to manage and maintain documentation for each internal project separately.
This structure will help to keep the documentation organized and easy to navigate. It will also make it easier to maintain and update the documentation as needed. Additionally, it will allow for better access control, ensuring that sensitive information is only accessible to authorized personnel.

I want to use wiki.js but still maintain the existing mkdocs structure

I also have recommendation like this

```

🎯 Target Struktur Baru

Kita geser ke struktur yang lebih rapi:

docs/
  public/
  internal/
  clients/
    bjbs/
    bcas/

👉 Tapi URL lama seperti:

/bjbs/...
/bcas/...

tetap bisa diakses (backward compatible)

🧱 Step 1 — Pindahkan Folder (fisik)

Dari:

docs/
  bjbs/
  bcas/
  internal/

Menjadi:

docs/
  clients/
    bjbs/
    bcas/
  internal/
  public/   ← (baru)
🔁 Step 2 — Jaga URL lama di MkDocs (PENTING)

Di MkDocs, kamu bisa “alias” path via nav.

Contoh mkdocs.yml
docs_dir: docs

nav:
  - Public:
      - Home: public/index.md

  # URL BARU (rapi)
  - Clients:
      - BJBS:
          - Home: clients/bjbs/index.md
      - BCAS:
          - Home: clients/bcas/index.md

  - Internal:
      - Home: internal/index.md

  # BACKWARD COMPATIBILITY (URL LAMA)
  - BJBS (Legacy):
      - Home: clients/bjbs/index.md
  - BCAS (Legacy):
      - Home: clients/bcas/index.md

👉 Ini bikin:

/clients/bjbs/ → jalan
/bjbs/ → masih bisa diakses via nav (atau link lama)
🔗 Step 3 — Redirect URL lama (Best Practice 🔥)

Supaya clean, tambahkan redirect:

Pakai plugin:
pip install mkdocs-redirects
Config:
plugins:
  - redirects:
      redirect_maps:
        'bjbs/index.md': 'clients/bjbs/index.md'
        'bcas/index.md': 'clients/bcas/index.md'

👉 Jadi:

link lama otomatis redirect
SEO & bookmark aman
🔐 Step 4 — Mapping di Wiki.js

Di Wiki.js, kamu tinggal:

Path Permission
/public/* anonymous
/clients/bjbs/* group bjbs
/clients/bcas/* group bcas
/internal/* internal

👉 jauh lebih clean dibanding sebelumnya

🧠 Kenapa ini aman?
MkDocs tetap pakai file .md yang sama ✅
path lama tidak langsung hilang ✅
Wiki.js dapat struktur yang scalable ✅
⚠️ Hal kecil yang perlu dicek
1. Relative links di dalam markdown

Kalau sebelumnya:

[Link](../guide.md)

```
