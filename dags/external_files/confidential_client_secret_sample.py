import sys
import json
import logging
import requests
import msal
import os

def get_files_ids(endpoint_name):
    dict={}
    graph_data = requests.get(  # Use token to call downstream service
        config[endpoint_name],
        headers={'Authorization': 'Bearer ' + result['access_token']}, ).json()
    graph_data_value=graph_data["value"]
    for i in range(len(graph_data_value)):
        # if graph_data_value[i]["name"] in ("waves","transcriptions"):
        dict[graph_data_value[i]["name"]]=graph_data_value[i]["id"]
    return dict
def download_waves_files(dict,folder_name):
    L=[]
    headers={'Authorization': 'Bearer ' + result['access_token']}
    save_location=("/opt/airflow/files/{}/").format(folder_name)
    if not os.path.exists(save_location):
        os.makedirs(save_location)
    # Step 1. get the file name
    for file_id in list(dict.values()):
        response_file_info = requests.get(
            config["endpoint"] + f'drive/items/{file_id}',
            headers=headers,
            params={'select': 'name'}
        )
        file_name = response_file_info.json().get('name')

        # Step 2. downloading OneDrive file
        response_file_content = requests.get(config["endpoint"] + f'drive/items/{file_id}/content', headers=headers)
        with open(os.path.join(save_location, file_name), 'wb') as _f:
            _f.write(response_file_content.content)
        L.append(file_name.split(".")[0])
    return L
def download_transcriptions_files(dict,folder_name,List):
    headers={'Authorization': 'Bearer ' + result['access_token']}
    save_location=("/opt/airflow/files/{}/").format(folder_name)
    if not os.path.exists(save_location):
        os.makedirs(save_location)
    # Step 1. get the file name
    for file_id in list(dict.values()):
        response_file_info = requests.get(
            config["endpoint"] + f'drive/items/{file_id}',
            headers=headers,
            params={'select': 'name'}
        )
        file_name = response_file_info.json().get('name')
        if file_name.split(".")[0] in List: 
            # Step 2. downloading OneDrive file
            response_file_content = requests.get(config["endpoint"] + f'drive/items/{file_id}/content', headers=headers)
            with open(os.path.join(save_location, file_name), 'wb') as _f:
                _f.write(response_file_content.content)
            print(file_name.split(".")[0])


config = json.load(open("/opt/airflow/dags/external_files/parameters.json",'r'))
print(config)

# Create a preferably long-lived app instance which maintains a token cache.
app = msal.ConfidentialClientApplication(
    config["client_id"], authority=config["authority"],
    client_credential=config["secret"],
    )

# # The pattern to acquire a token looks like this.
result = None
result = app.acquire_token_silent(config["scope"], account=None)
waves_dict_ids={}
transcriptions_dict_ids={}


if not result:
    logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
    result = app.acquire_token_for_client(scopes=config["scope"])

if "access_token" in result:
    waves_dict_ids=get_files_ids("endpoint_waves")
    transcriptions_dict_ids=get_files_ids("endpoint_transcriptions")
    print("Graph API call result: ")
    print(waves_dict_ids)
    print(transcriptions_dict_ids)
else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You may need this when reporting a bug





