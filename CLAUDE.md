# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

Documentation hub for **iBank**, an Indonesian core banking system. The repo contains:
- MkDocs-based documentation site (primary purpose)
- Functional/technical specs (FSD, TSD, BRD, PRD) in Indonesian
- SQL scripts and migration files accompanying feature docs
- Source code for two applications embedded under `apps/`:
  - `ei-ledger-gql` — Go + GraphQL backend for the General Ledger module
  - `gl-module` — Next.js 16 frontend for the GL module

## Documentation Site

### Local Development

```bash
pip install mkdocs mkdocs-material
mkdocs serve          # serves at http://localhost:8000, hot-reload
mkdocs build          # builds static site to ./site/
```

### Docker

```bash
docker build -t ibank-docs .
docker run -p 8000:8000 ibank-docs
```

### Deployment

- **GitHub Pages**: auto-deployed via `.github/workflows/deploy.yml` on push to `dev` branch
- **GitLab Pages**: auto-deployed via `.gitlab-ci.yml`
- Manual: `mkdocs gh-deploy`

### Merging Docs

`merge.py` at the repo root merges multiple markdown files into a single document (used for dormant account docs):

```bash
python merge.py
```

## Documentation Structure

```
docs/
├── ibank/          # Core iBank feature docs (GL, Chart of Accounts, Reports)
├── bjbs/           # BJBS bank project (fingerscan, enhance-dormant)
├── bcas/           # BCAS bank project (enhance-dormant, saku-valas)
└── SAMPLE/         # Templates for FSD, TSD, C4 diagrams, Mermaid examples
```

Each feature folder typically contains: BRD → PRD → FSD → TSD → TEST → SQL scripts.

### Document Conventions

- All documentation is written in **Indonesian**
- Diagrams use **Mermaid** syntax (rendered by MkDocs Material)
- SQL files accompany feature docs for DDL/DML changes
- Screenshots (`.png`) stored alongside the docs they illustrate

## MkDocs Configuration

`mkdocs.yml` defines the full navigation tree. When adding new docs:
1. Place the `.md` file under the appropriate `docs/` subfolder
2. Register it in `mkdocs.yml` under the correct nav section

Key plugins enabled: `search`, `mermaid2`. Material theme features include `navigation.tabs`, `navigation.sections`, `content.code.copy`.

## Apps: ei-ledger-gql (Go backend)

Located at `apps/ei-ledger-gql/`.

```bash
cd apps/ei-ledger-gql
make run              # run the server
make build            # build binary
go test ./...         # run all tests
go test ./path/...    # run tests in a package
```

Stack: Fiber (HTTP), gqlgen (GraphQL), GORM (ORM), OpenTelemetry, Minio, supports MySQL/PostgreSQL/SQLite/SQL Server.

## Apps: gl-module (Next.js frontend)

Located at `apps/gl-module/`. Dev server runs on **port 3002**.

```bash
cd apps/gl-module
npm install
npm run dev           # dev server at http://localhost:3002
npm run build         # production build
npm run lint          # ESLint
npx playwright test   # E2E tests
```

Stack: Next.js 16, React 19, TypeScript, Tailwind CSS, Flowbite, CKEditor 5, OpenTelemetry.

## Git Remotes

- `origin` → personal GitHub (`wisnu/ibank-docs`)
- `origin-github` → organization GitHub (`ihsansolusi/ibank-docs`)

Active development branch is `dev`; PRs target `main`.
