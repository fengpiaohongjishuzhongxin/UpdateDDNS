import requests
import base64
from xml.dom.minidom import parse
import xml.dom.minidom


def get_ip(ip_address, username, userpwd):
    r = requests.get("http://{IP}/Main_Login.asp".format(IP=ip_address))
    userdata = base64.b64encode(("{user}:{pwd}".format(user=username, pwd=userpwd)).encode("utf-8"))
    userdata = str(userdata, "GBK")
    data = "group_id=&action_mode=&action_script=&action_wait=5&current_" \
           "page=Main_Login.asp&next_page=index.asp&login_" \
           "authorization={_userdata}".format(_userdata=userdata)
    headers = {'referer': 'http://{IP}/Main_Login.asp'.format(IP=ip_address)}
    r = requests.post("http://{IP}/login.cgi".format(IP=ip_address), data, headers=headers)
    r = requests.get("http://{IP}/ajax_status.xml".format(IP=ip_address), cookies=r.cookies)
    r.encoding = "utf-8"
    # print(r.text)

    ip_list = []

    # 使用minidom解析器打开 XML 文档
    DOMTree = xml.dom.minidom.parseString(r.text)
    collection = DOMTree.documentElement
    wans = collection.getElementsByTagName("wan")
    for w in wans:
        # print(w.childNodes[0].data)
        str_pos = str(w.childNodes[0].data).find("ipaddr")
        if str_pos != -1:
            # print(w.childNodes[0].data[str_pos + len("ipaddr="):])
            ip_list.append(w.childNodes[0].data[str_pos + len("ipaddr="):])
    return ip_list


# print(get_ip("192.168.11.11", "Admin", "225588"))
