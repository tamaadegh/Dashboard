FROM python:3.11-slim-bookworm

# Cache-busting argument - change this to force rebuild from this point
# Usage: docker build --build-arg CACHEBUST=$(date +%s) -t yourimage .
ARG CACHEBUST=1

# Copy dependency files FIRST to leverage Docker layer caching
# When these files change, Docker will rebuild from this point forward
COPY ./Pipfile /Pipfile
COPY ./Pipfile.lock /Pipfile.lock
COPY ./requirements.txt /tmp/requirements.txt

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    netcat-traditional \
 && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir -q 'pipenv==2020.11.15' && pipenv install --deploy --system

# Explicitly install dj-database-url and imagekitio (latest versions)
RUN pip install --no-cache-dir dj-database-url 

# Install all requirements including cloudinary (MUST be after Pipfile to override if needed)
RUN pip install --upgrade --no-cache-dir -r /tmp/requirements.txt

RUN mkdir /backend
COPY ./ /backend
WORKDIR /backend

RUN chmod +x /backend/scripts/entrypoint.sh

RUN mkdir -p /backend/media
RUN chmod +x /backend/media


CMD ["/backend/scripts/entrypoint.sh"]

# docker build -t nxtbn/nxtbn:latest .
# docker login
# docker push nxtbn/nxtbn:latest