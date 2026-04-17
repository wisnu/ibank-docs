import os

f1_path = r"d:\Docs\ibank-docs\docs\bcas\enhance_dormant\Design Plan.md"
f2_path = r"d:\Docs\2026 03 12 BCAS Rekening Dormant\Design Plan.md"

with open(f1_path, 'r', encoding='utf-8') as f:
    f1_content = f.read()

with open(f2_path, 'r', encoding='utf-8') as f:
    f2_content = f.read()

# Extract Section 9 from f1
section9_idx = f1_content.find('## 9. Matriks Status Rekening Berdasarkan Aktivitas dan Jenis Transaksi')
if section9_idx != -1:
    section9_content = f1_content[section9_idx:]
else:
    section9_content = ''

# Process f2 to merge missing items in Section 8
f2_content = f2_content.replace(
'''## 8. Jenis Aktivitas Non-Finansial yang Dicatat

| Kode `kode_aktivitas` | Deskripsi | Channel |
|---|---|---|
| `CEK_SALDO` | Cek saldo | ATM, MOBILE, IB, TELLER |
| `CEK_MUTASI` | Cek mutasi / histori transaksi | ATM, MOBILE, IB, TELLER |
| `LOGIN_MB` | Login Mobile Banking | MOBILE |
| `LOGIN_IB` | Login Internet Banking | IB |
| `LOGIN_ATM` | Akses menu ATM (tanpa transaksi) | ATM |
| `TRX` | Transaksi finansial (diisi oleh Alur A) | semua |''',
'''## 8. Jenis Aktivitas Non-Finansial yang Dicatat

| Kode `kode_aktivitas` | Deskripsi | Channel |
|---|---|---|
| `CEK_SALDO` | Cek saldo | ATM, MOBILE, IB, TELLER |
| `CEK_MUTASI` | Cek mutasi / histori transaksi | ATM, MOBILE, IB, TELLER |
| `CETAK_PASSBOOK` | Cetak passbook | TELLER |
| `CETAK_SALDO` | Cetak saldo passbook | TELLER |
| `LOGIN_MB` | Login Mobile Banking | MOBILE |
| `LOGIN_IB` | Login Internet Banking | IB |
| `LOGIN_ATM` | Akses menu ATM (tanpa transaksi) | ATM |
| `TRX` | Transaksi finansial (diisi oleh Alur A) | semua |''')

# Rename section 9 to 10 in the extracted content
section9_content = section9_content.replace('## 9. Matriks', '## 10. Matriks')
section9_content = section9_content.replace('### 9.1', '### 10.1')
section9_content = section9_content.replace('### 9.2', '### 10.2')
section9_content = section9_content.replace('### 9.3', '### 10.3')

end_idx = f2_content.rfind('---')
if end_idx != -1:
    final_content = f2_content[:end_idx] + '---\n\n' + section9_content + '\n' + f2_content[end_idx:]
else:
    final_content = f2_content + '\n\n---\n\n' + section9_content

with open(f1_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print('Done')
