#!/usr/bin/python

import os, sys, re
import smtplib, imaplib
import glob
import email
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
import mimetypes

VERBOSE = False

def IFELSE(b, x, y):
   if b: return x
   else: return y

from mail import mail


if __name__ == "__main__":

   # command line options
   import os, sys, getopt
   try:
      print ("sys.argv[1:]:", sys.argv[1:])
      if sys.argv[1:]==[]: raise
      opt = getopt.gnu_getopt(sys.argv[1:], '', ['attach=', 'to='])
   except:
      print(e)
      print("ERROR!")
      print("Usage:")
      print("    python sendgmail --attach=helloworld.py")
      print("    python sendgmail helloworld.py")
      print("    python sendgmail *.py")
      sys.exit()

   d = dict(opt[0])
   if d.has_key('--attach'):
      d['--attach'] = d['--attach'].split(",")
   else:
      d['--attach'] = []

   import glob
   for x in opt[1]:
      for y in glob.glob(x):
         d['--attach'].append(y)

   try:
      d['--to'] = d['--to'].strip()
   except:
      d['--to'] = 'yliow@ccis.edu'

   subject = ', '.join([os.path.abspath(_) for _ in d['--attach']])
   subject = 'sendgmail'
   body = '<br>'.join([os.path.abspath(_) for _ in d['--attach']])
   mail(to = d['--to'],
        from_ = "yliow@ccis.edu",
        subject = subject,
        html = "<html><body><h1>%s</h1></body></html>" % body,
        attach = d['--attach'],
        )
