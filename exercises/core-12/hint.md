A `docker-compose.yml` file has a clear, hierarchical structure. Here is a template to get you started.

```yaml
services:
  # This is the logical name for your service.
  redis-server:
    # Specify the image to use.
    image: redis:alpine

    # Set a predictable name for the container.
    container_name: c12-redis

    # Define the port mappings.
    # The format is a list of "HOST:CONTAINER".
    ports:
      - "6379:6379"
