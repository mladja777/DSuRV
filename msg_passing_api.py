import sys
from multiprocessing import Process, Queue
from multiprocessing.connection import Client, Listener
from array import array

parent = None
children = []

shouldRun = True

def server_fun(local_port, queue):
    global shouldRun
    print("Server started.")
    # Set the address of the local node's server
    local_server_address = ('localhost', local_port)
    # Send fixed message
    with Listener(local_server_address, authkey=b'Lets work together') as listener:
        while True:
            with listener.accept() as conn:
                #print('connection accepted from', listener.last_accepted)
                msg = conn.recv()
                #print(msg)
                print("New message arrived...")
                
                # Forward msg to local node's process
                queue.put(msg)
                
                # Exit if msg is 'exit'
                if msg[1:] == 'exit':
                    shouldRun = False
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
        msgs.append( rcvMsg(queue) )
    
    return msgs

def passAlong(message, targetServers, thisId, msgSource):
    global children
    global parent
    for it in children:
        if msgSource != it[0]:
            sendMsg((it[1], it[2]), message)

    if msgSource != parent[0]:
        sendMsg((parent[1], parent[2]), message)

    if message == 'exit':
        shouldRun = False

def receiveData(thisId, targetServers, queue):
    global shouldRun
    global parent
    global children
    # Get message from local node's server
    while shouldRun:
        print("-------------------------------------------------------------------")
        msg = rcvMsg(queue)
        msgSource = int(msg[0])
        msg = msg[1:]
        if msg == "init_tree":
            if parent == None:
                for it in targetServers:
                    if it[0] == msgSource:
                        parent = it
                print("Parent ", parent, " initialized.")
                print("-------------------------------------------------------------------")
                msg = str(thisId) + "tree_parent"
                sendMsg((parent[1], parent[2]), msg)
            else:
                msg = str(thisId) + "tree_reject"
                sendMsg((parent[1], parent[2]), msg)
                print("Reject sent.")
                print("-------------------------------------------------------------------")
        elif msg == "tree_parent":    
            for it in targetServers:
                if it[0] == msgSource:
                    children.append(it)
                    print("Child ", children, " initialized.")
                    print("-------------------------------------------------------------------")
        elif msg == "tree_reject":
            pass
        else:
            print('Message received:', msg)
            msg = str(thisId) + msg
            passAlong(msg, targetServers, thisId, msgSource)
            print("-------------------------------------------------------------------")

def sending(thisId, relations):
    global parent
    global children
    # Input message
    msg = input('Enter message: ')
    if msg == "init_tree":
        msg = str(thisId) + msg
        for it in relations:
            try:
                sendMsg((it[1], it[2]), msg)
            except:
                pass
    else:
        msg = str(thisId) + msg
        print(children)
        for it in children:
            sendMsg((it[1], it[2]), msg)
        print(parent)
        if parent != None:
            sendMsg((parent[1], parent[2]), msg)
    #print('Message sent: %s \n' % (msg))
    
    if msg[1:] == 'exit':
        shouldRun = False
