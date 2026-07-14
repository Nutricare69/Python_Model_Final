# Use a clean, stable Python runtime base
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system-level compilers and math libraries required for SciPy and Scikit-Learn
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  gfortran \
  libopenblas-dev \
  liblapack-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy your requirements list inside
COPY requirements.txt .

# Install dependencies smoothly with clean library packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy all local project source assets and datasets
COPY . .

# Expose the API port
EXPOSE 8000

# Run Uvicorn server bound to 0.0.0.0 for cross-container gateway communication
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]