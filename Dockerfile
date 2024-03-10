# Use an official Python runtime as a base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Install required Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install supervisor to run multiple processes, makes log files directory
RUN apt-get update && apt-get install -y supervisor && mkdir -p /var/log/supervisor


COPY nlp/spacy_models/full_model_v1/model-best /app/nlp/spacy_models/full_model_v1/model-best
COPY nlp/categorisation_model /app/nlp/categorisation_model

COPY nlp/__init__.py /app/nlp/__init__.py
COPY nlp/spacy_models/relation_extraction.py /app/nlp/spacy_models/relation_extraction.py
COPY nlp/spacy_models/relation_component.py /app/nlp/spacy_models/relation_component.py
COPY nlp/spacy_models/entity_resolver_model.py /app/nlp/spacy_models/entity_resolver_model.py
COPY nlp/spacy_models/entity_resolver_component.py /app/nlp/spacy_models/entity_resolver_component.py
COPY nlp/tweet_categorisation_load.py /app/nlp/tweet_categorisation_load.py

COPY nlp/format_rel_resolver_predictions.py /app/nlp/format_rel_resolver_predictions.py
COPY nlp/normalise_data.py /app/nlp/normalise_data.py
COPY nlp/team_names.json /app/nlp/team_names.json
COPY nlp/common_addons.txt /app/nlp/common_addons.txt

COPY nlp/transfermarktscraper /app/nlp/transfermarktscraper


COPY --chmod=0755 transfer_sources/twitter/get_tweets.bin /app/transfer_sources/twitter/get_tweets.bin
COPY transfer_sources/twitter/twitter_sources.txt /app/transfer_sources/twitter/twitter_sources.txt

COPY /utility /app

COPY database_functions.py .
COPY update_database.py .

COPY server.py .
COPY wsgi.py .

COPY gunicorn.conf.py .
COPY certs /app/certs


# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf


# Set default values for MySQL environment variables
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=my_password
ENV MYSQL_PORT=3306
ENV TIME_WAIT=1800
ENV TWITTER_USERNAME=TSferapp2
ENV TWITTER_PASSWORD=transfer_app

ENV TOKENIZERS_PARALLELISM=false

# Expose the port of python scripts
EXPOSE 8000

# Run python scripts using supervisord when the container launches
CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
