from netmiko import ConnectHandler


class Switch:
    """A class to handle network switches"""
    def __init__(
        self,
        host,
        username,
        password,
        type="cisco_ios",
    ):
        self.host = host
        self.username = username
        self.password = password
        self.type = type
        self.connect = None

    def ssh(self):
        """Establishes an SSH connection"""
        if not self.connect:
            self.connect = ConnectHandler(
                ip=self.host,
                username=self.username,
                password=self.password,
                device_type=self.type,
            )
        if not self.connect.is_alive():
            self.connect = None
            self.connect = self.ssh()
        return self.connect
