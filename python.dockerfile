# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

#copy requirements.txt
COPY requirements.txt .

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY *.py /app
COPY /serverConfig /app/serverConfig
COPY base.html /app

# Run app.py when the container launches
CMD ["python", "tool_process_zip_files.py"]
