import os
from flask import Flask
from redis import Redis

app = Flask(__name__)
# The hostname 'redis' is the service name from our docker-compose.yml
redis_host = os.environ.get("REDIS_HOST", "localhost")
redis = Redis(host=redis_host, port=6379)


@app.route("/")
def hello():
    count = redis.incr("hits")
    return f"This page has been visited {count} times."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
