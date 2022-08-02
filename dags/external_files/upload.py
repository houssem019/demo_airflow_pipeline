from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
import os

def upload(hook,file_type):
    dir_path=("/opt/airflow/files/{}/").format(file_type)
    L=os.listdir(dir_path)
    print(L)
    for name in L:
        file_path=os.path.join(dir_path,name)
        hook.load_file(file_path=file_path,container_name=file_type,blob_name=name.split(".")[0])