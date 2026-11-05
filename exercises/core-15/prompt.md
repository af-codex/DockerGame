Directory: exercises/core-15

The Python application in this exercise can be precompiled to bytecode in a builder stage. The final image only needs the Python runtime and the app bytecode, not the larger builder image.

**Multi-stage builds** let you use a larger image to prepare an application, then copy only the files needed to run it into a smaller runtime image.

## Your Task

In this directory, you will find a simple Python web application and a `Dockerfile` that builds it using a single stage.

Your task is to **refactor the `Dockerfile`** to use a multi-stage build with Python bytecode:

1.  **The first stage** (the "builder"):
    *   Should use `python:3.12` and copy in `app/app.py`.
    *   Should compile the app with `python -m compileall -b -o 2`.

2.  **The second stage** (the "final" image):
    *   Should use the smaller `python:3.12-alpine` runtime image.
    *   Should copy only the compiled `app.pyc` from the builder stage.
    *   Should expose port `8080` and run the compiled application with Python.

The verification checks that your final image is significantly smaller than the original single-stage image and that the web app still responds correctly.
