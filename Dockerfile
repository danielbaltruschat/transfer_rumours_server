# Use an official Python runtime as a base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
#COPY . /app

# Install required Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install supervisor to run multiple processes, makes log files directory
RUN apt-get update && apt-get install -y supervisor && mkdir -p /var/log/supervisor

COPY nlp/__init__.py /app/nlp/__init__.py
COPY nlp/spacy_load_ner.py /app/nlp/spacy_load_ner.py
COPY nlp/tweet_categorisation_load.py /app/nlp/tweet_categorisation_load.py
COPY nlp/categorisation_model /app/nlp/categorisation_model
COPY nlp/ner_model/model-best /app/nlp/ner_model/model-best

COPY --chmod=0755 transfer_sources/twitter/get_tweets.bin /app/transfer_sources/twitter/get_tweets.bin
COPY transfer_sources/twitter/twitter_sources.txt /app/transfer_sources/twitter/twitter_sources.txt


COPY update_database.py .

#TODO move server to separate container
COPY server.py .
COPY wsgi.py .
COPY transfermarktscraper /app/transfermarktscraper


# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf


# Set default values for MySQL environment variables
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=my_password
ENV MYSQL_PORT=3306
ENV TIME_WAIT=1800

ENV TOKENIZERS_PARALLELISM=false

# Expose the port of python scripts and MySQL
EXPOSE 8000

# Run python scripts using supervisord when the container launches
CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
