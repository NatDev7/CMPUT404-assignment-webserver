#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    #learned about encode() from here: https://www.programiz.com/python-programming/methods/string/encode
    #learned about decode from here: https://www.tutorialspoint.com/python/string_decode.htm
    #used TA Jihoon Og's notes from page 6 and on found here: https://github.com/jihoonog/School-Notes-Public/tree/master/CMPUT-404

    def return_405(self):
        #throw a 405
        self.request.sendall("HTTP/1.1 405 Method Not Allowed\r\n\r\n".encode())

    def return_404(self):
        #throw a 404 
        self.request.sendall("HTTP/1.1 404 Not Found\r\n\r\n".encode())
    
    def return_200(self, path, fileType):
        #open and read the file if its in path
        #throw a 200 OK
        readFile = open(path, "r")
        self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Type: text/" + fileType + "\r\n\r\n" + 
        "\n".join(readFile.readlines())).encode())
        readFile.close()
    
    def return_301Redirect(self, path):
        #open the file if found, send a 200 
        if path[-1] == "/":
            readFile = open("./www/index.html", "r")
            self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + 
            "\n".join(readFile.readlines())).encode())
            readFile.close()

        #send a 301 and redirect to the correct path
        elif path[-1] != "/":
            readFile = open("./www/index.html", "r")
            self.request.sendall(("HTTP/1.1 301 Moved Permanently Location: " + 'http://localhost:8080/www/' + path + 
            "/" + "\r\nContent-Type: text/html\r\n\r\n" + "\n".join(readFile.readlines())).encode())
            readFile.close()
        
    def handle(self):
        self.data = self.request.recv(1024).decode("utf-8").strip().split()
        #print ("Got a request of: %s\n" % self.data)
        requestMethod = self.data[0]
        #set path of the file
        path = "./www/" + self.data[1][1:]
        
        #get the file type, is it .html, .css, etc..
        fileType = self.data[1][1:].split('.')[-1].strip()
        #print(fileType)
        #see what the data list looks like
        #print (self.data)
        
        #return 405 for any requestMethod that is not GET
        if requestMethod != "GET":
            self.return_405()
        
        #handle the 404 and 405 test cases
        #throw a 404 is we have no data, empty list
        if self.data == []:
            self.return_404()

        if "../" in self.data[1][1:]:
            self.return_404()
        
        #if the request method is a GET and
        #the file is in the path we open, read it, display it, return proper HTTP response
        if requestMethod == "GET":
            if os.path.isfile(path):
                self.return_200(path, fileType)
            
            #check if in the directory
            elif os.path.isdir(path):
                #redirect if "/" is not in the end of our path
                self.return_301Redirect(path)
            
            #send a 404 if we can't find the file or directory
            else:
                self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n", "utf-8"))
        
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()