FROM python:3.9

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

COPY static/ ./static/

RUN pip install pipenv

RUN pipenv run pip install --upgrade setuptools wheel

# Install GroundingDINO at 856dde20aee659246248e20734ef9ba5214f5e44
RUN git clone https://github.com/IDEA-Research/GroundingDINO.git && \
    cd GroundingDINO && \
    git checkout 856dde20aee659246248e20734ef9ba5214f5e44 && \
    cd .. && \
    pipenv run pip install -e GroundingDINO

# Install lang-segment-anything
RUN git clone https://github.com/luca-medeiros/lang-segment-anything.git && \
    cd lang-segment-anything && \
    git checkout 05c386ee95b26a8ec8398bebddf70ffb8ddd3faf && \
    cd .. && \
    pipenv run pip install -e lang-segment-anything

# Copy Pipfile and Pipfile.lock
COPY Pipfile ./

RUN pipenv install

# Copy the rest of the application
COPY . .

ENV FLASK_APP=src/app.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

CMD ["pipenv", "run", "python", "-m", "flask", "run", "--host=0.0.0.0", "--port=4002"]
