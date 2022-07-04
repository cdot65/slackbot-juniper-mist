"""Slackbot for Juniper Mist."""

# standard library
import os
import json
import logging
import time


# third party
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv


# local
from mist_helper import MarvisIssues, MistApi, SiteAlerts

# -----------------------------------------------------------------------------
# Load environment variables as new objects for our script
# -----------------------------------------------------------------------------
load_dotenv()

# Registers our environment variables as new objects
api_token = os.environ.get("MIST_API_TOKEN")
org_id = os.environ.get("MIST_ORG_ID")
slack_channel = os.environ.get("SLACK_CHANNEL")

# create an instance of our logging object
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Initialize app with bot token and socket mode handler
# -----------------------------------------------------------------------------
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


# -----------------------------------------------------------------------------
# Handle logging in a more graceful way than printing to screen
# -----------------------------------------------------------------------------
@app.event("message")
def handle_message_events(body, logger):
    """When a message is recorded, send it to our logging object."""
    logger.info(body)


# -----------------------------------------------------------------------------
# Present the user with our modal when /mist is executed
# -----------------------------------------------------------------------------
@app.command("/mist")
def open_modal(ack, body, client):
    """Create a view and present it to the user."""

    # Acknowledge the slash command request
    ack()

    logo = "https://raw.githubusercontent.com/cdot65/svg-locker-shhhhh/master/slack-modal.png"
    # logo = "img/slack-modal.png"

    # Call views_open with the built-in client
    client.views_open(
        # Pass a valid trigger_id within 3 seconds of receiving it
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            # View identifier
            "callback_id": "task-menu",
            "title": {
                "type": "plain_text",
                "text": "Juniper Mist Slack bot",
                "emoji": True,
            },
            # "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
            "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
            "blocks": [
                {
                    "type": "image",
                    "image_url": logo,
                    "alt_text": "Juniper Mist Slack bot",
                },
                {"type": "divider"},
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Please select a task",
                        "emoji": True,
                    },
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "Retrieve site alerts",
                        "emoji": True,
                    },
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Click Here"},
                        "action_id": "site_alerts",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "Run Automated Reports",
                        "emoji": True,
                    },
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Click Here"},
                        "action_id": "automated_reports",
                    },
                },
            ],
        },
    )


# -----------------------------------------------------------------------------
# When `site_alerts` button is clicked in the main modal view
# -----------------------------------------------------------------------------
@app.action("site_alerts")
def site_alerts_view(ack, body, client):
    """Update the view when Site Alerts has been selected."""

    # Acknowledge the command request
    ack(response_action="clear")

    # Site Report view
    client.views_update(
        view_id=body["view"]["id"],  # Pass the view_id
        hash=body["view"][
            "hash"
        ],  # hash string that represents view state to protect against race conditions
        # View payload with updated blocks
        view={
            "type": "modal",
            "callback_id": "site_alerts",  # View identifier
            "private_metadata": json.dumps(body),
            "title": {
                "type": "plain_text",
                "text": "Juniper Mist",
                "emoji": True,
            },
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": ":bar_chart:  Reports",
                        "emoji": True,
                    },
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "text": "Slack bot automation",
                            "type": "mrkdwn",
                        }
                    ],
                },
                {
                    "type": "divider",
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": " :spiral_note_pad: *List of sites*",
                    },
                },
                {
                    "type": "input",
                    "block_id": "site_name",
                    "element": {
                        "type": "plain_text_input",
                        "initial_value": "978c48e6-6ef6-11e6-8bbf-02e208b2d34f",
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Name of site",
                        "emoji": True,
                    },
                },
                {"type": "divider"},
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": ":pushpin: Do you have something that you would like to see automated? Here's *how to submit a request*.",
                        }
                    ],
                },
            ],
            "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
            "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
        },
    )


# -----------------------------------------------------------------------------
# When `site_alerts_view` has been submitted with the input field
# -----------------------------------------------------------------------------
@app.view("site_alerts")
def site_alerts_view(ack, body, logger, client):
    """Handle the submission of our site's name."""

    # Acknowledge the view submission request
    ack(response_action="clear")

    # send body payload to logging object
    logger.info(body)

    # define input_site object based on the value passed in the form
    input_site = body["view"]["state"]["values"]["site_name"]
    user = body["user"]["username"]

    for key, value in input_site.items():
        if key is None:
            pass
        user_input = value["value"]

    message = f"user_input:\n{user_input}\n\nuser:\n{user}"

    try:
        epoch_time = time.time()
        current_time = int(epoch_time)

        # ask Marvis for a list of issues in our organization
        query = f"limit=100&start={current_time - 21600}&end={current_time}&severity=critical,warn,info"
        mist_request = MistApi(
            api_token=api_token, path=f"sites/{user_input}/alarms/search?{query}"
        )
        alerts = mist_request.get()

        site_alerts = SiteAlerts(**alerts)

        message = mist_request.template(site_alerts, "site_alerts.j2")

    except AssertionError as msg:
        print(msg)

    # send message to slack
    slack_message(message, client)


# -----------------------------------------------------------------------------
# When `automated_reports` button is clicked in the main modal view
# -----------------------------------------------------------------------------
@app.action("automated_reports")
def automated_reports_view(ack, body, client):
    """Update the view when Automated Reports has been selected."""

    # Acknowledge the command request
    ack(response_action="clear")

    # Site Report view
    client.views_update(
        view_id=body["view"]["id"],  # Pass the view_id
        hash=body["view"][
            "hash"
        ],  # hash string that represents view state to protect against race conditions
        # View payload with updated blocks
        view={
            "type": "modal",
            "callback_id": "automated_reports_view",  # View identifier
            "private_metadata": json.dumps(body),
            "title": {
                "type": "plain_text",
                "text": "Juniper Mist",
                "emoji": True,
            },
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": ":bar_chart:  Reports",
                        "emoji": True,
                    },
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "text": "Slack bot automation",
                            "type": "mrkdwn",
                        }
                    ],
                },
                {
                    "type": "divider",
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": " :spiral_note_pad: *List of sites*",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Retrieve a list of sites within an organization.",
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Create Report",
                            "emoji": True,
                        },
                        "action_id": "list_of_sites",
                    },
                },
                {
                    "type": "divider",
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": " :robot_face: *Marvis Issues*",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Retrieve a list of issues reported by Marvis.",
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Create Report",
                            "emoji": True,
                        },
                        "action_id": "marvis_issues",
                    },
                },
                {"type": "divider"},
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": ":pushpin: Do you have something that you would like to see automated? Here's *how to submit a request*.",
                        }
                    ],
                },
            ],
            # "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
            "close": {"type": "plain_text", "text": "Close Window", "emoji": True},
        },
    )


# -----------------------------------------------------------------------------
# When `list_of_sites` button is clicked in the `automated_reports_view` view
# -----------------------------------------------------------------------------
@app.action("list_of_sites")
def list_of_sites_action(ack, logger, client):
    """Actions to take after submission of site report form."""

    # Acknowledge the slash command request
    ack(response_action="clear")

    try:
        mist_request = MistApi(api_token=api_token, path=f"orgs/{org_id}/sites")
        sites = mist_request.get()
        message = mist_request.template(sites, "list_of_sites.j2")

        # send message to slack
        slack_message(message, client)

    except AssertionError as msg:
        print(msg)


# -----------------------------------------------------------------------------
# When `marvis_issues` button is clicked in the `automated_reports_view` view
# -----------------------------------------------------------------------------
@app.action("marvis_issues")
def marvis_issues_action(ack, logger, client):
    """Actions to take after submission of site report form."""

    # Acknowledge the slash command request
    ack(response_action="clear")

    try:
        # ask Marvis for a list of issues in our organization
        query = "query=group_by_category_symptom&display_priority=high&active=true"
        mist_request = MistApi(
            api_token=api_token, path=f"labs/orgs/{org_id}/suggestions?{query}"
        )
        issues = mist_request.get()
        marvis_issues = MarvisIssues(**issues["data"])
        message = mist_request.template(marvis_issues, "marvis_issues.j2")

        # send message to slack
        slack_message(message, client)

    except AssertionError as msg:
        print(msg)


# -----------------------------------------------------------------------------
# Send message back to Slack channel
# -----------------------------------------------------------------------------
def slack_message(message, client):
    """Send our message to Slack."""

    # ID of the channel you want to send the message to
    channel_id = f"{slack_channel}"
    try:
        # Call the chat.postMessage method using the WebClient
        result = client.chat_postMessage(
            channel=channel_id,
            text=f"*Successfully requested a report*: \n{message}",
        )
        logger.info(result)

    except SlackApiError as error_message:
        logger.error(error_message)


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
