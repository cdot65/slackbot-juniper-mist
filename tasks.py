"""Tasks for use with Invoke.

(c) 2021 Calvin Remsburg
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import logging
from invoke import task


# ---------------------------------------------------------------------------
# SYSTEM PARAMETERS
# ---------------------------------------------------------------------------
PWD = os.getcwd()

# ---------------------------------------------------------------------------
# SLACK TOKENS CAN BE LOADED FROM ENVIRONMENT OR TYPED AS A STRING
# ---------------------------------------------------------------------------
# try:
#     SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
# except KeyError:
#     SLACK_APP_TOKEN = "xapp-123"


# try:
#     SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
# except KeyError:
#     SLACK_BOT_TOKEN = "xoxb-123"


SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "xapp-1234")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "xoxb-1234")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "A1B2C3D4E5F")
MIST_ORG_ID = os.environ.get("MIST_ORG_ID", "12345678-1234-1234-1234-123456123456")
MIST_API_TOKEN = os.environ.get("MIST_API_TOKEN", "ABCDELICIOUS")

# ---------------------------------------------------------------------------
# DOCKER PARAMETERS
# ---------------------------------------------------------------------------
DOCKER_IMG = "ghcr.io/cdot65/slackbot-juniper-mist"
DOCKER_TAG = "0.0.1"


# ---------------------------------------------------------------------------
# LOGGING PARAMETERS
# ---------------------------------------------------------------------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
log_format = "%(asctime)s | %(levelname)s: %(message)s"
console_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(console_handler)


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------
def console_msg(message):
    """Provide a little formatting help for console messages."""
    logger.info(message)


def run_command(context, command, **kwargs):
    """Helper function to run commands based on arguments."""
    context.run(command, **kwargs)


# ---------------------------------------------------------------------------
# DOCKER CONTAINER IMAGE BUILD
# ---------------------------------------------------------------------------
@task(
    help={
        "force_rm": "Always remove existing containers.",
        "cache": "Determine whether or not to use local cache.",
    }
)
def build(context, force_rm=False, cache=True):
    """Build our docker container image.
    Args:
        context (obj): Used to run specific commands
        force_rm (Bool): will remove any local instance [default: False]
        cache (Bool): determine whether or not to use cache [default: True]
    """

    # build command pointing to a folder outside our local context
    command = "docker build -f docker/Dockerfile"

    if not cache:
        command += " --no-cache"
    if force_rm:
        command += " --force-rm"

    # tokens used by our app are passed into the container build process
    slack_app_token = f"SLACK_APP_TOKEN={SLACK_APP_TOKEN}"
    slack_bot_token = f"SLACK_BOT_TOKEN={SLACK_BOT_TOKEN}"
    slack_channel = f"SLACK_CHANNEL={SLACK_CHANNEL}"
    mist_org_id = f"MIST_ORG_ID={MIST_ORG_ID}"
    mist_api_token = f"MIST_API_TOKEN={MIST_API_TOKEN}"

    # build arguments pass our tokens into the build process
    slack_arguments = f"--build-arg={slack_app_token} --build-arg={slack_bot_token} --build-arg={slack_channel}"
    mist_arguments = f"--build-arg={mist_org_id} --build-arg={mist_api_token}"

    console_msg(f"Building our Docker container image {DOCKER_IMG}:{DOCKER_TAG}")
    context.run(
        f"{command} {slack_arguments} {mist_arguments} -t {DOCKER_IMG}:{DOCKER_TAG} .",
    )


# ------------------------------------------------------------------------------
# START / STOP / DEBUG
# ------------------------------------------------------------------------------
@task()
def local(context):
    """Test our slackbot by running it locally."""

    # run an ephemeral container in the foreground
    command = "docker run -it --rm"

    # specify working directory
    # workdir = "/home/slackbot"

    # mount our app/ directory to user home
    # volume = f"{PWD}/app:{workdir}"

    console_msg(f"Building our Docker container image {DOCKER_IMG}:{DOCKER_TAG}")
    context.run(f"{command} {DOCKER_IMG}:{DOCKER_TAG}", pty=True)


# ------------------------------------------------------------------------------
# ACTIONS
# ------------------------------------------------------------------------------
@task
def shell(context):
    # Get access to the BASH shell within our container
    print("Jump into a container")
    context.run(
        f"docker run -it --rm \
            -v {PWD}/cdot65/apstra:/home/apstra \
            -w /home/apstra/ \
            {DOCKER_IMG}:{DOCKER_TAG} /bin/bash",
        pty=True,
    )


# ------------------------------------------------------------------------------
# TESTS / LINTING
# ------------------------------------------------------------------------------
@task
def black(context):
    """Run black to check that Python files adhere to its style standards.

    Args:
        context (obj): Used to run specific commands
    """
    command = "black --check --diff ."
    run_command(context, command)


@task
def yamllint(context):
    """Run yamllint to validate formating adheres to NTC defined YAML standards.

    Args:
        context (obj): Used to run specific commands
    """
    command = "yamllint . --format standard"
    run_command(context, command)


@task
def flake8(context):
    """Check for PEP8 compliance and other style issues."""
    command = "flake8 ."
    run_command(context, command)


@task
def tests(context):
    """Run all tests for this plugin.

    Args:
        context (obj): Used to run specific commands
    """
    # Sorted loosely from fastest to slowest
    console_msg("Running black...")
    black(context)
    console_msg("Running yamllint...")
    yamllint(context)
    console_msg("Running flake8...")
    flake8(context)
    console_msg("All tests have passed!")
