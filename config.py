
import os

devices = {
    "ax-lsi": {
        "host": "10.0.0.160",
        "username": "admin",
        "password": os.environ['AX_PASSWORD'],
        "port": 8443,
        "api_version": "2.1",
    },
}
