import socket 
import sys               
import os.path
import os
import threading
from os import path

document_root = "./www"

def bind_ip(ip,port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	print ("Socket successfully created")
	sock.bind((ip,port))         
	print ("socket binded to %s" %(port))
	return sock   

def start_server(sock):
	sock.listen(5)      
	print ("socket is listening")            

	while True: 
		c, addr = sock.accept()
		print ('Got connection from', addr)
		t1 = threading.Thread(target = handle_request(c)) 
		t1.start()
		#os.fork()
		#handle_request(c)
		

def handle_request(c):
	http_request = c.recv(1024).decode()
	http_response = process_request(http_request)
	c.sendall(http_response) 
	c.close() 

def process_request(http_request):
	uri = http_request.split(" ")
	uri = uri[1]
	print(uri)   
	if(uri.find("favicon")!=-1):
		return "".encode()
	if(uri=="/"):
		content = directory_listing(document_root,uri)
		content_type = "text/html"
		http_response = prepare_response("200","OK",content_type,content.encode())
		return http_response
   
	if(path.isdir(document_root+uri) ):
		content = directory_listing(document_root+uri,uri)
		content_type = "text/html"
		http_response = prepare_response("200","OK",content_type,content.encode())
		return http_response
	if "/bin/" in uri:
		print(uri)
		ans = parent_child(uri)
		content_type = "text/html"
		http_response = prepare_response("200","OK",content_type,ans.encode())
		return http_response
	if (uri.find("scripts")!=-1):
		print(uri)
		ans = parent1child(uri)
		content_type = "text/html"
		http_response = prepare_response("200","OK",content_type,ans.encode())
		return http_response
	if(path.isfile("./www"+uri)):
		f = open("./www"+uri, "rb")
		content = f.read()
		f.close()
		content_type = "text/html"
		if(uri.find(".png") != -1):
			content_type = "image/png"
		if(uri.find(".gif") != -1):
			content_type = "image/gif"
		http_response = prepare_response("200","OK",content_type,content)
		return http_response
   
	http_response = prepare_response("404","Not Found","text/html","<h1>File Not Found</h1>".encode())
	return http_response


def prepare_response(code, message, content_type, content):
	http_response = "HTTP/1.1 "+code+" "+message+"\r\n"
	http_response = http_response+"Content-Type:"+content_type+"\r\n"
	http_response = http_response+"Content-Length:"+str(len(content))+"\r\n\r\n"
	http_response = http_response.encode()+content
	return http_response

def directory_listing(dir_path,uri):
	listOfFiles = os.listdir(dir_path)
	if(uri == "/"):
		uri = ""
	resp = "<html><body>"
	str = uri.split("/")
	str.pop()
	u = "/"
	if(len(str) == 1 and str[0] == ""):
		u = "/"
	else:
		u = u.join(str)
	resp = resp+"<a href='"+u+"' >parent</a></br>"
	for entry in listOfFiles:
		resp = resp+"<a href='"+uri+"/"+entry +"'>"+entry+"</a></br>"
	return resp+"</body></html>"

def parent_child(uri):
	uri = "." + uri
	stdin  = sys.stdin.fileno() # usually 0
	stdout = sys.stdout.fileno() # usually 1
	r, w = os.pipe()
	r1, w1 = os.pipe()
	n = os.fork()
	if n > 0: 
		os.close(w1)
		w = os.fdopen(w,'w')		
		w.write(uri)
		w.close()
 
		os.dup2(r1, stdin)
		r1 = os.fdopen(r1,'r')
		out = r1.read()
		out.replace("/n","<br/>")
		r1.close()
		
		return out

	else:
		os.close(w)
		r = os.fdopen(r,'r') 
		file_path = r.read()
		file_path = file_path.split(" ")
		r.close()

		os.dup2(w1, stdout)
		w1 = os.fdopen(stdout,'w')
		os.execvp(file_path[0],file_path)

def parent1child(uri):
	uri = "www" + uri
	stdin  = sys.stdin.fileno() # usually 0
	stdout = sys.stdout.fileno() # usually 1
	r, w = os.pipe()
	r1, w1 = os.pipe()
	n = os.fork()
	if n > 0: 
		os.close(w1)
		w = os.fdopen(w,'w')		
		w.write(uri)
		w.close()
 
		os.dup2(r1, stdin)
		r1 = os.fdopen(r1,'r')
		out1 = r1.read()
		r1.close()
		
		return out1

	else:
		os.close(w)
		r = os.fdopen(r,'r') 
		filepath = r.read()
		r.close()

		os.dup2(w1, stdout)
		w1 = os.fdopen(stdout,'w')
		exec(open(filepath).read())


sock = bind_ip("",8888)
start_server(sock)
