Directory: exercises/core-04

This exercise will teach you the full workflow of managing files and executing commands in a running container. To prove you can do this, you won't be creating the file content yourself. Instead, you will execute a script inside the container that generates the content for you.

## Task

Your task is to copy a script into a running Nginx container, execute it, and then copy the resulting output file back to your host machine.

1.  **Run a container** in detached mode from the `nginx` image. Name it `c4-container`.
    ```bash
    docker run -d --name c4-container nginx
    ```

2.  **Copy the script** from your host into the container. The script `run-inside-container.sh` is provided in this directory. Copy it to the `/tmp` directory inside the container.

3.  **Make the script executable** inside the container using `docker exec`.

4.  **Execute the script** inside the container, also using `docker exec`. The script will generate a new file at `/tmp/container-info.txt`.

5.  **Copy the output file** (`/tmp/container-info.txt`) from the container back to your current directory on the host.

The verification script will then check this `container-info.txt` file for the correct content.

**Cleanup:** When you are done, stop and remove the container: `docker stop c4-container && docker rm c4-container`.
