# cosmos_api_tools
cosmos_api_tools for validators

1. Package installation

- (sudo) pip(pip3) install requests
- (sudo) pip(pip3) install flask

2. Get parameters for configuration

- validator_address = node_id for your validator
- telegram_token = token for your telegram bot
- telegram_chat_id = open a chatroom with your telegram bot and check the chat id of the chatroom
- node_IP_port = array of "ip:port" that you want to monitor its current peer number.
- commit_history_period = array of integer for different block periods of recent missing status
- httpAddress = "http://ip:port" for request general commit data from any full-node whose 26657 port is open


3. Security configure

- should open inbound 26657 port for all node_IP_port and httpAddress servers
- you can just open it for only IP of monitoring server

4. Run and check your webpage

- visit http://<monitoraddress>:5000/ for monitoring your validator's missing behavior
- please report bugs or ideas on adding new features to b-harvest on riot chatroom
