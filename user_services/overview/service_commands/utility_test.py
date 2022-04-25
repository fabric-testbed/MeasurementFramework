import json
import overview_utilities as ou
#import overview_utilities

def main():

    print("Service List")
    s = ou.get_services_list()
    print(s)

    print("READMEs")
    r = ou.get_services_readme()
    print(r)
    #print( json.dumps(result) )

    print("Data json")
    data = ou.get_data()
    print(data) 

    print("Print JSON")
    data["more"] = "Another item"
    json_str = ou.get_json_string(data)
    print(json_str)

if __name__ == "__main__":
    main()
