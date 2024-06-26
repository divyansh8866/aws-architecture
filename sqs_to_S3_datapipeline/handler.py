
try:
    import pyodbc
    import requests
    import json
    import os
    from time import time
    from distutils.log import error
    from requests.exceptions import HTTPError
except Exception as e:
    print(" ERROR: Importing Modules")
    print(e)


# Environment variables
# URL
# TOKEN
# SQLSERVER
# SQLDATABASE
# UDI
# PWD
# MAXTRIES

DEBUG = False 
EXECUTION_TIME = {}
RUN_SUMMERY = {}



class LoadDataSql:
    """
    This class is responsible to load the tuple of datas to sql.

    Attributes
    ----------
    data_list : list
        list of data tulples

    Mehods
    ------
    load_data() --> None
        This method is responsible to load all the tuples in a list to SQL.
    """

    def __init__(self):
        self.__server = os.environ["SQLSERVER"]
        self.__database = os.environ["SQLDATABASE"]
        self.__udi = os.environ["UDI"]
        self.__pwd = os.environ["PWD"]
        pass

    def load_data(self, data_list: list = None) -> None:
        try:
            print("> LOADING data to SQL")
            connection = pyodbc.connect(
                f"""DRIVER={'ODBC Driver 17 for SQL Server'};
                            SERVER= { self.__server}; 
                            Database={self.__database}; 
                            UID={self.__udi}; 
                            PWD={self.__pwd};"""
            )
            cursor = connection.cursor()
            insert_string = """
                        """
            cursor.fast_executemany = True
            cursor.executemany(insert_string, data_list)

        except pyodbc.DatabaseError as err:
            connection.rollback()
            print(">> ERROR: SQL ERROR | ROLLING BACK <<")
            raise Exception(err)
        else:
            connection.commit()
            cursor.close()
            connection.close()


class Request:
    """
    This class call the POST method and returns the dictonary.

    Attributes
    ----------
    description : str
        This is the job description paramater.
    job_id : str
        This paramater holds the job ID number.

    Mehods
    ------
    post()-->dict
        returns the response obtained from the API.
    """

    def __init__(self):
        self.token = os.environ["TOKEN"]
        self.url = os.environ["URL"]

    
    def post(self, job_title, description):
        doc = f"{job_title} {description}"
        job_data = {"document": doc, "num_topics": 1,    "model_version":1}
        for no_of_tries in range(int(os.environ["MAXTRIES"])):
            try:
                response = requests.post( self.url,data=json.dumps(job_data),headers={"x-api-key": self.token},timeout=600)
                if DEBUG: print("""
                Payload: {}
                response :{}
                """.format(
                    job_data, response.json()
                ))
                
                if response.status_code == 200:
                    if isinstance (response.json(), dict):
                        dummy_data=[{'topic_num': -1, 'topic_scores': 0.0, 'model_version': '1.0.0'}]
                        print(">>API Call Failed<< | OriginalStatusCode : ",int(response.json().get("OriginalStatusCode")))
                        if DEBUG: print(f"""
                            [payload] : {job_data}
                            [json Response] : {response.json()}
                            [raw] : {response.text}""")
                        print("Uploading Dummy Data : ", dummy_data)
                        return dummy_data
                        
                    print("Response : <200> OK")
                    return response.json()
                    
                else:
                    print(f"> Retrying to POST. Retry : {no_of_tries+1}")
                    
            except Exception as e:
                print("""
                ---------------------
                Error: In POST method
                ---------------------
                    Payload: {}
                    Error : {}
                """.format(job_data, e))
                raise Exception(e)
        response.raise_for_status()
        



class Handeler(Request, LoadDataSql):
    """
    This class is a Fasad class and inherites all the other calsses
    and acts like a control class.

    Attributes
    ----------
    sql_data : list
        It holds a list of datas from SQL

    Mehods
    ------
    sqs_to_64recs --> None
        It is a controller method which controls all the other operations.

    execution_time --> None
        This method prints time taken by different operations in the program.
    """

    def __init__(self):
        Request.__init__(self)
        LoadDataSql.__init__(self)
        


    def sqs_to_64rec(self, sql_data_batch: list = None):
        print("> STARTING [Topic Model 64rec] ")
        start_time = time()
        data_list = []
        count=0
        print("> READING data and Calling API")
        try:
            for batch in sql_data_batch:
                count+=1
                RUN_SUMMERY["SQS Batch Size"] = len(sql_data_batch)
                RUN_SUMMERY["No of Records in a batch"] = len(batch["data"])
                for data_dict in batch["data"]:
                    api_response = self.post(
                        data_dict.get("title", ""), data_dict.get("job_description", "")
                    )
                    api_response=api_response[0]
                    data_tuple = (
                        int(data_dict["job_id"]), int(api_response["topic_num"]), round(float(api_response["topic_scores"]), 17),api_response["model_version"],
                    )
                    if DEBUG:
                        print(
                            f"> SUCCESS : [{data_dict['job_id']}] :: ",
                            data_tuple,
                        )
                    data_list.append(data_tuple)
                    del data_tuple
                print(f"Batch No : {count} | SUCCESS")
            
            self.load_data(data_list=data_list)
            print("> Data Loaded to SQL | SUCCESS")
        except Exception as e :
            raise Exception(f">Execution FAILED< | ERROR : {e} ")

    def execution_time(self):
        print("========= Run Summery =========")
        for k, v in RUN_SUMMERY.items():
            print(f"{k} : {v}")
        print("==================================")


def lambda_handeler(event, context):
    data_transfer = Handeler()
    if DEBUG:
        print("\n\n========= DEBUGING MODE =========\n")
    path_to_data_list = [json.loads(record.get("body")) for record in event["Records"]]
    data_transfer.sqs_to_64rec(path_to_data_list)
    data_transfer.execution_time()
    return "ok"
