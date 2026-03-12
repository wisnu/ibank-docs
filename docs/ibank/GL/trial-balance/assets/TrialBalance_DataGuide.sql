-- =============================================================================
-- TRIAL BALANCE DATA RETRIEVAL GUIDE
-- =============================================================================
-- Referensi: Query Trial Balance.sql & GetTrialBalancePerCabang.py
--
-- PARAMETER YANG PERLU DIGANTI:
--   :BEGIN_DATE      = Tanggal awal periode (format: DD-MM-YYYY)
--   :END_DATE        = Tanggal akhir periode (format: DD-MM-YYYY)
--   :BALANCE_DATE    = Tanggal saldo awal (BEGIN_DATE - 1 hari)
--   :TODAY           = Tanggal hari ini untuk jurnal belum posting
--   :BRANCH_CODE     = Kode cabang (atau kosongkan untuk semua cabang)
--   :CURRENCY_CODE   = Kode mata uang (atau kosongkan untuk semua mata uang)
-- =============================================================================


-- =============================================================================
-- BAGIAN 1: QUERY UNTUK AKUN NERACA (Account Type: A, L, E, M)
-- A = Asset, L = Liability, E = Equity, M = Administratif
-- =============================================================================

SELECT
    ac.account_code,
    ac.account_name,
    ac.account_type,
    etype.enum_description AS account_type_desc,
    ai.branch_code,
    ai.currency_code,
    ' ' AS project_no,
    ac.account_level,

    -- Saldo Awal (per tanggal BALANCE_DATE)
    NVL(db_begin.balancecumulative, 0.0) AS begin_balance,
    NVL(db_begin.balancecumulative_ekuiv, 0.0) AS begin_balance_ekuiv,

    -- Mutasi periode (dari BEGIN_DATE s/d END_DATE)
    NVL(mut.debit, 0.0) AS debit,
    NVL(mut.debit_ekuiv, 0.0) AS debit_ekuiv,
    NVL(mut.credit, 0.0) AS credit,
    NVL(mut.credit_ekuiv, 0.0) AS credit_ekuiv,

    -- Saldo Akhir (per tanggal END_DATE)
    NVL(db_end.balancecumulative, 0.0) AS end_balance,
    NVL(db_end.balancecumulative_ekuiv, 0.0) AS end_balance_ekuiv,

    -- Jurnal hari ini (jika END_DATE = TODAY dan jurnal belum diposting ke dailybalance)
    NVL(j_today.debit, 0.0) AS today_debit,
    NVL(j_today.debit_ekuiv, 0.0) AS today_debit_ekuiv,
    NVL(j_today.credit, 0.0) AS today_credit,
    NVL(j_today.credit_ekuiv, 0.0) AS today_credit_ekuiv,
    NVL(j_today.balance, 0.0) AS today_balance,
    NVL(j_today.balance_ekuiv, 0.0) AS today_balance_ekuiv

FROM account ac
INNER JOIN accountinstance ai
    ON ai.account_code = ac.account_code
LEFT OUTER JOIN enum_varchar etype
    ON etype.enum_value = ac.account_type
    AND etype.enum_name = 'eAccountType'

-- Subquery: Saldo Awal (ambil saldo kumulatif terakhir <= BALANCE_DATE)
LEFT OUTER JOIN (
    SELECT d1.accountinstance_id,
           d1.balancecumulative,
           d1.balancecumulative_ekuiv
    FROM dailybalance d1
    INNER JOIN (
        SELECT d.accountinstance_id,
               MAX(d.datevalue) AS maxdate
        FROM dailybalance d
        INNER JOIN accountinstance ai
            ON ai.accountinstance_id = d.accountinstance_id
        WHERE d.datevalue <= TO_DATE(:BALANCE_DATE, 'DD-MM-YYYY')
        -- AND ai.branch_code = :BRANCH_CODE  -- Uncomment jika filter cabang
        GROUP BY d.accountinstance_id
    ) d2 ON d1.accountinstance_id = d2.accountinstance_id
        AND d1.datevalue = d2.maxdate
) db_begin ON ai.accountinstance_id = db_begin.accountinstance_id

-- Subquery: Saldo Akhir (ambil saldo kumulatif terakhir <= END_DATE)
LEFT OUTER JOIN (
    SELECT d1.accountinstance_id,
           d1.balancecumulative,
           d1.balancecumulative_ekuiv
    FROM dailybalance d1
    INNER JOIN (
        SELECT d.accountinstance_id,
               MAX(d.datevalue) AS maxdate
        FROM dailybalance d
        INNER JOIN accountinstance ai
            ON ai.accountinstance_id = d.accountinstance_id
        WHERE d.datevalue <= TO_DATE(:END_DATE, 'DD-MM-YYYY')
        -- AND ai.branch_code = :BRANCH_CODE  -- Uncomment jika filter cabang
        GROUP BY d.accountinstance_id
    ) d2 ON d1.accountinstance_id = d2.accountinstance_id
        AND d1.datevalue = d2.maxdate
) db_end ON ai.accountinstance_id = db_end.accountinstance_id

-- Subquery: Mutasi periode (sum debit/credit dari BEGIN_DATE s/d END_DATE)
LEFT OUTER JOIN (
    SELECT
        d.accountinstance_id,
        SUM(d.debit) AS debit,
        SUM(d.debit_ekuiv) AS debit_ekuiv,
        SUM(d.credit) AS credit,
        SUM(d.credit_ekuiv) AS credit_ekuiv,
        SUM(d.balance) AS balance,
        SUM(d.balance_ekuiv) AS balance_ekuiv
    FROM dailybalance d
    INNER JOIN accountinstance ai
        ON ai.accountinstance_id = d.accountinstance_id
    WHERE d.datevalue >= TO_DATE(:BEGIN_DATE, 'DD-MM-YYYY')
      AND d.datevalue <= TO_DATE(:END_DATE, 'DD-MM-YYYY')
    -- AND ai.branch_code = :BRANCH_CODE  -- Uncomment jika filter cabang
    GROUP BY d.accountinstance_id
) mut ON ai.accountinstance_id = mut.accountinstance_id

-- Subquery: Jurnal hari ini (untuk transaksi yang belum masuk dailybalance)
LEFT OUTER JOIN (
    -- Jurnal langsung ke akun
    SELECT
        ai.accountinstance_id,
        SUM(ji.amount_debit) AS debit,
        SUM(ji.amount_credit) AS credit,
        SUM((ji.amount_credit - ji.amount_debit) * ai.balance_sign) AS balance,
        SUM(ji.amount_debit * j.nilai_kurs) AS debit_ekuiv,
        SUM(ji.amount_credit * j.nilai_kurs) AS credit_ekuiv,
        SUM((ji.amount_credit - ji.amount_debit) * j.nilai_kurs * ai.balance_sign) AS balance_ekuiv
    FROM journal j
    INNER JOIN journalitem ji ON j.journal_no = ji.fl_journal
    INNER JOIN accountinstance ai ON ai.accountinstance_id = ji.accountinstance_id
    WHERE j.journal_date = TO_DATE(:TODAY, 'DD-MM-YYYY')
    -- AND ai.branch_code = :BRANCH_CODE  -- Uncomment jika filter cabang
    GROUP BY ai.accountinstance_id

    UNION ALL

    -- Jurnal ke akun CPA (Contra Per Account) - untuk konsolidasi antar cabang
    SELECT
        ai2.accountinstance_id,
        SUM(ji.amount_debit) AS debit,
        SUM(ji.amount_credit) AS credit,
        SUM((ji.amount_credit - ji.amount_debit) * ai1.balance_sign) AS balance,
        SUM(ji.amount_debit * j.nilai_kurs) AS debit_ekuiv,
        SUM(ji.amount_credit * j.nilai_kurs) AS credit_ekuiv,
        SUM((ji.amount_credit - ji.amount_debit) * j.nilai_kurs * ai1.balance_sign) AS balance_ekuiv
    FROM journal j
    INNER JOIN journalitem ji ON j.journal_no = ji.fl_journal
    INNER JOIN accountinstance ai1 ON ai1.accountinstance_id = ji.accountinstance_id
    INNER JOIN accountinstance ai2 ON ai2.accountinstance_id = ai1.fl_cpa_accountinstance
    WHERE j.journal_date = TO_DATE(:TODAY, 'DD-MM-YYYY')
    -- AND ai2.branch_code = :BRANCH_CODE  -- Uncomment jika filter cabang
    GROUP BY ai2.accountinstance_id
) j_today ON ai.accountinstance_id = j_today.accountinstance_id

WHERE ac.is_detail = 'T'
  AND ac.account_type IN ('A', 'L', 'E', 'M')
  -- AND ai.branch_code = :BRANCH_CODE      -- Uncomment jika filter cabang
  -- AND ai.currency_code = :CURRENCY_CODE  -- Uncomment jika filter mata uang


-- =============================================================================
-- BAGIAN 2: QUERY UNTUK AKUN LABA RUGI (Account Type: I, X)
-- I = Income/Pendapatan, X = Expense/Beban
-- Akun laba rugi memerlukan breakdown per project
-- =============================================================================

UNION ALL

SELECT
    ac.account_code,
    ac.account_name,
    ac.account_type,
    etype.enum_description AS account_type_desc,
    ai.branch_code,
    ai.currency_code,
    p.project_no,
    ac.account_level,

    -- Saldo Awal
    NVL(db_begin.balancecumulative, 0.0) AS begin_balance,
    NVL(db_begin.balancecumulative_ekuiv, 0.0) AS begin_balance_ekuiv,

    -- Mutasi periode
    NVL(mut.debit, 0.0) AS debit,
    NVL(mut.debit_ekuiv, 0.0) AS debit_ekuiv,
    NVL(mut.credit, 0.0) AS credit,
    NVL(mut.credit_ekuiv, 0.0) AS credit_ekuiv,

    -- Saldo Akhir
    NVL(db_end.balancecumulative, 0.0) AS end_balance,
    NVL(db_end.balancecumulative_ekuiv, 0.0) AS end_balance_ekuiv,

    -- Jurnal hari ini
    NVL(j_today.debit, 0.0) AS today_debit,
    NVL(j_today.debit_ekuiv, 0.0) AS today_debit_ekuiv,
    NVL(j_today.credit, 0.0) AS today_credit,
    NVL(j_today.credit_ekuiv, 0.0) AS today_credit_ekuiv,
    NVL(j_today.balance, 0.0) AS today_balance,
    NVL(j_today.balance_ekuiv, 0.0) AS today_balance_ekuiv

FROM account ac
INNER JOIN accountinstance ai
    ON ai.account_code = ac.account_code
INNER JOIN project p
    ON 1 = 1  -- Cross join untuk mendapat semua kombinasi akun-project
LEFT OUTER JOIN enum_varchar etype
    ON etype.enum_value = ac.account_type
    AND etype.enum_name = 'eAccountType'

-- Subquery: Saldo Awal Project
LEFT OUTER JOIN (
    SELECT d1.accountinstance_id,
           d1.project_no,
           d1.balancecumulative,
           d1.balancecumulative_ekuiv
    FROM dailyprojectbalance d1
    INNER JOIN (
        SELECT d.accountinstance_id,
               d.project_no,
               MAX(d.datevalue) AS maxdate
        FROM dailyprojectbalance d
        INNER JOIN accountinstance ai
            ON ai.accountinstance_id = d.accountinstance_id
        WHERE d.datevalue <= TO_DATE(:BALANCE_DATE, 'DD-MM-YYYY')
        -- AND ai.branch_code = :BRANCH_CODE  -- Uncomment jika filter cabang
        GROUP BY d.accountinstance_id, d.project_no
    ) d2 ON d1.accountinstance_id = d2.accountinstance_id
        AND d1.project_no = d2.project_no
        AND d1.datevalue = d2.maxdate
) db_begin ON ai.accountinstance_id = db_begin.accountinstance_id
          AND p.project_no = db_begin.project_no

-- Subquery: Saldo Akhir Project
LEFT OUTER JOIN (
    SELECT d1.accountinstance_id,
           d1.project_no,
           d1.balancecumulative,
           d1.balancecumulative_ekuiv
    FROM dailyprojectbalance d1
    INNER JOIN (
        SELECT d.accountinstance_id,
               d.project_no,
               MAX(d.datevalue) AS maxdate
        FROM dailyprojectbalance d
        INNER JOIN accountinstance ai
            ON ai.accountinstance_id = d.accountinstance_id
        WHERE d.datevalue <= TO_DATE(:END_DATE, 'DD-MM-YYYY')
        -- AND ai.branch_code = :BRANCH_CODE  -- Uncomment jika filter cabang
        GROUP BY d.accountinstance_id, d.project_no
    ) d2 ON d1.accountinstance_id = d2.accountinstance_id
        AND d1.project_no = d2.project_no
        AND d1.datevalue = d2.maxdate
) db_end ON ai.accountinstance_id = db_end.accountinstance_id
        AND p.project_no = db_end.project_no

-- Subquery: Mutasi Project periode
LEFT OUTER JOIN (
    SELECT
        d.accountinstance_id,
        d.project_no,
        SUM(d.debit) AS debit,
        SUM(d.debit_ekuiv) AS debit_ekuiv,
        SUM(d.credit) AS credit,
        SUM(d.credit_ekuiv) AS credit_ekuiv,
        SUM(d.balance) AS balance,
        SUM(d.balance_ekuiv) AS balance_ekuiv
    FROM dailyprojectbalance d
    INNER JOIN accountinstance ai
        ON ai.accountinstance_id = d.accountinstance_id
    WHERE d.datevalue >= TO_DATE(:BEGIN_DATE, 'DD-MM-YYYY')
      AND d.datevalue <= TO_DATE(:END_DATE, 'DD-MM-YYYY')
    -- AND ai.branch_code = :BRANCH_CODE  -- Uncomment jika filter cabang
    GROUP BY d.accountinstance_id, d.project_no
) mut ON ai.accountinstance_id = mut.accountinstance_id
     AND p.project_no = mut.project_no

-- Subquery: Jurnal hari ini per Project (menggunakan rc_code sebagai project)
LEFT OUTER JOIN (
    SELECT
        ai.accountinstance_id,
        ji.rc_code AS project_no,
        SUM(ji.amount_debit) AS debit,
        SUM(ji.amount_credit) AS credit,
        SUM((ji.amount_credit - ji.amount_debit) * ai.balance_sign) AS balance,
        SUM(ji.amount_debit * j.nilai_kurs) AS debit_ekuiv,
        SUM(ji.amount_credit * j.nilai_kurs) AS credit_ekuiv,
        SUM((ji.amount_credit - ji.amount_debit) * j.nilai_kurs * ai.balance_sign) AS balance_ekuiv
    FROM journal j
    INNER JOIN journalitem ji ON j.journal_no = ji.fl_journal
    INNER JOIN accountinstance ai ON ai.accountinstance_id = ji.accountinstance_id
    WHERE j.journal_date = TO_DATE(:TODAY, 'DD-MM-YYYY')
    -- AND ai.branch_code = :BRANCH_CODE  -- Uncomment jika filter cabang
    GROUP BY ai.accountinstance_id, ji.rc_code
) j_today ON ai.accountinstance_id = j_today.accountinstance_id
         AND p.project_no = j_today.project_no

WHERE ac.is_detail = 'T'
  AND ac.account_type IN ('I', 'X')
  -- AND ai.branch_code = :BRANCH_CODE      -- Uncomment jika filter cabang
  -- AND ai.currency_code = :CURRENCY_CODE  -- Uncomment jika filter mata uang
  -- Filter: hanya tampilkan jika ada nilai atau project_no = '0000'
  AND (
      p.project_no = '0000'
      OR (
          p.project_no <> '0000'
          AND (
              NVL(db_begin.balancecumulative, 0) <> 0
              OR NVL(db_end.balancecumulative, 0) <> 0
              OR NVL(mut.debit, 0) <> 0
              OR NVL(mut.credit, 0) <> 0
              OR NVL(j_today.debit, 0) <> 0
              OR NVL(j_today.credit, 0) <> 0
          )
      )
  )

ORDER BY branch_code, currency_code, account_code, project_no;
