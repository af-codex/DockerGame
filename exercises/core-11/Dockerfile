FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

# The application inside the container listens on port 8080.
# TODO: Add an instruction to inform Docker that the container listens on this port.


CMD ["python", "app.py"]
