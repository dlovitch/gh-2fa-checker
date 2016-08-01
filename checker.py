#! /usr/bin/env python
# -*- coding: utf-8 -*-

import click
import requests
import json
import yaml
import os
import os.path
import slacker

##############################################################################
##############################################################################
# requires: yaml, os, os.path
class Config(object):
    def __init__(self, config_filename=None):
        if config_filename:
            if os.path.isfile(config_filename):
                with open(config_filename, "r") as f:
                    self.config = yaml.load(f)

    def __getattr__(self, attribute):
        # NOTE: if neither an environment variable nor a file exists, the
        # following error will occur: RecursionError: maximum recursion depth
        # exceeded while calling a Python object

        # prioritize environment variables for configuration over the
        # configuration file
        if attribute in os.environ:
            return os.environ[attribute]
        else:
            if attribute in self.config:
                return self.config[attribute]
##############################################################################
##############################################################################

def get_admins_without_2fa(github_username, github_token, github_org):
    headers = {
        "Authorization": "token {}".format(github_token)
    }
    r = requests.get("https://api.github.com/orgs/{}/members?filter=2fa_disabled&role=admin".format(github_org), auth=(github_username, github_token))
    admins_without_2fa = [(u["login"]) for u in r.json()]
    if r.status_code == 200:
        return admins_without_2fa

@click.command()
@click.option("--config-file", default=None, help="Config filename")
def main(config_file):
    config = Config(config_file)

    if (not config.GITHUB_USERNAME or
        not config.GITHUB_TOKEN or
        not config.GITHUB_ORG or
        not config.SLACK_API_TOKEN or
        not config.SLACK_NOTIFICATION_CHANNEL):
       print("ERROR: Missing configuration parameter.")
       print("Known parameters: {} {} {} {} {}".format(config.GITHUB_USERNAME, config.GITHUB_TOKEN, config.GITHUB_ORG, config.SLACK_API_TOKEN, config.SLACK_NOTIFICATION_CHANNEL))

    admins_without_2fa = get_admins_without_2fa(config.GITHUB_USERNAME, config.GITHUB_TOKEN, config.GITHUB_ORG)
    notification_message = "The following users are admins without 2FA enabled in the {} GitHub org: {}".format(config.GITHUB_ORG, admins_without_2fa)

    if admins_without_2fa:
        print(notification_message)
        slack = slacker.Slacker(config.SLACK_API_TOKEN)
        slack.chat.post_message("#{}".format(config.SLACK_NOTIFICATION_CHANNEL), notification_message, username="custodian", as_user="false")

if __name__ == "__main__":
    main()