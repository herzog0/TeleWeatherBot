# Use an official Python runtime as a parent image
FROM python:3.6

# Set the working directory to /app
WORKDIR /vai_chover_bot

# Copy the current directory contents into the container at /app
COPY . /vai_chover_bot

# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt

# Run app.py when the container launches
CMD ["python3", "main.py"]
