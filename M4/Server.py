import socket
import os
import mimetypes
import sys
import time
import signal

# gettinf the file descriptor values of stdin and stdout
stdin  = sys.stdin.fileno() # usually 0
stdout = sys.stdout.fileno() # usually 1

class HTTPServer:
    def __init__(self, IP, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.server:
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((IP, port))
            self.server.listen()
            while True:
                client_socket, address = self.server.accept()
                print("Connected by: ", address)
                # getting the request from the client
                client_request = client_socket.recv(1024).decode('UTF-8')
                print(client_request)
                if len(client_request) > 0:
                    client_request = client_request.split(" ")[1]
                else:
                    continue
                # Check for the dynamic content request
                print(client_request)
                if client_request.startswith("/bin"):
                    # we have received a dynamic content request
                    # code, c_type, c_length, data = self.load_dynamic_content(client_request)
                    dynamic_data = self.load_dynamic_content(client_request)
                    if dynamic_data is None:
                        print("check done****")
                        continue
                    else:
                        code, c_type, c_length, data = dynamic_data
                    header = self.response_headers(code, c_type, c_length).encode()
                    client_socket.sendall(header + data.encode())
                    client_socket.close()

                    
    def load_dynamic_content(self, uri):
        """
        loads the dynamic content
        executes the executable files and sends the output
        to the browser
        """
        # print("The uri", uri)
        if uri == "/bin":
            path = uri.split("/")[1]
            path = os.getcwd() + "/scripts/"
            # display the files in the contents directory
            file_list = os.listdir(path)
            directory_data = ""
            for file_name in file_list:
                href = self.buil_href(file_name, uri)
                temp_string = "<a " + "href = " + href + ">" + file_name + "</a>"
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
            # here we have to process the executable files
            parentStdin, childStdout  = os.pipe()
            childStdin, parentStdout = os.pipe()
            command = uri.split("/")[-1]
            path = os.getcwd() + "/scripts/" + command
            newpid = os.fork()
            # if newpid == 0:
            #     # calling the child prcommandocess that
            #     # executes the command
            #     os.close(parentStdin)
            #     os.close(parentStdout)
            #     # using dup2 to redirect the output given to
            #     # the stdout to the childstdout FD
            #     os.dup2(childStdin, stdin)
            #     os.dup2(childStdout, stdout)
            #     self.execute_command(command, path)
            if newpid == 0:
                if "?" in command:
                    os.close(parentStdout)
                else:
                    os.close(parentStdin)
                os.dup2(childStdin, stdin)
                os.dup2(childStdout, stdout)
                self.execute_command(command, path)
            elif newpid > 0:
                # we are in the parent process    
                fh = open("parent.log", "w")
                if "?" in command:
                    # check the pipes
                    # os.close(childStdout)
                    os.close(childStdin)
                    os.dup2(parentStdout, stdout)
                    # getting the argument
                    argument = command.split("?")[1]
                    argument = argument.split("=")[1]
                    # sending the output to the parentstdout descriptor
                    print(argument)
                
                # check to see if we have a python file request
                if ".py" in command:
                    time.sleep(3)
                    p, s = os.waitpid(newpid, os.WNOHANG)
                    if p == 0:
                        os.kill(newpid, signal.SIGSTOP)
                        response = "Execution timed out"
                        http_response = '''
                        <!DOCTYPE html>
                            <html>
                                <head>
                                    <title> execution page </title>
                                </head>
                                <body>
                                    <h1> The output of the request is </h1>
                        ''' + response + "</body>\n</html>"
                        return 200, 'text/html', len(http_response), http_response
                os.close(childStdout)
                os.dup2(parentStdin, stdin)

                # reading the data from the parentstdin pipe
                response = os.read(parentStdin, 1024).decode()
                if response is None:
                    return None
                
                http_response = '''
                <!DOCTYPE html>
                    <html>
                        <head>
                            <title> execution page </title>
                        </head>
                        <body>
                            <h1> The output of the request is </h1>
                ''' + response + "</body>\n</html>"
                fh.write(response)
                fh.close()
                return 200, 'text/html', len(http_response), http_response
            else:
                os.dup2(stdout, stdout)
                print("something went wrong")
                sys.exit()


    
    def execute_command(self, command, path):
        """
        This executes the file
        """
        # check to see if we have any
        # arguments to the command
        fh_child = open("child.log", "w")
        if "?" in command and ".py" in command:
            file_name = path.split("/")[-1].split("?")[0]
            path = os.getcwd() + "/scripts/" + file_name
            exec(open(path).read())
        if ".py" in command:
            # call the exec
            # the output of this file is redirected to the childstdout FD
            fh_child.write("in python execution")
            args = ["/usr/bin/python3", os.getcwd() + "/scripts/" + command]
            os.execvp(args[0], args)
        elif command == "ls":
            # execute the ls command
            os.execvp("/bin/ls", sys.argv)
            # sys.stdout.flush()
        elif command == "du":
            os.execvp(os.getcwd() + "/scripts/" + command, sys.argv)
            


    def buil_href(self, file_name, uri):
        """
        builds the href for the files
        """
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
    print("abc")
    HTTPServer('127.0.0.1', 8888)

if __name__ == "__main__":
    main() 
