# Use an official lightweight Python image as a parent
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code into the container
COPY . .

# Expose the port that Gunicorn will run on inside the container
EXPOSE 8000

# The command to run the application using Gunicorn as a production server
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "app:app"]