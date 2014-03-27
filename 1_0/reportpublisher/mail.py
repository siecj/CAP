import os
import smtplib
#import mandrill

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.utils import COMMASPACE,formatdate
from email import encoders

def send_mail(fro, to, subject, text, files=[]):
    #assert type(server) == dict 
    assert type(to) == list
    assert type(files) == list
    
    msg = MIMEMultipart('alternative')
    
    msg['Subject'] = subject
    msg['From'] = 'CAP_TEAM@thomsonreuters.com' # Your from name and email address
    msg['To'] = ','.join(to)
    #print msg['To']
    msg['Date'] = formatdate(localtime=True)
    msg.attach(MIMEText(text, 'html', 'utf-8'))
    
    for file in files:
        data = open(file, 'rb')
        part = MIMEBase('application', 'octet-stream') #'octet-stream': binary data 
        part.set_payload(data.read()) 
        data.close()
        encoders.encode_base64(part) 
        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file)) 
        msg.attach(part)
        
    s = smtplib.SMTP('10.80.81.132', 25)    
    #s.login(username, password)
    s.sendmail(fro, to, msg.as_string())
    s.quit()
    
    ''' mandrill web api way
    try:
        mandrill_client = mandrill.Mandrill('ElZncQlS9DXqotj0TMjuJA')
        #to = ['chao.xie@thomsonreuters.com', 'yang.yang@thomsonreuters.com']
        raw_message = msg.as_string()
        #print raw_message
        result = mandrill_client.messages.send_raw(raw_message, from_email=None, from_name='Chao Xie', to=None, async=False, ip_pool='Main Pool', send_at=None, return_path_domain=None)

    except mandrill.Error, e:
        # Mandrill errors are thrown as exceptions
        print 'A mandrill error occurred: %s - %s' % (e.__class__, e)
        # A mandrill error occurred: <class 'mandrill.UnknownSubaccountError'> - No subaccount exists with the id 'customer-123'    
        raise
    '''

def send_mail_ex(to, subject, content, fro='CAP_TEAM@thomsonreuters.com', cc=[], bcc=[], images=[], attaches=[]):
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot['From'] = fro # Your from name and email address
    msgRoot['To'] = ','.join(to)
    msgRoot['Cc'] = ','.join(cc)
    msgRoot['Bcc'] = ','.join(bcc)

    # Add image html into body
    ind = 1
    for img in images:
        content += '<br/><br/><img src="cid:image' + str(ind) + '" />'
        ind += 1

    # Body
    msgText = MIMEText(content, 'html', 'utf-8')
    msgRoot.attach(msgText)

    # Image in body
    ind = 1
    for img in images:
        fp = open(img, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<image'+str(ind)+'>')
        msgRoot.attach(msgImage)
        ind += 1

    # Attachment
    for f in attaches:
        data = open(f, 'rb')
        part = MIMEBase('application', 'octet-stream') #'octet-stream': binary data 
        part.set_payload(data.read()) 
        data.close()
        encoders.encode_base64(part) 
        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(f)) 
        msgRoot.attach(part)

    s = smtplib.SMTP('10.80.81.132', 25)
    s.sendmail(fro, [','.join(to), ','.join(cc), ','.join(bcc)], msgRoot.as_string())
    s.quit()

    
if __name__ == "__main__":
    cclist = ['jiu.chen@thomsonreuters.com']
    to = ['jiu.chen@thomsonreuters.com', 'hongfeng.yao@thomsonreuters.com']
    subject = "Python Email with Pictures"
    text1 = '<b>HTML content</b><br><a href="http://www.baidu.com">baidu</a><br>'
    att = ['tickets-per-region.png']
    images = ['total-tickets.png', 'tickets-per-system.png']
    # send_mail(fro, to, subject, text, files)
    send_mail_ex(to, subject, text1, images=images, cc=cclist)
