#!/usr/bin/env python

import datetime, os, imaplib, email, mimetypes, errno, logging, ConfigParser, sys

detach_dir = '/volume1/data/Samen/administratie/downloads/'

LOGGER_FILE = '/volume1/data/Joep/Projects/python/gmail_downloader/gmail_downloader.log'
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-15s %(levelname)-8s %(message)s',
                    filename=LOGGER_FILE)
LOGGER = logging.getLogger('gmail_downloader')
LOGGER.info('Start gmail downloader script')
config = ConfigParser.ConfigParser()
config.read('/volume1/data/Joep/Projects/python/gmail_downloader/config.cfg')

counter = 0

def process_mail(part, counter):
    filename = part.get_filename()

    if not filename:
        ext = mimetypes.guess_extension(part.get_content_type())
        if not ext:
            ext = '.bin'
        filename = 'part-%03d%s' % (counter, ext)

    att_dir = m["From"]
    att_dir = att_dir[att_dir.find("<")+1:-1]

    try:
        os.mkdir(detach_dir + att_dir)
    except:
        LOGGER.info('Directory already exists: %s' % att_dir)

    att_path = os.path.join(detach_dir+att_dir, filename)
    if os.path.isfile(att_path):
        filename = "double " + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + " - " + filename
        att_path = os.path.join(detach_dir+att_dir, filename)
    fp = open(att_path, 'wb')
    fp.write(part.get_payload(decode=True))
    fp.close()
    LOGGER.info('added: %s in folder: %s' % (filename, att_dir))
    

#log in and select the inbox
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(config.get('login', 'user'), config.get('login', 'password'))
mail.select('Administratie')

result, data = mail.uid('search', None, r'(X-GM-RAW "in:administratie has:attachment (newer_than:24h OR label:unread)")') 

for num in data[0].split():
    result, test = mail.uid('fetch', num, '(RFC822)')
    m = email.message_from_string(test[0][1])

    for part in m.walk():
        if part.get_content_maintype() == 'multipart': continue
        if part.get('Content-Disposition') is None: continue        
        if part.get('Content-Disposition')[:10] =='attachment':
            try:
                process_mail(part, counter)
                counter +=1
            except:
                LOGGER.error('Error processing mail')


LOGGER.info('finished script with: %02d parts' % counter)
mail.close()
mail.logout()