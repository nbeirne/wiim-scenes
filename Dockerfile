
# Use Python as the base image 
FROM python:3.9

# Define the working directory
WORKDIR /app

# Install dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./app/*.py /app

# Expose the application port
EXPOSE 5000

# Set the startup command
CMD ["python", "flask_server.py"]

