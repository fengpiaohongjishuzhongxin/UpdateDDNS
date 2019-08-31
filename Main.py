import sys
import json
import os
import re
from datetime import datetime




import GetIPByRouter

print(sys.argv)

ip_list = GetIPByRouter.get_ip("192.168.11.11", "Admin", "225588")
print(ip_list)