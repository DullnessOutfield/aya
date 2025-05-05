import json
import requests

class Connection:
    def __init__(
        self, username="kismet", password="kismet", address="localhost", port=2501
    ):
        self.username = username
        self.password = password
        self.address = address
        self.port = port
        self.check_connection()

    @property
    def baseurl(self):
        return f"http://{self.username}:{self.password}@{self.address}:{self.port}"

    def deviceurl(self, devicekey):
        return f"{self.baseurl}/devices/by-key/{devicekey}/device.json"

    def device_since_time_url(self, timestamp):
        return f"{self.baseurl}/devices/last-time/{timestamp}/devices.json"
    
    def check_connection(self):
        requests.get(self.baseurl)


def connection_from_config(config_file) -> dict:
    """
    Generates a Kismet REST connection from a configuration file
    Accepted file keys:
    Username: "username","user"
    Password: "password","pass"
    Host: "host","ip"
    Port: "port"
    """
    field_mappings = {
        "username": {"keys": ["username", "user"], "default": "kismet"},
        "password": {"keys": ["password", "pass"], "default": "kismet"},
        "address": {"keys": ["host", "ip"], "default": "localhost"},
        "port": {"keys": ["port"], "default": 2501},
    }

    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise e

    connection_params = {}
    for param_name, options in field_mappings.items():
        for key in options["keys"]:
            if key in config:
                connection_params[param_name] = config[key]
                break
        if param_name not in connection_params:
            connection_params[param_name] = options["default"]

    return connection_params


if __name__ == "__main__":
    connection = connection_from_config("./test_connection.json")
    print(connection.baseurl)