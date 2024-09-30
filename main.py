import configparser
from flask import Flask, request, Response
import json
import subprocess
import os

dirList = os.listdir(os.getcwd() + "/config")
validConfigFiles = [file for file in dirList if file.endswith('.config')]
repos = []

for validFile in validConfigFiles:

    config = configparser.ConfigParser()
    print(validFile)
    config.read("./config/" + validFile)
    
    repos.append({
        "name": config.get('MAIN', 'REPO_NAME'),
        "url": config.get('MAIN', 'GIT_REPO'),
        "branch": config.get('MAIN', 'BRANCH'),
        "command": config.get('COMMANDS', 'COMMAND_TO_EXECUTE')
    })

config = configparser.ConfigParser()
config.read('server.config')
port = config.get('MAIN', 'PORT')

app = Flask(__name__)

for repo in repos:

    @app.route('/' + repo['name'], methods=['POST'])
    def respond():
        body = request.json

        if body['repository']['url'] == repo['url']:

            if body['ref'] == ("refs/heads/" + repo['branch']):

                print("Executing command")
                with open("executed.log", "w") as file:
                    result = subprocess.run(repo['command'].split(), capture_output=True, text=True)
                    file.write(result.stdout)
                    if result.returncode == 0:
                        print("Command was executed successfully")
                    else:
                        print(result.returncode)

                return Response(status=200)

            else:
                print("Webhook received was not send for branch refs/heads/" + repo['branch'] + " but instead for branch " + body['ref'])

        else:
            print("URL of repo does not match configuration")
        
        return Response(status=400)
    
if __name__ == '__main__':
    app.run(debug=False, port=port)