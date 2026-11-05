A `Dockerfile` is a sequence of instructions. Here are the key ones you'll need:

-   **`FROM python:3.9-slim`**: Specifies the starting image for your build.
-   **`WORKDIR /app`**: Sets the current directory for all subsequent commands (`COPY`, `RUN`, `CMD`).
-   **`COPY <source> <destination>`**: Copies files from your host into the image.
    *Tip: To optimize build caching, you should copy `requirements.txt` and run `pip install` *before* copying the rest of your application code.*
-   **`RUN <command>`**: Executes a command during the image build. This is used for installing dependencies.
    ```
    RUN pip install -r requirements.txt
    ```
-   **`EXPOSE 5000`**: Informs Docker that the application listens on this port. This is good practice for documentation.
-   **`CMD ["python", "app.py"]`**: Provides the default command to execute when the container starts. You should use the JSON array format for commands.
