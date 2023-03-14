import os
import json
import subprocess

import elk_utilities as eu

def main():
    ret_val = { "success":True}
    data = eu.get_data()

    if "get" in data:
        if "nginx_password" in data["get"] or "nginx_id" in data["get"]:
            try:
                with open(eu.nginx_password_filename, 'r') as f:
                    nginx_password = f.read().strip()
                if "nginx_password" in data["get"]:
                    ret_val["nginx_password"] = nginx_password
                if "nginx_id" in data["get"]:
                    ret_val["nginx_id"] = "fabric"
            except IOError:
                ret_val["error"] = "Nginx credential file does not appear to exist."
        if "index_names" in data["get"]:
            try:
                # Calls index name API
                r = subprocess.run(["curl","-XGET","http://localhost:9200/_cat/indices/?h=index"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                # Gathers all external user indices, ignoring internal "." prefixed indices.
                indices = []
                for line in r.stdout.splitlines():
                    if line[0] != ".":
                        indices.append(line)
                indices = tuple(indices)
                ret_val["index_names"] = indices
            except:
                ret_val = {"success": False, "ERROR": "Failed to fetch ELK index data."}
    else:
        ret_val["info"] = "Pass in a dictionary with the info you want to get. For example: data['get'] = ['info_type']. info types include nginx_id, nginx_password, and index_names"

    print(eu.get_json_string(ret_val))
    #print(json.dumps(ret_val))

if __name__ == "__main__":
    main()