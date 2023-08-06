Example for Configuration file.

Reference: https://docs.python.org/3/library/logging.config.html#configuration-file-format

```
[handler_slack]
class = log2slack.SlackHandler
args = ('domain.slack.com', 'slack_token', '#channel', 'display_name')
level = ERROR
formatter = generic
```
