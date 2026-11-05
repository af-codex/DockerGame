FROM python:3.12-slim

# TODO: Add a LABEL with the key "org.dockerlings.author" and your name as the value.
# For example: LABEL org.dockerlings.author="your.name@example.com"

# TODO: Set the PORT environment variable to 8000.


WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

# The application listens on the port defined by the PORT environment variable.
# TODO: EXPOSE the port defined in the ENV instruction.


# TODO: Set the default command to run the application.
# The `app.py` script will automatically use the $PORT variable.
