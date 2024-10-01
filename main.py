import configparser
from flask import Flask, request, Response
import subprocess
import os
import time

def generateTimeString():
    curTime = time.localtime(time.time())
    return str(curTime.tm_mday) + "." + str(curTime.tm_mon) + "." + str(curTime.tm_year)[2:] + ", " + str(curTime.tm_hour) + ":" + str(curTime.tm_min) 

def log(input, repo):
    with open('./logs/main.log', "a") as file:
        file.write(generateTimeString() + " : " + repo + " : " + input + "\n")

dirList = os.listdir(os.getcwd() + "/config")
validConfigFiles = [file for file in dirList if file.endswith('.config')]
repos = []

for validFile in validConfigFiles:

    config = configparser.ConfigParser()
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
    app.run(debug=False, port=port)

