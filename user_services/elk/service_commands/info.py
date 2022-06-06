import os
import json

def main():
    ret_val = {}

    try:
        f = open('/home/mfuser/mf_git/instrumentize/elk/credentials/nginx_passwd', 'r')
        ret_val["nginx_password"] = f.read()
        ret_val["nginx_id"] = "fabric"
    except IOError:
        ret_val["error"] = "File does not appear to exist."

    print(json.dumps(ret_val))

if __name__ == "__main__":
    main()