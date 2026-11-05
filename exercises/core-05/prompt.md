Directory: exercises/core-05

It's time to build your own custom image!

Running pre-built images like `nginx` is useful, but the real power of Docker comes from packaging your own applications. This is done by writing a set of instructions in a file named `Dockerfile`.

## Your Task

In this directory, you will find a simple Python Flask application (`app.py`) and its dependencies (`requirements.txt`).

Your task is to **create a `Dockerfile`** in this directory that packages this application into an image.

Your `Dockerfile` should perform the following steps:
1.  Start from a suitable Python base image (e.g., `python:3.9-slim`).
2.  Set a working directory inside the image (e.g., `/app`).
3.  Copy the `requirements.txt` file into the image.
4.  Install the Python dependencies using `pip`.
5.  Copy the application source code (`app.py`) into the image.
6.  Inform Docker that the container will listen on port `5000` at runtime.
7.  Set the default command to run the Flask application when a container starts.

Once you have created your `Dockerfile`, the `check` command will build it and test if your application container runs correctly.
