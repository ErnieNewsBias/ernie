# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# ----- CHANGES START HERE -----

# Expose the port Flask will run on inside the container
EXPOSE 8080 

# Set environment variables for Flask's development server
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080    

# Run the application using Flask's built-in server
# It will listen on the port specified by FLASK_RUN_PORT (8080)
CMD ["flask", "run"]

# ----- CHANGES END HERE -----

# --- Alternative CMD (if you prefer python app.py) ---
# If you choose this, make sure your app.py has the following block:
# if __name__ == '__main__':
#    # Note: Port needs to be int here, host needs to be '0.0.0.0'
#    app.run(host='0.0.0.0', port=8080, debug=True) # <-- Changed port
#
# And uncomment the following line INSTEAD of CMD ["flask", "run"]
# CMD ["python", "app.py"]
# You would also remove the FLASK_RUN_HOST and FLASK_RUN_PORT ENV variables above if using this method.