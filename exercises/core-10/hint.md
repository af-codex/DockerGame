Here are the commands you'll need.

1.  **To create a network:**
    ```bash
    docker network create c10-network
    ```

2.  **To run a container on a specific network:**
    Use the `--network` flag in your `docker run` command.

    For the database container:
    ```bash
    docker run -d \
      --name c10-db \
      --network c10-network \
      -e POSTGRES_PASSWORD=mysecretpassword \
      postgres:14-alpine
    ```

    For the application container:
    ```bash
    docker run -d \
      --name c10-app \
      --network c10-network \
      busybox sleep 3600
    ```

Put these `docker run` commands into the `run-containers.sh` script.
