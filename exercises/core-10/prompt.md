Directory: exercises/core-10

By default, containers can communicate with the outside world, but they have limited ability to discover and talk to each other. While you could link them, the modern and recommended approach is to use custom **bridge networks**.

When you place multiple containers on the same custom network, they get an internal DNS service that allows them to find and communicate with each other using their container names as hostnames. This is fundamental for building multi-service applications (e.g., a web server talking to a database).

## Your Task

Your task is to create a network and a script that launches two containers on that network.

1.  **Create a custom bridge network** and name it `c10-network`. You can do this as a one-time command in your terminal.

2.  **Edit the `run-containers.sh` script** provided in this directory. The script should perform the following actions:
    *   Run a `postgres:14-alpine` container named `c10-db`.
    *   Run a `busybox` container named `c10-app`.
    *   **Both** containers must be attached to the `c10-network` you created.
    *   The `busybox` container should be kept running with a long-running command like `sleep 3600`.

The verification script will execute your `run-containers.sh` script and then test if the `c10-app` container can successfully ping the `c10-db` container by its name.
