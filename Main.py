#!/usr/local/bin/python3
# Author: FengPiaoHong
import sys
import GetIPByRouter
from UpdateAliyunDDNS import AliyunDDNS

# 成功标志符
Success = True

# 操作阿里云DNS所需的参数
ApiKey = sys.argv[1]
ApiSecretKey = sys.argv[2]
Domain = sys.argv[3]

# 获取要更新的二级域名
subdomains = sys.argv[7:]
print(subdomains)

# 获取路由WAN IP列表
ip_list = GetIPByRouter.get_ip_Merlin(sys.argv[4], sys.argv[5], sys.argv[6])
# 先添加或修改第二个WAN IP,不需要者可以把下面这行注释掉
ip_list.reverse()

# 取WAN IP列表长度
ip_count = len(ip_list)
# 如果长度不合法,说明获取失败或者不是拨号上网,直接退出
if ip_count <= 0:
    print("IP列表长度错误,当前IP长度: {ipLen}".format(ipLen=ip_count))
    exit(-1)
print("成功获取路由器WAN IP: ", ip_list)



# 初始化工具时需要参数,可以自行去阿里云生成提取
handle = AliyunDDNS(ApiKey, ApiSecretKey, Domain)



# 要添加的DNSlist
add_list = []

# 遍历所有需要更新的二级域名列表并更新他们
for subdomain in subdomains:
    # 获取该二级域名下的记录
    record = handle.get_record(subdomain)
    while record is None:
        record = handle.get_record(subdomain)
    # 取记录个数
    record_len = len(record)
    count_flag = 0
    # 遍历IP列表
    for ip_item in ip_list:
        print("正在检查 {_subdomain} 第{_count}条记录值是否为 {_ip}".format(_subdomain=subdomain, _count=count_flag+1, _ip=ip_item))
        # 判断ip当前记录位置是否比DNS记录长度大
        #   IP记录位置比DNS记录长度小则更新记录
        #   IP记录位置比DNS记录长度大则新增记录
        if count_flag < record_len:
            if record[count_flag]['Value'] == ip_item:
                print("当前记录存与现在记录相同,无需修改")
                count_flag += 1
                continue
            r = handle.update_record(
                SubDomain=subdomain,
                SubIp=ip_item,
                SubRecordId=record[count_flag]['RecordId'],
                SubTpye="A"
            )
            # 为了防止Timeout导致更新失败,则加入循环
            while r is None:
                r = handle.update_record(
                    SubDomain=subdomain,
                    SubIp=ip_item,
                    SubRecordId=record[count_flag]['RecordId'],
                    SubTpye="A"
                )
            if r["Result"]:
                print("当前记录存与现在记录不同,已更新为{_ip}".format(_ip=ip_item))
            else:
                print("当前记录修改失败,二级域名为{_subdomain}, 第{_count}条记录, IP为{_ip}, 错误信息为:{_msg}"
                      .format(_subdomain=subdomain, _count=count_flag+1, _ip=ip_item, _msg=r["Message"]))
                Success = False
            count_flag += 1
        else:
            r = handle.add_record(
                SubDomain=subdomain,
                SubIp=ip_item,
                SubTpye="A"
            )
            # 为了防止Timeout导致新增失败,则加入循环
            while r is None:
                r = handle.add_record(
                    SubDomain=subdomain,
                    SubIp=ip_item,
                    SubTpye="A"
                )

            if r["Result"]:
                print("当前记录数{_count}不存在,现已增加,二级域名为{_subdomain}, 值为{_ip}".format(_count=count_flag + 1,
                                                                                _subdomain=subdomain, _ip=ip_item))
            else:
                print("当前记录新增失败,二级域名为{_subdomain}, 第{_count}条记录, IP为{_ip}, 错误信息为:{_msg}"
                      .format(_subdomain=subdomain, _count=count_flag + 1, _ip=ip_item, _msg=r["Message"]))
                Success = False
            count_flag += 1
    pass


if len(ip_list) >= 2:
    # 分别登记双线路
    # 登记 WAN 1 线路
    print("正在准备 WAN 1 线路更新")
    subdomain = "wan1"
    ip_item = ip_list[0]
    record = handle.get_record(subdomain)
    while record is None:
        record = handle.get_record(subdomain)
    if not record:
        # 没有 WAN 1 线路DNS记录,则新增
        r = handle.add_record(
            SubDomain=subdomain,
            SubIp=ip_item,
            SubTpye="A"
        )
        # 为了防止Timeout导致新增失败,则加入循环
        while r is None:
            r = handle.add_record(
                SubDomain=subdomain,
                SubIp=ip_item,
                SubTpye="A"
            )

        if r["Result"]:
            print("当前记录不存在,现已增加,二级域名为{_subdomain}, 值为{_ip}".format(_subdomain=subdomain, _ip=ip_item))
        else:
            print("当前记录新增失败,二级域名为{_subdomain},IP为{_ip}, 错误信息为:{_msg}"
                  .format(_subdomain=subdomain, _ip=ip_item, _msg=r["Message"]))
    else:
        # 有 WAN 1 线路,判断需不需要更新
        if record[0]['Value'] == ip_item:
            print("当前记录 {_subdomain} 存与现在记录相同,无需修改".format(_subdomain=subdomain))
        else:
            # WAN 1 线路需要更新
            r = handle.update_record(
                SubDomain=subdomain,
                SubIp=ip_item,
                SubRecordId=record[0]['RecordId'],
                SubTpye="A"
            )
            # 为了防止Timeout导致更新失败,则加入循环
            while r is None:
                r = handle.update_record(
                    SubDomain=subdomain,
                    SubIp=ip_item,
                    SubRecordId=record[0]['RecordId'],
                    SubTpye="A"
                )
            if r["Result"]:
                print("当前记录存与现在记录不同,已更新为{_ip}".format(_ip=ip_item))
            else:
                print("当前记录修改失败,二级域名为{_subdomain},IP为{_ip}, 错误信息为:{_msg}"
                      .format(_subdomain=subdomain, _ip=ip_item, _msg=r["Message"]))
                Success = False

    print("正在准备 WAN 2 线路更新")
    # 登记 WAN 2 线路
    subdomain = "wan2"
    ip_item = ip_list[1]
    record = handle.get_record(subdomain)
    while record is None:
        record = handle.get_record(subdomain)
    if not record:
        # 没有 WAN 2 线路DNS记录,则新增
        r = handle.add_record(
            SubDomain=subdomain,
            SubIp=ip_item,
            SubTpye="A"
        )
        # 为了防止Timeout导致新增失败,则加入循环
        while r is None:
            r = handle.add_record(
                SubDomain=subdomain,
                SubIp=ip_item,
                SubTpye="A"
            )

        if r["Result"]:
            print("当前记录不存在,现已增加,二级域名为{_subdomain}, 值为{_ip}".format(_subdomain=subdomain, _ip=ip_item))
        else:
            print("当前记录新增失败,二级域名为{_subdomain},IP为{_ip}, 错误信息为:{_msg}"
                  .format(_subdomain=subdomain, _ip=ip_item, _msg=r["Message"]))
    else:
        # 有 WAN 2 线路,判断需不需要更新
        if record[0]['Value'] == ip_item:
            print("当前记录 {_subdomain} 存与现在记录相同,无需修改".format(_subdomain=subdomain))
        else:
            # WAN 2 线路需要更新
            r = handle.update_record(
                SubDomain=subdomain,
                SubIp=ip_item,
                SubRecordId=record[0]['RecordId'],
                SubTpye="A"
            )
            # 为了防止Timeout导致更新失败,则加入循环
            while r is None:
                r = handle.update_record(
                    SubDomain=subdomain,
                    SubIp=ip_item,
                    SubRecordId=record[0]['RecordId'],
                    SubTpye="A"
                )
            if r["Result"]:
                print("当前记录存与现在记录不同,已更新为{_ip}".format(_ip=ip_item))
            else:
                print("当前记录修改失败,二级域名为{_subdomain},IP为{_ip}, 错误信息为:{_msg}"
                      .format(_subdomain=subdomain, _ip=ip_item, _msg=r["Message"]))
                Success = False


if Success:
    exit(0)
else:
    exit(-1)