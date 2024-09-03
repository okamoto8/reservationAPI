import requests
import json

def main():
    url = 'http://127.0.0.1:8000/items/'
    body={
        
        "name":"fkajgao",
        "startTime":"fakjafa",
        "endTime":"galfmval"
    }
    res = requests.post( url,json.dumps(body))
    print(res.json())

if __name__ == "__main__":
    main()