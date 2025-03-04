# Use the official Windows Server Core image from the Docker Hub
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Python
RUN powershell -Command \
    Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe -OutFile python-installer.exe; \
    Start-Process -FilePath .\python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -NoNewWindow -Wait; \
    Remove-Item -Force .\python-installer.exe

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install the dependencies
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Set the working directory to the folder containing manage.py
WORKDIR /app/panel_project

# Expose the port the app runs on
EXPOSE 6000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "8000"]