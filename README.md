# deployOnPush
deployOnPush is a **lightweight** utility tailored for individual developers working on personal or hobby projects. It simplifies the process of automatically updating and deploying your application whenever new commits are pushed to a GitHub repository.
It supports multiple projects with different routes and different deploymment commands.

## Setup / Installation
### On Server
First clone this git repository in the working directory of your project (or somewhere else if you please).

```bash
git clone https://github.com/Alphinux/deployOnPush
cd deployOnPush
```

Secondly install the required pip modules.

```
pip install -r requirements.txt
```

Then configure the server by adding a new file to the ``config`` directory based on ``default.config``.

```text
[MAIN]
REPO_NAME = <repo_name>
GIT_REPO = <repo_url>
BRANCH = <branch>

[COMMANDS]
COMMAND_TO_EXECUTE = <command>
```
``COMMAND_TO_EXECUTE`` is the command that will be executed when a webhook that fits the configuration is received. In order to chain multiple commands you can use the ``&&`` operator like in ``git pull && systemctl restart httpd``.
This will only execute the second command if the first one succeded. Alternatively to always also execute the second command you can use the ``;`` operator like in ``git pull; systemctl restart httpd``.

deployOnPush supports multiple projects and configurations. Too add a second project you can just create a new file with a ``.config`` extension.

> **The endpoint of each project is the name of the repository, so for example ``/deployOnPush`` for this repository.**
### On Github (or similar)
Setup a webhook by going to ``Settings > Webhooks`` and clicking on ``Add webhook`` and setting the following:
- "Payload URL" as your servers domain and port and the corresponding route (f.e. https://ruser.dev:8000/deployOnPush)
- "Content" type as ``application/json``
- Enable or disable SSL according to your website configuration
- Set the events to "Just the push event."
- Make sure "Active" is ticked

Add the webhook.

## Running the server
The server can now be run with this command where ``<port>`` is the port you want the server to listen on:
```bash
gunicorn --log-level warning --bind 0.0.0.0:<port> main:app
```

## Troubleshooting / Logging
The logs are saved in the ``logs`` directory. The ``main.log`` contains the logs for received webhooks. The ``executed.log`` contains the log of the last command that was executed by the server.
