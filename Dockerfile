# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install system dependencies for Playwright and browsers
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
    libappindicator3-1 \
    libindicator3-0.7 \
    libgbm1 \
    libnspr4 \
    libnss3 \
    libxss1 \
    fonts-liberation \
    libappindicator1 \
    libxtst6 \
    xdg-utils \
    --no-install-recommends \
    && apt-get clean

# Install ffmpeg
RUN apt-get install -y ffmpeg && apt-get clean

# Install Playwright dependencies and Playwright itself
RUN pip3 install playwright
RUN playwright install

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the port the app runs on (not strictly necessary for a Telegram bot)
#EXPOSE 8000

# Run the bot when the container launches
CMD python3 bot.py
