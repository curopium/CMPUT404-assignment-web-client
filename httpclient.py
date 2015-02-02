#!/usr/bin/env python
# coding: utf-8
# Copyright 2015 Thomas Curnow
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
# used for getting the host from a url
from urlparse import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        #if there is no port, make it 80
        if(port == None):
            port = 80
        #tries to create socket
        try:
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        except socket.error as msg:
            print("failed to create socket")
            print('Error code: ' + str(msg[0]) + ' , Error message: ' + msg[1])
            sys.exit()

        s.connect((host, port))
        return s

    def get_code(self, data):
        header = self.get_headers(data)
        code = header.split(' ')[1]
        return code

    def get_headers(self,data):
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        code = 500
        body = ""

        url = urlparse(url)
        host = url.hostname
        directory = url.path
    
        if(directory == ''):
            directory = '/'
        
        header = 'GET ' + directory + ' HTTP/1.1\r\n'
        header = header + 'Host: ' + host + '\r\n'
        header = header + 'Accept: */*\r\n'
        header = header + 'Connection: close\r\n'
        header = header + '\r\n'
         
        sock = self.connect(host, url.port)
        sock.send(header)
        sock_return = self.recvall(sock)

        code = int(self.get_code(sock_return))
        body = self.get_body(sock_return)

        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        url = urlparse(url)
        host = url.hostname
        directory = url.path
        if(directory == ''):
            directory = '/'
        
        if(args == None):
            content_length = 0;
        else:
            send_body = urllib.urlencode(args)
            content_length = len(send_body)            

        #Create the header to be sent to socket
        header = 'POST '+directory+' HTTP/1.1\r\n'
        header = header + 'Host: ' + host +'\r\n'
        header = header + 'Accept: */*\r\n'
        header = header + 'Content-Length: ' + str(content_length) + '\r\n'
        header = header + 'Content-Type:application/x-www-form-urlencoded \r\n'
        header = header + 'Connection: close\r\n'
        header = header + '\r\n'

        #add the body only if there is a body
        if(content_length > 0):
            header = header + send_body
            header = header + '\r\n\r\n'

        sock = self.connect(host, url.port)
        sock.send(header)
        sock_return = self.recvall(sock)

        code = int(self.get_code(sock_return))
        body = self.get_body(sock_return)
        
        return HTTPRequest(code, body)

    #def command(self, url, command="GET", args=None):
    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"

    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )    
        
