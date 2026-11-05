Directory: exercises/core-03

This exercise will teach you how to retrieve the logs from a container. This is a fundamental skill for debugging applications running inside Docker.

A container's standard output and standard error streams are captured and can be accessed at any time during the container's lifecycle.

## Task

In this directory, you will find a `Dockerfile`. Your task is to perform the following steps:

1.  **Build** the Docker image from the `Dockerfile` in this directory. Give it a memorable tag, for example: `logging-app`.
    ```bash
    docker build -t logging-app .
    ```

2.  **Run** the image in **detached mode** (`-d`). This keeps the container running in the background so you can retrieve its logs even after the process finishes. Give the container a name so you can easily reference it, for example: `my-logger`.
    ```bash
    docker run -d --name my-logger logging-app
    ```

3.  **Retrieve the logs** from the `my-logger` container using the `docker logs` command and save them to a file named `logs.txt` in this directory.

The verification script will check if the `logs.txt` file exists and if its content is correct. After you have captured the logs, you can clean up by stopping and removing the container.
