# Review Perbandingan Format FSD

Dokumen ini mencatat perbedaan antara dua format FSD yang tersedia untuk modul FingerScan Biometrik.

---

## Informasi Dokumen

| Item | Nilai |
|------|-------|
| Tanggal Review | 2025 |
| Dokumen yang Dibandingkan | Draft FSD FIngerscan Biometrik.md (v1) vs FSD_Fingerscan_Biometrik_v2.md (v2) |
| Referensi PRD | PRD-BJBS-FingerScan-01 |

---

## Ringkasan Perbedaan

| Aspek | FSD v1 (Original) | FSD v2 (Alternatif) |
|-------|-------------------|---------------------|
| **Jumlah Halaman** | ~500 baris | ~1200 baris |
| **Format** | Mengikuti template repository | Format independen & komprehensif |
| **Diagram** | Tidak ada | ASCII diagrams lengkap |
| **API Specification** | Tidak ada | Lengkap dengan contoh |
| **Database Schema** | Entity sederhana | ERD + Data Dictionary |
| **UI Specification** | Komponen saja | ASCII mockup |
| **Error Handling** | Tidak ada | Kode error lengkap |
| **Target Audience** | Developer internal | Developer + QA + Stakeholder |

---

## Perbandingan Detail per Section

### 1. Pendahuluan & Metadata

| Komponen | FSD v1 | FSD v2 |
|----------|--------|--------|
| Document Metadata | Ada (tabel sederhana) | Ada (tabel sederhana) |
| Tujuan Dokumen | Tidak ada section khusus | Ada section dedicated |
| Definisi & Istilah | Tidak ada | Ada (glossary lengkap) |
| Referensi Dokumen | Tidak ada | Ada |

**Catatan:** FSD v2 memiliki pendahuluan yang lebih lengkap untuk membantu pembaca baru memahami konteks dokumen.

---

### 2. Overview & Arsitektur

| Komponen | FSD v1 | FSD v2 |
|----------|--------|--------|
| Perspektif Sistem | Deskripsi teks | Deskripsi + diagram |
| Arsitektur High-Level | Tidak ada | ASCII diagram lengkap |
| Component Diagram | Tidak ada | Ada (3 layer) |
| Deployment View | Tidak ada | Ada (Kantor Pusat + Cabang) |

**Catatan:** FSD v2 menyediakan visualisasi arsitektur yang membantu pemahaman teknis secara keseluruhan.

---

### 3. Actors & Roles

| Komponen | FSD v1 | FSD v2 |
|----------|--------|--------|
| Daftar Aktor | 5 aktor | 6 aktor (+ System) |
| Hak Akses | Deskripsi umum | Tabel permission detail |
| Role Mapping | Tidak ada | Ada |

**Catatan:** FSD v2 menambahkan aktor "System" untuk automated processes dan merinci hak akses per role.

---

### 4. Modul Sistem

| Komponen | FSD v1 | FSD v2 |
|----------|--------|--------|
| Fingerstation | Tidak ada detail | Fungsi + State Diagram |
| Fingerscan Service | Tidak ada detail | Sub-modul lengkap |
| Management Portal | Tidak ada detail | Menu structure lengkap |

**Catatan:** FSD v2 memberikan breakdown detail setiap modul termasuk teknologi yang digunakan.

---

### 5. Spesifikasi Fungsional (Use Cases)

| Komponen | FSD v1 | FSD v2 |
|----------|--------|--------|
| Format Use Case | Sederhana | Lengkap (Purpose, Precondition, Flow, Rules, I/O) |
| Flow Diagram | Tidak ada | Sequence diagram per use case |
| Alternative Flow | Tidak ada | Ada (contoh: verification failed) |
| Business Rules | Tabel terpisah | Embedded per use case + summary |

**Perbandingan Use Case Enrollment:**

| Aspek | FSD v1 | FSD v2 |
|-------|--------|--------|
| Purpose | Ada | Ada |
| Precondition | Ada (3 item) | Ada (4 item) |
| Input | Ada (3 field) | Ada (5 field dengan validasi) |
| Process | Ada (5 step) | Ada (5 step) + Sequence Diagram |
| Output | Ada (2 field) | Ada (4 field) |
| Business Rules | Referensi ID | Embedded + referensi |

---

### 6. Spesifikasi Antarmuka (API)

| Komponen | FSD v1 | FSD v2 |
|----------|--------|--------|
| Base URL | Tidak ada | Ada (Production + Staging) |
| Authentication | Tidak ada | Ada (Bearer Token) |
| Endpoint List | Tidak ada | 17 endpoints |
| Request/Response Example | Tidak ada | Ada (JSON lengkap) |
| WebSocket Events | Tidak ada | Ada (6 events) |
| External Integration | Tabel sederhana | Detail dengan endpoint |

**Catatan:** FSD v2 dapat langsung digunakan sebagai referensi untuk development API tanpa dokumen tambahan.

---

### 7. Spesifikasi Data

| Komponen | FSD v1 | FSD v2 |
|----------|--------|--------|
| ERD | Tidak ada | Ada (ASCII diagram) |
| Table List | 4 entity | 5 tables |
| Column Definition | Ada (sederhana) | Ada (lengkap dengan type, nullable, default) |
| Relationship | Tidak ada | Ada dalam ERD |
| Index | Tidak ada | Tidak ada |

**Perbandingan Entity:**

| Entity | FSD v1 | FSD v2 |
|--------|--------|--------|
| User Fingerprint / fp_user | 10 kolom | 7 kolom (lebih normalized) |
| Finger Template / fp_finger | Embedded | Separate table |
| Verification Session | 7 kolom | 12 kolom (lebih detail) |
| Fingerstation / fp_station | 6 kolom | 10 kolom |
| Audit Log | 9 kolom | 11 kolom |
| Fallback | Embedded in user | Separate table (fp_fallback) |

---

### 8. Spesifikasi User Interface

| Komponen | FSD v1 | FSD v2 |
|----------|--------|--------|
| Screen List | 3 screens | 3 screens + sub-screens |
| UI Components | Tabel deskripsi | Tabel + ASCII mockup |
| Field Specification | Ada (Appendix) | Embedded per screen |
| Validation Rules | Ada | Ada |
| State/Behavior | Tidak ada | Ada dalam mockup |

**Catatan:** FSD v2 menyediakan ASCII mockup yang membantu developer dan designer memahami layout UI.

---

### 9. Business Rules

| Komponen | FSD v1 | FSD v2 |
|----------|--------|--------|
| Jumlah Rules | 10 rules | 15 rules |
| Kategorisasi | Tidak ada | Ada (Enrollment, Verification, Lock, Fallback, Audit) |
| Implementation Notes | Tidak ada | Ada |

---

### 10. Error Handling

| Komponen | FSD v1 | FSD v2 |
|----------|--------|--------|
| Error Codes | Tidak ada | 18 error codes |
| Error Categories | Tidak ada | 5 kategori (E0xx - E9xx) |
| Error Response Format | Tidak ada | Ada (JSON structure) |
| Action/Resolution | Tidak ada | Ada per error |

**Catatan:** FSD v2 menyediakan error handling yang dapat langsung diimplementasikan.

---

### 11. Security Specification

| Komponen | FSD v1 | FSD v2 |
|----------|--------|--------|
| Data Security | Appendix (5 item) | Section dedicated |
| Encryption | Disebutkan | Detail (AES-256, TLS 1.3) |
| Access Control | Tidak ada | Matrix per role |
| Network Security | Tidak ada | ASCII diagram |
| Audit Trail | Disebutkan | Detail field yang dicatat |

---

### 12. Performance Requirements

| Komponen | FSD v1 | FSD v2 |
|----------|--------|--------|
| Metrics | 5 item (Appendix) | 7 item (Section dedicated) |
| Target Values | Ada | Ada dengan measurement method |
| Response Time | < 5 detik | < 5 detik (P95) |
| Concurrent Users | Disebutkan | 100/detik (specific) |
| Availability | Disebutkan | 99.9% (specific) |

---

### 13. Lampiran & Appendix

| Komponen | FSD v1 | FSD v2 |
|----------|--------|--------|
| UI Field Spec | Appendix A | Embedded per screen |
| Backend Data Mapping | Appendix B | Section 6 |
| Traceability Matrix | Appendix C | Tidak ada |
| Open Points | Appendix F | Tidak ada (asumsi lengkap) |
| Finger Index Mapping | Tidak ada | Lampiran A |
| Status Transition | Tidak ada | Lampiran B |
| Deployment Checklist | Tidak ada | Lampiran C |

---

## Kelebihan dan Kekurangan

### FSD v1 (Original)

**Kelebihan:**
- Konsisten dengan format dokumen lain di repository
- Lebih ringkas dan mudah dibaca cepat
- Ada Traceability Matrix ke PRD
- Ada Open Points untuk tracking

**Kekurangan:**
- Tidak ada visualisasi arsitektur
- Tidak ada API specification detail
- Tidak ada error handling
- UI specification terbatas

### FSD v2 (Alternatif)

**Kelebihan:**
- Komprehensif dan self-contained
- Visualisasi dengan ASCII diagram
- API spec lengkap dengan contoh
- Error handling detail
- Dapat langsung digunakan untuk development
- Performance target terukur
- Deployment checklist

**Kekurangan:**
- Lebih panjang (memerlukan waktu baca lebih lama)
- Tidak ada Traceability Matrix
- Tidak ada Open Points section
- Format berbeda dari dokumen lain di repository

---

## Rekomendasi Penggunaan

| Situasi | Rekomendasi |
|---------|-------------|
| Review cepat oleh stakeholder | FSD v1 |
| Development reference | FSD v2 |
| QA test case preparation | FSD v2 |
| Dokumentasi formal | FSD v1 (konsisten dengan repo) |
| Onboarding developer baru | FSD v2 |
| Integration dengan tim eksternal | FSD v2 |
| Audit compliance | FSD v1 (ada traceability) |

---

## Kesimpulan

Kedua format FSD memiliki kelebihan masing-masing:

1. **FSD v1** cocok untuk dokumentasi formal yang konsisten dengan format repository dan memiliki traceability ke PRD.

2. **FSD v2** cocok sebagai referensi teknis lengkap untuk tim development, QA, dan integrasi dengan pihak eksternal.

Disarankan untuk memiliki kedua versi:
- **FSD v1** sebagai dokumen formal untuk approval dan audit
- **FSD v2** sebagai referensi teknis detail untuk implementasi

---

## Riwayat Review

| Tanggal | Reviewer | Catatan |
|---------|----------|---------|
| 2025 | - | Initial review |
