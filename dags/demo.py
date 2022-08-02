from airflow import DAG
from datetime import datetime
import json
from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from external_files.confidential_client_secret_sample import *
from external_files.upload import *

with DAG(dag_id="Demo",schedule_interval="0 9 * * *", start_date=datetime(2022, 3, 5),catchup=False,  tags=["demo"]) as dag:
    #downloading waves and transcriptions files from OneDrive to upload it later to Azure Blob Storage
    def download_data():
        print(config)
        print(waves_dict_ids)
        print(transcriptions_dict_ids)
        List_files_names=download_waves_files(waves_dict_ids,"waves")
        print(List_files_names)
        download_transcriptions_files(transcriptions_dict_ids,"transcriptions",List_files_names)
        return 0
    
    #uploading waves and transcriptions files to Azure Blob Storage
    def upload_data():
        test=WasbHook(wasb_conn_id="azure_demo")
        print("connection made successfully")
        test.create_container(container_name="waves")
        test.create_container(container_name="transcriptions")
        print("containers created successfully")
        upload(test,"waves")
        upload(test,"transcriptions")
        print("files loaded successfully")
        return 0
    
    #fetching data from azure blob storage account to upload it later u=in mongodb demodb database
    def fetch_data(ti):
        test=WasbHook(wasb_conn_id="azure_demo")
        List_names=test.get_blobs_list(container_name="transcriptions")
        #the function read_file returns a string so it must be converted to json object
        List_contents=[]
        for name in List_names:
            file=test.read_file(container_name="transcriptions",blob_name=name)
            List_contents.append(file)
        ti.xcom_push(key="list_names",value=List_names)
        ti.xcom_push(key="list_contents",value=List_contents)
        # print(file)
        return 0
    #save files records in a databse on postgresql
    def save_records(ti):
        List=ti.xcom_pull(key="list_names",task_ids='data_fetching')
        print(List)
        postgres_hook=PostgresHook("postgres_demo")
        postgres_hook.run(sql="""CREATE TABLE IF NOT EXISTS public."Files"
                            (
                                id integer NOT NULL,
                                name varchar(50) NOT NULL,
                                CONSTRAINT "Files_pkey" PRIMARY KEY (id)
                            )""")
        
        for i in range(len(List)):
            sql=f"""INSERT INTO public."Files"(
                                id,name)
                                VALUES({i+1},'{List[i]}');"""
            postgres_hook.run(sql)
        return 0
                        
    #upload data to mongo database
    def upload_data_mongodb(ti):
        test=MongoHook(conn_id="mongodb_demo")
        List=ti.xcom_pull(key="list_contents",task_ids='data_fetching')
        for content in List:
            file_json=json.loads(content)
            test.insert_one(mongo_collection="transcriptions",doc=file_json,mongo_db="demo_db")
        print("files added to transcriptions collection successfully")
        return 0


    download_data_task = PythonOperator(
        task_id='data_downloading',
        python_callable=download_data,
    )

    upload_data_task = PythonOperator(
        task_id='data_uploading',
        python_callable=upload_data,
    )

    fetch_data_task = PythonOperator(
        task_id='data_fetching',
        python_callable=fetch_data,
    )

    save_records_task = PythonOperator(
        task_id='records_saving',
        python_callable=save_records,
    )

    upload_data_mongodb_task = PythonOperator(
        task_id='data_uploading_mongodb',
        python_callable=upload_data_mongodb,
    )

    download_data_task >> upload_data_task >> fetch_data_task >> save_records_task >> upload_data_mongodb_task