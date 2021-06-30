
import os
import sys

import logging
# Disable ssl warnings? Needed if using requests?
import urllib3
# Need these logging/warning settings so we don't see all the urllib messages
urllib3.disable_warnings()
logging.getLogger("urllib3").setLevel(logging.ERROR)
import requests
logging.getLogger("requests").setLevel(logging.ERROR)
import ssl
# Avoid errors when using test certs - common in corrections
# Needed if using requests?
#ssl._create_default_https_context = ssl._create_unverified_context

#import base64
import json

import util
from color import p

from mgmt_Encryption import Encryption
from mgmt_RegistrySettings import RegistrySettings

class RestClient:

    def __ini__(self):
        pass
    
    @staticmethod
    def send_rest_call(server, api_endpoint, method="GET", params=None, auth_user=None,
        auth_password=None, json_params=None, timeout=30):
        # Get the complete URL for the call 
        rest_url = server
        if not rest_url.endswith("/"):
            rest_url += "/"
        if api_endpoint.startswith("/"):
            api_endpoint = api_endpoint[1:]
        rest_url = rest_url + api_endpoint
        
        headers = dict()

        auth = None
        if (auth_user is not None and auth_password is not None):
            #key = base64.b64encode(str(auth_user + ':' + auth_password).encode()).decode()
            #headers = {'Authorization': 'Basic ' + key}
            auth = (auth_user, auth_password)
        
        try:
            if method.upper() == "GET":
                resp = requests.get(rest_url, params=params, headers=headers,
                    auth=auth, verify=False, json=json_params, timeout=timeout)
            elif method.upper() == "POST":
                resp = requests.post(rest_url, params=params, headers=headers,
                    auth=auth, verify=False, json=json_params, timeout=timeout)
            else:
                p("}}rb*** METHOD NOT IMPLEMENTED! ***}}xx")
                return None
        except requests.exceptions.ConnectionError as ex:
            p("}}rb*** Connection error trying to connect to server ***}}xx")
            p("}}yn" + str(ex) + "}}xx")
            return None
        except requests.exceptions.MissingSchema as ex:
            p("}}rb*** Connection error trying to connect to server ***}}xx")
            p("}}yn" + str(ex) + "}}xx")
            return None
        except Exception as ex:
            p("}}rb*** Connection error trying to connect to server ***}}xx")
            p("}}yn" + str(ex) + "}}xx")
            return None
            
        if resp is None:
            # Unable to get a response?
            p("}}rb*** Invalid response from server! ***}}xx " + str(server))
            return None
        
        if resp.status_code == requests.codes.forbidden:
            p("}}rb*** Error authenticating with server - check password and try again ***}}xx")
            return None
        
        try:
            resp.raise_for_status()
        except Exception as ex:
            p("}}rb*** General error trying to connect to server ***}}xx")
            p("}}ybMake sure this software and the SMC is fully up to date}}xx")
            p("}}yn" + 
            str(ex) + "}}xx")
            return None
            
        json_response = None
        try:
            json_response = resp.json()
        except ValueError as ex:
            p("}}rb*** Invalid JSON reponse from server ***}}xx")
            p("}}yn" + str(ex) + "}}xx")
            return None
        except Exception as ex:
            p("}}rb*** UNKNOWN ERROR ***}}xx")
            p("}}yn" + str(ex) + "}}xx")
            return None
        
        return json_response

    @staticmethod
    def credential_student_in_smc(student_user, smc_url, smc_admin_user, smc_admin_pw, ex_info):
        # Send the info to the SMC server to 
        json_response = RestClient.send_rest_call(server=smc_url,
            api_endpoint="lms/credential_student.json/" + student_user,
            method="POST", json_params=ex_info,
            auth_user=smc_admin_user, auth_password=smc_admin_pw)

        if json_response is None:
            # If None - fatal error!
            return None
        
        # Interpret response from SMC
        try:
            #p("RESP: " + str(smc_response))
            msg = util.get_dict_value(json_response, "msg", default="missing")
            if msg == "missing":
                p("}}rbUnable to interpret response from SMC - no msg parameter returned}}xx")
                return None
            if msg == "Invalid User!":
                p("\n}}rbInvalid User!}}xx")
                p("}}mnUser doesn't exit in system, please import this student in the SMC first!}}xx")
                return None
            if msg == "No username specified!":
                p("\n}}rbInvalid User!}}xx")
                p("}}mnNo user with this name exists, please import this student in the SMC first!}}xx")
                return None
            if "unable to connect to canvas db" in msg:
                p("\n}}rbSMC Unable to connect to Canvas DB - make sure canvas app is running and\n" +
                "the SMC tool is configured to talk to Canvas}}xx")
                p("}}yn" + str(msg) + "}}xx")
                return None
            if "Unable to find user in canvas:" in  msg:
                p("\n}}rbInvalid User!}}xx")
                p("}}mnUser exists in SMC but not in Canvas, please rerun import this student in the SMC to correct the issue!}}xx")
                return None
            #full_name = util.get_dict_value(json_response, "full_name")
            canvas_access_token = util.get_dict_value(json_response, "key")
            student_hash = util.get_dict_value(json_response, "hash")
            admin_hash = util.get_dict_value(json_response, "admin_hash")
            student_full_name = util.get_dict_value(json_response, "full_name")
            canvas_url = util.get_dict_value(json_response, "canvas_url")
        except Exception as ex:
            p("}}rbUnable to interpret response from SMC - no msg parameter returned}}xx")
            p("}}mn" + str(ex) + "}}xx")
            return None
        
        # Decrypt scrambled parts
        student_password = Encryption.decrypt(student_hash, canvas_access_token)
        laptop_admin_password = Encryption.decrypt(admin_hash, canvas_access_token)
        # TODO - DEBUG - Disable this line!
        adm_pw_masked = (len(laptop_admin_password)-1) * "*" + laptop_admin_password[-1:]
        #p(student_password + "/" + adm_pw_masked, log_level=5)

        return (student_full_name, canvas_url, canvas_access_token,
            student_password, laptop_admin_password)

    @staticmethod
    def verify_ope_account_in_smc(student_user, smc_url, smc_admin_user, smc_admin_pw):
        # Bounce off the SMC server to see if the student account exists in SMC
        # NOTE - this one does NOT check canvas for the user
        
        laptop_admin_user = ""
        laptop_admin_password = ""
        student_full_name = ""
        smc_version = ""
        
        p("\n}}gnChecking user status in SMC tool...}}xx")
        
        json_response = RestClient.send_rest_call(server=smc_url,
            api_endpoint="lms/verify_ope_account_in_smc.json/" + student_user,
            auth_user=smc_admin_user, auth_password=smc_admin_pw)

        if json_response is None:
            # If None - fatal error!
            return None
        
        # Interpret response from SMC
        try:
            msg = util.get_dict_value(json_response, "msg")
            if msg == "":
                p("}}rbUnable to interpret response from SMC - no msg parameter returned}}xx")
                p(json_response)
                return None
            if msg.startswith("Invalid User!"):
                p("\n}}rbInvalid User!}}xx")
                p("}}ynUser doesn't exit in system, please import this student in the SMC first!}}xx")
                return None
            if msg == "No username specified!":
                p("\n}}rbInvalid User!}}xx")
                p("}}mnNo user with this name exists, please import this student in the SMC first!}}xx")
                return None
            student_full_name = util.get_dict_value(json_response, "student_full_name")
            laptop_admin_user = util.get_dict_value(json_response, "laptop_admin_user")
            smc_version = util.get_dict_value(json_response, "smc_version")
            # Password moved to credential step
            #laptop_admin_password = util.get_dict_value(json_response, "laptop_admin_password")
        except Exception as ex:
            p("}}rbUnable to interpret response from SMC - no msg parameter returned}}xx")
            p("}}mn" + str(ex) + "}}xx")
            # p(str(smc_response))
            return None
        
        if laptop_admin_user == "": # or laptop_admin_password == "":
            p("}}rbERR - Please set the laptop admin credentials in the SMC before continuing (Admin -> Configure App -> Laptop Admin Credentials) }}xx")
            return None # sys.exit(-1)
        
        if student_full_name == "":
            p("}}rbERR - Unable to find student user in the SMC? Make sure it is imported.}}xx")
            return None # sys.exit(-1)

        
        #return (laptop_admin_user, laptop_admin_password, student_full_name)
        return (laptop_admin_user, student_full_name, smc_version)


    @staticmethod
    def ping_smc(smc_url):

        json_response = RestClient.send_rest_call(server=smc_url,
            api_endpoint="lms/ping.json", timeout=3
            )

        if json_response is None:
            # If None - unable to communicate - likely offline
            p("}}ynNo response from smc server}}xx", log_level=4)
            return False
        
        server_time = util.get_dict_value(json_response, "server_time")
        RegistrySettings.set_reg_value(value_name="server_time", value=server_time)
        p("}}mnPING - Got SMC Server time: " + str(server_time) + "}}xx")

        return True

if __name__ == "__main__":
    # Run Tests
    r = RestClient.ping_smc("https://bad_url.com")
    p("Response: " + str(r))
