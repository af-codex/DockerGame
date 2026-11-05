1.  **In your Dockerfile:**
    The `EXPOSE` instruction simply takes the port number.
    ```Dockerfile
    EXPOSE 8080
    ```

2.  **On the command line:**
    The `-p` flag maps the host port to the container port.
    ```bash
    # Usage: docker run -d --name <container_name> -p <host_port>:<container_port> <image_name>

    docker run -d --name c11-server -p 8011:8080 c11-app
    ```
