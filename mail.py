import smtplib

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
