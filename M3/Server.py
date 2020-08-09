import socket
import os
import mimetypes

class HTTPServer:
    def __init__(self, IP, port):
        # setting up the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.server:
            self.server.bind((IP, port))
            self.server.listen()
            while True:
                client_socket, address = self.server.accept()
                with client_socket:
                    print("connected by: ", address)
                    # getting the request
                    client_request = client_socket.recv(1024)
                    if len(client_request) == 0:
                        continue
                    client_request = client_request.decode('UTF-8').split(" ")[1]
                    # code, c_type, c_length, data = self.directory_browsing(client_request)
                    code, c_type, c_length, data = self.browsing(client_request)
                    header = self.response_headers(code, c_type, c_length).encode()
                    if c_type == "image/png" or c_type == "image/gif":
                        client_socket.sendall(header + data)
                    else: 
                        client_socket.sendall(header + data.encode())
                    client_socket.close()


    def browsing(self, uri):
        path = os.getcwd() + uri
        print(path)
        if os.path.isdir(path):
            file_list = os.listdir(path)
            directory_data = ""
            for ele in file_list:
                href = self.build_href(path, ele, uri)
                temp_string = "<a " + "href = " + href + ">" + ele + "</a>"
                directory_data += temp_string
                directory_data += "<br/>"
            http_response = '''
            <!DOCTYPE html>
                <html>
                <head>
                    <title>Home page</title>
                </head>
                <body>
                <h1>The list of the file present in the root directory</h1>
            ''' + directory_data + "</body>\n</html>"
            return 200, 'text/html', len(http_response), http_response
        else:
            # getting the mimetypepath
            mime_data = mimetypes.guess_type(uri)
            # check to see if it's a html file
            if mime_data[0] == 'text/html':
                with open(path, "r") as f:
                    html_text = f.read()
                    print(html_text)
                    return 200, mime_data[0], len(html_text), html_text
            else:
                with open(path, "rb") as f:
                    data = f.read()
                    return 200, mime_data[0], len(data), data
            

    def build_href(self, path, file_name, uri):
        """
        This method builds the href attributes
        for the files passed as the parameter
        """
        if uri == "/":
            return uri + file_name
        else:
            return uri + "/" + file_name
        

    def response_headers(self, status_code, content_type, length):
        """
        This method creates the response headers
        for the http response
        """
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
