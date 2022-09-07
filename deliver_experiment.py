import directories as DIR
import sender_data as DS
import asyncio
import ftplib
import os
import re

async def send(ftp, conv_path, gzfile):
    filename = gzfile
    if re.search(r'copy_\d+$', gzfile):
        filename = re.sub(r'copy_\d+$', '', gzfile)
        while filename in ftp.nlst():
            pass
     
    ftp.storbinary(f'STOR {filename}', open(f'{conv_path}{DIR.OUTPUT}{gzfile}', 'rb'))
  
      
async def send_all(ftp, conv_path, max_thread, gzfiles):
    semaphore = asyncio.Semaphore(max_thread)

    async def sema_func(cour):
        async with semaphore:
            return await cour
            
    return await asyncio.gather(*(sema_func(send(ftp, conv_path, gzfile)) for gzfile in gzfiles))
    

def deliver(conv_path):
    TIME_OUT=1000
    MAX_THREAD = 10
    
    ftp = ftplib.FTP(DS.HOST, timeout=TIME_OUT)
    ftp.login(DS.USR,DS.PSWD)
    ftp.cwd(DS.PATH)
    _, _, gzfiles = next(os.walk(conv_path + DIR.OUTPUT))
    
    try:
        asyncio.run(send_all(ftp, conv_path, MAX_THREAD, gzfiles))
    except Exception as e:
        raise Exception(str(e) + '\n')
    finally:    
        ftp.quit()
        
    return len(gzfiles)