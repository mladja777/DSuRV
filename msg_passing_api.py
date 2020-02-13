import sys
from multiprocessing import Process, Queue, Manager
from multiprocessing.connection import Client, Listener
from array import array


# parent = None
# children = []

# shouldRun = True

def server_fun(local_port, queue):
    print("Server started.")
    # Set the address of the local node's server
    local_server_address = ('localhost', local_port)
    # Send fixed message
    with Listener(local_server_address, authkey=b'Lets work together') as listener:
        while True:
            with listener.accept() as conn:
                # print('connection accepted from', listener.last_accepted)
                msg = conn.recv()

                # Forward msg to local node's process
                queue.put(msg)

                # Exit if msg is 'exit'
                if msg[1:] == 'exit':
                    break


def sendMsg(remote_server_address, msg):
    with Client(remote_server_address, authkey=b'Lets work together') as conn:
        conn.send(msg)


def rcvMsg(queue):
    return queue.get()


def broadcastMsg(list_of_remote_server_address, msg):
    for remote_server_address in list_of_remote_server_address:
        sendMsg(remote_server_address, msg)


def rcvMsgs(queue, no_of_messages_to_receive):
    msgs = []

    for i in range(no_of_messages_to_receive):
        msgs.append(rcvMsg(queue))

    return msgs


def passAlong(message, msgSource, children, parent):
    for it in children:
        if msgSource != it[0]:
            sendMsg((it[1], it[2]), message)

    if len(parent) != 0:
        p = parent[0]
        if msgSource != p[0]:
            sendMsg((p[1], p[2]), message)

    if message == 'exit':
        pass


def receiveData(thisId, targetServers, queue, children, parent):
    # Get message from local node's server
    while True:
        msg = rcvMsg(queue)
        msgSource = int(msg[0])
        msg = msg[1:]
        if msg == "init_tree":
            if len(parent) == 0:
                for it in targetServers:
                    if it[0] == msgSource:
                        parent.append(it)
                print("Parent ", parent, " initialized.")
                print("---------------------------")
                msg = str(thisId) + "tree_parent"
                p = parent[0]
                sendMsg((p[1], p[2]), msg)
                initMsg = str(thisId) + "init_tree"
                for it in targetServers:
                    if msgSource != it[0]:
                        sendMsg((it[1], it[2]), initMsg)
            else:
                p = parent[0]
                msg = str(thisId) + "tree_reject"
                sendMsg((p[1], p[2]), msg)
                print("Reject sent.")
                print("---------------------------")
        elif msg == "tree_parent":
            for it in targetServers:
                if it[0] == msgSource:
                    children.append(it)
                    print("Child ", children, " initialized.")
                    print("---------------------------")
        elif msg == "tree_reject":
            pass
        else:
            print('Message received:', msg)
            msg = str(thisId) + msg
            passAlong(msg, msgSource, children, parent)
            print("---------------------------")
            if msg[1:] is "exit":
                break


def sending(thisId, relations, children, parent):
    # Input message
    msg = input()
    if msg == "init_tree":
        msg = str(thisId) + msg
        for it in relations:
            try:
                sendMsg((it[1], it[2]), msg)
            except:
                pass
    else:
        msg = str(thisId) + msg
        for it in children:
            sendMsg((it[1], it[2]), msg)
        if len(parent) != 0:
            p = parent[0]
            sendMsg((p[1], p[2]), msg)

    if msg[1:] == 'exit':
        return False
    else:
        return True
