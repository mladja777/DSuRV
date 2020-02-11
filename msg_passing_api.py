import sys
from multiprocessing import Process, Queue
from multiprocessing.connection import Client, Listener
from array import array

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

def client_fun(remote_servers):
    print("Client started.")
    global shouldRun
    while shouldRun:
        # Input message
        msg = input('Enter message: ')
        print('Message sent: %s \n' % (msg))
        
        for it in remote_servers:
            sendMsg( it, 'exit')
            
        if msg == 'exit':
            shouldRun = False
            break

def passAlong(message, targetServers, thisId, msgSource):
    for it in targetServers:
        if thisId != it[0] and msgSource != it[0]:
            sendMsg((it[1], it[2]), message)

    if message == 'exit':
        shouldRun = False

def receiveData(thisId, targetServers, queue):
    global shouldRun
    # Get message from local node's server
    while shouldRun:
        print("-------------------------------------------------------------------")
        msg = rcvMsg(queue)
        msgSource = int(msg[0])
        msg = msg[1:]
        print('Message received:', msg)
        msg = str(thisId) + msg
        passAlong(msg, targetServers, thisId, msgSource)
        print("-------------------------------------------------------------------")
