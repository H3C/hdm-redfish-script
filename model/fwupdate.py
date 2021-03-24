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


import time
import os
import threading
import json
from exception.ToolException import FailException
from utils.client import FwUpdateClient
from utils.model import BaseModule
from utils.common import Constant
from utils.tools import init_args

LOG_JSON_LIST = []
PSN = "Unknown"
SET_FW_FAILED = "Set FW type failed"
IS_OVERRIDE = False
IS_AUTO = False
FW_NAME = None
FW_CUR_VER = None
FW_NEW_VER = None
UPLOAD_COMPLETE = False
NEW_CLIENT = None
IS_DUAL = False
FW_BACKUP_VER = None
FW_PRIMARY_VER = None
OUTPUT_FORMAT = "%-30s: %s"
LOG_PATH = "%s/%s/%s" % (os.path.pardir, "update",
                         time.strftime("%Y%m%d%H%M%S", time.localtime()))


class Fwupdate(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["activate_mode", "firmware_type",
                         "image_uri", "is_override", "has_me", "is_dual_image"]

    def run(self, args):

        init_args(args, self.args_lst)

        if args.is_dual_image == "Dual" and (args.firmware_type != "BMC" or
                                             args.activate_mode != "Auto"):
            err_info = ("Failure: to upgrade dual mirrors, the firmware type "
                        "must be BMC and the startup mode must be automatic, "
                        "please check the parameters")
            self.err_list.append(err_info)
            raise FailException(*self.err_list)

        global IS_DUAL
        if args.is_dual_image == "Dual":
            IS_DUAL = True
        client = FwUpdateClient(args)
        try:

            if IS_DUAL:
                url = "/api/maintenance/primary_backup_version"
                resp = client.send_request("GET", url)
                if (isinstance(resp, dict) and
                        Constant.SUCCESS_0 == resp.get("cc", None)):
                    global FW_BACKUP_VER, FW_PRIMARY_VER
                    FW_BACKUP_VER = resp.get("backup_version")
                    FW_PRIMARY_VER = resp.get("primary_version")
                else:
                    err_info = (
                        "Failure: failed to obtain the HDM version "
                        "of the standby partition")
                    self.err_list.append(err_info)
                    raise FailException(*self.err_list)
            client = start_fwupdate(client, args)
        finally:
            if client.cookie:
                client.delete_session()
        if client.err_message:
            self.err_list.extend(client.err_message)
            raise FailException(*self.err_list)
        if client.suc_message:
            self.suc_list.extend(client.suc_message)
        return self.suc_list


def check_args(args):

    if args.is_dual_image == "Dual" and (args.firmware_type != "BMC" or
                                         args.activate_mode != "Auto"):
        return False
    global IS_DUAL
    IS_DUAL = True
    return True


def log_json_append(stage, state, note):

    time_s = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    log_time = "%s%s" % (time_s, zone())
    log_json = {
        "Time": log_time,
        "Stage": stage,
        "State": state,
        "Note": note
    }
    LOG_JSON_LIST.append(log_json)


def log_json_write():

    logs = {
        "log": LOG_JSON_LIST
    }
    log_name = "%s_%s%s%s" % (LOG_PATH, PSN, os.path.sep, "fwupdate.log")
    log = open(log_name, "a+")
    json.dump(logs, log, indent=4, separators=(",", ": "))
    LOG_JSON_LIST.clear()
    log.close()


def zone():

    sec = ("+" if time.timezone < 0 else "-")
    hours = (0 - time.timezone) / 3600
    if abs(hours) < 10:
        resp = sec + "0%d:00" % hours
    else:
        resp = sec + "%d:00" % hours
    return resp


def reset_hdm(client, reset_cmd=False, args=None):

    url = "/api/maintenance/restore_hdm"
    payload = {
        "reset": 1
    }

    if reset_cmd:
        retry = 0
        while retry < 3:
            retry = retry + 1
            resp = client.send_request("POST", url, payload)
            if resp and isinstance(resp, dict):
                if resp.get(Constant.COMPLETE_CODE, None) == 0:
                    log_json_append("Retry", "Reset bmc",
                                    "Update firmware failure, Reset bmc")
                    info = "Update firmware failure, Reset bmc"
                    print(print_console_info(info))
                    break
                else:
                    log_json_append("Retry", "Reset bmc",
                                    "Reset bmc failed, delay 60s reset bmc")
                    info = "Reset bmc failed, delay 60s reset bmc"
                    print(print_console_info(info))
                    time.sleep(60)
            else:
                time.sleep(60)
                continue

    time.sleep(300)
    return check_restart_ok(args)


def check_restart_ok(args):

    url = "/api/maintenance/firmware/type"
    retry = 0

    while retry < 18:

        global NEW_CLIENT
        NEW_CLIENT = FwUpdateClient(args)
        resp = NEW_CLIENT.send_request("GET", url)
        if resp is None:
            time.sleep(10)
        elif resp and isinstance(resp, dict):
            if resp.get(Constant.COMPLETE_CODE) == 0:
                info = "BMC reboot complete"
                print(print_console_info(info))
                return True
            else:
                time.sleep(10)
        retry = retry + 1
    return False


def get_psn(client):

    url = "/api/fru"
    resp = client.send_request("GET", url)
    if resp is None:
        pass
    elif resp and isinstance(resp, list):
        for mess in resp:
            if (mess.get("device_id", None) == 0 and
                    mess.get("device_name", None) == "BaseBoard"):
                product = mess.get("product")
                if isinstance(product, dict) and product.get("serial_number",
                                                             None) is not None:
                    return product["serial_number"]
    else:
        return "Unknown"
    return "Unknown"


class UploadThread(threading.Thread):

    def __init__(self, thread_id, name, client, args):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.client = client
        self.args = args

    def run(self):
        upload_progress(self.client, self.args)


def upload_progress(client, args):

    url = "/api/maintenance/firmware"
    global UPLOAD_COMPLETE

    bin_file = args.image_uri
    if bin_file is None or not os.path.exists(bin_file):
        log_json_append("Upload File", "Failure", "File Not Exist")
        err_message = "file not exist"
        client.err_message.append(err_message)
        UPLOAD_COMPLETE = False
        return
    with open(bin_file, "rb") as file_:
        file_read = file_.read()

    file_name = os.path.split(bin_file)[1]

    fields = {
        "fwimage": (file_name, file_read, "application/octet-stream")
    }
    info = "Upload file inprogress..."
    print(print_console_info(info))
    resp = client.upload_request("POST", url, fields=fields)
    if resp is None:
        UPLOAD_COMPLETE = False
    elif resp and isinstance(resp, dict):
        for key, value in resp.items():
            if key == Constant.COMPLETE_CODE and value == 0:
                info = "Upload file successfully"
                print(print_console_info(info))
                log_json_append("Upload File", "Finish", "Upload file success")
                UPLOAD_COMPLETE = True
                break
            elif key == Constant.COMPLETE_CODE and value != 0:
                info = "Upload file failed"
                print(print_console_info(info))
                log_json_append("Upload File", "Finish", "Upload file failed")
                err_message = "upload file failed"
                client.err_message.append(err_message)
                UPLOAD_COMPLETE = False
    else:
        log_json_append("Upload File", "Finish", "Upload file failed")
        info = "Upload file error"
        print(print_console_info(info))
        err_message = "upload file failed"
        client.err_message.append(err_message)
        UPLOAD_COMPLETE = False


def bmc_ver_same():

    bmc_cur_version = get_bmc_ver()
    ver_len = min(len(FW_NEW_VER), len(bmc_cur_version))
    if ver_len == len(FW_NEW_VER):
        flag = (FW_NEW_VER in bmc_cur_version)
    else:
        flag = (FW_NEW_VER[:ver_len] == bmc_cur_version[:ver_len])
    return flag


def get_bmc_ver():

    url = "/api/maintenance/primary_backup_version"
    resp = NEW_CLIENT.send_request("GET", url)
    if resp is None:
        pass
    elif resp and isinstance(resp, dict):
        for key, value in resp.items():
            if key == Constant.COMPLETE_CODE and value != 0:
                break
            if key == "primary_version":
                return value
            if key == "backup_version":
                continue
    else:
        return "Unknown"
    return "Unknown"


def set_fw_type(client, args):

    global IS_OVERRIDE
    url = "/api/maintenance/firmware/type"
    payload = construct_request_parameters(args)
    resp = client.send_request("POST", url, payload)
    flag = False
    if resp is None:
        pass
    elif resp and isinstance(resp, dict):
        for key, value in resp.items():
            if key == Constant.COMPLETE_CODE and value == 0:
                if args.is_override == 1:
                    IS_OVERRIDE = True
                info = "Set fw type success"
                print(print_console_info(info))
                log_json_append("Upload File", "Start", "Set fw type is %s"
                                % args.firmware_type)
                flag = True
                break
            elif key == Constant.COMPLETE_CODE and value != 0:
                log_json_append(
                    "Upload File",
                    "Set FW Type Failed",
                    "Set fw type is %s failed" %
                    args.firmware_type)
                client.err_message.append(SET_FW_FAILED)
    else:
        log_json_append("Upload File", "Connect Failed",
                        "Set fw type is %s failed" % args.firmware_type)
        print(print_console_info(SET_FW_FAILED))
        client.err_message.append(SET_FW_FAILED)
    return flag


def construct_request_parameters(args):

    global IS_AUTO
    IS_AUTO = (True if args.activate_mode == "Auto" and args.
               firmware_type == "BMC" else False)
    global FW_NAME
    FW_NAME = ("HDM" if args.firmware_type == "BMC" else args.firmware_type)
    payload = {
        "preserve_config": (1 if args.is_override == 1 else 0),
        "fw_type_name": ("HDM" if args.firmware_type == "BMC"
                         else args.firmware_type),
        "reboot_type": (0 if IS_AUTO and args.firmware_type == "BMC" else 2),
        "reboot_time": 0,
        "bios_update_flag": (
            1 if args.has_me == 0 else 2 if args.has_me == 2 else 0)
    }
    return payload


def prepare_flash(client):

    url = "/api/maintenance/flash"
    client.no_return_request("PUT", url)
    info = "Upload file start"
    print(print_console_info(info))
    log_json_append("Upload File", "In Progress", "Prepare flash")
    return


def upload_firmware(client, args):

    try:
        thread = UploadThread(1, "upload-thread", client, args)
        thread.start()
    except (TypeError, KeyError, ValueError, NameError, AttributeError):
        info = "Unable to start upload thread"
        print(print_console_info(info))
        log_json_append("Upload File", "Start",
                        "Upload file failed start thread")
        err_message = "upload file failed start thread"
        client.err_message.append(err_message)
        return False
    count = 100
    global UPLOAD_COMPLETE
    while count > 0:
        if not thread.is_alive():
            return bool(UPLOAD_COMPLETE)
        time.sleep(3)
        count = count - 1
    if count == 0:
        log_json_append("Upload File", "Finish", "Upload file failed timeout")
        info = "Upload file failed timeout"
        print(print_console_info(info))
        err_message = "upload file failed timeout"
        client.err_message.append(err_message)
        return False


def verification(client):

    url = "/api/maintenance/firmware/verification"
    resp = client.send_request("GET", url)
    flag = False
    if resp is None:
        pass
    elif resp and isinstance(resp, dict):
        if Constant.COMPLETE_CODE in resp:
            if resp[Constant.COMPLETE_CODE] == 0:
                global FW_CUR_VER
                global FW_NEW_VER
                FW_CUR_VER = resp["current_image_version"]
                FW_NEW_VER = resp["new_image_version"]
                info = "File verify successfully"
                print(print_console_info(info))
                log_json_append("File Vertify", "Version Vertify OK", info)
                flag = True
            else:
                info = "File vertify failed"
                print(print_console_info(info))
                log_json_append("File Vertify", "Version Vertify Failed",
                                "File vertify failed")
                err_message = "file vertify failed"
                client.err_message.append(err_message)
        elif "code" in resp:
            info = "File vertify failed"
            print(print_console_info(info))
            log_json_append("File Vertify", "Version Vertify Failed",
                            "Image and Target Component Mismatch")
            err_message = "Image and Target Component Mismatch"
            client.err_message.append(err_message)
    else:
        info = "File vertify error"
        print(print_console_info(info))
        log_json_append("File Vertify", "Finish",
                        "Image and Target Component Mismatch")
        err_message = "File Vertify request failed"
        client.err_message.append(err_message)
    return flag


def upgrade(client):

    url = "/api/maintenance/firmware/upgrade"
    payload = {"flash_status": 1}
    resp = client.send_request("PUT", url, payload)
    flag = False
    if resp is None:
        pass
    elif resp and isinstance(resp, dict):
        for key, value in resp.items():
            if key == Constant.COMPLETE_CODE and value == 0:
                info = "Apply(Flash) start"
                print(print_console_info(info))
                flag = True
                break
    else:
        info = "Apply(Flash) start error"
        print(print_console_info(info))
        log_json_append("Apply", "Failed", "Upgrade command success")
        err_message = "Upgrade request failed"
        client.err_message.append(err_message)
    return flag


def flash_progress(client, write_log=True):

    url = "/api/maintenance/firmware/flash_progress"
    resp = client.send_request("GET", url)
    if resp is None:
        pass
    elif resp and isinstance(resp, dict):
        if Constant.COMPLETE_CODE in resp:
            if resp[Constant.COMPLETE_CODE] == 0:
                if write_log:
                    log_json_append(
                        "Apply",
                        (resp["action"] if "action" in resp else "Flashing"),
                        (resp["progress"] if "progress" in resp else "Doing"))
                info = ("Apply(Flash) ingrogress, process: %s" %
                        resp.get("progress"))
                print("\r%s" % print_console_info(info), end="")
            if resp[Constant.COMPLETE_CODE] == 255:
                print()
                info = "Apply(Flash) successfully"
                print(print_console_info(info))
                log_json_append("Apply", (resp["action"] if "action" in resp
                                          else "Flashing"),
                                (resp["progress"] if
                                 "progress" in resp else "Doing"))
                return 100
            return resp[Constant.COMPLETE_CODE]
    else:
        print()
        err_message = "Apply(Flash) error"
        print(print_console_info(err_message))
        client.err_message.append(err_message)
        return -1


def start_fwupdate(client, args):

    if not os.path.isfile(args.image_uri):
        err_info = "Firmware file does not exist"
        client.err_message.append(err_info)
        return client
    try:

        global PSN
        PSN = get_psn(client)
        info = "Get product serial number : %s" % PSN
        print(print_console_info(info))
        os.makedirs(LOG_PATH + "_" + PSN)
        for i in range(2):
            retry = 0
            retry_times = 3
            while retry < retry_times:
                if env_ok(client):
                    if firmware_upgrade(client, args, i):
                        client = (
                            NEW_CLIENT if (IS_AUTO and args.firmware_type ==
                                           "BMC" and not IS_OVERRIDE)
                            else client)

                        if args.firmware_type == "BMC":
                            if i == 0:
                                suc_message = ("%s upgrade successfully, "
                                               "Version: primary image "
                                               "change from %s to %s" %
                                               (FW_NAME, FW_PRIMARY_VER,
                                                FW_NEW_VER))
                            else:
                                suc_message = ("%s upgrade successfully, "
                                               "Version: primary image "
                                               "change from %s to %s, "
                                               "backup image change from"
                                               " %s to %s" %
                                               (FW_NAME, FW_PRIMARY_VER,
                                                FW_NEW_VER, FW_BACKUP_VER,
                                                FW_NEW_VER))
                        else:
                            suc_message = ("%s upgrade successfully, Version: "
                                           "image change from %s to %s"
                                           % (FW_NAME, FW_CUR_VER, FW_NEW_VER))
                        client.suc_message.append(suc_message)

                        if not IS_DUAL or (IS_DUAL and i == 1):
                            log_json_write()
                            client.err_message = list()
                            return client

                        break

                info = 'Firmware update failed, Retry %d, waiting...' % (
                    retry + 1)
                print(print_console_info(info))
                time.sleep(120)
                retry = retry + 1

                if (IS_AUTO and
                        args.firmware_type == "BMC" and reset_hdm(client, True,
                                                                  args)):

                    client = FwUpdateClient(args)
                elif IS_AUTO and args.firmware_type == "BMC":
                    log_json_append("Restart", "Failure",
                                    args.firmware_type +
                                    " FW upgrade failure, "
                                    "get restart status is timeout")
                    err_message = ("Failure" + args.firmware_type +
                                   " FW update failure, get restart status is "
                                   "timeout")
                    client.err_message.append(err_message)
                else:
                    log_json_append(
                        "Retry",
                        "Finish",
                        "Firmware update failure, Retry %d" %
                        retry)
                    err_message = "Failure" + args.firmware_type + \
                                  " FW update failure, Retry %d" % retry
                    client.err_message.append(err_message)
            if retry == retry_times:
                log_json_append("Retry", "Finish",
                                "Can not firmware update, Retry %d" % retry)
                err_message = "Retry %d can not firmware update" % retry
                client.err_message.append(err_message)

            if not IS_DUAL:
                break
    except (TypeError, KeyError, ValueError, NameError, AttributeError):
        log_json_append("FWupdate", "Failed", "FWupdate catch exception error")
        err_message = "FWupdate catch exception error"
        client.err_message.append(err_message)
    log_json_write()
    return client


def env_ok(client):

    url = "/api/maintenance/firmware/type"
    resp = client.send_request("GET", url)
    flag = False
    if resp is None:
        pass
    elif resp and isinstance(resp, dict):
        for key, value in resp.items():
            if key == Constant.COMPLETE_CODE and value == 0:
                log_json_append("Check", "Network Ping OK",
                                "Check environment is ok")
                info = "Check environment is ok"
                print(print_console_info(info))
                flag = True
                break
            elif key == Constant.COMPLETE_CODE and value != 0:
                log_json_append("Check", "Connect Failed",
                                "Check environment is not ok")
                err_message = (resp["error"] if "error" in resp
                               else "Check environment is not ok")
                client.err_message.append(err_message)
        if "code" in resp:
            log_json_append("Check", "Finish",
                            resp["error"] if "error" in resp else
                            "Check environment is not ok")
            err_message = (resp["error"] if "error" in resp
                           else "Check environment is not ok")
            client.err_message.append(err_message)
    else:
        info = "Check environment is not ok"
        print(print_console_info(info))
        err_message = "Check environment is not ok"
        client.err_message.append(err_message)
        log_json_append("Check", "Finish", "Check environment is not ok")
    return flag


def firmware_upgrade(client, args, index):

    global IS_OVERRIDE
    complete_ok = set_fw_type(client, args)
    if not complete_ok:
        return False

    prepare_flash(client)

    complete_ok = upload_firmware(client, args)
    if not complete_ok:
        return False

    time.sleep(1)
    complete_ok = verification(client)
    if not complete_ok:
        return False

    complete_ok = upgrade(client)
    if not complete_ok:
        return False
    time.sleep(1)

    count = 1
    write_log = True
    is_complete = False
    while count < 100:
        count += 1
        code_int = flash_progress(client, write_log)
        if code_int == 100:
            is_complete = True
            break
        if code_int == 0:
            write_log = False
            time.sleep(5)
    if count == 100:
        log_json_append("Activate", "Failure", args.firmware_type +
                        " FW upgrade failure, get progress timeout")
        err_message = ("Failure" + args.firmware_type +
                       " FW update failure, get progress timeout")
        client.err_message.append(err_message)
        return False
    if is_complete:

        if IS_AUTO:
            info = "Auto model BMC restart, please waiting..."
            print(print_console_info(info))
            log_json_append("Restart", "Start",
                            "Auto model BMC restart, please waiting...")
            if not IS_OVERRIDE:
                if reset_hdm(client, False, args):

                    if bmc_ver_same():

                        if index == 0:
                            log_json_append("Restart", "Success",
                                            "%s FW upgrade success, primary "
                                            "image from %s to %s"
                                            % (FW_NAME, FW_PRIMARY_VER,
                                               FW_NEW_VER))
                        else:
                            log_json_append("Restart", "Success",
                                            "%s FW upgrade success, backup "
                                            "image from %s to %s"
                                            % (FW_NAME, FW_BACKUP_VER,
                                               FW_NEW_VER))
                        info = "Version verify ok"
                        print(print_console_info(info))

                        return True
                    else:
                        log_json_append("Restart", "Failure",
                                        args.firmware_type +
                                        " FW upgrade failure, restart version "
                                        "is not same")
                        err_message = (
                            "Failure" + args.firmware_type +
                            " FW update failure, restart "
                            "version is not same")
                        client.err_message.append(err_message)
                        return False
                else:
                    log_json_append("Restart", "Failure", args.firmware_type +
                                    " FW upgrade failure, "
                                    "get restart status is timeout")
                    err_message = (
                        "Failure" + args.firmware_type +
                        " FW update failure, get restart status is timeout")
                    client.err_message.append(err_message)
                    return False
            else:
                time.sleep(300)
                log_json_append("Activate", "Success",
                                "%s FW upgrade success, from %s to %s" %
                                (FW_NAME, FW_CUR_VER, FW_NEW_VER))
                return True

        else:
            log_json_append("Activate", "Success",
                            "%s FW upgrade success, from %s to %s" %
                            (FW_NAME, FW_CUR_VER, FW_NEW_VER))
            return True
    else:
        return False


def print_console_info(info):

    new_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    info_str = "%s %s" % (new_time, info)
    return info_str
