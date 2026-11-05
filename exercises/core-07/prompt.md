Directory: exercises/core-07

So far, you've built an image by packaging a Python application. A common use case for Docker is also to package and serve static websites.

The `COPY` instruction is one of the most fundamental commands in a `Dockerfile`. It lets you copy files and directories from your local filesystem (the build context) into the image you are creating.

## Your Task

In this directory, you will find a subdirectory named `html` containing a simple website.

Your task is to **create a `Dockerfile`** that builds a new Nginx image serving this custom static content instead of the default Nginx welcome page.

Your `Dockerfile` should:
1.  Start from a lightweight Nginx image, such as `nginx:stable-alpine`.
2.  Use the `COPY` instruction to copy the contents of the `html` directory into the location where Nginx serves its static files from, which is `/usr/share/nginx/html`.

The verification script will build your image, run it, and check to see if your custom website is being served correctly.
