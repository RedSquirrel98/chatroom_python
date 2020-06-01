# import socket

# HEADERSIZE = 10 
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((socket.gethostname(),1236)) #connect to the server (in this case on the same machine)



# full_msg= ''   # set a received message buffer that will accumulate the full message length
# new_msg=True   # set bool to true, indicating we are receiving a new 
#                # message (only do once at the beginning of socket communication being established, and reset the bool within the loop later on)
 
# while True:   # run this in an infinite loop for now: we will terminate sockets later
#     msg=s.recv(16)  # receive 16 bytes at once, which is larger than the blank buffer (HEADER) size 
#     if new_msg:    
#         print(f"new message length: {msg[:HEADERSIZE]}") #print the message length by displaying the blank buffer (HEADER) appended to the start of msg (first x characters will give msg length)
#         msglen= int(msg[:HEADERSIZE]) # convert the length of the message from a 10 element buffer into an int (delete all the extra buffer spaces that are not used)
#         new_msg= False                # set to false so that we concatenate parts of message until it is fully recvd
#     full_msg+=msg.decode("utf-8")     # decode utf-8 formatted message and concatenate into string

#     if len(full_msg)-HEADERSIZE == msglen:  # if we have received the full message, execute the following:
#         print(full_msg[HEADERSIZE:])        # display message
#         new_msg= True                       # get ready to accept new message
#         full_msg= ''                        # re-intialize blank reception buffer
     
import socket
import select
import errno   
import sys

HEADERLENGTH=10
IP = '127.0.0.1'
PORT=5550


# create a username:

my_username = input("Username: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((IP, PORT)) #connect to the server (in this case on the same machine)
client_socket.setblocking(False)  # make the socket non-blocking, so that methods don't stall the program

username= my_username.encode("utf-8")
username_header= f'{len(username):< {HEADERLENGTH }}'.encode("utf-8")
client_socket.send(username_header + username)


while True:
    message = input(f'{my_username}>')
    if message:
        message = message.encode("utf-8")
        message_header=f"{len(message):<{HEADERLENGTH}}".encode("utf-8")
        client_socket.send(message_header + message) #does it make sense to send the full message at once?
    
    try:
        while True:
            username_header = client_socket.recv(HEADERLENGTH)
            if not len(username_header):
                print('Connection closed by server')
                sys.exit
                               
# this may be a piss poor way of receiving username and message all jumbled up together
            username_length= int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            message_header = client_socket.recv(HEADERLENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            # Print message
            print(f'{username} > {message}')

    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        continue

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error:{}'.format(str(e)))
        sys.exit()
