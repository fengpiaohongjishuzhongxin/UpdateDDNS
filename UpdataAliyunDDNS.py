import time
from hashlib import sha1
import hmac
import base64
from urllib import parse
import requests
import json


class UpdateAliyunDDNS:
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
        return time.strftime("%Y-%m-%dT%H%%3A%M%%3A%SZ", time.gmtime())

    def get_urlendcode(self, code) -> str:
        return parse.quote(code)

    def get_signature(self, query: str) -> str:
        encoded_query = self.get_urlendcode(query)
        message = "GET&%2F&{_query}".format(_query=encoded_query)
        h = str(base64.b64encode(
            hmac.new(("{_Api}&".format(_Api=self.AccessKeySecret)).encode("utf-8"),
                     message.encode("utf-8"), sha1).digest()), "utf-8")
        return self.get_urlendcode(h)

    def send_request(self, query: str) -> str:
        sig = self.get_signature(query)
        result = requests.get("https://alidns.aliyuncs.com?{_query}&Signature={_sig}".format(_query=query, _sig=sig))
        return result.text

    def get_record(self, sub_domain="") -> list:
        if sub_domain == "":
            sub_domain = self.SubDomainName
        if sub_domain == "@":
            sub_domain == ""

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
            _Nonce=self.get_timestamp(),
            _SubDomain=self.get_urlendcode(sub_domain),
            _Domain=self.DomainName,
            _Timestamp=self.get_timestamp(),
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
            _Nonce=self.get_timestamp(),
            _SubDomain=self.get_urlendcode(sub_domain),
            # _SubDomain="fengpiaohong.vip",
            _Timestamp=self.get_timestamp(),
            _Type=self.RecordType
        )
        # print(queryString)
        result = self.send_request(queryString)
        if result.find("Err") != -1 or result.find("err") != -1:
            return None
        js = json.loads(result)
        return js["DomainRecords"]["Record"]

    def get_all_records(self) -> list:
        print("正在获取所有记录")
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
            _Nonce=self.get_timestamp(),
            _Domain=self.DomainName,
            _Timestamp=self.get_timestamp()
        )
        result = self.send_request(queryString)
        if result.find("Err") != -1 or result.find("err") != -1:
            return None
        js = json.loads(result)
        return js["DomainRecords"]["Record"]


x = UpdateAliyunDDNS("LTAIFde2JtIkveMO", "31qkWF6LkB6ym75xQuuGUuLxZfaAht", "fengpiaohong.vip", "smtp")

# x.get_record("xxx")
print(x.get_all_records())
# ss = hmac.new("fengpiaohong".encode("utf-8"),"fengpiaoxu".encode("utf-8"),sha1).digest();
# print(str(base64.b64encode(ss), "utf-8"))
