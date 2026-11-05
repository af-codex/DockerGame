import os
from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    # We can get the port from an environment variable, defaulting to 8080
    port = os.environ.get("APP_PORT", 8080)
    return f"Hello from a container listening on port {port}!"


if __name__ == "__main__":
    # Default to port 8080 if APP_PORT is not set
    port = int(os.environ.get("APP_PORT", 8080))
    app.run(host="0.0.0.0", port=port)
