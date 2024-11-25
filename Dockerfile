# Use the official Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Set the PYTHONPATH to include the working directory
ENV PYTHONPATH=/app

# Copy the local requirements.txt file into the container
COPY requirements.txt /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application into the container
COPY . /app/

# Expose the port for Gunicorn/Flask
EXPOSE 8000

# Run Gunicorn for the Flask app and start the bot in the background
CMD gunicorn --bind 0.0.0.0:8000 app.flask_server:app & python3 app/bot.py
