Directory: exercises/core-09

Volumes are great for persisting data, but what about developing your application? You don't want to rebuild your image every time you change a single line of code.

This is where **bind mounts** come in. A bind mount links a directory or file from your host machine directly into a container. Any changes you make on the host are instantly reflected inside the container, making them perfect for live development workflows.

## Your Task

Your task is to run an `nginx` container and serve a simple static website from the `app` directory provided. The key is to use a bind mount so that changes to the website on your host machine are immediately live without restarting or rebuilding anything.

1.  **Examine the `app/index.html` file**. This is the file you will be serving.

2.  **Run an `nginx` container**.
    - Name it `c9-dev-server`.
    - Map host port `8009` to container port `80`.
    - **Crucially**, create a bind mount that maps the local `./app` directory to the Nginx web root directory inside the container (`/usr/share/nginx/html`). Make sure it's read-only to follow best practices for serving static content.

3.  **Verify it's working**. Once the container is running, check the content with `curl http://localhost:8009`. You should see the "Version 1" heading.

### Good Practice: Test the Live Reload

This is the core benefit of a bind mount. It's good practice to confirm your development setup is working as expected. To see it in action:

1.  Open the `app/index.html` file on your local machine in a text editor.
2.  Change the text inside the `<h1>` tag from "Version 1" to "My Live Update!".
3.  Save the file.
4.  Run `curl http://localhost:8009` again **without restarting the container**. You will see your new message served immediately from the container.

**To complete the exercise, leave the container running.** The checker will perform a similar test automatically to verify your solution.
