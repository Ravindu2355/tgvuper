# Use the official Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Set the PYTHONPATH to include the working directory
ENV PYTHONPATH=/app

# Copy the local requirements.txt file into the container
COPY requirements.txt /app/

# Install the Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application into the container
COPY . /app/

# Expose the port that Flask will run on
EXPOSE 5000

# Command to run the bot and Flask server
CMD ["python3", "app/flask_server.py"]
