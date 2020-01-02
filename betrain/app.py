import datetime
import time
from urllib.parse import urljoin

import pytz
import requests
from flask import Flask
from jinja2 import Environment, PackageLoader

app = Flask(__name__)
env = Environment(loader=PackageLoader("betrain", "templates"), autoescape=True)


def convert_to_datetime(value, tz, from_tz=pytz.UTC):
    val = time.gmtime(int(value))
    dt = datetime.datetime(
        val.tm_year, val.tm_mon, val.tm_mday, val.tm_hour, val.tm_min, val.tm_sec
    )
    if isinstance(tz, str):
        tz = pytz.timezone(tz)
    return dt.replace(tzinfo=from_tz).astimezone(tz)


class IRailApi:
    URI = "https://api.irail.be"

    @staticmethod
    def fetch_connection(connection=("Brussels-North", "Namur")):
        uri = urljoin(IRailApi.URI, "connections")
        response = requests.get(
            uri, params={"from": connection[0], "to": connection[1], "format": "json"}
        )

        if response.status_code != 200:
            raise IOError(
                f"Could not fetch data for {connection}\n"
                f"STATUS CODE is {response.status_code}\n"
                f"URI is {uri}"
            )

        return [TrainConnection(conn) for conn in response.json().get("connection", [])]


class TrainConnection:
    def __init__(self, data):
        departure = data["departure"]
        arrival = data["arrival"]

        self.departure_delay = int(departure["delay"]) // 60
        self.departure_station = departure["station"]
        self.departure_time = convert_to_datetime(departure["time"], "Europe/Brussels")

        self.arrival_delay = int(arrival["delay"]) // 60
        self.arrival_station = arrival["station"]
        self.arrival_time = convert_to_datetime(arrival["time"], "Europe/Brussels")

        self.direction = arrival["direction"]["name"]
        self._vehicle = departure["vehicle"]

    @property
    def vehicle_type(self):
        return self._vehicle.split(".")[-1]

    @property
    def name(self):
        return self.direction

    @property
    def islate(self):
        return self.departure_delay > 0


@app.route("/")
def train_dashboard():
    connections = IRailApi.fetch_connection()
    return env.get_template("dashboard.html").render(connections=connections)
