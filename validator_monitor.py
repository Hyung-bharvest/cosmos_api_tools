# -*- coding: utf8 -*-

# monitor validator's commit activity & alert by telegram message
# by dlguddus(B-Harvest)

import time
import requests
import json
import os
import threading
import sys
import datetime
from flask import Flask
from flask import Markup
from flask import Flask
from flask import render_template

validator_address = "" # put your validator hex address here
telegram_token = "" # put your telegram bot token here
telegram_chat_id = "" # put your telegram chat_id here
height_before = -1
height = 0
validator_height = 0
validator_timestamp = ""
count = 0


app = Flask(__name__)
@app.route("/")

def flask_view():

    if height - validator_height <= 3:
        commit_status = "OK"
    else:
        commit_status = "Missing!"

    reternscript = '<meta http-equiv="refresh" content="5">'
    reternscript = reternscript + 'validator address : ' + str(validator_address) + '</br>'
    reternscript = reternscript + 'height : ' + str(height) + '</br>validator height : ' + str(validator_height) + '</br>'
    reternscript = reternscript + 'commit status : ' + str(commit_status)
    return reternscript

def get_data():

    global height
    global height_before
    global round
    global step
    global validator_data
    global validator_address
    global validator_height
    global validator_timestamp
    global count

    while True:
        # get consensus state from seednode
        Response_ConsensusState = requests.get("https://gaia-seeds.interblock.io/consensus_state", timeout=10)
        if str(Response_ConsensusState) == "<Response [200]>" :
            JSON_ConsensusState = json.loads(Response_ConsensusState.text)
            height_round_step = JSON_ConsensusState["result"]["round_state"]["height/round/step"]
            height_round_step_split = height_round_step.split("/")
            height = int(height_round_step_split[0])
            round = int(height_round_step_split[1])
            step = int(height_round_step_split[2])

            # get validator's commit
            Response_CommitHeight = requests.get("https://gaia-seeds.interblock.io/commit?height=" + str(height-2), timeout=10)
            validator_data = ""
            if str(Response_CommitHeight) == "<Response [200]>" :
                JSON_CommitHeight = json.loads(Response_CommitHeight.text)
                for item in JSON_CommitHeight["result"]["SignedHeader"]["commit"]["precommits"] :
                    if str(item) == "null" or item == None : pass
                    else :
                        if item["validator_address"] == validator_address :
                            validator_data = item
                            validator_height = int(validator_data["height"])
                            validator_timestamp = str(validator_data["timestamp"])
                            break
            else :
                pass

            # send telegram message when missing commits
            if height_before < height:
                if validator_data == "" :
                    requestURL = "https://api.telegram.org/bot" + str(telegram_token) + "/sendMessage?chat_id=" + telegram_chat_id + "&text="
                    requestURL = requestURL + str(datetime.datetime.now()) + ':MissingCommits!!!'
                    response = requests.get(requestURL, timeout=10)
                else :
                    if count > 720:
                        requestURL = "https://api.telegram.org/bot" + str(telegram_token) + "/sendMessage?chat_id=" + telegram_chat_id + "&text="
                        requestURL = requestURL + str(datetime.datetime.now()) + ':Height=' + str(height) +'/Status:OK'
                        response = requests.get(requestURL, timeout=10)
                        count = 0
                height_before = height
                count = count + 1
        else :
            requestURL = "https://api.telegram.org/bot" + str(telegram_token) + "/sendMessage?chat_id=" + telegram_chat_id + "&text="
            requestURL = requestURL + str(datetime.datetime.now()) + ':RequestError!!!'
            response = requests.get(requestURL, timeout=10)


def flask_run():
    app.run(host='0.0.0.0', port='5000')



t1 = threading.Thread(name='flask_run', target=flask_run)
t2 = threading.Thread(name='get_data', target=get_data)

t1.start()
t2.start()
