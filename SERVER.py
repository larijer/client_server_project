""" Server able to handle several
clients and record there Cpu usage as well as dataroll over & heartbeat
uses threads and sockets to achieve this functionality
"""

import select
import socket
import sys
import threading
import time
import os


class Server(object):
    """Server docstring"""
    def __init__(self):
        self.host = ''
        self.port = 12355
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []
        self.kill_message = []
    def open_socket(self):
        """Server class, method used to listen for connections"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            print 'Socket bind complete'
            print "\nListening for incoming connections..."
        except socket.error, (message):
            if self.server:
                self.server.close()

            print "Could not open socket: " + message
            sys.exit(1)

    def run(self):
        """Servers class, method used to connect and start threads"""
        self.open_socket()
        inp = [self.server, sys.stdin]
        start_time =  time.time()
        running = 1
        count_of_clients = 10

        while running:
            inputready, outputready, exceptready = select.select(inp, [], [])

            for i in inputready:

                if i == self.server:
                    # handle the server socket
                    clie = Client(self.server.accept(), self.port)
                    if clie.client.recv(self.size) == "kill":

                        self.kill_message.append(clie)
                        if len(self.kill_message) == count_of_clients:
                            running = 0
                    else:
                        print ('Connected with {0}: {1}'
                            .format(clie.address[0], str(clie.address[1])))
                        clie.start()
                        self.threads.append(clie)
                        count_of_clients = len(self.threads)
                elif i == sys.stdin:
                    # handle standard input
                    sys.stdin.readline()
                    running = 0

        # close all threads

        self.server.close()
        for i in self.threads:
            i.join()
        pidd = os.getpid()
        computer_usage = os.popen("ps -p {0} -o %cpu,%mem".format(pidd)).read()
        print "Number of Connections: " + str(count_of_clients)
        print  "Server connection time: {0} Seconds".format(int(time.time() - start_time))
        print computer_usage

class Client(threading.Thread):
    """Thread class called Client, used in handling multiple socket
    connections and writing several files.
    """

    def __init__(self, (client, address), port):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        self.port = port

    def run(self):
        """Method of thread to accept data and process through
        logfile function.
        """
        self.client.send(str(self.address[1]))
        address_id = str(self.address[1])
        data = "dummy data"

        while data:
            data = self.client.recv(self.size)
            if is_number(data) == False:
                logfile(data, address_id)


def is_number(number):
    """Simple function to check if string is a number"""
    try:
        float(number)
        return float(number)
    except ValueError:
        return False
def logfile(data, addr):
    """This function is used in threads to write performance
    stats & heartbeats to separate files. It relys on the
    presence of CPU to distinguish which file which type of input
    goes to.
    """
    if "%CPU" in str(data):
        filename = "performance_database" + addr + ".txt"
        with open(filename, "a") as myfile:
            myfile.write(str(data) + ",")
    else:
        filename1 = "logfile" + addr + ".txt"
        with open(filename1, "a") as myfil:
            myfil.write(str(data) + ",")



if __name__ == "__main__":
    S = Server()
    S.run()




