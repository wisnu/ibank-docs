-- ============================================================
-- EOD01 - PINDAHKAN TRANSAKSI KE HISTORI
-- Tanggal: 30-03-2026
-- ============================================================

-- TransaksiLiabilitas
INSERT INTO ibankcore.HistTransaksiLiabilitas (ID_DETIL_TRANSAKSI, JENIS_TRANSAKSI_LIABILITAS, KODE_POSTING)
SELECT r.ID_DETIL_TRANSAKSI, r.JENIS_TRANSAKSI_LIABILITAS, r.KODE_POSTING
FROM ibankcore.TransaksiLiabilitas r, ibankcore.DetilTransaksi d, ibankcore.Transaksi t
WHERE r.ID_DETIL_TRANSAKSI = d.ID_DETIL_TRANSAKSI
  AND d.ID_TRANSAKSI = t.ID_TRANSAKSI
  AND t.TANGGAL_TRANSAKSI <= to_date('30-03-2026', 'dd-mm-yyyy');

DELETE FROM ibankcore.TransaksiLiabilitas r
WHERE EXISTS (
  SELECT 1 FROM ibankcore.DetilTransaksi d, ibankcore.Transaksi t
  WHERE r.id_detil_transaksi = d.id_detil_transaksi
    AND d.id_transaksi = t.id_transaksi
    AND t.tanggal_transaksi <= to_date('30-03-2026', 'dd-mm-yyyy')
);

-- TransaksiTRR
INSERT INTO ibankcore.HistTransaksiTRR (id_detil_transaksi, Id_Proses, Is_Sudah_Proses, Jenis_Transaksi_TRR, Nomor_Rekening_Sumber)
SELECT r.id_detil_transaksi, r.Id_Proses, r.Is_Sudah_Proses, r.Jenis_Transaksi_TRR, r.Nomor_Rekening_Sumber
FROM ibankcore.TransaksiTRR r, ibankcore.DetilTransaksi d, ibankcore.Transaksi t
WHERE r.ID_DETIL_TRANSAKSI = d.ID_DETIL_TRANSAKSI
  AND d.ID_TRANSAKSI = t.ID_TRANSAKSI
  AND t.TANGGAL_TRANSAKSI <= to_date('30-03-2026', 'dd-mm-yyyy');

DELETE FROM ibankcore.TransaksiTRR r
WHERE EXISTS (
  SELECT 1 FROM ibankcore.DetilTransaksi d, ibankcore.Transaksi t
  WHERE r.id_detil_transaksi = d.id_detil_transaksi
    AND d.id_transaksi = t.id_transaksi
    AND t.tanggal_transaksi <= to_date('30-03-2026', 'dd-mm-yyyy')
);

-- TransaksiTransitKas
INSERT INTO ibankcore.HistTransaksiTransitKas (ID_DETIL_TRANSAKSI, NOMINAL_SELISIH_KURS, KODE_POSTING)
SELECT r.ID_DETIL_TRANSAKSI, r.NOMINAL_SELISIH_KURS, r.KODE_POSTING
FROM ibankcore.TransaksiTransitKas r, ibankcore.DetilTransaksi d, ibankcore.Transaksi t
WHERE r.ID_DETIL_TRANSAKSI = d.ID_DETIL_TRANSAKSI
  AND d.ID_TRANSAKSI = t.ID_TRANSAKSI
  AND t.TANGGAL_TRANSAKSI <= to_date('30-03-2026', 'dd-mm-yyyy');

DELETE FROM ibankcore.TransaksiTransitKas r
WHERE EXISTS (
  SELECT 1 FROM ibankcore.DetilTransaksi d, ibankcore.Transaksi t
  WHERE r.id_detil_transaksi = d.id_detil_transaksi
    AND d.id_transaksi = t.id_transaksi
    AND t.tanggal_transaksi <= to_date('30-03-2026', 'dd-mm-yyyy')
);

-- DTransaksiCounter
INSERT INTO ibankcore.HistDTransaksiCounter (ID_DETIL_TRANSAKSI, JENIS_TRANSAKSI_COUNTER)
SELECT r.ID_DETIL_TRANSAKSI, r.JENIS_TRANSAKSI_COUNTER
FROM ibankcore.DTransaksiCounter r, ibankcore.DetilTransaksi d, ibankcore.Transaksi t
WHERE r.ID_DETIL_TRANSAKSI = d.ID_DETIL_TRANSAKSI
  AND d.ID_TRANSAKSI = t.ID_TRANSAKSI
  AND t.TANGGAL_TRANSAKSI <= to_date('30-03-2026', 'dd-mm-yyyy');

DELETE FROM ibankcore.DTransaksiCounter r
WHERE EXISTS (
  SELECT 1 FROM ibankcore.DetilTransaksi d, ibankcore.Transaksi t
  WHERE r.id_detil_transaksi = d.id_detil_transaksi
    AND d.id_transaksi = t.id_transaksi
    AND t.tanggal_transaksi <= to_date('30-03-2026', 'dd-mm-yyyy')
);

-- DTransaksiATM
INSERT INTO ibankcore.HistDTransaksiATM (ID_DETIL_TRANSAKSI, FEE_ACQUIRER, FEE_DESTINATION, FEE_ERROR, FEE_ISSUER, FEE_NETWORK)
SELECT r.ID_DETIL_TRANSAKSI, r.FEE_ACQUIRER, r.FEE_DESTINATION, r.FEE_ERROR, r.FEE_ISSUER, r.FEE_NETWORK
FROM ibankcore.DTransaksiATM r, ibankcore.DetilTransaksi d, ibankcore.Transaksi t
WHERE r.ID_DETIL_TRANSAKSI = d.ID_DETIL_TRANSAKSI
  AND d.ID_TRANSAKSI = t.ID_TRANSAKSI
  AND t.TANGGAL_TRANSAKSI <= to_date('30-03-2026', 'dd-mm-yyyy');

DELETE FROM ibankcore.DTransaksiATM r
WHERE EXISTS (
  SELECT 1 FROM ibankcore.DetilTransaksi d, ibankcore.Transaksi t
  WHERE r.id_detil_transaksi = d.id_detil_transaksi
    AND d.id_transaksi = t.id_transaksi
    AND t.tanggal_transaksi <= to_date('30-03-2026', 'dd-mm-yyyy')
);

-- DTKliringTarikan
INSERT INTO ibankcore.HistDTKliringTarikan (ID_DETIL_TRANSAKSI, ID_DETIL_TOLAKAN, JENIS_WARKAT, NOMOR_WARKAT)
SELECT r.ID_DETIL_TRANSAKSI, r.ID_DETIL_TOLAKAN, r.JENIS_WARKAT, r.NOMOR_WARKAT
FROM ibankcore.DTKliringTarikan r, ibankcore.DetilTransaksi d, ibankcore.Transaksi t
WHERE r.ID_DETIL_TRANSAKSI = d.ID_DETIL_TRANSAKSI
  AND d.ID_TRANSAKSI = t.ID_TRANSAKSI
  AND t.TANGGAL_TRANSAKSI <= to_date('30-03-2026', 'dd-mm-yyyy');

DELETE FROM ibankcore.DTKliringTarikan r
WHERE EXISTS (
  SELECT 1 FROM ibankcore.DetilTransaksi d, ibankcore.Transaksi t
  WHERE r.id_detil_transaksi = d.id_detil_transaksi
    AND d.id_transaksi = t.id_transaksi
    AND t.tanggal_transaksi <= to_date('30-03-2026', 'dd-mm-yyyy')
);

-- DTKliringTolakan
INSERT INTO ibankcore.HistDTKliringTolakan (ID_DETIL_TRANSAKSI, ID_PARAMETER_TOLAKAN, ID_DETIL_TARIKAN, KODE_BANK, KODE_ACCOUNT_TITIPAN, KODE_CABANG_TITIPAN)
SELECT r.ID_DETIL_TRANSAKSI, r.ID_PARAMETER_TOLAKAN, r.ID_DETIL_TARIKAN, r.KODE_BANK, r.KODE_ACCOUNT_TITIPAN, r.KODE_CABANG_TITIPAN
FROM ibankcore.DTKliringTolakan r, ibankcore.DetilTransaksi d, ibankcore.Transaksi t
WHERE r.ID_DETIL_TRANSAKSI = d.ID_DETIL_TRANSAKSI
  AND d.ID_TRANSAKSI = t.ID_TRANSAKSI
  AND t.TANGGAL_TRANSAKSI <= to_date('30-03-2026', 'dd-mm-yyyy');

DELETE FROM ibankcore.DTKliringTolakan r
WHERE EXISTS (
  SELECT 1 FROM ibankcore.DetilTransaksi d, ibankcore.Transaksi t
  WHERE r.id_detil_transaksi = d.id_detil_transaksi
    AND d.id_transaksi = t.id_transaksi
    AND t.tanggal_transaksi <= to_date('30-03-2026', 'dd-mm-yyyy')
);

-- DTKliringOutward
INSERT INTO ibankcore.HistDTKliringOutward (ID_DETIL_TRANSAKSI, ID_NOTADEBITOUTWARD)
SELECT r.ID_DETIL_TRANSAKSI, r.ID_NOTADEBITOUTWARD
FROM ibankcore.DTKliringOutward r, ibankcore.DetilTransaksi d, ibankcore.Transaksi t
WHERE r.ID_DETIL_TRANSAKSI = d.ID_DETIL_TRANSAKSI
  AND d.ID_TRANSAKSI = t.ID_TRANSAKSI
  AND t.TANGGAL_TRANSAKSI <= to_date('30-03-2026', 'dd-mm-yyyy');

DELETE FROM ibankcore.DTKliringOutward r
WHERE EXISTS (
  SELECT 1 FROM ibankcore.DetilTransaksi d, ibankcore.Transaksi t
  WHERE r.id_detil_transaksi = d.id_detil_transaksi
    AND d.id_transaksi = t.id_transaksi
    AND t.tanggal_transaksi <= to_date('30-03-2026', 'dd-mm-yyyy')
);

-- DetilTransVA
INSERT INTO ibankcore.HistDetilTransVA (ID_DETIL_TRANSAKSI, BillTotalAmount, BillTotalPayment, VABatchId, BatchProcessStatus, BillingId)
SELECT r.ID_DETIL_TRANSAKSI, r.BillTotalAmount, r.BillTotalPayment, r.VABatchId, r.BatchProcessStatus, r.BillingId
FROM ibankcore.DetilTransVA r, ibankcore.DetilTransaksi d, ibankcore.Transaksi t
WHERE r.ID_DETIL_TRANSAKSI = d.ID_DETIL_TRANSAKSI
  AND d.ID_TRANSAKSI = t.ID_TRANSAKSI
  AND t.TANGGAL_TRANSAKSI <= to_date('30-03-2026', 'dd-mm-yyyy');

DELETE FROM ibankcore.DetilTransVA r
WHERE EXISTS (
  SELECT 1 FROM ibankcore.DetilTransaksi d, ibankcore.Transaksi t
  WHERE r.id_detil_transaksi = d.id_detil_transaksi
    AND d.id_transaksi = t.id_transaksi
    AND t.tanggal_transaksi <= to_date('30-03-2026', 'dd-mm-yyyy')
);

-- DetilTransaksiExt
INSERT INTO ibankcore.HistDetilTransaksiExt (Id_Detil_Transaksi, Nomor_Rekening_Ext, Nama_Rekening_Ext, Kode_Sistem_Ext)
SELECT r.Id_Detil_Transaksi, r.Nomor_Rekening_Ext, r.Nama_Rekening_Ext, r.Kode_Sistem_Ext
FROM ibankcore.DetilTransaksiExt r, ibankcore.DetilTransaksi d, ibankcore.Transaksi t
WHERE r.ID_DETIL_TRANSAKSI = d.ID_DETIL_TRANSAKSI
  AND d.ID_TRANSAKSI = t.ID_TRANSAKSI
  AND t.TANGGAL_TRANSAKSI <= to_date('30-03-2026', 'dd-mm-yyyy');

DELETE FROM ibankcore.DetilTransaksiExt r
WHERE EXISTS (
  SELECT 1 FROM ibankcore.DetilTransaksi d, ibankcore.Transaksi t
  WHERE r.id_detil_transaksi = d.id_detil_transaksi
    AND d.id_transaksi = t.id_transaksi
    AND t.tanggal_transaksi <= to_date('30-03-2026', 'dd-mm-yyyy')
);

-- DetilTransaksi
INSERT INTO ibankcore.HistDetilTransaksi (
  ID_DETIL_TRANSAKSI, TANGGAL_TRANSAKSI, JENIS_MUTASI, NILAI_MUTASI,
  KETERANGAN, KODE_ACCOUNT, KODE_CABANG, KODE_VALUTA, JENIS_DETIL_TRANSAKSI,
  NILAI_KURS_MANUAL, SALDO_AWAL, NILAI_EKUIVALEN, NOMOR_REFERENSI,
  ID_TRANSAKSI, NOMOR_REKENING, ID_PARAMETER_TRANSAKSI,
  ISBILLERTRANSACTION, KODE_KURS, KODE_JURNAL,
  KODE_VALUTA_RAK, NOMINAL_BIAYA, KODE_SUBTX_CLASS,
  FLAG_PROSES, FLAG_TIDAK_JURNAL, KODE_TX_CLASS, ID_DETILTRANSGROUP,
  HIDE_GENTRANS, HIDE_PASSBOOK, HIDE_STATEMENT,
  IS_CREATE_REMITTANCE, SEQUENCE, KODE_RC, KODE_PRODUK
)
SELECT
  d.ID_DETIL_TRANSAKSI, t.TANGGAL_TRANSAKSI, d.JENIS_MUTASI, d.NILAI_MUTASI,
  d.KETERANGAN, d.KODE_ACCOUNT, d.KODE_CABANG, d.KODE_VALUTA, d.JENIS_DETIL_TRANSAKSI,
  d.NILAI_KURS_MANUAL, d.SALDO_AWAL, d.NILAI_EKUIVALEN, d.NOMOR_REFERENSI,
  t.ID_TRANSAKSI, d.NOMOR_REKENING, d.ID_PARAMETER_TRANSAKSI,
  d.ISBILLERTRANSACTION, d.KODE_KURS, d.KODE_JURNAL,
  d.KODE_VALUTA_RAK, d.NOMINAL_BIAYA, d.KODE_SUBTX_CLASS,
  d.FLAG_PROSES, d.FLAG_TIDAK_JURNAL, d.KODE_TX_CLASS, d.ID_DETILTRANSGROUP,
  d.HIDE_GENTRANS, d.HIDE_PASSBOOK, d.HIDE_STATEMENT,
  d.IS_CREATE_REMITTANCE, d.SEQUENCE, d.KODE_RC, d.KODE_PRODUK
FROM ibankcore.DetilTransaksi d, ibankcore.Transaksi t
WHERE d.id_transaksi = t.id_transaksi
  AND t.tanggal_transaksi <= to_date('30-03-2026', 'dd-mm-yyyy');

DELETE FROM ibankcore.DetilTransaksi d
WHERE d.id_transaksi IN (
  SELECT id_transaksi FROM ibankcore.Transaksi
  WHERE id_transaksi = d.id_transaksi
    AND tanggal_transaksi <= to_date('30-03-2026', 'dd-mm-yyyy')
);

-- DetilTransGroup
INSERT INTO ibankcore.HistDetilTransGroup (id_detiltransgroup, keterangan, tx_source_type, tx_source_id, kode_entri, Id_Transaksi, Nomor_Rekening)
SELECT d.id_detiltransgroup, d.keterangan, d.tx_source_type, d.tx_source_id, d.kode_entri, d.Id_Transaksi, d.Nomor_Rekening
FROM ibankcore.DetilTransGroup d, ibankcore.Transaksi t
WHERE d.id_transaksi = t.id_transaksi
  AND t.tanggal_transaksi <= to_date('30-03-2026', 'dd-mm-yyyy');

DELETE FROM ibankcore.DetilTransGroup d
WHERE EXISTS (
  SELECT 1 FROM ibankcore.Transaksi
  WHERE id_transaksi = d.id_transaksi
    AND tanggal_transaksi <= to_date('30-03-2026', 'dd-mm-yyyy')
);

-- Transaksi
INSERT INTO ibankcore.HistTransaksi (
  ID_TRANSAKSI, TANGGAL_TRANSAKSI, NOMOR_REFERENSI, USER_INPUT,
  TERMINAL_INPUT, USER_OVERIDE, KETERANGAN, TERMINAL_OVERIDE,
  USER_OTORISASI, TERMINAL_OTORISASI, TANGGAL_OTORISASI,
  JAM_INPUT, BIAYA, JAM_OTORISASI, JENIS_APLIKASI, JENIS_TRANSAKSI,
  KODE_CABANG_TRANSAKSI, KODE_VALUTA_TRANSAKSI, KURS_MANUAL,
  NILAI_EKUIVALEN, NILAI_TRANSAKSI, PAJAK, TANGGAL_INPUT,
  ZAKAT, ID_BATCH_TRANSAKSI, KODE_TRANSAKSI, ID_TRANSACTION_GROUP,
  ID_BLOK_JURNAL, STATUS_OTORISASI, IS_SUDAH_DIJURNAL, JOURNAL_NO,
  NOMOR_SERI, IS_REVERSED, STATUS_TRANSAKSI_UMUM, REF_ID_TRANSAKSI,
  ACCESS_FLAG, NOMOR_COUNTER, IS_CONFIDENTIAL, ID_CONFIDENTIAL, KETERANGAN_TAMBAHAN,
  IS_REVERSE_ALLOWED, TANGGAL_BAGIHASIL, IS_SEND_EKSTERNAL
)
SELECT
  ID_TRANSAKSI, TANGGAL_TRANSAKSI, NOMOR_REFERENSI, USER_INPUT,
  TERMINAL_INPUT, USER_OVERIDE, KETERANGAN, TERMINAL_OVERIDE,
  USER_OTORISASI, TERMINAL_OTORISASI, TANGGAL_OTORISASI,
  JAM_INPUT, BIAYA, JAM_OTORISASI, JENIS_APLIKASI, JENIS_TRANSAKSI,
  KODE_CABANG_TRANSAKSI, KODE_VALUTA_TRANSAKSI, KURS_MANUAL,
  NILAI_EKUIVALEN, NILAI_TRANSAKSI, PAJAK, TANGGAL_INPUT,
  ZAKAT, ID_BATCH_TRANSAKSI, KODE_TRANSAKSI, ID_TRANSACTION_GROUP,
  ID_BLOK_JURNAL, STATUS_OTORISASI, IS_SUDAH_DIJURNAL, JOURNAL_NO,
  NOMOR_SERI, IS_REVERSED, STATUS_TRANSAKSI_UMUM, REF_ID_TRANSAKSI,
  ACCESS_FLAG, NOMOR_COUNTER, IS_CONFIDENTIAL, ID_CONFIDENTIAL, KETERANGAN_TAMBAHAN,
  IS_REVERSE_ALLOWED, TANGGAL_BAGIHASIL, IS_SEND_EKSTERNAL
FROM ibankcore.Transaksi
WHERE TANGGAL_TRANSAKSI <= to_date('30-03-2026', 'dd-mm-yyyy');

DELETE FROM ibankcore.Transaksi
WHERE Tanggal_Transaksi <= to_date('30-03-2026', 'dd-mm-yyyy');

-- BatchTransaksi
UPDATE ibankcore.BatchTransaksi SET status_batch = 'C'
WHERE tanggal_buat = to_date('30-03-2026', 'dd-mm-yyyy');

COMMIT;
