import os
import sys
"""uwsgi_portsniffer.py
Use a uwsgi log file to find the bound uwsgi port
"""

def portsniffer(log_file):
    if not os.path.exists(log_file):
        print 'Log file not found: %s' % log_file
        return None
    try:
        fo = open(log_file, 'r')
    except:
        print 'Could not open log file: %s' % log_file
        return None

    current_port = None
    try:
        for l in fo.readlines():
            if 'bound to TCP address' in l:
                before0, after0 = l.split('address')
                before1, after1 = after0.split('(port')
                before1=before1.strip()
                ip, port = before1.split(':')
                current_port = port
        fo.close()
    except:
        print 'Error scanning log file: %s' % log_file
        return None
    return current_port



