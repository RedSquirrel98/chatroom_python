import socket
import selectors

IP = '127.0.0.1'
PORT= 5550
HEADER_LENGTH= 10
server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1) # allows us to reuse port number upon reconnection
server_socket.bind((IP, PORT))
server_socket.listen()  # socket listens for incoming connections, will become available to read from when a connection is pending
server_socket.setblocking(False)
message=[]

print(f'Listening for connections on {IP}:{PORT}...')
 
clients= {}     # create a dictionary where user socket object ids and usernames are stored. Any new user that signs up will be
                # prompted to create a username, which is then stored as { fileobj : username} 
client_messages={}                
select=selectors.DefaultSelector()
select.register(server_socket, selectors.EVENT_READ, data= None)


def receive_message(client_socket):
    try:
        message_header= client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length= int(message_header.decode('utf-8').strip())
        return{'header':message_header, 'data':client_socket.recv(message_length)}
    except:
        return False    


def new_connection(server_sockobj):

    client_conn, client_addr= server_sockobj.accept()  # conn is a new socket object usable to send and receive data, addr is the address bound to the socket on the other end of the connection.
    client_conn.setblocking(False)                     # set new socket object to be non-blocking
    username = receive_message(client_conn)            # when connecting for the first time to the socket, we will received the username only
    
    if username is False:
        print('New user has disconnected')  #this means user has disconnected before sending its data 
 
    print('Accepted new connection from {}:{}, username: {}'.format(*client_addr, username['data'].decode('utf-8')))
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
                          # save username and blank message for later
    select.register(client_conn, events, data=username)  # register the new socket object and username for monitoring
    # Find a way to handle for KeyError here, if the file object is already registered.
    clients[client_conn] = username # relate dictionary message data to client in array  
    return clients                                     

def messaging_function(key,events,clients):
    client_conn= key.fileobj
    username= key.data
    if events & selectors.EVENT_READ:
        message= receive_message(client_conn) # receive the message from the user
        
        if message is False:
            print('Closed connection from: {}'.format(username['data'].decode('utf-8')))
            select.unregister(client_conn)
            del clients[client_conn]
            client_conn.close()
            return()

        namedisplay=username['data'].decode("utf-8")
        messagedisplay=message['data'].decode("utf-8")        
        print(f'Received message from {namedisplay}: {messagedisplay}')
        for sending_socks in clients:
            if sending_socks != client_conn: 
                sending_socks.send(username['header'] + username['data'] + message['header'] + message['data'])

while True: 
    sockets_tuple= select.select(timeout=None)   # this call will return a dict  of all socket
                                                 # objects registered as well as a mask indicating whether they are read or write ready.

    
    for key, events in sockets_tuple:            # accessing each part of the dict
        if key.data is None:                     # if key has no data (username) then we have an unregistered user waiting on a server connection
            clients= new_connection(key.fileobj)
        else:
            messaging_function(key, events,clients)      # if username is present then we need to service the read or write request
 


