import msal
import os
from office365.graph_client import GraphClient
from office365.onedrive.drives.drive import Drive

def acquire_token_func():
    """
    Acquire token via MSAL
    """
    authority_url = 'https://login.microsoftonline.com/e0cf9a78-c695-404d-a358-126ac5781e34'
    app = msal.ConfidentialClientApplication(
        authority=authority_url,
        client_id='4003d5f2-9e46-4ae3-8ded-bc2c9f68d76c',
        client_credential='Eix8Q~WkJx80SwjB6AQMvELypTvrIlj8TdxXldvq'
    )
    token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return token

token =acquire_token_func()
print(token)


client = GraphClient(acquire_token_func)

target_drive = client.users["houssem@yq1ws.onmicrosoft.com"].drive.get().execute_query()
local_path = "C:/Users/user/Desktop/demo/demo_airflow_pipeline/files/example_2.json"
with open(local_path, 'rb') as f:
    file_content = f.read()
file_name = os.path.basename(local_path)
target_file = target_drive.root.upload(file_name, file_content).execute_query()
print(f"File {target_file.web_url} has been uploaded")
