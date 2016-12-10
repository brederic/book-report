import smtplib
from email.mime.text import MIMEText



check_book_addrs = ['x+226502906786752@mail.asana.com', 'sarah@brentnrachel.com']

def send_check_book(subject, msg):
    fromaddr = 'brederic@gmail.com'
    sendIt(fromaddr, check_book_addrs, subject, msg)

def sendEmail(subject, msg):
    fromaddr = 'brederic@gmail.com'
    toaddrs  = 'brederic@gmail.com'
    #msg = 'There was a terrible error that occured and I wanted you to know!'
    print('Sending mail:' + msg)
    msg = u"\r\n".join([
  "From: " + fromaddr,
  "To: " + toaddrs,
  "Subject: [book-report] " + subject,
  "",
  msg
  ])
    send (toaddrs, msg)

def sendEmailTo(toaddrs, subject, msg):
    fromaddr = 'brederic@gmail.com'
    #msg = 'There was a terrible error that occured and I wanted you to know!'
    print('Sending mail:' + msg)
    msg = u"\r\n".join([
  "From: " + fromaddr,
  "To: " + toaddrs,
  "Subject: [book-report] " + subject,
  "",
  msg
  ])
    send (toaddrs, msg)
    
def sendIt(sender, recipients, subject, body):
    # Credentials (if needed)
    username = 'brederic@gmail.com'
    password = 'd3st1n0!'
    s = smtplib.SMTP('smtp.gmail.com:587')
    s.set_debuglevel(1)
    s.starttls()
    s.login(username,password)
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    msg["Cc"] = "brent@brentnrachel.com"

    s.sendmail(sender, recipients, msg.as_string())

def send(toaddrs, msg):
    fromaddr = 'brederic@gmail.com'


    # Credentials (if needed)
    username = 'brederic@gmail.com'
    password = 'd3st1n0!'

    # The actual mail send
    success = False
    while (success == False):
        try:
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.starttls()
            server.login(username,password)
            server.sendmail(fromaddr, toaddrs, msg.encode('utf-8'))
            server.quit()
            success = True
        except (OSError):
            print("Error sending email.... Will retry.")
            time.sleep(5)
        
# test
#sendEmail('test', 'This is a test')
#send_check_book('test', 'This is a test')
