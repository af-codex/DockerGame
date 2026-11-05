Directory: exercises/core-14

You've successfully orchestrated a multi-service application. Now it's time to add robust data persistence and networking best practices using Docker Compose.

- **Named Volumes**: Unlike bind mounts, which depend on the host's directory structure, named volumes are managed by Docker itself. They are the preferred way to persist data for services like databases.
- **Custom Networks**: While Compose creates a default network, defining your own provides better isolation and organization, and allows for more complex network topologies.

## Your Task

Modify the `docker-compose.yml` from the previous exercise to include a named volume for Redis data and to place both services on a custom, user-defined network.

1.  **Define a top-level `networks` section** and create a network named `c14-app-net`.

2.  **Define a top-level `volumes` section** and create a named volume called `redis-data`.

3.  **Modify the `redis` service:**
    *   Give it the container name `c14-redis`.
    *   Connect it to the `c14-app-net` network.
    *   Mount the `redis-data` volume to the `/data` directory inside the container. This is where Redis stores its data.

4.  **Modify the `web` service:**
    *   Give it the container name `c14-web`.
    *   Connect it to the `c14-app-net` network.
    *   Map host port `8014` to container port `5000`.

The directory structure and application code are the same as in the previous exercise. You only need to create and modify the `docker-compose.yml` file.
