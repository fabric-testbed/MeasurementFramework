import os
import json

import elk_utilities as eu

def main():
    ret_val = { "success":True, "msg":"" }
    data = eu.get_data()
    
    if "get" in data:
        try:
            with open('/home/mfuser/mf_git/instrumentize/elk/credentials/nginx_passwd', 'r') as f:
                nginx_password = f.read().strip()
            
            if "nginx_password" in data["get"]:
                ret_val["nginx_password"] = nginx_password          
            if "nginx_id" in data["get"]:
                ret_val["nginx_id"] = "fabric"

        except IOError:
            ret_val["error"] = "Nginx credential file does not appear to exist."
        


    else:
        try:
            with open('/home/mfuser/mf_git/instrumentize/elk/credentials/nginx_passwd', 'r') as f:
                ret_val["nginx_password"] = f.read().strip()
            ret_val["nginx_id"] = "fabric"
        except IOError:
            ret_val["error"] = "File does not appear to exist."

    print(eu.get_json_string(ret_val))
    #print(json.dumps(ret_val))

if __name__ == "__main__":
    main()