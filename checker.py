#! /usr/bin/env python
# -*- coding: utf-8 -*-

import click
import requests
import json
import yaml
import os
import os.path
import slacker
import sys

##############################################################################
##############################################################################
# requires: yaml, os, os.path
class Config(object):
    config_filename = None

    def __init__(self, config_filename=None):
        if config_filename:
            self.config_filename = config_filename
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
            if attribute == "ADMINS_ONLY":
                if os.environ[attribute] in ["true", "yes"]:
                    return True
                else:
                    return False
            return os.environ[attribute]
        else:
            if self.config_filename and attribute in self.config:
                return self.config[attribute]
##############################################################################
##############################################################################
class GitHub2FA:
    def get_users_without_2fa(self, github_username, github_token, github_org, admins_only):
        headers = {
            "Authorization": "token {}".format(github_token)
        }
        request_url = "https://api.github.com/orgs/{}/members?filter=2fa_disabled".format(github_org)
        if admins_only:
            request_url += "&role=admin"
        r = requests.get(request_url, auth=(github_username, github_token))
        users_without_2fa = [(u["login"]) for u in r.json()]
        if r.status_code == 200:
            return users_without_2fa
##############################################################################
##############################################################################

@click.command()
@click.option("--config", default=None, help="Config filename")
@click.option('-v', '--verbose', count=True)
def main(config, verbose):
    cfg = Config(config)

    if (not cfg.GITHUB_USERNAME or
        not cfg.GITHUB_TOKEN or
        not cfg.GITHUB_ORG or
        not cfg.SLACK_API_TOKEN or
        not cfg.SLACK_NOTIFICATION_CHANNEL):
       sys.exit("ERROR: Missing at least one configuration parameter.")

    if verbose: print("Known parameters: {} {} {} {} {} {}".format(cfg.GITHUB_USERNAME, cfg.GITHUB_TOKEN, cfg.GITHUB_ORG, cfg.SLACK_API_TOKEN, cfg.SLACK_NOTIFICATION_CHANNEL, cfg.ADMINS_ONLY))

    gh2fa = GitHub2FA()
    users_without_2fa = gh2fa.get_users_without_2fa(cfg.GITHUB_USERNAME, cfg.GITHUB_TOKEN, cfg.GITHUB_ORG, cfg.ADMINS_ONLY)
    notification_message = "The following users do not have 2FA enabled in the {} GitHub org: {}".format(cfg.GITHUB_ORG, users_without_2fa)

    if users_without_2fa:
        print(notification_message)
        slack = slacker.Slacker(cfg.SLACK_API_TOKEN)
        slack.chat.post_message("#{}".format(cfg.SLACK_NOTIFICATION_CHANNEL), notification_message, username="custodian", as_user="false")

if __name__ == "__main__":
    main()