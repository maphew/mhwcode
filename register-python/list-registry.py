# File: winreg-example-1.py
from _winreg import *

explorer = OpenKey(
    HKEY_CURRENT_USER,
    "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer"
    )

# list values owned by this registry key
try:
    i = 0
    while 1:
        name, value, type = EnumValue(explorer, i)
        print repr(name),
        i += 1
except WindowsError:
    print

value, type = QueryValueEx(explorer, "Logon User Name")

print
print "user is", repr(value)

