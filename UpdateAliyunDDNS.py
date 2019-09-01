#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Author: FengPiaoHong
import time
from hashlib import sha1
import hmac
import base64
from urllib import parse
import requests
import json


class AliyunDDNS:
    # AccessKeyId
    AccessKeyId = ""

    # AccessKeySecret
    AccessKeySecret = ""

    # Action
    Action = ""

    # DomainName
    DomainName = ""

    # SubDomain
    SubDomainName = ""

    # 记录类型
    RecordType = ""

    def __init__(self, _AccessKeyId, _AccessKeySecret, _Domain, _SubDomain="", _Type="A"):
        self.AccessKeyId = _AccessKeyId
        self.AccessKeySecret = _AccessKeySecret
        self.DomainName = _Domain
        self.SubDomainName = _SubDomain
        self.RecordType = _Type

    def get_timestamp(self) -> str:
        """
        获取时间戳
        :return:返回阿里云DNS时间戳
        """
        return time.strftime("%Y-%m-%dT%H%%3A%M%%3A%SZ", time.gmtime())

    def get_urlendcode(self, code: str) -> str:
        """
        URL编码
        :param code: 要编码的文本
        :return:返回编码后的字符串
        """
        return parse.quote(code)

    def get_signature(self, query: str) -> str:
        """
        DNS验证用的签名
        :param query: 要进行签名的字符串
        :return:返回签名后的字符串
        """
        encoded_query = self.get_urlendcode(query)
        message = "GET&%2F&{_query}".format(_query=encoded_query)
        h = str(base64.b64encode(
            hmac.new(("{_Api}&".format(_Api=self.AccessKeySecret)).encode("utf-8"),
                     message.encode("utf-8"), sha1).digest()), "utf-8")
        return self.get_urlendcode(h)

    def send_request(self, query: str) -> str:
        """
        发送Alidns请求并返回请求结果
        :param query: 请求参数
        :return: 返回请求结果的字符串
        """
        sig = self.get_signature(query)
        result = requests.get("https://alidns.aliyuncs.com?{_query}&Signature={_sig}".format(_query=query, _sig=sig))
        return result.text

    def get_record(self, sub_domain="") -> dict:
        """
        通过二级域名获取DNS相关记录
        :param sub_domain: 二级域名
        :return: 返回相关DNS的字典
        """
        j = "{\"Message:\":\"参数错误\"}"
        j = json.loads(j)
        j["Result"] = False
        if sub_domain == "":
            sub_domain = self.SubDomainName
        if sub_domain == "@":
            sub_domain == ""
        timestamp = self.get_timestamp()

        queryString = "AccessKeyId={_ApiId}&" \
                      "Action=DescribeSubDomainRecords&" \
                      "Format=JSON&" \
                      "SignatureMethod=HMAC-SHA1&" \
                      "SignatureNonce={_Nonce}&" \
                      "SignatureVersion=1.0&" \
                      "SubDomain={_SubDomain}.{_Domain}&" \
                      "Timestamp={_Timestamp}&" \
                      "Type={_Type}&" \
                      "Version=2015-01-09".format(
            _ApiId=self.AccessKeyId,
            _Nonce=timestamp,
            _SubDomain=self.get_urlendcode(sub_domain),
            _Domain=self.DomainName,
            _Timestamp=timestamp,
            _Type=self.RecordType
        )

        queryString2 = "AccessKeyId={_ApiId}&" \
                       "Action=DescribeSubDomainRecords&" \
                       "DomainName={_Domain}&" \
                       "Format=JSON&" \
                       "RegionId=default&" \
                       "SecureTransport=true&" \
                       "SignatureMethod=HMAC-SHA1&" \
                       "SignatureNonce={_Nonce}&" \
                       "SignatureVersion=1.0&" \
                       "SubDomain={_SubDomain}.{_Domain}&" \
                       "Timestamp={_Timestamp}&" \
                       "Type={_Type}&" \
                       "Version=2015-01-09".format(
            _ApiId=self.AccessKeyId,
            _Domain=self.DomainName,
            _Nonce=timestamp,
            _SubDomain=self.get_urlendcode(sub_domain),
            # _SubDomain="fengpiaohong.vip",
            _Timestamp=timestamp,
            _Type=self.RecordType
        )
        # print(queryString)
        try:
            result = self.send_request(queryString)
        except:
            return None
        # print(result)
        js = json.loads(result)
        if result.find("Err") != -1 or result.find("err") != -1 or result.find("Invalid") != -1:
            if js["Code"] == "SignatureNonceUsed":
                return None
            else:
                return j
        return js["DomainRecords"]["Record"]

    def get_record_by_recordid(self, record_id: str) -> dict:
        """
        通过记录ID获取相关DNS记录
        :param record_id: 记录ID
        :return: 返回相关DNS记录的字典
        """
        j = "{\"Message:\":\"参数错误\"}"
        j = json.loads(j)
        j["Result"] = False
        if record_id == "":
            return j
        timestamp = self.get_timestamp()

        queryString = \
            "AccessKeyId={_ApiId}&" \
            "Action=DescribeDomainRecordInfo&" \
            "Format=JSON&" \
            "RecordId={_RecordId}&" \
            "RegionId=default&" \
            "SecureTransport=true&" \
            "SignatureMethod=HMAC-SHA1&" \
            "SignatureNonce={_Nonce}&" \
            "SignatureVersion=1.0&" \
            "Timestamp={_Timestamp}&" \
            "Version=2015-01-09".format(
                _ApiId=self.AccessKeyId,
                _RecordId=record_id,
                _Nonce=timestamp,
                _Timestamp=timestamp
            )
        try:
            result = self.send_request(queryString)
        except:
            return None
        js = json.loads(result)
        if result.find("Err") != -1 or result.find("err") != -1 or result.find("Invalid") != -1:
            return j
        if js.get("RecordId") is None:
            return []
        return js

    def get_all_records(self) -> dict:
        """
        获取所有名下DNS记录
        :return: 返回名下所有DNS记录的字典
        """
        # print("正在获取所有记录")
        j = "{\"Message:\":\"参数错误\"}"
        j = json.loads(j)
        j["Result"] = False
        timestamp = self.get_timestamp()
        queryString = "AccessKeyId={_ApiId}&" \
                      "Action=DescribeDomainRecords&" \
                      "DomainName={_Domain}&" \
                      "Format=JSON&" \
                      "PageSize=100&" \
                      "SignatureMethod=HMAC-SHA1&" \
                      "SignatureNonce={_Nonce}&" \
                      "SignatureVersion=1.0&" \
                      "Timestamp={_Timestamp}&" \
                      "Version=2015-01-09".format(
            _ApiId=self.AccessKeyId,
            _Nonce=timestamp,
            _Domain=self.DomainName,
            _Timestamp=timestamp
        )
        try:
            result = self.send_request(queryString)
        except:
            return None
        js = json.loads(result)
        if result.find("Err") != -1 or result.find("err") != -1 or result.find("Invalid") != -1:
            if js["Code"] == "SignatureNonceUsed":
                return None
            else:
                return j
        return js["DomainRecords"]["Record"]

    def add_record(self, **kwargs) -> dict:
        """
        新增DNS记录
        :param kwargs: SubIp:域名IP SubDomain:二级域名 SubType:域名类型
        :return:返回新增DNS结果
        """
        j = "{\"Message:\":\"参数错误\"}"
        j = json.loads(j)
        j["Result"] = False
        sub_ip = kwargs['SubIp']
        sub_domain = kwargs['SubDomain']
        sub_type = kwargs['SubTpye']
        if sub_ip == "":
            print("IP格式错误")
            return j
        if sub_domain == "":
            sub_domain = self.SubDomainName
        if sub_domain == "":
            sub_domain = "@"
        if sub_type == "":
            sub_type = "A"

        timestamp = self.get_timestamp()

        queryString = \
            "AccessKeyId={_ApiId}&" \
            "Action=AddDomainRecord&" \
            "DomainName={_Domain}&" \
            "Format=JSON&" \
            "RR={_SubDomain}&" \
            "RegionId=default&" \
            "SecureTransport=true&" \
            "SignatureMethod=HMAC-SHA1&" \
            "SignatureNonce={_Nonce}&" \
            "SignatureVersion=1.0&" \
            "Timestamp={_Timestamp}&" \
            "Type={_Type}&" \
            "Value={_Ip}&" \
            "Version=2015-01-09".format(
                _ApiId=self.AccessKeyId,
                _Domain=self.DomainName,
                _SubDomain=sub_domain,
                _Nonce=timestamp,
                _Timestamp=timestamp,
                _Type=sub_type,
                _Ip=sub_ip
            )
        # print(queryString)
        try:
            result = self.send_request(queryString)
        except:
            return None
        js = json.loads(result)
        if result.find("Err") != -1 or result.find("err") != -1 or result.find("Invalid") != -1:
            if js["Code"] == "SignatureNonceUsed":
                return None
            else:
                return j
        if js.get("RecordId") is not None:
            js["Result"] = True
        else:
            js["Result"] = False
        return js

    def update_record(self, **kwargs):
        """
        更新DNS域名
        :param kwargs:  SubIp:域名IP SubDomain:二级域名 SubType:域名类型 SubRecordId:Dns记录ID
        :return: 返回更新DNS域名结果的字典
        """
        j = "{\"Message:\":\"参数错误\"}"
        j = json.loads(j)
        j["Result"] = False
        sub_ip = kwargs['SubIp']
        sub_domain = kwargs['SubDomain']
        sub_type = kwargs['SubTpye']
        sub_recordid = kwargs['SubRecordId']
        if sub_ip == "":
            print("IP格式错误")
            return j
        if sub_domain == "":
            sub_domain = self.SubDomainName
        if sub_domain == "":
            sub_domain = "@"
        if sub_type == "":
            sub_type = "A"
        if sub_recordid == "":
            return None
        timestamp = self.get_timestamp()

        queryString = \
            "AccessKeyId={_ApiId}&" \
            "Action=UpdateDomainRecord&" \
            "Format=JSON&" \
            "RR={_SubDomain}&" \
            "RecordId={_RecordId}&" \
            "RegionId=default&" \
            "SecureTransport=true&" \
            "SignatureMethod=HMAC-SHA1&" \
            "SignatureNonce={_Nonce}&" \
            "SignatureVersion=1.0&" \
            "Timestamp={_Timestamp}&" \
            "Type={_Type}&" \
            "Value={_Ip}&" \
            "Version=2015-01-09".format(
                _ApiId=self.AccessKeyId,
                _SubDomain=sub_domain,
                _RecordId=sub_recordid,
                _Nonce=timestamp,
                _Timestamp=timestamp,
                _Type=sub_type,
                _Ip=sub_ip
            )
        try:
            result = self.send_request(queryString)
        except:
            return None
        js = json.loads(result)
        if result.find("Err") != -1 or result.find("err") != -1 or result.find("Invalid") != -1:
            if js["Code"] == "SignatureNonceUsed":
                return None
            else:
                return j
        if js.get("RecordId") is not None:
            js["Result"] = True
        else:
            js["Result"] = False
        return js

    def delete_record(self, recordId: str) -> dict:
        """
        删除DNS记录
        :param recordId:DNS记录ID
        :return: 返回删除DNS记录结果
        """
        j = "{\"Message:\":\"参数错误\"}"
        j = json.loads(j)
        j["Result"] = False
        if recordId == "" or len(recordId) != 17:
            return j
        timestamp = self.get_timestamp()
        queryString = \
            "AccessKeyId={_ApiId}&" \
            "Action=DeleteDomainRecord&" \
            "Format=JSON&" \
            "RecordId={_RecordId}&" \
            "RegionId=default&" \
            "SecureTransport=true&" \
            "SignatureMethod=HMAC-SHA1&" \
            "SignatureNonce={_Nonce}&" \
            "SignatureVersion=1.0&" \
            "Timestamp={_Timestamp}&" \
            "Version=2015-01-09".format(
                _ApiId=self.AccessKeyId,
                _RecordId=recordId,
                _Nonce=timestamp,
                _Timestamp=timestamp,
            )
        try:
            result = self.send_request(queryString)
        except:
            return None
        js = json.loads(result)
        if result.find("Err") != -1 or result.find("err") != -1 or result.find("Invalid") != -1:
            if js["Code"] == "SignatureNonceUsed":
                return None
            else:
                return j
        if js.get("RecordId") is not None:
            js["Result"] = True
        else:
            js["Result"] = False
        return js


'''
x = UpdateAliyunDDNS("LTAI4Fm3ho4w6nREbtDnkYAP", "UNLJsYQv7yh633NXdAAPme01ov1VxM", "fengpiaohong.vip", "smtp")

print(x.add_record(SubIp="2.2.2.2", SubDomain="test", SubTpye="A"))
r = x.get_record("test")
print(r)
# print(x.get_record("test"))
# print(x.get_all_records())
# print(x.add_record(SubIp="2.2.2.2", SubDomain="test", SubTpye="A"))
# print(x.update_record(SubDomain="test", SubIp="4.4.4.4", SubTpye="A", SubRecordId=r[0]["RecordId"]))
print(x.delete_record(r[0]["RecordId"]))
# ss = hmac.new("fengpiaohong".encode("utf-8"),"fengpiaoxu".encode("utf-8"),sha1).digest();
# print(str(base64.b64encode(ss), "utf-8"))
'''