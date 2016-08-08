# gh-2fa-checker

This script checks a GitHub organization for all admins that do not have 2FA enabled and then outputs the results to a Slack channel.

Configuration parameters can be supplied via a YAML file (and named on the command line with the `--config-file` option) or environment variables.

The required variables are:
```
GITHUB_USERNAME
GITHUB_TOKEN
GITHUB_ORG
SLACK_API_TOKEN
SLACK_NOTIFICATION_CHANNEL
```

1. Generate a GitHub token for the `GITHUB_TOKEN` parameter by going here: https://github.com/settings/tokens
  * The only required permission is `read:org`
1. Create a new Slack bot user via this page: https://slack.com/apps/A0F7YS25R-bots and use that bot's API token for the `SLACK_API_TOKEN` parameter.
