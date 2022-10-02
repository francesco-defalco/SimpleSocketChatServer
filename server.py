import socket
import concurrent.futures
import logging

logging.getLogger().setLevel(logging.DEBUG)


'''
In this file, we will create a server that will handle multiple clients at the same time.
Setting statically the PORT without reading it from the command line or configuration file.
'''
try:
    PORT = 10000
    IP = socket.gethostbyname(socket.gethostname())
except Exception as e:
    logging.error('Error: {}'.format(e))
    exit(1)
'''
Simple chat server that receive messages from clients and send them to all the other clients.
'''
class Server():
    '''
    1) Constructor of the class Server
    2) port: port number of the server
    3) ip: ip address of the server
    4) number_of_threads: number of threads to handle the clients
    5) server_socket: socket of the server
    6) connections_list: list of the connections
    7) executor: executor to handle the threads
    8) size: size of the message
    9) format: format of the message
    '''
    def __init__(self, port, ip, number_of_threads):
        logging.debug("__init__")
        self.port = port
        self.ip = ip
        self.number_of_threads = number_of_threads
        self.server_socket = None
        self.connections_list = []
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.number_of_threads)
        self.size = 1024
        self.format = "utf-8"
        logging.debug("__init__ finished")
    
    # Wait for the client message
    def wait_client_message(self, conn, addr):
        logging.debug("wait_client_message")
        logging.info("Address {} connected.".format(addr))
        print(self.connections_list)

        while True:
            message = conn.recv(1024).decode(self.format)
            logging.debug("Message received: {}".format(message))
            # If the message is empty, we continue
            if not message:
                break
            # If the message is empty, we continue
            if message and message == "":
                continue
            # If the message is QUIT, the client is disconnected
            elif message == "QUIT\r\n":
                for connection in self.connections_list:
                    if connection == conn:
                        logging.debug("Closing connection {}".format(connection))
                        conn.close()
                        self.connections_list.remove(connection)
                break
            
            message = "Message to Chat: {}".format(message)
            # Send the message to all the clients
            self.send_message_to_clients(message, conn)
            
            logging.debug("Message sent to clients: {}".format(message))
        logging.debug("wait_client_message finished")
    
    def send_message_to_clients(self, message, conn):
        logging.debug("send_message_to_clients")
        
        if not self.connections_list:
            logging.debug("No clients connected")
            return
        
        for connection in self.connections_list:
            # If the connection is the same of the client that sent the message, we continue
            if connection != conn:
                try:
                    logging.info("Sending message to {}".format(connection))
                    connection.send(message.encode(self.format))
                except:
                    # If the connection is closed, we remove it from the list or if the message is empty, we continue
                    connection.close()
                    # if the link is broken, we remove the client
                    self.connections_list.remove(connection)
                    logging.error("Connection {} closed".format(connection))
        logging.debug("send_message_to_clients finished")

    def start_server(self):
        logging.debug("start_server")
        print("Server is starting...")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(10)
        
        logging.info("Server is listening on {}:{}".format(self.ip, self.port))
        while True:
            try:
                conn, addr = self.server_socket.accept()
                if not conn or not addr:
                    continue
                
                # Add the connection to the list
                self.connections_list.append(conn)
                logging.debug("Connection {} added to connections_list".format(conn))
                
                # Start a thread to handle the client
                self.executor.submit(self.wait_client_message, conn, addr)
                logging.debug("Thread started")
            except Exception as e:
                logging.error(e)
                break
        logging.debug("start_server finished")

if __name__ == '__main__':
    server = Server(PORT, IP, 5)
    logging.info("Server created")
    server.start_server()
