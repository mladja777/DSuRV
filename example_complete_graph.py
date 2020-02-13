import sys
from multiprocessing import Process, Queue, Manager
from msg_passing_api import *
import sqlite3


def main():
    # Parse command line arguments
    if len(sys.argv) != 2:
        print('Program usage: example_complete_graph this_client_id')
        print('Example:')
        print('example_complete_graph 1, example_complete_graph 2, and example_complete_graph 3')
        exit()
    #
    thisId = int(sys.argv[1])
    # Parse database
    # Get this client information
    dbConnection = sqlite3.connect('network.db')
    dbCursor = dbConnection.cursor()
    dbCursor.execute("SELECT * FROM clients")
    clients = dbCursor.fetchall()
    for it in clients:
        if it[0] == thisId:
            thisClient = it
            break
    # Get all clients which this client connects to
    dbCursor.execute("SELECT * FROM relations WHERE sourceid=?", (thisClient[0],))
    relations = dbCursor.fetchall()
    tmp = []
    for it in relations:
        for cli in clients:
            if it[2] == cli[2]:
                tmp.append(cli)
    relations = tmp

    # Set ports
    local_port = thisClient[2]
    remote_ports = []
    for it in relations:
        remote_ports.append(it[2])

    with Manager() as manager:
        # Create queue for messages from the local server
        queue = Queue()
        # Create lists for IPC
        children = manager.list()
        parent = manager.list()

        # Create and start server process
        server = Process(target=server_fun, args=(local_port, queue,))
        server.start()
        receive = Process(target=receiveData, args=(thisId, relations, queue, children, parent,))
        receive.start()

        # Send a message to the peer node and receive message from the peer node.
        # To exit send message: exit.
        print('Send a message to the peer node and receive message from the peer node.')
        print('Before sending any message, initialize spanning tree.')
        print('Type: "init_tree"')
        print("-----------------------------------------------------------------------")

        shouldRun = True
        while shouldRun:
            shouldRun = sending(thisId, relations, children, parent)

        # Join with server process
        server.join()
        receive.join()

        # Delete queue and server
        del queue
        del server
        del receive


if __name__ == '__main__':
    main()
