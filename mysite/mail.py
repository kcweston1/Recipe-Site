import os, sys
import smtplib
import email

#from email.MIMEMultipart import MIMEMultipart
#from email.MIMEBase import MIMEBase
#from email.MIMEText import MIMEText
#from email.MIMEImage import MIMEImage

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage

from email import encoders
import mimetypes

from SMTP_config import *

def emailpart(path):
   if not os.path.isfile(path):
      raise BaseException("emailpart ERROR: file %s cannot be found" % path)
   # Guess the content type based on the file's extension.  Encoding
   # will be ignored, although we should check for simple things like
   # gzip'd or compressed files.
   ctype, encoding = mimetypes.guess_type(path)
   if ctype is None or encoding is not None:
      # No guess could be made, or the file is encoded (compressed), so
      # use a generic bag-of-bits type.
      ctype = 'application/octet-stream'
   maintype, subtype = ctype.split('/', 1)
   if maintype == 'text':
      # Note: we should handle calculating the charset
      msg = MIMEText(file(path).read(), _subtype=subtype)
   elif maintype == 'image':
      msg = MIMEImage(file(path, 'rb').read(), _subtype=subtype)
   elif maintype == 'audio':
      msg = MIMEAudio(file(path, 'rb').read(), _subtype=subtype)
   else:
      msg = MIMEBase(maintype, subtype)
      msg.set_payload(file(path, 'rb').read())
      # Encode the payload using Base64
      encoders.encode_base64(msg)
   # Set the filename parameter
   _, filename = os.path.split(path)
   msg.add_header('Content-Disposition', 'attachment', filename=filename)
   return msg


class SMTP_server:

   def __init__(self,
                server=None,
                servers=None,
                port=None,
                user=None,
                password=None,
                verbose=False):
      if server == None and servers == None:
         servers = SMTP_SERVERS
      elif server != None:
         servers = [server]

      self.server = None

      AUTHREQUIRED = 1 # check
      e_ = None # for exception
      if verbose:
         pass
         #print "servers:", servers
      for server in servers:
         if verbose:
            #print "  logging in to SMTP server at", server, "...",
            sys.stdout.flush()
         try:
            self.server = s = smtplib.SMTP(server, port)
            s.set_debuglevel(0)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(user, password)
            if verbose:
               pass # print "done"
            break
         except Exception as e:
            if verbose:
               pass # print e
            e_ = e
      if e_ is not None: raise e_ # raise last exception

   def sendmail(self,
                from_=None,
                to=None,
                msg_str='HELLO WORLD'):
      self.server.sendmail(from_, to, msg_str)

   def __del__(self):
      if self.server is not None:
         self.server.close() # <------ DON'T FORGET


def mail(to,                   # string of list of strings
         subject,              # string
         from_=USER,           #
         text=None, html=None, # mail body
         attach=None,          # filename or list of filenames
                               # of files to be attached
         server=None,
         servers=None,
         port=SMTP_PORT,
         user=USER,
         password=PASSWORD,
         verbose=True):

   #if isinstance(to, unicode): to = str(to)
   if isinstance(to, str): to = [to]

   if isinstance(attach, str):
      attaches = [attach]
   elif isinstance(attach, list):
      attaches = attach
   elif attach == None:
      attaches = []

   msg = MIMEMultipart()
   msg['From'] = from_
   msg['Subject'] = subject

   alternative = MIMEMultipart('alternative')
   msg.attach(alternative)
   if text: alternative.attach(MIMEText(text))
   if html: alternative.attach(MIMEText(html, 'html'))

   for attach in attaches:
      part = emailpart(attach)
      msg.attach(part)

   server = SMTP_server(server=server,
                        servers=servers,
                        port=port,
                        user=user,
                        password=password)

   """
   python SMTP library is broken and cannot send to multiple recipients.
   Send to individual using a loop instead.
   """
   for x in to:
      msg['To'] = x

      if verbose:
         #print """mail ...
         #from   : %s
         #to     : %s
         #subject: %s""" % (from_, x, subject)
         pass

      try:
         server.sendmail(from_, x, msg.as_string())
      except Exception as e:
         raise e


if __name__ == '__main__':
   s = "Test mail: one recipient, text body"
   mail(to = "ejohnson16@cougars.ccis.edu",
        from_ = "cctabletennisclub@gmail.com",
        subject = s,
        text = s,
        verbose=False)
