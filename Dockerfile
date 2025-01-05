# Use the official Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the app files into the container
COPY . /app

# Install required Python packages
RUN pip install --no-cache-dir flask yt-dlp

# Expose the port your app runs on
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
