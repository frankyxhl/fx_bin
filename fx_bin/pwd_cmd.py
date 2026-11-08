import os
import socket


def logical_directory() -> str:
    env_pwd = os.environ.get("PWD")
    if env_pwd and os.path.isabs(env_pwd):
        try:
            if os.path.samefile(env_pwd, "."):
                return env_pwd
        except OSError:
            pass
    return os.getcwd()


def pwd_line(with_host: bool) -> str:
    path = logical_directory()
    if with_host:
        return f"{socket.gethostname()}:{path}"
    return path
