import configparser
from flask import Flask, request, Response
import json
import subprocess

config = configparser.ConfigParser()
config.read('server.config')

port = config.get('MAIN', 'PORT')
repo = config.get('MAIN', 'REPO_NAME')
repoUrl = config.get('MAIN', 'GIT_REPO')
branch = str(config.get('MAIN', 'BRANCH'))

command = config.get('COMMANDS', 'COMMAND_TO_EXECUTE')

app = Flask(__name__)

@app.route('/' + repo, methods=['POST'])
def respond():
    body = request.json

    if body['repository']['url'] == repoUrl:

        if body['ref'] == ("refs/heads/" + branch):

            print("Executing command")
            with open("executed.log", "w") as file:
                result = subprocess.run(command.split(), capture_output=True, text=True)
                file.write(result.stdout)
                if result.returncode == 0:
                    print("Command was executed successfully")
                else:
                    print(result.returncode)

            return Response(status=200)

        else:
            print("Webhook received was not send for branch refs/heads/" + branch + " but instead for branch " + body['ref'])

    else:
        print("URL of repo does not match configuration")
    
    return Response(status=400)

if __name__ == '__main__':
    app.run(debug=True, port=port)