""" client able to handle several
thread processes send Cpu usage as well as dataroll over & heartbeat
uses threads and sockets to achieve this functionality
"""
import os
import socket
import time
import threading
import random
import string


HOST = ''   # Symbolic name meaning the local host
PORT = 12355    # Arbitrary non-privileged port
S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'
S.connect((HOST, PORT))

def is_number(number):
    """Simple function to check if string is a number"""
    try:
        int(number)
        return int(number)
    except ValueError:
        return False

TIMERAW = raw_input("What is Run Time:")
while is_number(TIMERAW) is False:
    print "Not an integer"
    TIMERAW = raw_input("What is Run Time:")
else:
    TIME = int(TIMERAW)
CHUNK_SIZERAW = raw_input("Roll Over:")
while is_number(CHUNK_SIZERAW) is False:
    print "Not an integer"
    CHUNK_SIZERAW = raw_input("Roll Over:")
else:
    CHUNK_SIZE = int(CHUNK_SIZERAW)
BYTE_SIZERAW = raw_input("Byte amount:")
while is_number(BYTE_SIZERAW) is False:
    print "Not an integer"
    BYTE_SIZERAW = raw_input("Byte amount:")
else:
    BYTE_SIZE = int(BYTE_SIZERAW)

if (TIME * BYTE_SIZE)/2 <= CHUNK_SIZE:
    print "Warning time/chunksize doesn't alllow 2 rollovers"
S.send("Smile")
ADDRES = S.recv(1024)

class HeartBeat(threading.Thread):
    """Thread that sends heartbeat signal every 5 seconds"""
    def __init__(self, name, tmaster):
        threading.Thread.__init__(self)
        self.name = name
        self.tmaster = tmaster
    def run(self):
        """Method for HeartBeat runs heartbeet method"""
        self.heartbeet()



    def heartbeet(self):
        """Method for HeartBeat sends a heartbeat to server every 5
        seconds, runs for as long as thread master is alive.
        """
        while self.tmaster.isAlive():

            time.sleep(5)

            heartbeat = ("Heartbeat from client-{0} ".format(self.name))
            S.send(heartbeat)

        S.send(", End Connection from {0}".format(ADDRES))

class DataReport(threading.Thread):
    """Thread that sends CPU usage signal every 10 seconds"""
    def __init__(self, name, tim):
        threading.Thread.__init__(self)
        self.name = name
        self.tim = tim
    def run(self):
        """Method for DataReport runs process_check method"""

        self.process_check()

    def process_check(self):
        """Method for DataReport sends a CPU usage to server every 10
        seconds, runs for as long as time specificed.
        """
        S.send("conected with {0}".format(ADDRES))
        time_start = time.time()
        time.sleep(1)

        while time.time() - time_start < self.tim:
            time.sleep(10)
            pid = os.getpid()

            tip = os.popen("ps -p {0} -o %cpu,%mem".format(pid)).read()
            S.send(str(tip))

class Writing(threading.Thread):
    """Thread that sends writes data to a file storage."""
    def __init__(self, bisize, chunksize, tmaster,):
        threading.Thread.__init__(self)
        self.bisize = bisize
        self.tmaster = tmaster
        self.chunksize = chunksize

    def run(self):
        """Method for Writing runs client1 method"""
        self.client1()

    def client1(self):
        """Method for Writing sends a dataroll over to server every
        times data rollovers over. Also writes data to a file runs
        as long as thread master is alive.
        """
        time.sleep(1)
        rstr = "".join(random.sample(string.letters, 5))
        tmpfile = "incomplete_file" + rstr + ".txt"

        text = os.urandom(self.bisize)
        size = 0
        storage_file = open(tmpfile, 'w')
        while self.tmaster.isAlive():

            time.sleep(1)

            try:
                if self.chunksize > size:
                    storage_file.write(text)
                    size += len(text)

                    rollover_message = " Data Rollover"

                else:
                    my_file = "Datastorage" + str(time.time()) + ".txt"
                    os.rename(tmpfile, my_file)
                    storage_file.close()
                    S.send(rollover_message)
                    storage_file = open(tmpfile, 'w')
                    size = 0

            except KeyboardInterrupt:
                break
        print "end connection"
        #s.close()

THREAD1 = DataReport("Client-1", TIME)
THREAD3 = Writing(BYTE_SIZE, CHUNK_SIZE, THREAD1)
THREAD2 = HeartBeat(ADDRES, THREAD1)


THREAD1.start()
THREAD2.start()
THREAD3.start()

while THREAD1.isAlive() or THREAD2.isAlive() or THREAD3.isAlive():
    time.sleep(1)
SI = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SI.connect((HOST, PORT))
SI.send("kill")# create new conn to the server and tell it they're all done

