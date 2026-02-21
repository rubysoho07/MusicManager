# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy pyproject.toml
COPY pyproject.toml .

# Install project dependencies and gunicorn
RUN pip install --no-cache-dir . && pip install gunicorn

# Copy the rest of the application
COPY . .

# Create a non-root user and switch to it
RUN useradd -m -u 1000 musicmanager && chown -R musicmanager:musicmanager /app
USER musicmanager

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run app.py when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
