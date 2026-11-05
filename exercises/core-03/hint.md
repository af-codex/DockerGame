Use the following commands to complete the exercise:

- **To build an image:**
  `docker build -t <image-name> .`

- **To run a container in detached mode:**
  `docker run -d --name <container-name> <image-name>`

- **To get logs from a container:**
  `docker logs <container-name>`

- **To save output to a file (redirection):**
  `docker logs <container-name> > logs.txt`

Remember to stop and remove the container to keep your system clean:
`docker stop <container-name>`
`docker rm <container-name>`
