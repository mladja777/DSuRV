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
    # print("-------------------------------------------------------------------")
    # Get this client information
    dbConnection = sqlite3.connect('network.db')
    dbCursor = dbConnection.cursor()
    dbCursor.execute("SELECT * FROM clients")
    clients = dbCursor.fetchall()
    for it in clients:
        if it[0] == thisId:
            thisClient = it
            break
    # print("This client info (id, ip, port):")
    # print(thisClient)
    # print("-------------------------------------------------------------------")
    # Get all clients which this client connects to
    dbCursor.execute("SELECT * FROM relations WHERE sourceid=?", (thisClient[0],))
    relations = dbCursor.fetchall()
    # print("This client is connected to (this_id, client_ip, client_port): ")
    tmp = []
    # print(relations)
    # print("-------------------------------------------------------------------")
    for it in relations:
        for cli in clients:
            if it[2] == cli[2]:
                tmp.append(cli)
    relations = tmp
    # print(relations)
    # print("-------------------------------------------------------------------")

    # Set ports
    local_port = thisClient[2]
    remote_ports = []
    for it in relations:
        remote_ports.append(it[2])

    with Manager() as manager:
        # Create queue for messages from the local server
        queue = Queue()
        children = manager.list()
        parent = manager.list()

        # Create and start server process
        server = Process(target=server_fun, args=(local_port, queue,))
        server.start()
        # client = Process(target=client_fun, args=(remote_ports,))
        # client.start()
        receive = Process(target=receiveData, args=(thisId, relations, queue, children, parent,))
        receive.start()

        # Set the lst of the addresses of the peer node's servers
        # remote_server_addresses = []
        # for it in relations:
        # remote_server_addresses.append((it[1], it[2]))

        # Send a message to the peer node and receive message from the peer node.
        # To exit send message: exit.
        print('Send a message to the peer node and receive message from the peer node.')
        print('Before sending any message, initialize spanning tree.')
        print('Type: "init_tree"')

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
