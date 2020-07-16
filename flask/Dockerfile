# Use the Python3.7.6 container image
FROM python:3.7.6-stretch

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

COPY model.pkl /app/

# Install the dependecies
RUN pip install -r requirements.txt

# run the command to start uWSGI
CMD ["uwsgi", "app.ini"]