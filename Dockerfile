FROM pytorch/pytorch:2.5.1-cuda12.1-cudnn9-runtime

WORKDIR /app

# Basic tools only
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 3000

CMD ["python", "app.py"]