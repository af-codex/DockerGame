To complete this exercise, you'll need to use the `COPY` instruction.

-   **`FROM <image>`**: Start your `Dockerfile` with a base image. A good choice is `nginx:stable-alpine` because it's small and efficient.
    ```Dockerfile
    FROM nginx:stable-alpine
    ```

-   **`COPY <source> <destination>`**: The syntax for copying is straightforward. The `<source>` is relative to your build context (the current directory), and the `<destination>` is an absolute path inside the image.
    ```Dockerfile
    # This copies the *contents* of the 'html' directory
    COPY html/ /usr/share/nginx/html/
    ```

**Note:** The trailing slash on the source (`html/`) is important. It tells Docker to copy the contents of the directory, not the directory itself.
