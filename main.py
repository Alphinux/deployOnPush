import configparser
from flask import Flask, request, Response
import subprocess
import os
import time
import logging

# --- Logging ---
logger = logging.getLogger(__name__)
logging.basicConfig(filename='logs/main.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def log(message, repo, level = 0):

    match level:
        case 0:
            logging.info(repo + " : " + message)
        case 1:
            logging.warning(repo + " : " + message)
        case 2:
            logging.error(repo + " : " + message)
        case 3:
            logging.critical(repo + " : " + message)

# --- Read possible configuration files ---
dirList = os.listdir(os.getcwd() + "/config")
possibleConfigFiles = [file for file in dirList if file.endswith('.config') and not file == 'default.config']
repos = []

for possibleFile in possibleConfigFiles:

    try:
        config = configparser.ConfigParser()
        config.read("./config/" + possibleFile)
        
        repos.append({
            "name": config.get('MAIN', 'REPO_NAME'),
            "url": config.get('MAIN', 'GIT_REPO'),
            "branch": config.get('MAIN', 'BRANCH'),
            "command": config.get('COMMANDS', 'COMMAND_TO_EXECUTE')
        })
    except:
        print("There's been an error when reading " + possibleFile + ". Maybe the configuration's not in the right format?")

# --- Setup server ---
if len(repos) != 0:

    config = configparser.ConfigParser()
    config.read('server.config')
    port = config.get('MAIN', 'PORT')

    app = Flask(__name__)

    for repo in repos:

        @app.route('/' + repo['name'], methods=['POST'])
        def respond():
            body = request.json

            log("Received hook for commit " + body['after'], repo['name']) 

            if body['repository']['name'] == repo['name'] and body['repository']['url'] == repo['url']:

                if body['ref'] == ("refs/heads/" + repo['branch']):

                    with open("./logs/executed.log", "w") as file:
                        result = subprocess.run(repo['command'].split(), capture_output=True, text=True, check=False, shell=True)
                        file.write(str(result.stdout))
                        if result.returncode == 0:
                            log("Command was executed successfully", repo['name'])
                            return Response(status=200)
                        else:
                            log("Command failed with code " + str(result.returncode), repo['name'])
                            return Response(status=500)

                else:
                    log("Webhook received was not send for branch refs/heads/" + repo['branch'] + " but instead for branch " + body['ref'], repo['name'])

            else:
                log("Name or URL of repo does not match configuration", repo['name'])
            
            return Response(status=400)

    if __name__ == '__main__':
        print("Run the server according to the documentation in README.md")
    else:
        print("Server has been started")
        
else:
    print("No server has been configured.")

