Directory: exercises/core-13

The real power of Docker Compose is defining and running an entire application stack with multiple, interconnected services.

In this exercise, you will define a two-service application: a Python web app and a Redis cache. You will also use `depends_on` to tell Compose that the web app should not start until the Redis service has started. This helps control the startup order of your application stack.

## Your Task

Create a `docker-compose.yml` file that orchestrates the web app (provided in the `app` directory) and a Redis database.

Your `docker-compose.yml` file must define two services: `web` and `redis`.

1.  **The `redis` service:**
    *   Should use the `redis:alpine` image.
    *   Can be named `c13-redis` for clarity.

2.  **The `web` service:**
    *   Should be built from the `Dockerfile` in the `./app` directory.
    *   Should be named `c13-web`.
    *   Should map port `8013` on the host to port `5000` in the container.
    *   Must use `depends_on` to ensure it starts after the `redis` service.
    *   Must have an environment variable `REDIS_HOST` set to `redis`. This is how the Python app knows the hostname of the Redis service on the internal Docker network.

After creating the file, you can test it with `docker compose up --build`. The verification script will do this for you.
