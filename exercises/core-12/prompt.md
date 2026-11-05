Directory: exercises/core-12

So far, you've been running containers using long `docker run` commands. This is fine for one or two containers, but it quickly becomes difficult to manage as applications grow.

**Docker Compose** is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application’s services, networks, and volumes. Then, with a single command, you can create and start all the services from your configuration.

This is the standard way to manage local development environments.

## Your Task

Your task is to create a `docker-compose.yml` file in this directory to define a single Redis service.

Your `docker-compose.yml` file should define the following:
1.  A service named `redis-server`.
2.  The service should use the `redis:alpine` image.
3.  The container should be explicitly named `c12-redis`.
4.  It should map port `6379` on your host to port `6379` in the container.

After creating the file, you can test it yourself by running `docker compose up`. The verification script will run this command for you to check your work.
