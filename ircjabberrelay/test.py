import re
import sys

msg = "<#00315#002#002Leodin#003> Miau"
sys.stdout.write('.')
sys.stdout.flush()
pattern = re.compile("<#\d{5}#\d{3}#\d{3}([^#]*)#\d{3}>(.*)", re.IGNORECASE)
if pattern.search(msg.rstrip()) is not None:
    msg = "<%s> %s" % (re.search(pattern, msg).group(1), re.search(pattern, msg).group(2))
