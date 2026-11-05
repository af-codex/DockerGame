Use this sequence of commands to solve the exercise.

1.  **Copy a file *into* a container:**
    The syntax is `docker cp <host-path> <container-name>:<container-path>`.
    ```bash
    docker cp run-inside-container.sh c4-container:/tmp/
    ```

2.  **Make the script executable:**
    You must use `docker exec` to run the `chmod` command inside the container.
    ```bash
    docker exec c4-container chmod +x /tmp/run-inside-container.sh
    ```

3.  **Execute the script:**
    Use `docker exec` again to run the script you just copied.
    ```bash
    docker exec c4-container /tmp/run-inside-container.sh
    ```

4.  **Copy the result file *out* of the container:**
    The syntax is `docker cp <container-name>:<container-path> <host-path>`.
    ```bash
    docker cp c4-container:/tmp/container-info.txt .
    ```
