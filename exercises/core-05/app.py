from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

if __name__ == '__main__':
    # This makes the server accessible from outside the container
    app.run(host='0.0.0.0', port=5000)
