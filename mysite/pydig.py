from subprocess import Popen, PIPE
import re
import os

def dig(s='smtp.gmail.com', verbose=False):
    domain_name = s
    #print "dig ..."
    if os.name == 'posix':
        old_s = s
        try:
            stdout = Popen("dig %s" % s, shell=True,
                           bufsize=4096, stdout=PIPE).stdout
            s = stdout.read()
            #print s
            p = re.compile(";; ANSWER SECTION:([^;]*)")
            s = p.search(s).group(1)

            p = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
            IP_addresses = p.findall(s)

            if verbose:
                pass
                #print "IP addresses for %s" % domain_name
                #for x in IP_addresses:
                #    print "   ", x
            return IP_addresses
        except:
            #print e
            return [old_s]
    else:
        return [domain_name]

if __name__ == '__main__':
    print("Testing imap.gmail.com, verbose=True")
    xs = dig('imap.gmail.com', verbose=True)
    print ("return value:", xs)
    print
