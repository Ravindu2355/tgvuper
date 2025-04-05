# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install system dependencies required for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    ca-certificates \
    curl \
    libglib2.0-0 \
    libnss3 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgdk-pixbuf2.0-0 \
    libdbus-1-3 \
    libpango-1.0-0 \
    libcups2 \
    libx11-xcb1 \
    libgbm1 \
    libnspr4 \
    libxss1 \
    fonts-liberation \
    libxtst6 \
    xdg-utils \
    --no-install-recommends \
    && apt-get clean

# Install ffmpeg (only if needed for video handling)
RUN apt-get install -y ffmpeg && apt-get clean

# Install Playwright and its dependencies
RUN pip3 install playwright
RUN playwright install

# Install Python dependencies from the requirements file
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Run the bot when the container launches
CMD python3 bot.py
