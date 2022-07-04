FROM python:3.10-alpine

# ---------------------------------------------------------------------------
# METADATA
# ---------------------------------------------------------------------------
LABEL name="slackbot-juniper-mist"
LABEL maintainer="cremsburg.dev@gmail.com"
LABEL description="Slackbot container to interact with Juniper Mist"
LABEL license="Apache 2.0"
LABEL url="https://github.com/cdot65/slackbot-juniper-mist"
LABEL build-date="20220701"


# ---------------------------------------------------------------------------
# Change directory to /home/slackbot
# ---------------------------------------------------------------------------
WORKDIR /home/slackbot

# ---------------------------------------------------------------------------
# Add and install python packages
# ---------------------------------------------------------------------------
ADD docker/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# ---------------------------------------------------------------------------
# Add Slackbot script
# ---------------------------------------------------------------------------
ADD app /home/slackbot

# ---------------------------------------------------------------------------
# ENVIRONMENT SETUP, NOTE THAT WE HAVE TO HAVE PLACEHOLDER ARGS
# ---------------------------------------------------------------------------
ARG SLACK_APP_TOKEN="placeholder, will be replaced by build-arg" 
ARG SLACK_BOT_TOKEN="placeholder, will be replaced by build-arg" 
ARG SLACK_CHANNEL="placeholder, will be replaced by build-arg"
ARG MIST_ORG_ID="placeholder, will be replaced by build-arg" 
ARG MIST_API_TOKEN="placeholder, will be replaced by build-arg" 

ENV SLACK_APP_TOKEN=${SLACK_APP_TOKEN}
ENV SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
ENV SLACK_CHANNEL=${SLACK_CHANNEL}
ENV MIST_ORG_ID=${MIST_ORG_ID}
ENV MIST_API_TOKEN=${MIST_API_TOKEN}

# ---------------------------------------------------------------------------
# Execute our app.py script
# ---------------------------------------------------------------------------
CMD ["app.py"]
ENTRYPOINT ["python"]
