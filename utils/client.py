###
# Copyright 2021 New H3C Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

# -*- coding: utf-8 -*-


import json
import base64
import ssl
import urllib3
import requests
from utils.common import Constant
from exception.ToolException import FailException
from urllib.parse import urlencode


ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings()
HTTP = urllib3.PoolManager()


class Client(object):

    def __init__(self, args):

        self.host = args.host
        self.port = args.port
        self.username = args.username
        self.password = args.password
        self.err_message = list()
        self.suc_message = list()
        self.data = dict()


class RestfulClient(Client):

    def __init__(self, args):

        super(RestfulClient, self).__init__(args)
        self.token = ""
        self.cookie = ""

        if args.port is None:
            url = "https://%s/api/session" % self.host
        else:
            url = "https://%s:%s/api/session" % (self.host, self.port)

        fields = {
            "username": args.username,
            "password": args.password,
            "log_Type": "1",
        }
        try:
            resp = HTTP.request("POST", url, retries=False,
                                fields=fields, timeout=20)
            result = json.loads(resp.data.decode("utf-8"))

        except (KeyError, TypeError, AttributeError, Exception) as err:
            self.err_message.append("%s: %s" % (err, "get cookie"))
            raise FailException(*self.err_message)
        if (isinstance(result, dict) and result.get("cc", None) ==
                Constant.SUCCESS_0):
            try:

                self.token = result["CSRFToken"]
                cookie = resp.headers.get("set-cookie")

                session_id = str(cookie).split("ID=")[-1].split("; Pa")[0]
                my_cookie = "QSESSIONID=%s;CSRF=%s" % (session_id, self.token)
                self.cookie = my_cookie

            except (IndexError, KeyError, Exception) as err:
                self.err_message.append(str(err))
                raise FailException(*self.err_message)
        else:
            fields = {
                "username": args.username,
                "password": args.password,
                "log_Type": "1",
            }
            data = urlencode(fields)
            if args.port is None:
                url = "https://%s/api/session?%s" % (self.host, data)
            else:
                url = ("https://%s:%s/api/session?%s" % (self.host,
                                                         self.port, data))
            try:
                resp = HTTP.request("POST", url, retries=False, timeout=20)
                result = json.loads(resp.data.decode("utf-8"))

            except (KeyError, TypeError, AttributeError, Exception) as err:
                self.err_message.append("%s: %s" % (err, "get cookie"))
                raise FailException(*self.err_message)

            if (isinstance(result, dict) and result.get("cc", None) ==
                    Constant.SUCCESS_0):
                try:

                    self.token = result["CSRFToken"]
                    cookie = resp.headers.get("set-cookie")

                    session_id = str(cookie).split("ID=")[-1].split("; Pa")[0]
                    my_cookie = "QSESSIONID=%s;CSRF=%s" % (
                        session_id, self.token)
                    self.cookie = my_cookie

                except (IndexError, KeyError, Exception) as err:
                    self.err_message.append(str(err))
                    raise FailException(*self.err_message)
            else:
                err_message = ("Failure: failed to establish a new "
                               "connection to the host")
                self.err_message.append(err_message)
                raise FailException(*self.err_message)

    def request(self, method, url, body=None):

        headers = {
            "X-CSRFTOKEN": self.token,
            "Cookie": self.cookie
        }

        if isinstance(body, dict):
            try:
                payload = json.dumps(body)
            except (KeyError, TypeError, AttributeError, Exception) as err:
                self.err_message.append(str(err))
                raise FailException(*self.err_message)
            else:
                headers["Content-Type"] = u"application/json"
        else:
            payload = body
        if self.port is not None:
            url = r"https://%s:%s%s" % (self.host, self.port, url)
        else:
            url = r"https://%s%s" % (self.host, url)
        try:
            resp = HTTP.request(method, url, body=payload,
                                retries=False, headers=headers, timeout=30)
            result = json.loads(resp.data.decode("utf-8"))
        except (TypeError, AttributeError, Exception) as err:
            self.err_message.append(str(err))
            raise FailException(*self.err_message)
        return result

    def request_hdm(self, method, url, body=None):

        headers = {
            "X-CSRFTOKEN": self.token,
            "Cookie": self.cookie
        }

        if isinstance(body, dict):
            try:
                payload = json.dumps(body)
            except (KeyError, TypeError, AttributeError, Exception) as err:
                self.err_message.append(str(err))
                raise FailException(*self.err_message)
            else:
                headers["Content-Type"] = u"application/json"
        else:
            payload = body
        if self.port is not None:
            url = r"https://%s:%s%s" % (self.host, self.port, url)
        else:
            url = r"https://%s%s" % (self.host, url)
        try:
            resp = HTTP.request(method, url, body=payload,
                                retries=False, headers=headers, timeout=30)
            result = resp.data
        except (TypeError, AttributeError, Exception) as err:
            self.err_message.append(str(err))
            raise FailException(*self.err_message)
        return result

    def send_request(self, method, url, payload=None):

        if method.upper() in {"GET", "PUT", "POST", "DELETE"}:
            resp = self.request(method, url, payload)
        else:
            err_message = "Failure: the request method is illegal"
            self.err_message.append(err_message)
            raise FailException(*self.err_message)
        return resp

    def send_hdm_request(self, method, url, payload=None):

        if method.upper() in {"GET", "PUT", "POST", "DELETE"}:
            resp = self.request_hdm(method, url, payload)
        else:
            err_message = "Failure: the request method is illegal"
            self.err_message.append(err_message)
            raise FailException(*self.err_message)
        return resp

    def upload_request(self, method, url, fields):

        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/76.0.3809.132 Safari/537.36",
            "X-CSRFTOKEN": self.token,
            "Cookie": "custom_id=2; product_board_id=g3; "
            "productID_num=16978692; lang=auto; safe_switch=0; "
            "oem_flag=0; buid_time=2019; extended_privilege=259; "
            "privilege_id=4; un=root; ldap_user=0; network_access=0; "
            "user_access=0; basic_access=0; power_access=0; "
            "firmware_access=0; health_access=0; remote_access=0; "
            "kvm_access=1; vmedia_access=1; %s" %
            self.cookie}
        if self.port is not None:
            url = r'https://%s:%s%s' % (self.host, self.port, url)
        else:
            url = r'https://%s%s' % (self.host, url)
        try:
            resp = HTTP.request(method, url, fields=fields, headers=headers,
                                multipart_boundary=boundary, timeout=300)
            result = json.loads(resp.data.decode("utf-8"))
        except (KeyError, TypeError, AttributeError, Exception) as err:
            self.err_message.append(str(err))
            raise FailException(*self.err_message)
        return result

    def get_screen_capture(self, url, body=None):

        headers = {
            "X-CSRFTOKEN": self.token,
            "Cookie": self.cookie
        }
        if isinstance(body, dict):
            try:
                payload = json.dumps(body)
            except (KeyError, TypeError, AttributeError, Exception) as err:
                self.err_message.append(str(err))
                raise FailException(*self.err_message)
            else:
                headers["Content-Type"] = u"application/json"
        else:
            payload = body

        if self.port is not None:
            url = r"https://%s:%s%s" % (self.host, self.port, url)
        else:
            url = r"https://%s%s" % (self.host, url)
        try:
            res = HTTP.request("GET", url, retries=False,
                               headers=headers, body=payload)
            result = res.data
        except (KeyError, TypeError, AttributeError, Exception) as err:
            self.err_message.append(str(err))
            raise FailException(*self.err_message)
        return result

    def http_get(self, url):

        headers = {
            "X-CSRFTOKEN": self.token,
            "Cookie": self.cookie
        }
        if self.port is not None:
            url = r"https://%s:%s%s" % (self.host, str(self.port), url)
        else:
            url = r"https://%s%s" % (self.host, url)
        try:
            resp = HTTP.request('GET', url, retries=False,
                                headers=headers, timeout=300)
            return resp.data
        except (KeyError, TypeError, AttributeError, Exception) as err:
            self.err_message.append(str(err))
            raise FailException(*self.err_message)

    def delete_session(self):

        try:
            self.send_request("DELETE", "/api/session")
        except FailException:
            pass


class FwUpdateClient(Client):

    def __init__(self, args):

        super(FwUpdateClient, self).__init__(args)
        self.token = ""
        self.cookie = ""

        if args.port is None:
            url = "https://%s/api/session" % self.host
        else:
            url = "https://%s:%s/api/session" % (self.host, self.port)

        fields = {
            "username": args.username,
            "password": args.password,
            "log_Type": "1",
        }
        try:
            resp = HTTP.request("POST", url, retries=False,
                                fields=fields, timeout=20)
            result = json.loads(resp.data.decode("utf-8"))

        except (KeyError, TypeError, AttributeError, Exception) as err:
            self.err_message.append("%s: %s" % (err, "get cookie"))
            return None
        if (isinstance(result, dict) and result.get("cc", None) ==
                Constant.SUCCESS_0):
            try:

                self.token = result["CSRFToken"]
                cookie = resp.headers.get("set-cookie")
                session_id = str(cookie).split("ID=")[-1].split("; Pa")[0]
                my_cookie = "QSESSIONID=%s;CSRF=%s" % (session_id, self.token)
                self.cookie = my_cookie

            except (IndexError, KeyError, Exception) as err:
                self.err_message.append(str(err))
                return None
        else:

            fields = {
                "username": args.username,
                "password": args.password,
                "log_Type": "1",
            }
            data = urlencode(fields)
            if args.port is None:
                url = "https://%s/api/session?%s" % (self.host, data)
            else:
                url = ("https://%s:%s/api/session?%s" % (self.host,
                                                         self.port, data))
            try:
                resp = HTTP.request("POST", url, retries=False, timeout=20)
                result = json.loads(resp.data.decode("utf-8"))

            except (KeyError, TypeError, AttributeError, Exception) as err:
                self.err_message.append(str(err))
                return None

            if (isinstance(result, dict) and result.get("cc", None) ==
                    Constant.SUCCESS_0):
                try:

                    self.token = result["CSRFToken"]
                    cookie = resp.headers.get("set-cookie")
                    session_id = str(cookie).split("ID=")[-1].split("; Pa")[0]
                    my_cookie = "QSESSIONID=%s;CSRF=%s" % (
                        session_id, self.token)
                    self.cookie = my_cookie

                except (IndexError, KeyError, Exception) as err:
                    self.err_message.append(str(err))
                    return None
            else:
                err_message = ("Failure: failed to establish a new "
                               "connection to the host")
                self.err_message.append(err_message)
                return None

    def request(self, method, url, body=None):

        headers = {
            "X-CSRFTOKEN": self.token,
            "Cookie": self.cookie
        }

        if isinstance(body, dict):
            try:
                payload = json.dumps(body)
            except (KeyError, TypeError, AttributeError, Exception) as err:
                self.err_message.append(str(err))
                return None
            else:
                headers["Content-Type"] = u"application/json"
        else:
            payload = body
        if self.port is not None:
            url = r"https://%s:%s%s" % (self.host, self.port, url)
        else:
            url = r"https://%s%s" % (self.host, url)
        try:
            resp = HTTP.request(method, url, body=payload,
                                retries=False, headers=headers, timeout=30)
            result = json.loads(resp.data.decode("utf-8"))
        except (TypeError, AttributeError, Exception) as err:
            if method not in {"DELETE", "delete"}:
                self.err_message.append(str(err))
            return None
        return result

    def send_request(self, method, url, payload=None):

        resp = None
        if method.upper() in {"GET", "PUT", "POST", "DELETE"}:
            resp = self.request(method, url, payload)
        else:
            err_message = "Failure: the request method is illegal"
            self.err_message.append(err_message)
        return resp

    def upload_request(self, method, url, fields):

        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/76.0.3809.132 Safari/537.36",
            "X-CSRFTOKEN": self.token,
            "Cookie": "custom_id=2; product_board_id=g3; "
            "productID_num=16978692; lang=auto; safe_switch=0; "
            "oem_flag=0; buid_time=2019; extended_privilege=259; "
            "privilege_id=4; un=root; ldap_user=0; network_access=0; "
            "user_access=0; basic_access=0; power_access=0; "
            "firmware_access=0; health_access=0; remote_access=0; "
            "kvm_access=1; vmedia_access=1; %s" %
            self.cookie}
        if self.port is not None:
            url = r'https://%s:%s%s' % (self.host, self.port, url)
        else:
            url = r'https://%s%s' % (self.host, url)
        try:
            resp = HTTP.request(method, url, fields=fields, headers=headers,
                                multipart_boundary=boundary, timeout=300)
            result = json.loads(resp.data.decode("utf-8"))
        except (KeyError, TypeError, AttributeError, Exception) as err:
            self.err_message.append(str(err))
            return None
        return result

    def no_return_request(self, method, url, body=None):

        headers = {
            "X-CSRFTOKEN": self.token,
            "Cookie": self.cookie
        }
        if isinstance(body, dict):
            try:
                payload = json.dumps(body)
            except (KeyError, TypeError, AttributeError, Exception) as err:
                self.err_message.append(str(err))
                return None
            else:
                headers["Content-Type"] = u"application/json"
        else:
            payload = body
        if self.port is not None:
            url = r"https://%s:%s%s" % (self.host, self.port, url)
        else:
            url = r"https://%s%s" % (self.host, url)
        try:
            HTTP.request(method, url, body=payload, retries=False,
                         headers=headers, timeout=300)
        except (KeyError, TypeError, AttributeError, Exception):
            pass

    def delete_session(self):

        self.send_request("DELETE", "/api/session")


class RedfishClient(Client):

    def __init__(self, args):

        super(RedfishClient, self).__init__(args)
        auth = "%s:%s" % (self.username, self.password)
        self.auth = base64.b64encode(auth.encode(encoding="utf-8"))

    def request(self, method, url, data=None, timeout=100):

        if isinstance(data, dict):
            try:
                payload = json.dumps(data)
            except (KeyError, TypeError, AttributeError, Exception) as err:
                self.err_message.append(str(err))
                raise FailException(*self.err_message)
        else:
            payload = data

        if self.port is not None:
            url = r"https://%s:%s%s" % (self.host, self.port, url)
        else:
            url = r"https://%s%s" % (self.host, url)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic %s" % self.auth.decode("utf-8"),
        }
        try:
            response = requests.request(method, url, data=payload,
                                        headers=headers, verify=False,
                                        timeout=timeout)
            if response is None:
                err_message = ("Failure: failed to establish a new "
                               "connection to the host")
                self.err_message.append(err_message)
                raise FailException(*self.err_message)
            if method == "GET":
                resp = {"status_code": response.status_code,
                        "resource":
                            json.loads(response.content.decode('utf8'))}
            elif method == "POST":
                resp = {"status_code": response.status_code,
                        "resource": response.text}
            elif method == "DELETE":
                resp = {"status_code": response.status_code,
                        "resource": response.content}
            elif method == "PATCH":
                resp = {"status_code": response.status_code,
                        "resource": response.content}
        except (KeyError, TypeError, AttributeError, Exception) as err:
            self.err_message.append(str(err))
            raise FailException(*self.err_message)
        return resp

    def get_systems_id(self):

        url = "/redfish/v1/Managers/"
        ret = self.request("GET", url)
        if (isinstance(ret, dict) and ret.get("status_code", None) ==
                Constant.SUCCESS_200):
            try:

                index = (ret["resource"]["Members"][0]["@odata.id"].split(
                    r"/")[4])
            except (IndexError, KeyError, Exception):
                err_info = "Failure: cannot get the machine systems id"
                self.err_message.append(err_info)
                raise FailException(*self.err_message)
        else:
            err_info = "Failure: cannot get the machine systems id"
            self.err_message.append(err_info)
            raise FailException(*self.err_message)
        return index

    def send_request(self, method, url, payload=None, timeout=None):

        method = method.upper()
        if method in {"GET", "PATCH", "POST", "DELETE"}:
            resp = self.request(method, url, payload, timeout=timeout)
        else:
            err_message = "Failure: the request method is illegal"
            self.err_message.append(err_message)
            raise FailException(*self.err_message)
        return resp
