FROM python:3.12-slim

# set working directory
WORKDIR /app

# install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project files
COPY . .

# gunicorn server
CMD ["gunicorn", "project_hub.wsgi:application", "--bind", "0.0.0.0:8000"]
