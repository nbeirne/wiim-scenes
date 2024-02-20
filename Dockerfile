
# Use Python as the base image 
FROM python:3.9

# Define the working directory
WORKDIR /app

# Copy the application code into the container
COPY ./requirements.txt /app/requirements.txt
COPY ./app/* /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 5000

# Set the startup command
CMD ["python", "flask_server.py"]

