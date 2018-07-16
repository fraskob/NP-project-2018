# NP-project-2018
Final project: 'Netzwerk Programmierung'

# USAGE
Server:
The server needs to be started befor the client. You can do that by going to
.../NP-project-2018/server/src and typing './server.py host port'. As host you
presumably want to use your own machine, so you can replace it with 'localhost'.
For choosing a port, it is recommended to choos a port above 40000, to make
shure that the port is not used otherwise.

If the server is running it waits for clients to connect.

Updates, upgrades and pakets provided for the cliens are saved in the
corresponding directorys at NP-project-2018/server/src/

Heartbeat: The server expects a heartbeat message from the client at least 
every ten seconds. If no hearbeat is received for more than ten seconds the 
client connection will be closed.


Client:
To start the client you need a server with which it can connect with. To start
the client and connect to a server go to NP-project-2018/client/src and type
'./client.py host port'. Use the host on which the server is listening and the
same port like for the server. If the client is connected to the server you
can type '/help' to get an overview of the possibli operations. If you just
type something the client will send it as message to the server.

Pakets which are installed on the client are saved in 
NP-project-2018/client/src/pakets/
