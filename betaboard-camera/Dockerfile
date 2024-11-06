FROM arm32v6/alpine:3.18

# Install Python and build dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    opencv \
    mesa-dev \
    glib-dev

WORKDIR /app

# Install pipenv
RUN pip3 install pipenv

# Copy the application
COPY . .

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies
RUN pipenv install --system --deploy

ENV FLASK_APP=src/betaboard_camera/app.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

EXPOSE 8000

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]