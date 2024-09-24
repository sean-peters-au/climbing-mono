FROM python:3.9

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

RUN pip install pipenv

RUN pipenv run pip install --upgrade setuptools wheel

# Copy the GroundingDINO directory
COPY GroundingDINO/ GroundingDINO/
RUN pipenv run pip install -e GroundingDINO

# Copy the lang-segment-anything directory
COPY lang-segment-anything/ lang-segment-anything/
RUN pipenv run pip install -e lang-segment-anything

# Copy Pipfile and Pipfile.lock
COPY Pipfile ./

RUN pipenv install

# Copy the rest of the application
COPY . .

ENV FLASK_APP=src/app.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

CMD ["pipenv", "run", "python", "-m", "flask", "run", "--host=0.0.0.0", "--port=4001"]
