import datetime

from typing import Optional, List
from fastapi import FastAPI, Response, Header
import pandas as pd

# RACECSV_FILEPATH = "./dummycreator/race.csv"
# TEAMCSV_FILEPATH = "./dummycreator/teams.csv"

RACECSV_FILEPATH = "./resources/2023_Rd1_Suzuka_race.csv"
TEAMCSV_FILEPATH = "./resources/2023_Rd1_Suzuka_teams.csv"
RACESTART = datetime.datetime(2023,3,19,11,50,9)
RACEEND = datetime.datetime(2023,3,19,16,20,1)


IMAGECSV_FILEPATH = "./resources/time-imagelist.csv"

class MyAPI(FastAPI):
    def __init__(self):
        super().__init__()
        self.df_race = pd.read_csv(RACECSV_FILEPATH)
        self.df_teams = pd.read_csv(TEAMCSV_FILEPATH)
        self.df_images = pd.read_csv(IMAGECSV_FILEPATH)

    def calc_duration(self, dt: datetime.datetime):
        time_of_start: datetime.datetime = RACESTART
        duration = dt - time_of_start
        return duration.total_seconds()

    def find_dataID(self, carNo: int, time_from_start: float):
        df_carNo = self.df_race[self.df_race["carNo"]==carNo]
        df_carNo = df_carNo.rename(columns={"Unnamed: 0":"dataID"})
        df_carNo_findlap = df_carNo[df_carNo["cumlative_laptime"] <= time_from_start]
        return list(df_carNo_findlap["dataID"])[-1]

    def find_driverInfo(self, carNo:int, driverCategory: str):
        df_team = self.df_teams[self.df_teams["carNo"]==carNo]
        df_driver = df_team[df_team["drivercategory"]==driverCategory]
        del df_driver["Unnamed: 0"]
        data_columns = list(df_driver.columns)
        driver_info = {}
        for key in data_columns:
            value = list(df_driver[key])
            driver_info[key] = value[0]
        return driver_info

    def return_data(self, data_id: int):
        df_matched = self.df_race.query('index =='+ str(data_id))
        df_matched = df_matched.rename(columns={"Unnamed: 0":"dataID"})
        data_columns = list(df_matched.columns)
        racedata = {}
        for key in data_columns:
            value = list(df_matched[key])
            racedata[key] = value[0]
        content = self.find_driverInfo(racedata["carNo"], racedata["drivercategory"])
        return content

    def isExistCarNo(self, carNo: int):
        list_carNo = self.df_race["carNo"].unique()
        if carNo in list_carNo:
            return True
        else:
            return False

    def find_imageName(self, hour:int, minute:int):
        df_matched = self.df_images[(self.df_images["hour"]==hour) & (self.df_images["minute"]==minute)]
        if df_matched.empty:
            return None
        else:
            fname = list(df_matched["fname"])[0]
            return fname

    def isInRaceTime(self, dt_photo):
        timedelta = dt_photo - RACESTART
        if timedelta.total_seconds() < 0:
            return False
        timedelta = RACEEND - dt_photo
        if timedelta.total_seconds() < 0:
            return False
        return True

app = MyAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}

@app.get("/data/{carNo}")
def read_data(
        response: Response,
        carNo: int,
        yr: int = None,
        mt: int = None,
        dy: int = None,
        hr: int = None,
        mi: int = None,
        se: int = None,
        options = None
        ):
    query = {
        "yr": yr,
        "mt": mt,
        "dy": dy,
        "hr": hr,
        "mi": mi,
        "se": se
    }
    if not check_query(query):
        response.headers["Access-Control-Allow-Origin"] = "*"
        content_data = "Err: Query parameter format wrong!"
        print(content_data)
        print(type(content_data))
        return {
            "query": query,
            "carNo": carNo,
            "content": content_data,
            "class": None,
            "carname": None,
            "drivercategory": None,
            "drivername": None
            }

    if not app.isExistCarNo(carNo):
        response.headers["Access-Control-Allow-Origin"] = "*"
        content_data = "Err: CarNo does not exists!"
        print(content_data)
        print(type(content_data))
        return {
            "query": query,
            "carNo": carNo,
            "content": content_data,
            "class": None,
            "carname": None,
            "drivercategory": None,
            "drivername": None
            }

    dt_photo = datetime.datetime(yr, mt, dy, hr, mi, se)

    if not app.isInRaceTime(dt_photo):
        response.headers["Access-Control-Allow-Origin"] = "*"
        content_data = "Err: Photo time out of range!"
        print(content_data)
        print(type(content_data))
        return {
            "query": query,
            "carNo": carNo,
            "content": content_data,
            "class": None,
            "carname": None,
            "drivercategory": None,
            "drivername": None
            }

    time_from_start = app.calc_duration(dt_photo)
    dataID = app.find_dataID(carNo, time_from_start)

    content_data = app.return_data(dataID)

    print(content_data)
    print(type(content_data))

    response.headers["Access-Control-Allow-Origin"] = "*"
    return {
        "query": query,
        "content": "success",
        "carNo": content_data["carNo"],
        "class": content_data["class"],
        "carname": content_data["carname"],
        "drivercategory": content_data["drivercategory"],
        "drivername": content_data["drivername"]
        }


def check_query(query: dict):
    keys = query.keys()
    for key in keys:
        if query[key] == None:
            return False
    return True

"""
def parse_query(q: str):
    q_split = q.split("&")
    params = ["yr", "mt", "dy", "hr", "mi", "se"]

    return_dict = {
        "yr": None,
        "mt": None,
        "dy": None, 
        "hr": None, 
        "mi": None, 
        "se": None
    }

    for param in params:
        for query_string in q_split:
            if param in query_string:
                return_dict[param] = query_string.split("=")[1]
                continue

    for param in params:
        if return_dict[param] == None:
            return "Err"

    return return_dict
"""

@app.get("/ltcapture/")
def read_capture(
        response: Response,
        yr: int = None,
        mt: int = None,
        dy: int = None,
        hr: int = None,
        mi: int = None,
        se: int = None,
        options = None
        ):
    query = {
        "yr": yr,
        "mt": mt,
        "dy": dy,
        "hr": hr,
        "mi": mi,
        "se": se
    }
    if not check_query(query):
        response.headers["Access-Control-Allow-Origin"] = "*"
        content_data = "Err: Query parameter format wrong!"
        print(content_data)
        print(type(content_data))
        return {
            "query": query,
            "content": content_data,
            "fname": None
            }

    fname = app.find_imageName(hr, mi)
    if fname == None:
        response.headers["Access-Control-Allow-Origin"] = "*"
        content_data = "Err: Image file does not exists!"
        print(content_data)
        print(type(content_data))
        return {
            "query": query,
            "content": content_data,
            "fname": None
            }
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
        content_data = "success"
        print(content_data)
        print(type(content_data))
        return {
            "query": query,
            "content": content_data,
            "fname": fname
            }

if __name__ == "__main__":
    # read_item(100, 2023)
    # parse_query("yr=2023&mt=03&dy=19&hr=12&mi=34&se=56")
    read_data(Response,carNo=1,yr=2023,mt=3,dy=19,hr=12,mi=34,se=56)