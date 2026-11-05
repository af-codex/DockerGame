Your `docker-compose.yml` file will now have two top-level keys under `services`. You will also introduce the `build`, `environment`, and `depends_on` keys.

```yaml
services:
  # The web application service
  web:
    # Tells Compose to build an image from the Dockerfile in the 'app' directory
    build: ./app
    container_name: c13-web
    ports:
      - "8013:5000"
    # The app.py script will use this to connect to the redis service
    environment:
      - REDIS_HOST=redis
    # This ensures the redis service is started before the web service
    depends_on:
      - redis

  # The Redis database service
  redis:
    image: redis:alpine
    container_name: c13-redis
