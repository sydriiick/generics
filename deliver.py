import directories as DIR
import sender_data as DS
import ftplib
import os
import re

def deliver(conv_path):
    sent = 0
    TIME_OUT=1000
    BLOCK_SIZE=262144
    ftp = ftplib.FTP(DS.HOST, timeout=TIME_OUT)
    ftp.login(DS.USR,DS.PSWD)
    ftp.cwd(DS.PATH)
    _, _, gzfiles = next(os.walk(conv_path + DIR.OUTPUT))

    try:
        for gzfile in gzfiles:         
            ftp.storbinary('STOR ' + gzfile, open(f'{conv_path}{DIR.OUTPUT}{gzfile}', 'rb'), blocksize=BLOCK_SIZE)
            sent += 1
            
            
    except Exception as e:
        raise Exception('sent - ' + str(sent) + '\n' + str(e))
    finally:    
        ftp.quit()
        
    return sent