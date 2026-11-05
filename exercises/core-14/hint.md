Your `docker-compose.yml` should now have top-level `volumes` and `networks` keys, in addition to the `services` key.

```yaml
# Define the custom network at the top level
networks:
  c14-app-net:

# Define the named volume at the top level
volumes:
  redis-data:

services:
  web:
    build: ./app
    container_name: c14-web
    ports:
      - "8014:5000"
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis
    # Connect this service to the network
    networks:
      - c14-app-net

  redis:
    image: redis:alpine
    container_name: c14-redis
    # Mount the named volume
    volumes:
      - redis-data:/data
    # Connect this service to the network
    networks:
      - c14-app-net
```
Note: The `redis:alpine` image is configured to automatically save its data to the `/data` directory. By mounting a volume there, we ensure the data persists.
