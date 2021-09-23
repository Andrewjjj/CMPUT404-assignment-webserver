#  coding: utf-8 
import socketserver

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
import os

class MyWebServer(socketserver.BaseRequestHandler):
    

    def handle(self):
        self.data = self.request.recv(1024).strip().decode().split("\r\n")
        self.method = self.data[0].split(" ")[0]
        self.url = self.data[0].split(" ")[1]
        self.http_version = self.data[0].split(" ")[2]
        if(self.method != "GET"):
            self.send_405()
            return
        if self.url[-1] == '/':
            self.url += "index.html"
        if self.url[-1] != '/' and len(self.url.split(".")) == 2:
            self.send_file(self.url, self.url.split('.')[1])
            return
        else:
            if(not os.path.isdir(os.getcwd()+"/www"+self.url)):
                self.send_404()
                return
            self.send_redirect(self.url+"/")
            return

    def send_file(self, file_name, extension):
        root_path = os.getcwd()+"/www"
        path = root_path + file_name
        if(os.path.isfile(path) is False):
            self.send_404()
            return
        if not path.startswith(root_path):
            self.send_404()
            return
        response = f"{self.http_version} 200 Ok Found\r\n"
        f=open(path).read()
        response += "Content-Length: " + str(len(f)) + "\r\n"
        if extension == "html":
            mimetype = "text/html"
        elif extension == "css":
            mimetype = "text/css"
        else:
            mimetype = "application/octet-stream"
        response += f"Content-Type: {mimetype}\r\n"
        response += "Connection: Closed\r\n\r\n"
        self.request.sendall(bytearray(response+f, "utf-8"))

    def send_404(self):
        response = f"{self.http_version} 404 Not Found\r\n"
        html_response = """
        <h1>404 Not Found</h1>
        """
        response += "Content-Length: " + str(len(html_response)) + "\r\n"
        response += "Content-Type: text/html\r\n"
        response += "Connection: Closed\r\n\r\n"
        self.request.sendall(bytearray(response+html_response, "utf-8"))
        
    def send_405(self):
        response = f"{self.http_version} 405 Method Not Allowed\r\n"
        html_response = """
        <h1>405 Method Not Allowed</h1>
        """
        response += "Content-Length: " + str(len(html_response)) + "\r\n"
        response += "Content-Type: text/html\r\n"
        response += "Connection: Closed\r\n\r\n"
        self.request.sendall(bytearray(response+html_response, "utf-8"))
        
    def send_redirect(self, new_location):
        response = f"{self.http_version} 301 Moved Permanantly\r\n"
        response += f"Location: http://127.0.0.1:8080{new_location}\r\n"
        html_response = f"""
        <h1>301 Moved Permanantly</h1>
        <a href="http://127.0.0.1:8080{new_location}">Moved Here</a>
        """
        self.request.sendall(bytearray(response+html_response, "utf-8"))
    

    def send_response(self):
        response = f"{self.http_version} {self.status_code} {self.status_message}\r\n"
        self.request.sendall(bytearray(response, "utf-8"))
    

if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
