Directory: exercises/core-11

A common point of confusion for beginners is the difference between `EXPOSE` in a `Dockerfile` and the `--publish` (or `-p`) flag used with `docker run`.

-   **`EXPOSE <port>`**: This is a documentation instruction. It signals to the person running the container which port the application inside is intended to listen on. It does **not** open the port or make it accessible from the host.

-   **`docker run -p <host_port>:<container_port>`**: This is a runtime instruction. It actively creates a network rule that maps traffic from a port on the host machine to a port inside the container.

## Your Task

Your task is to correctly document and run a web application container.

1.  **Modify the `Dockerfile`**. Inside the provided `Dockerfile`, add an `EXPOSE` instruction to document that the application listens on port **8080**.

2.  **Build your image**. Give it a tag like `c11-app`.
    ```bash
    docker build -t c11-app .
    ```

3.  **Run the container**.
    - Name the container `c11-server`.
    - Publish the exposed container port (`8080`) to port `8011` on your host machine.

**To complete the exercise, leave the container running.** The checker will inspect both your built image and the running container to ensure they are configured correctly.
