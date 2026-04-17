import sys
import com.ihsan.util.dbutil as dbutil
import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.util.modman as modman
import com.ihsan.foundation.appserver as appserver

# application-level modules, loaded via modman
modman.loadStdModules(globals(), 
  [
    "sutil"
    , "AppError"
    , "scripts#batchprocess.batch_sql"
  ]
)

sutil.setDialectToORACLE()

# GLOBALS
config = appserver.ActiveConfig
helper = phelper.PObjectHelper(config)
app    = config.AppObject
_CONSOLE = False

def printOut(sOut):
  global app
  
  if _CONSOLE:
    print sOut
  else:
    app.ConWriteln(sOut)
  #--
    
def DAFScriptMain(config, parameter, returns):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  global _CONSOLE
  
  _CONSOLE = False
  batch_sql._CONSOLE = False
  batch_sql.app      = app
  batch_sql.updateResources(SQL_RESOURCES)
  
  main(config)
  returns.CreateValues(['Is_Err', 0])

  return 1

def main(config):
  helper = phelper.PObjectHelper(config)
  oToday = helper.CreateObject('PeriodHelper').GetToday()
  LibUtils = config.ModLibUtils
  
  if not _CONSOLE:  
    global app
    app.ConCreate('out')
  #--
                                
  #oToday = oToday.PrevWorkDay()
  DateValue = oToday.GetDate()
                                
  printOut('Processing tutup rekening otomatis %s...' % oToday.GetDateText())   

  oParamHariTutup = helper.GetObject('ParameterGlobal', 'TUTUP_NOL_HARI')
  nDefaultHariTutup = oParamHariTutup.GetInt()

  dictParam = { 
    'Today': sutil.toDate(config, oToday.GetDate()),
    'DefaultHariTutup': str(nDefaultHariTutup)
  }
  dictParam.update(dbutil.mapDBTableNames(config, 
    [
      'Transaksi'                     , 'Seq_Transaksi'
      , 'DetilTransaksi'              , 'Seq_DetilTransaksi'
      , 'RekeningTransaksi'           , 'Seq_TXSerialNumber'
      , 'RekeningLiabilitas'          , 'RekeningRencana'
      , 'StandingInstruction'         , 'RecurrentTransaction'
      , 'Produk'                      , 'ProdukRencana'
      , 'DetilTransaksiClass'         , 'TransaksiLiabilitas'
      , 'GLInterface'
      , 'RekeningCabang'              , 'Nasabah'
      , 'Deposito'                    , 'GLAccount'
      , 'AccountInstance'             , 'Journal'
      , 'JournalItem'                 , 'Seq_JournalItem'
      , 'HistTransaksi'               , 'HistDetilTransaksi'
      , 'InfoPenutupanRekening'
      , 'RegisterRT'                  , 'RegisterLayanan'
      , 'RegisterAutoSweep'
      , 'DailyBalanceRekening'
    ])
  )
  dictParam.update({
      'tmp_autoclose_candidate' : config.MapDBTableName('tmp.autoclose_candidate')
    , 'tmp_autoclose_zerobalance_candidate' : config.MapDBTableName('tmp.autoclose_zerobalance_candidate')
    , 'tmp_autoclose_card_candidate' : config.MapDBTableName('tmp.autoclose_card_candidate')
    , 'tmp_savingplan_autoclose_candidate' : config.MapDBTableName('tmp.savingplan_autoclose_candidate')
    , 'tmp_detil_candidate'     : config.MapDBTableName('tmp.detil_candidate')
    , 'tmp_seq_detil_candidate' : config.MapDBTableName('tmp.seq_detil_candidate')
    , 'tmp_tran_candidate'      : config.MapDBTableName('tmp.tran_candidate')
    , 'tmp_seq_tran_candidate'  : config.MapDBTableName('tmp.seq_tran_candidate')
    , 'tmp_tx_balance'          : config.MapDBTableName('tmp.tx_balance')
    , 'tmp_seq_tx_balance'      : config.MapDBTableName('tmp.seq_tx_balance')
    , 'rep_rekeningrencana_penutupan' : config.MapDBTableName('report.rekeningrencana_penutupan')
    , 'rep_rekening_tutupotomatis' : config.MapDBTableName('report.rekening_tutupotomatis')
    , 'rep_seq_rekening_tutupotomatis' : config.MapDBTableName('report.seq_rekening_tutupotomatis')
    , 'rep_kartu_tutupotomatis' : config.MapDBTableName('report.kartu_tutupotomatis')
    , 'rep_seq_kartu_tutupotomatis' : config.MapDBTableName('report.seq_kartu_tutupotomatis')
    , 'cms_card' : config.MapDBTableName('cms.card')
    , 'cms_historycardstatus' : config.MapDBTableName('cms.HistoryCardStatus')
    , 'cms_seq_historycardstatus' : config.MapDBTableName('cms.Seq_HistoryCardStatus')
    , 'fin_FinAccount' : config.MapDBTableName('financing.FinAccount')
    , 'Kode_Transaksi'          : 'TTR'
  })
  
  preparetmptable(config, dictParam)
  selectData(config, dictParam)
  batch_sql.createCoreTransaction(config, dictParam)  
  batch_sql.updateBalanceFromTransaction(config, dictParam)
  
  batch_sql.setTodayForJournal(config, dictParam, oToday)
  batch_sql.createJournalTransaction(config, dictParam)
  postProcess(config, dictParam)
  
  printOut('Auto close process done!')

def preparetmptable(config, params):
  printOut( 'Truncate autoclose_candidate tables')
  dbutil.runSQL(config, '''TRUNCATE TABLE {tmp_autoclose_candidate}'''.format(**params))
  printOut( 'Truncate autoclose_zerobalance_candidate tables')
  dbutil.runSQL(config, '''TRUNCATE TABLE {tmp_autoclose_zerobalance_candidate}'''.format(**params))
  printOut( 'Truncate savingplan_autoclose_candidate tables')
  dbutil.runSQL(config, '''TRUNCATE TABLE {tmp_savingplan_autoclose_candidate}'''.format(**params))
  printOut( 'Truncate autoclose_card_candidate tables')
  dbutil.runSQL(config, '''TRUNCATE TABLE {tmp_autoclose_card_candidate}'''.format(**params))
  
  
  """
  printOut( 'Create autoclose_candidate tables')
  try:
    dbutil.runSQL(config, '''DROP TABLE {tmp_autoclose_candidate}'''.format(**params))
  except:
    pass

  dbutil.runSQL(config, '''
    create table {tmp_autoclose_candidate}
    (
       Nomor_Rekening varchar2(20) primary key
       , kode_cabang varchar2(20)
       , kode_valuta varchar2(10)
       , kode_produk varchar2(10)
       , saldo number(38, 16) 
       , process_status integer
       , process_desc varchar2(100)
      ) 
    '''.format(**params)
  )
  
  
  create table {tmp_autoclose_card}
    (
       nomor_kartu varchar2(20) primary key
       , Nomor_Rekening varchar2(20) 
       , status_kartu integer
       , process_status integer
       , process_desc varchar2(100)
      ) 
      
       
  
  printOut( 'Create savingplan_autoclose_candidate tables')
  try:
    dbutil.runSQL(config, '''DROP TABLE {tmp_savingplan_autoclose_candidate}'''.format(**params))
  except:
    pass

  dbutil.runSQL(config, '''
    create table {tmp_savingplan_autoclose_candidate}
    (
       Nomor_Rekening varchar2(20) primary key
       , Nomor_Rekening_Induk varchar2(20)
       , kode_cabang varchar2(10)
       , kode_valuta varchar2(10)
       , kode_produk varchar2(10)
       , saldo number(38, 16)
       , is_maturity varchar2(1)
       , description varchar2(100)
       , id_transaksi integer
       , id_register integer
       , id_recurrent integer         
      ) 
    '''.format(**params)
  )
  """
  
def selectData(config, dictParam):
  SQLFlows = [
      'AC_SelectZeroBalance'
    , 'AC_SelectAccount'
    , 'AC_SelectCard'
    , 'AC_SelectForUpdate'
    , 'AC_CheckSIAsDebetAccount'
    , 'AC_CheckSIAsCreditAccount'
    , 'AC_CheckDepositProfitDistAccount'
    , 'AC_CheckDepositMaturityAccount'
    , 'AC_CheckAutoSave'
    , 'AC_CheckSAVPlanSourceAccount'
    , 'AC_CheckSAVPlanMaturityAccount'
    , 'AC_CheckFinAccount'
    , 'AC_AutoCloseAccount'
    , 'AC_CheckCardCandidateFailed'
    , 'AC_CheckCardAccountStillActive'
    , 'AC_AutoCloseCard'    
    , 'AC_CreateHistoryCardStatus'
    # EOD Tabungan Rencana di nonaktifkan sementara
    
    #, 'SAVPlan_SelectArrearOverLimit' # Select rekening rencana yang 3 bulan menunggak SI
    #, 'SAVPlan_SelectMaturity' # Select rekening rencana yang jatuh tempo    
    #, 'SAVPlan_SelectForUpdate' 
    #, 'SAVPlan_AutoClose' # Tutup rekening rencana yang 3 bulan menunggak SI
    #, 'SAVPlan_AutoCloseTranCandidate' # Transaksi Tutup rekening rencana 
    #, 'SAVPlan_AutoCloseDebetAccount' # Detil Transaksi Debet rekening rencana 
    #, 'SAVPlan_AutoCloseCreditAccount' # Detil Transaksi Kredit rekening induk dari rekening rencana
  ]
  
  batch_sql.executeFlow(config, SQLFlows, dictParam)

def postProcess(config, dictParam):
  SQLFlows = [
    'AC_SaveReportSuccess'
    , 'AC_SaveReportAll'
    , 'AC_SetClosingDate'
    , 'AC_SaveReportCardAll'
    # EOD Tabungan Rencana di nonaktifkan sementara
    #, 'SAVPlan_SaveInfoCloseAccount' # Simpan InfoPenutupanRekening 
    #, 'SAVPlan_SaveReportAutoClose' # Simpan Report Penutupan Rekening Rencana Otomatis
    #, 'SAVPlan_DisableRecurrentTrans' # Non Aktifkan RecurrentTransaction
    #, 'SAVPlan_DisableRegisterLayanan' # Non Aktifkan Registerlayanan
    #, 'SAVPlan_SetClosingDate' # Set Tanggal Tutup Rekening Rencana
    
  ]
  
  batch_sql.executeFlow(config, SQLFlows, dictParam)

SQL_RESOURCES = {
  'AC_SelectZeroBalance': '''
    insert into {tmp_autoclose_zerobalance_candidate} (
      nomor_rekening
      , kode_cabang
      , kode_valuta
      , saldo
      , kode_produk
      , tgl_saldo_nol
      , param_hari_tutup_oto
    )
    select
      t.nomor_rekening
      , t.kode_cabang
      , t.kode_valuta
      , t.saldo
      , p.kode_produk
      , ( select max(db.balance_date)
          from {DailyBalanceRekening} db
          where db.nomor_rekening = t.nomor_rekening
            and db.balance_field  = 'saldo'
            and db.balance        < 0.01
            and db.balance_date   < {Today}
        ) as tgl_saldo_nol
      , COALESCE(
          CASE WHEN p.is_custom_tutup_oto = 'T' THEN p.Jumlah_Hari_Tutup_Otomatis ELSE NULL END
          , {DefaultHariTutup}
        ) as param_hari_tutup_oto
    from
      {RekeningTransaksi} t, {RekeningLiabilitas} r
      , {Produk} p
    where
      t.nomor_rekening = r.nomor_rekening
      and r.kode_produk = p.kode_produk
      and t.kode_jenis in ('SAV', 'CA')
      and t.status_rekening <> 3
      and t.kode_valuta = 'IDR'
      and r.jenis_rekening_liabilitas <> 'D'
      and saldo < 0.01
      and jenis_rekening_liabilitas <> 'R'
      and COALESCE(CASE WHEN p.is_custom_tutup_oto = 'T' THEN p.Is_Tutup_Otomatis_Dormant ELSE 'T' END, 'T') = 'T'
  '''
  ,
  'AC_SelectAccount': '''
    insert into {tmp_autoclose_candidate} (
      nomor_rekening
      , kode_cabang
      , kode_valuta
      , saldo
      , kode_produk
      , process_status
      , process_desc
    )
    select
      c.nomor_rekening
      , c.kode_cabang
      , c.kode_valuta 
      , c.saldo
      , c.kode_produk
      , 1
      , 'Rekening Saldo Nol Lebih dari ketentuan limit'
    from
      {tmp_autoclose_zerobalance_candidate} c, {Produk} p
    where 
      c.kode_produk = p.kode_produk
      and exists ( 
          select db1.nomor_rekening
             , db1.balance
          from 
             {DailyBalanceRekening} db1                 
             , ( select nomor_rekening, max(balance_date) as balance_date 
                 from {DailyBalanceRekening} 
                 where balance_date < {Today}
                    and balance_field = 'saldo' 
                 group by nomor_rekening
                ) db2
          where db1.Nomor_Rekening = db2.Nomor_Rekening
                and db1.balance_field = 'saldo'
                and db1.balance_date = db2.balance_date
                and db1.nomor_rekening = c.nomor_rekening
                and db1.balance < 0.01
                and db1.balance_date < ({Today} - COALESCE(CASE WHEN p.is_custom_tutup_oto = 'T' THEN p.Jumlah_Hari_Tutup_Otomatis ELSE NULL END, {DefaultHariTutup}))
         )
  '''
  ,
  'AC_SelectCard' : '''
    insert into {tmp_autoclose_card_candidate} t
    ( nomor_kartu , status_kartu, nomor_rekening, process_status, process_desc)
    select cardid , cardstate, t.nomor_rekening, 1, 'Tutup Kartu Otomatis by Sistem karena Rekening Dorman'
    from {cms_card} c, {tmp_autoclose_candidate} t
    where 
      (c.savingaccountno = t.nomor_rekening 
        OR c.currentaccountno = t.nomor_rekening)
      and cardstate in (1, 5, 6, 7)
  '''
  , 
  'AC_SelectForUpdate': '''
    select 1 from {RekeningTransaksi} r
    where exists (
      select 1 from {tmp_autoclose_candidate} p
      where p.nomor_rekening = r.nomor_rekening)
    FOR UPDATE NOWAIT '''
  ,
  'AC_CheckSIAsDebetAccount' : '''
    update {tmp_autoclose_candidate} p
    set process_status = 2
        , process_desc = 'Rekening merupakan rekening debet untuk SI yang masih aktif'
    where 
      process_status = 1
      and exists (
         select 1 from     
          {RegisterLayanan} r, {RegisterRT} rr  
         where r.id_register = rr.id_register
          and r.nomor_rekening_layanan = p.nomor_rekening
          and r.Status_Register_Layanan = 'A'
      )
  '''
  ,
  'AC_CheckSIAsCreditAccount' : '''
    update {tmp_autoclose_candidate} p
    set process_status = 2
        , process_desc = 'Rekening merupakan rekening kredit untuk SI yang masih aktif'
    where 
      process_status = 1
      and exists (
         select 1 from     
          {RegisterLayanan} r, {RegisterRT} rr  
         where r.id_register = rr.id_register
          and rr.nomor_rekening_kredit = p.nomor_rekening
          and r.Status_Register_Layanan = 'A'
      )
  '''
  ,
  'AC_CheckDepositProfitDistAccount' : '''
    update {tmp_autoclose_candidate} p
    set process_status = 2
        , process_desc = 'Rekening merupakan rekening penampung bagi hasil deposito'
    where 
      process_status = 1
      and exists (      
            select 1
            from {RekeningTransaksi} rt
               , {RekeningLiabilitas} rl
            where rt.nomor_rekening = rl.nomor_rekening
                and status_rekening = 1
                and disposisi_bagi_hasil = 'P'
              and Nomor_Rekening_Disposisi = p.nomor_rekening
      )
  '''
  ,
  'AC_CheckDepositMaturityAccount' : '''
    update {tmp_autoclose_candidate} p
    set process_status = 2
        , process_desc = 'Rekening merupakan rekening penampung jatuh tempo deposito'
    where 
      process_status = 1
      and exists (      
            select 1
            from {RekeningTransaksi} rt
               , {Deposito} d
             where rt.nomor_rekening = d.nomor_rekening
                and rt.status_rekening = 1
                and d.disposisi_nominal = 'P'
                and d.rekening_disposisi = p.nomor_rekening
      )
  '''
  ,'AC_CheckAutoSave' :'''
    update {tmp_autoclose_candidate} p
    set process_status = 2
        , process_desc = 'Rekening masih memiliki register autosave yang masih aktif'
    where 
      process_status = 1       
       and exists (
       select 1
       from {RegisterLayanan} r
            , {RegisterAutoSweep} rr
       where r.id_register = rr.id_register
          and r.Status_Register_Layanan = 'A'
          and ( rr.Nomor_Rekening_Tujuan = p.Nomor_Rekening
                or r.Nomor_Rekening_Layanan = p.Nomor_Rekening )
       
       )
  '''
  ,
  'AC_CheckSAVPlanSourceAccount' : '''
    update {tmp_autoclose_candidate} p
    set process_status = 2
        , process_desc = 'Rekening merupakan rekening induk untuk tabungan rencana yang aktif'
    where 
       process_status = 1
       and exists (
           select 1
           from {RekeningTransaksi} r
              , {RekeningRencana} rr  
           where r.nomor_rekening = rr.nomor_rekening
              and rr.nomor_rekening_induk = p.nomor_rekening
              and r.status_rekening = 1   
       )
  '''
  ,
  'AC_CheckSAVPlanMaturityAccount' : '''
    update {tmp_autoclose_candidate} p
    set process_status = 2
        , process_desc = 'Rekening merupakan rekening pencairan untuk tabungan rencana yang aktif'
    where 
       process_status = 1
       and exists (
           select 1
           from {RekeningTransaksi} r
              , {RekeningRencana} rr  
           where r.nomor_rekening = rr.nomor_rekening
              and rr.nomor_rekening_pencairan = p.nomor_rekening
              and r.status_rekening = 1   
       )
  '''
  ,
  'AC_CheckFinAccount' : '''
    update {tmp_autoclose_candidate} p
    set process_status = 2
        , process_desc = 'Rekening merupakan rekening sumber autodebet pembiayaan yang masih aktif atau write off'
    where 
       process_status = 1
       and exists (
           select 1
           from {RekeningTransaksi} r
              inner join {fin_FinAccount} f  on r.nomor_rekening = f.nomor_rekening
           where f.norek_paymentsrc = p.nomor_rekening
              and r.status_rekening in (1,8)   
       )    
  '''
  ,  
  'AC_AutoCloseAccount': '''
    update {RekeningTransaksi} r
    set status_rekening = 3
    where exists (
      select 1 from {tmp_autoclose_candidate} p
      where p.nomor_rekening = r.nomor_rekening
        and p.process_status = 1
      )
    '''
  ,
  'AC_CheckCardCandidateFailed' : '''
    update {tmp_autoclose_card_candidate} c
    set process_status = 2
       , process_desc = 'Proses Tutup Rekening Gagal'
    where exists (
        select 1 from 
          {tmp_autoclose_candidate} p
        where p.nomor_rekening = c.nomor_rekening
          and p.process_status = 2
    ) and process_status = 1
  '''
  ,
  'AC_CheckCardAccountStillActive' : '''
    update {tmp_autoclose_card_candidate} c
    set process_status = 2
       , process_desc = 'Rekening masih aktif'
    where     
       exists (
              select 1 from 
                {cms_card} ca
                , {RekeningTransaksi} rt
              where (rt.nomor_rekening = ca.savingaccountno
                    or rt.nomor_rekening = ca.currentaccountno)
                and rt.status_rekening in (1,2)
                and ca.cardid = c.nomor_kartu
              ) 
       and process_status = 1
  '''
  ,
  'AC_AutoCloseCard' : '''
    update {cms_card} c
    set cardstate = 4
    where 
      cardstate in (1, 5, 6, 7)
      and 
      exists (
        select 1 from 
          {tmp_autoclose_card_candidate} p
        where p.nomor_kartu = c.cardid
          and p.process_status = 1
      )
  '''
  ,'AC_CreateHistoryCardStatus' : '''
     insert into {cms_historycardstatus}
         ( id_historycard
           , cardid
           , user_change
           , changedate
           , description
           , cardstate_before
           , cardstate_after
           , customername
           , customerno
         )
     select {cms_seq_historycardstatus}.nextval
          , t.nomor_kartu
          , 'SYSTEM'
          , {Today}
          , t.process_desc
          , t.status_kartu
          , 4
          , c.customername
          , c.customerno     
     from {cms_card} c, {tmp_autoclose_card_candidate} t
     where t.nomor_kartu = c.cardid
        and t.process_status = 1     
  '''    
  ,
  'SAVPlan_SelectMaturity' : '''
    insert into {tmp_savingplan_autoclose_candidate} (
      nomor_rekening
      , kode_cabang
      , kode_valuta
      , saldo
      , kode_produk
      , nomor_rekening_induk
      , id_transaksi
      , is_maturity
      , description
      , id_register
      , id_recurrent            
    )
    select
      t.nomor_rekening
      , t.kode_cabang
      , t.kode_valuta 
      , t.saldo
      , p.kode_produk
      , rr.Nomor_Rekening_Induk
      , {Seq_Transaksi}.nextval
      , 'T'
      , 'REKENING RENCANA JATUH TEMPO'
      , regl.id_register
      , regrt.RecId       
    from
      {RekeningTransaksi} t
      , {RekeningLiabilitas} r
      , {RekeningRencana} rr
      , {StandingInstruction} si
      , {RecurrentTransaction} rt      
      , {Produk} p
      , {ProdukRencana} pr
      , {RegisterRT} regrt
      , {RegisterLayanan} regl
    where 
      t.nomor_rekening = r.nomor_rekening
      and r.nomor_rekening = rr.nomor_rekening
      and r.kode_produk = p.kode_produk
      and si.CreditAccountNo = t.nomor_rekening
      and si.InstructionId = rt.InstructionId
      and p.kode_produk = pr.kode_produk
      and rt.RecId = regrt.RecId
      and regl.id_register = regrt.id_register      
      and pr.jenis_rencana = 'R' 
      and t.kode_valuta = 'IDR'
      and t.status_rekening <> 3
      and rr.id_register = regrt.id_register
      and rr.tanggal_jatuh_tempo <= {Today}
      and not exists(select 1 from {tmp_savingplan_autoclose_candidate} where nomor_rekening = r.nomor_rekening)
  '''    
  ,
  'SAVPlan_SelectArrearOverLimit' : '''
    insert into {tmp_savingplan_autoclose_candidate} (
      nomor_rekening
      , kode_cabang
      , kode_valuta
      , saldo
      , kode_produk
      , nomor_rekening_induk
      , id_transaksi
      , is_maturity
      , description
      , id_register
      , id_recurrent                  
    )
    select
      t.nomor_rekening
      , t.kode_cabang
      , t.kode_valuta 
      , t.saldo
      , p.kode_produk
      , rr.Nomor_Rekening_Induk
      , {Seq_Transaksi}.nextval
      , 'F'
      , 'REKENING RENCANA GAGAL DEBET 3 Bulan'
      , regl.id_register
      , regrt.RecId              
    from
      {RekeningTransaksi} t
      , {RekeningLiabilitas} r
      , {RekeningRencana} rr
      , {StandingInstruction} si
      , {RecurrentTransaction} rt      
      , {Produk} p
      , {RegisterRT} regrt
      , {RegisterLayanan} regl      
    where 
      t.nomor_rekening = r.nomor_rekening
      and r.nomor_rekening = rr.nomor_rekening
      and r.kode_produk = p.kode_produk
      and si.CreditAccountNo = t.nomor_rekening
      and si.InstructionId = rt.InstructionId
      and rt.RecId = regrt.RecId
      and regl.id_register = regrt.id_register             
      and t.kode_valuta = 'IDR'
      and t.status_rekening <> 3
      and rr.id_register = regrt.id_register
      and rt.status_data = 'A'
      and rt.tgl_proses_berikutnya < add_months({Today}, -3)
      and not exists(select 1 from {tmp_savingplan_autoclose_candidate} where nomor_rekening = r.nomor_rekening)
  '''
  , 
  'SAVPlan_SelectForUpdate': '''
    select 1 from {RekeningTransaksi} r
    where exists (
      select 1 from {tmp_savingplan_autoclose_candidate} p
      where p.nomor_rekening = r.nomor_rekening)
    FOR UPDATE NOWAIT '''
  ,
  'SAVPlan_AutoClose' : '''
    update {RekeningTransaksi} r
    set status_rekening = 3
    where exists (
      select 1 from {tmp_savingplan_autoclose_candidate} p
      where p.nomor_rekening = r.nomor_rekening)
  '''
  ,
  'SAVPlan_AutoCloseTranCandidate' : '''
    insert into {tmp_tran_candidate}
    (
      id_temp
      , id_transaksi, kode_cabang, description
      , kode_transaksi
    )
    select 
      {tmp_seq_tran_candidate}.nextval
      , p.id_transaksi, p.Kode_Cabang
      , p.description || ' - ' || p.nomor_rekening
      , {Kode_Transaksi!r}
    from 
      {tmp_savingplan_autoclose_candidate} p
    where 
      p.saldo > 0.0
  '''
  ,
  'SAVPlan_AutoCloseDebetAccount': '''
    insert into {tmp_detil_candidate}
    (
      id_temp
      , id_transaksi          , id_detil_transaksi
      , nomor_rekening        , kode_tx_class
      , mnemonic              , amount
      , kode_kurs             , nilai_kurs
      , description           
      , kode_cabang
      , kode_valuta           
      , kode_jurnal
    )
    select 
      {tmp_seq_detil_candidate}.nextval
      , p.id_transaksi        , {Seq_DetilTransaksi}.nextval
      , p.nomor_rekening      , Null
      , 'D'                   , p.saldo
      , Null                  , 1.0
      , p.description || ' - ' || p.nomor_rekening
      , p.Kode_Cabang
      , p.Kode_Valuta         
      , '10'        
    from 
      {tmp_savingplan_autoclose_candidate} p
    where p.saldo > 0.0
  '''
  ,
  'SAVPlan_AutoCloseCreditAccount': '''
    insert into {tmp_detil_candidate}
    (
      id_temp
      , id_transaksi          , id_detil_transaksi
      , nomor_rekening        , kode_tx_class
      , mnemonic              , amount
      , kode_kurs             , nilai_kurs
      , description           
      , kode_cabang
      , kode_valuta           
      , kode_jurnal
    )
    select 
      {tmp_seq_detil_candidate}.nextval
      , p.id_transaksi         , {Seq_DetilTransaksi}.nextval
      , p.nomor_rekening_induk , Null
      , 'C'                    , p.saldo
      , Null                   , 1.0
      , p.description || ' - ' || p.nomor_rekening
      , p.Kode_Cabang
      , p.Kode_Valuta         
      , '10'        
    from 
      {tmp_savingplan_autoclose_candidate} p
    where p.saldo > 0.0
  '''   
  ,
  'AC_SaveReportSuccess': '''
    insert into {InfoPenutupanRekening} (
      Nomor_Rekening
      , Tanggal_Proses
      , Nilai_Transaksi
      , UserInput
      , UserOtorisasi
      , Keterangan
    )
    select
      Nomor_Rekening
      , {Today}
      , saldo
      , 'SYSTEM'
      , 'SYSTEM'
      , process_desc
    from {tmp_autoclose_candidate} r
    where not exists (select 1 from {InfoPenutupanRekening} where nomor_rekening = r.nomor_rekening)
       and process_status = 1
  '''
  , 'AC_SaveReportAll' : '''
    insert into {rep_rekening_tutupotomatis}
    ( id_report
      , nomor_rekening
      , tanggal_proses
      , status_proses
      , keterangan
      , tgl_saldo_nol
      , param_hari_tutup_oto
    )
    select
      {rep_seq_rekening_tutupotomatis}.nextval
      , c.nomor_rekening
      , {Today}
      , c.process_status
      , c.process_desc
      , z.tgl_saldo_nol
      , z.param_hari_tutup_oto
    from {tmp_autoclose_candidate} c
    left join {tmp_autoclose_zerobalance_candidate} z
      on z.nomor_rekening = c.nomor_rekening
  '''
  ,
  'SAVPlan_SaveInfoCloseAccount' : '''
    insert into {InfoPenutupanRekening} (
      Nomor_Rekening
      , Tanggal_Proses
      , Nilai_Transaksi
      , UserInput
      , UserOtorisasi
      , Keterangan
    )
    select
      Nomor_Rekening
      , {Today}
      , saldo
      , 'SYSTEM'
      , 'SYSTEM'
      , description            
    from {tmp_savingplan_autoclose_candidate} r
    where not exists (select 1 from {InfoPenutupanRekening} where nomor_rekening = r.nomor_rekening)
  '''
  ,
  'SAVPlan_SaveReportAutoClose' : '''
    insert into {rep_rekeningrencana_penutupan} (
      Nomor_Rekening
      , Tanggal_Proses
      , Nilai_Transaksi
      , Is_Jatuhtempo 
      , Keterangan
    )
    select
      Nomor_Rekening
      , {Today}
      , saldo
      , is_maturity
      , description            
    from {tmp_savingplan_autoclose_candidate}
  '''
  , 
  'SAVPlan_DisableRecurrentTrans' : '''
     update {RecurrentTransaction} r 
     set status_data = 'N' 
     where exists (select 1 from {tmp_savingplan_autoclose_candidate} where id_recurrent = r.recid)
  '''
  , 
  'SAVPlan_DisableRegisterLayanan' : '''
     update {RegisterLayanan} r 
     set Status_Register_Layanan = 'T' 
     where exists (select 1 from {tmp_savingplan_autoclose_candidate} where id_register = r.id_register)
  '''
  ,
  'AC_SetClosingDate' : '''
     update {RekeningLiabilitas} r 
     set Tanggal_Tutup = {Today}
     where exists (select 1 from {tmp_autoclose_candidate} where nomor_rekening = r.nomor_rekening and process_status = 1 )
  '''
  ,
  'AC_SaveReportCardAll' : '''
     insert into {rep_kartu_tutupotomatis}
      ( id_report
        , nomor_kartu
        , nomor_rekening
        , tanggal_proses
        , status_proses
        , keterangan 
      ) 
      select 
        {rep_seq_kartu_tutupotomatis}.nextval
        , nomor_kartu
        , nomor_rekening
        , {Today}
        , process_status
        , process_desc
      from {tmp_autoclose_card_candidate}
  '''
  ,
  'SAVPlan_SetClosingDate' : '''
     update {RekeningLiabilitas} r 
     set Tanggal_Tutup = {Today}
     where exists (select 1 from {tmp_savingplan_autoclose_candidate} where nomor_rekening = r.nomor_rekening )
  '''
}



### DDL CREATE TABLE
"""
   create table ibankrep.rekeningrencana_penutupan
   (
       nomor_rekening varchar2(20) primary key
       , tanggal_proses timestamp(6)
       , nilai_transaksi number(22,8)
       , is_jatuhtempo varchar2(1)
       , keterangan varchar2(100) 
   )
   
   create table ibanktmp.autoclose_candidate
    (
       Nomor_Rekening varchar2(20) primary key
       , kode_cabang varchar2(20)
       , kode_valuta varchar2(10)
       , kode_produk varchar2(10)
       , saldo number(38, 8) 
      )

   create table ibanktmp.autoclose_zerobalance_candidate
    (
       Nomor_Rekening varchar2(20) primary key
       , kode_cabang varchar2(20)
       , kode_valuta varchar2(10)
       , kode_produk varchar2(10)
       , saldo number(38, 8) 
      )
      
    create table ibanktmp.savingplan_autoclose_candidate
    (
       Nomor_Rekening varchar2(20) primary key
       , Nomor_Rekening_Induk varchar2(20)
       , kode_cabang varchar2(10)
       , kode_valuta varchar2(10)
       , kode_produk varchar2(10)
       , saldo number(38, 8)
       , is_maturity varchar2(1)
       , description varchar2(100)
       , id_transaksi integer
       , id_register integer
       , id_recurrent integer         
      )
"""