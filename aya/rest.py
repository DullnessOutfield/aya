class Connection:
    def __init__(
        self, username="kismet", password="kismet", address="localhost", port=2501
    ):
        self.username = username
        self.password = password
        self.address = address
        self.port = port

    @property
    def baseurl(self):
        return f"http://{self.username}:{self.password}@{self.address}:{self.port}"
