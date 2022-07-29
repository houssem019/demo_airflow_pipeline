from airflow import DAG
from datetime import datetime
import json
from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.operators.python import PythonOperator

with DAG(dag_id="Demo",schedule_interval="0 9 * * *", start_date=datetime(2022, 3, 5),catchup=False,  tags=["demo"]) as dag:
    #creating a container named demo where i m gonna upload the data
    def create_container():
        # test=WasbHook(wasb_conn_id="azure_demo")
        # print(test)
        # print("connection made successfully")
        # test.create_container(container_name="demo")
        # print("container created successfully")
        return 0
    
    #uploading a json file to the created container
    def upload_data():
        # test=WasbHook(wasb_conn_id="azure_demo")
        # test.load_file(file_path="/opt/airflow/files/example_2.json",container_name="demo",blob_name="example")
        # print("file loaded successfully")
        return 0
    
    #fetching data from azure blob storage account to upload it later u=in mongodb demodb database
    def fetch_data(ti):
        test=WasbHook(wasb_conn_id="azure_demo")
        x=test.get_blobs_list(container_name="demo")
        print(x)
        #the function read_file returns a string so it must be converted to json object
        file=test.read_file(container_name="demo",blob_name="example")
        file_json=json.loads(file)
        ti.xcom_push(key="demo",value=file_json)
        print(file)
        
        return 0
    
    #upload data to mongo database
    def upload_data_mongodb(ti):
        file=ti.xcom_pull(key="demo",task_ids='data_fetching')
        test=MongoHook(conn_id="mongodb_demo")
        print("fdgsfgqgertrtzrththtey")
        test.insert_one(mongo_collection="demo",doc=file)
        print("file added to demo collection successfully")


    create_container_task = PythonOperator(
        task_id='container_creation',
        python_callable=create_container,
    )

    upload_data_task = PythonOperator(
        task_id='data_uploading',
        python_callable=upload_data,
    )

    fetch_data_task = PythonOperator(
        task_id='data_fetching',
        python_callable=fetch_data,
    )

    upload_data_mongodb_task = PythonOperator(
        task_id='data_uploading_mongodb',
        python_callable=upload_data_mongodb,
    )

    create_container_task >> upload_data_task >> fetch_data_task >> upload_data_mongodb_task