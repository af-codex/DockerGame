Here are the `Dockerfile` instructions you'll need.

-   **`LABEL`**: Used to add key-value metadata. Use a unique key to avoid conflicts with the base image.
    ```Dockerfile
    LABEL org.dockerlings.author="your.name@example.com"
    ```

-   **`ENV`**: Sets an environment variable. The container process will inherit this variable.
    ```Dockerfile
    ENV PORT=8000
    ```

-   **`EXPOSE`**: It's good practice to document which port the application uses.
    ```Dockerfile
    EXPOSE 8000
    ```
-   **`CMD`**: The `app.py` script has been written to read the `PORT` from the environment variables, so you just need to execute the script.
    ```Dockerfile
    CMD ["python", "app.py"]
