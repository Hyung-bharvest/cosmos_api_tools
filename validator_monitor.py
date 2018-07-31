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
node_IP_port = [] # put your node's IP:port(26657) for getting node info

height_before = -1
height = 0
validator_height = 0
validator_timestamp = ""
count = 0
n_peers = []

app = Flask(__name__)
@app.route("/")

def flask_view():

    if height - validator_height <= 3:
        commit_status = "OK"
    else:
        commit_status = "Missing!"

    reternscript = '<meta http-equiv="refresh" content="5">'
    reternscript = reternscript + 'height : ' + str(height) + '</br>validator height : ' + str(validator_height) + '</br>'
    reternscript = reternscript + 'commit status : ' + str(commit_status) + '</br>'
    for i in range(0,len(n_peers)):
         reternscript = reternscript + 'n_peers(' + str(i) +') : ' + str(n_peers[i]) + '</br>'
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
    global n_peers

    while True:

        try:

            # get consensus state from seednode
            Response_ConsensusState = requests.get("https://gaia-seeds.interblock.io/consensus_state", timeout=10)
            if str(Response_ConsensusState) == "<Response [200]>" :
                JSON_ConsensusState = json.loads(Response_ConsensusState.text)
                height_round_step = JSON_ConsensusState["result"]["round_state"]["height/round/step"]
                height_round_step_split = height_round_step.split("/")
                height = int(height_round_step_split[0])
                round = int(height_round_step_split[1])
                step = int(height_round_step_split[2])

                if height_before < height:
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
                    if validator_data == "" :
                        requestURL = "https://api.telegram.org/bot" + str(telegram_token) + "/sendMessage?chat_id=" + telegram_chat_id + "&text="
                        requestURL = requestURL + str(datetime.datetime.now()) + ':MissingCommits!!!'
                        response = requests.get(requestURL, timeout=10)
                    else :
                        pass
                    height_before = height

                    # get n_peers for each nodes
                    n_peers = []
                    for i in range(0,len(node_IP_port)):
                        response = requests.get("http://" + str(node_IP_port[i]) + "/net_info", timeout=10)
                        n_peers.append(int(json.loads(response.text)["result"]["n_peers"]))

                    # send message in every 1 hour
                    if count > 720:
                        requestURL = "https://api.telegram.org/bot" + str(telegram_token) + "/sendMessage?chat_id=" + telegram_chat_id + "&text="
                        requestURL = requestURL + str(datetime.datetime.now()) + ':Height=' + str(height) +'/Status:OK/Peers:'
                        for i in range(0,len(n_peers)):
                            requestURL = requestURL + str(n_peers[i]) + '.'
                        response = requests.get(requestURL, timeout=10)
                        count = 0

                    count = count + 1

            else :
                requestURL = "https://api.telegram.org/bot" + str(telegram_token) + "/sendMessage?chat_id=" + telegram_chat_id + "&text="
                requestURL = requestURL + str(datetime.datetime.now()) + ':RequestError!!!'
                response = requests.get(requestURL, timeout=10)

            time.sleep(1)

        except:
            requestURL = "https://api.telegram.org/bot" + str(telegram_token) + "/sendMessage?chat_id=" + telegram_chat_id + "&text="
            requestURL = requestURL + str(datetime.datetime.now()) + ':RequestError!!!'
            response = requests.get(requestURL, timeout=10)
            time.sleep(10)


def flask_run():
    app.run(host='0.0.0.0', port='5000')

t1 = threading.Thread(name='flask_run', target=flask_run)
t2 = threading.Thread(name='get_data', target=get_data)

t1.start()
t2.start()
