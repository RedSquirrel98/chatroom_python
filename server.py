import socket
import select

IP = '127.0.0.1
PORT= 5550

HEADER_LENGTH= 10
server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1) # allows us to reuse port number upon reconnection
server_socket.bind((IP, PORT))
server_socket.listen()  # socket listens for incoming connections, will become available to read from when a connection is pending

 
sockets_list=[server_socket] # create a blank list of active sockets
clients= {}

print(f'Listening for connections on {IP}:{PORT}...')

def receive_message(client_socket):
    try:
        message_header= client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length= int(message_header.decode('utf-8').strip())
        return{'header':message_header, 'data':client_socket.recv(message_length)}
    except:
        return False    

while True:
    

    # The first is a list of the objects to be checked for incoming data to be read, the second contains objects
    #  that will receive outgoing data when there is room in their buffer, and the third list of those that may have an error 
    read_sockets,_,exception_sockets= select.select(sockets_list,[],sockets_list)  # SELECT method interfaces with the operating system functions to poll a list of available sockets
     
    for notified_socket in read_sockets:
                 
         # A "readable" server socket is ready to accept a connection
        if notified_socket == server_socket:  
            client_conn, client_addr= server_socket.accept()  # conn is a new socket object usable to send and receive data, addr is the address bound to the socket on the other end of the connection.
            user = receive_message(client_conn)                                                               
            
            # !!! this is a very poor way to receive messages: instead, check if client sockets have become readable and place them into a queue. 
            # here we are assuming that while connecting the client will send its username
            if user is False:  #this means user has disconnected before sending its data
            
                pass 
            sockets_list.append(client_conn) # add the client socket object to the current list of active sockets      
            clients[client_conn] = user # relate dictionary message data to client in array   
            print('Accepted new connection from {}:{}, username: {}'.format(*client_addr, user['data'].decode('utf-8'))) 
        
        # !!! again, this is a very poor way to receive messages: instead, check if client sockets have become readable and place them into a queue. 
        # if one of the already established socket client connections is readable, this means it is ready to send data
        else:

            message= receive_message(notified_socket) # pass the message into a reading queue later on
            if message is False:
                 
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                 
                sockets_list.remove(notified_socket)
                 
                del clients[notified_socket] #remove the client socket from the dictionary if it has disconnected
                 
                continue

            user = clients[notified_socket]
            namedisplay=user['data'].decode("utf-8")
            messagedisplay=message['data'].decode("utf-8")
            print(f'Received message from {namedisplay}: {messagedisplay}')
           


            for client_conn in clients:
                if client_conn != notified_socket: 
                    
                        
                    client_conn.send(user['header'] + user['data'] + message['header'] + message['data'])
    
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

         # Remove from our list of users
        del clients[notified_socket]                 



                
