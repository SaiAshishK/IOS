'''
    Disclaimer
    tiny httpd is a web server program for instructional purposes only
    It is not intended to be used as a production quality web server
    as it does not fully in compliance with the 
    HTTP RFC https://tools.ietf.org/html/rfc2616

    This task is designed by Praveen Garimella and is to be used
    as part of the Learning by Doing, Project Based Course on Operating Systems
    Write to pg@fju.us for any questions or comments
'''

'''
    == Task 2 ==
    This file has the solution for M1 and the description for M2.
    Review this solution before you start implementing the M2.
    If you don't like our solution for M1 then
    tell us why so that we can improve it.

    In the M2 you have to write code to handle http requests for static content.
    Web servers maintain static content in a directory called document root.
    We have provided you with a directory with the name www.
    This directory has some html files and images.
    A web server may receive a request to access one of these files.

    When such a request is received you have to parse the HTTP request
    and extract the name of the file in the request aka Uniform Resourse Indicator    
    Learn the format of the http requests from the tutorial given below.
    https://www.tutorialspoint.com/http/http_requests.htm

    After extracting the URI,
    check if the file exists in the document root directory i.e., www

    If it exists, you have to read the file contents as the response data.
    If not you have to send a 404 file not found response.

    Construct the http response by invoking response_headers method
    This method is provided in the HTTPServer class
    Passing the appropriate response code, content type and length to the method
    
    A tricky part to the response construction is to identify the content type.
    Set the content type text/html for files that end with the extension .html
    
    What would be the content type for images? Review the link below.
    https://www.iana.org/assignments/media-types/media-types.xhtml#image

    How do we figure out the content subtype of an image?
    Explore the use of the library mimetype in python.
    https://www.tutorialspoint.com/How-to-find-the-mime-type-of-a-file-in-Python
'''

import socket
import os
import base64

class HTTPServer:
    def __init__(self, IP, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as self.s:
            self.s.bind((IP, port))
            self.s.listen()
            while True:
                conn, addr = self.s.accept()
                with conn:
                    print('Connected by', addr)
                    # TODO read the request and extract the URI
                    client_request = conn.recv(1024)
                    # check to see if the client request is empty
                    if len(client_request) == 0:
                        continue
                    client_request = client_request.decode('utf-8')
                    request_uri = client_request.split("/")[1].split()[0] 
                    # TODO update the parameter with the request URI
                    uri = request_uri
                    code, c_type, c_length, data = self.get_data(uri)
                    header = self.response_headers(code, c_type, c_length).encode()
                    if c_type == "image/png" or c_type == "image/gif":
                        conn.sendall(header + data)
                    else:
                        conn.sendall(header + data.encode())
                    conn.close()
    

    def get_data(self, uri):
        '''
            TODO: This function has to be updated for M2
        '''
        # check to see of there is not uri
        if "." not in uri:
            data = "<h1>Webserver Under construction</h1>"
            return (200, "text/html", len(data), data)

        # path_data = "/home/kalorirohit/Desktop/IOS/Sockets/Tiny Web Server/tws-m2/tws-m2/www/" + uri
        path_data = "./www/" + uri
        # check to see of the path exists
        if os.path.exists(path_data):

            # open the file requested and send it as a response
            if uri == "index.html":
                with open(path_data, "r", encoding="utf-8", errors='ignore') as f:
                    html_text = f.read()
                return (200, "text/html", len(html_text), html_text)

            elif uri == "second.html":
                with open(path_data, "r") as f:
                    html_text = f.read()
                return(200, "text/html", len(html_text), html_text)

            elif uri == "one.png":
                image_file = open(path_data, 'rb')
                data = image_file.read()
                image_file.close()
                return (200, "image/png", len(data), data)
            
            elif uri == "po.gif":
                gif_file = open(path_data, 'rb')
                data = gif_file.read()
                gif_file.close()
                return (200, "image/gif", len(data), data)

            else:
                data = "<h1>Webserver Under construction</h1>"
                return (200, "text/html", len(data), data)
        else:
            data = "<h1>File Not Found</h1>"
            return (404, "text/html", len(data), data)

    
    def response_headers(self, status_code, content_type, length):
        line = "\n"
        
        # TODO update this dictionary for 404 status codes
        response_code = {200: "200 OK", 404: "404 Not Found"}
        
        headers = ""
        headers += "HTTP/1.1 " + response_code[status_code] + line
        headers += "Content-Type: " + content_type + line
        headers += "Content-Length: " + str(length) + line
        headers += "Connection: close" + line
        headers += line
        return headers

def main():
    # test harness checks for your web server on the localhost and on port 8888
    # do not change the host and port
    # you can change  the HTTPServer object if you are not following OOP
    HTTPServer('127.0.0.1', 8888)

if __name__ == "__main__":
    main()                   