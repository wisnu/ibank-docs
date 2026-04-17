import sys
import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.util.modman as modman
import com.ihsan.foundation.appserver as appserver

#-- UPDATE TANGGAL TRANSAKSI TERAKHIR
#-- script ini bertujuan untuk melakukan update tanggal transaksi terakhir yang ditrigger oleh nasabah
#-- tabel parametertransaksiumum akan dimanfaatkan untuk klasifikasi kode transaksi yang ditrigger oleh nasabah atau oleh system ( yang ditrigger oleh system 'tag_batch'-nya SYS)
#-- tanggal transaksi terakhir akan dicatat dalam 3 bagian 
#-- * Tgl_Trans_Cabang_Terakhir = seluruh transaksi yang ditrigger oleh nasabah via front office (teller, BO, CS)
#-- * Tgl_Trans_Echannel_Terakhir = seluruh transaksi yang ditrigger oleh nasabah via transaksi channel (ATM, Mobile Banking dsb)
#-- * Tgl_Transaksi_Terakhir = seluruh transaksi yang ditrigger oleh nasabah via front office + channel
#-- 
#-- NOTES : Proses dilakukan memanfaatkan data transaksi dan detiltransaksi (transaksi H+0) sebelum pindah ke tabel histtransaksi, 
#--         agar data yang diproses lebih sedikit dibanding kalau sudah pindah ke histtransaksi       

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
config  = appserver.ActiveConfig
app     = config.AppObject
_CONSOLE = False
    
def DAFScriptMain(config, parameter, returns):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  
  global _CONSOLE
  
  _CONSOLE = False
  batch_sql._CONSOLE = False
  batch_sql.app      = app
  #batch_sql.updateResources(SQL_RESOURCES)
  
  main(config)
  returns.CreateValues(['Is_Err', 0])

  return 1

def main(config):
  helper = phelper.PObjectHelper(config)
  periodHelper = helper.CreateObject('PeriodHelper')

  oToday = periodHelper.GetToday()
  oNextDay = oToday.NextWorkDay()
    
  app = config.AppObject
  app.ConCreate('out')

  #####--- 1. UPDATE LAST TX DATE ---- #######
  
  batch_sql.printOut('>> Update last trx date')
  params = {
    'RekeningLiabilitas': config.MapDBTableName('RekeningLiabilitas')
    , 'Transaksi': config.MapDBTableName('Transaksi')
    , 'DetilTransaksi': config.MapDBTableName('DetilTransaksi')
    , 'ParameterTransaksiUmum' : config.MapDBTableName('ParameterTransaksiUmum')    
    , 'Today': sutil.toDate(config, oToday.GetDate())
    , 'NextDay': sutil.toDate(config, oNextDay.GetDate())
  }
  
  
  #####--- 1. UPDATE Tgl_Transaksi_Terakhir ---- #######
  batch_sql.printOut('>>> Update Tgl_Transaksi_Terakhir')
  
  # -- Seluruh kode transaksi yg tidak termasuk dalam tag_batch SYS diupdate ke Tgl_Transaksi_Terakhir
  # -- kalau tag_batch SYS dianggap transaksi yang ditrigger oleh system
  # -- jadi kode transaksi selain itu dianggap aktifitas nasabah
   
  batch_sql.runSQL(config, '''
  	UPDATE {RekeningLiabilitas} 
  	SET Tgl_Transaksi_Terakhir = {Today} 
  	WHERE 
  		nomor_rekening in (
        select d.nomor_rekening 
        from {Transaksi} t 
          inner join {DetilTransaksi} d on d.id_transaksi = t.id_transaksi
          left join {ParameterTransaksiUmum} ptu on t.kode_transaksi = ptu.kode_transaksi
        where t.status_otorisasi  = 1
          and NVL(ptu.is_exclude_aktivitas_nasabah, 'F') = 'F'
      )   
  '''.format(**params))  
  
  #####--- 2. UPDATE Tgl_Trans_Cabang_Terakhir dan Tgl_Trans_Echannel_Terakhir ---- #######
  batch_sql.printOut('>>> Update Tgl_Trans_Cabang_Terakhir dan Tgl_Trans_Echannel_Terakhir')
  
  # log tgl transaksi akan dibagi lagi menjadi :
  # - 'Tgl_Trans_Cabang_Terakhir' transaksi yg dilakukan di front office  --> tag_batch BO , TLR, CS  
  # - 'Tgl_Trans_Echannel_Terakhir'  transaksi yg dilakukan di channel    --> selain tag_batch BO , TLR, CS, SYS


  batch_sql.runSQL(config, '''
    UPDATE {RekeningLiabilitas} 
  	SET Tgl_Trans_Cabang_Terakhir = {Today} 
  	WHERE 
  		nomor_rekening in (
        select d.nomor_rekening 
        from {Transaksi} t 
          inner join {DetilTransaksi} d on d.id_transaksi = t.id_transaksi
        where t.kode_transaksi in (
            select kode_transaksi from {ParameterTransaksiUmum} p where tag_batch in ('CS','TLR','BO') and kode_transaksi is not null
        )
      )   
  '''.format(**params))     			
  
  batch_sql.runSQL(config, '''
  	UPDATE {RekeningLiabilitas} 
  	SET Tgl_Trans_Echannel_Terakhir = {Today} 
  	WHERE 
  		nomor_rekening in (
        select d.nomor_rekening 
        from {Transaksi} t 
          inner join {DetilTransaksi} d on d.id_transaksi = t.id_transaksi
        where t.kode_transaksi not in (
            select kode_transaksi from {ParameterTransaksiUmum} p where tag_batch in ('CS','TLR','BO','SYS') and kode_transaksi is not null
        )
      )   
  '''.format(**params))
  
  app.ConWriteln('>>> Process Update last trx date selesai')
  
  return 1