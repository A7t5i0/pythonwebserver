from concurrent.futures import thread
from posixpath import split
from re import I
import socket
import threading
from signal import signal, SIGPIPE, SIG_DFL
from datetime import datetime
from pathlib import Path
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert.pem', 'key.pem', password=None)


PORT = 5000

# SERVER = socket.gethostbyname(socket.gethostname())
SERVER = "192.168.1.166"
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
server.bind(ADDR)
# server = context.wrap_socket(server, server_side=True)

def readLine(buf, conn):
    while True:
        req = conn.recv(1).decode('utf-8')
        buf += req
        if "\n" in buf:
            url = buf.split(" ")[1]
            print("filename:\n" + url)
            break   
    print(buf)
    return buf

def readAll(buf, conn):
    while True:
        buf = readLine(buf, conn)
        if "\r\n\r\n" in buf:
            break
    
    return buf

def socketToFile(conn, buf):
    while True:
        req = conn.recv(1).decode('utf-8')
        buf += req
        if "\r\n\r\n" in buf:
            break

def getContentType(filename):
    contentType = "Content-Type: text/html; charset=UTF-8\r\n"
    if "." in filename:
        if ".js" in filename:
            contentType = "Content-Type: application/javascript; charset=UTF-8\r\n"
        elif ".png" in filename:
            contentType = "Content-Type: image/png; charset=UTF-8\r\n"
        elif ".jpg" in filename:
            contentType = "Content-Type: image/jpg; charset=UTF-8\r\n"
        elif ".jpeg" in filename:
            contentType = "Content-Type: image/jpeg; charset=UTF-8\r\n"
        elif ".mp4" in filename:
            contentType = "Content-Type: video/mp4; charset=UTF-8\r\n"
        else:
            contentType = "Content-Type: text/html; charset=UTF-8\r\n"
        
    return contentType

def writeFile(conn, filename):
    filesize = Path(filename).stat().st_size
    loops = filesize / 8192
    filesize = str(filesize)
    print(filesize)
    date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    contentType = getContentType(filename)
    headers = "HTTP/1.1 200 OK\r\nDate: " + str(date) + " GMT\r\nServer: GNU/linux\r\nLast-Modified: Tue, 8 Mar 2022 15:53:59 GMT\r\n" + contentType + "Content-Length: " + filesize + "\r\nConnection: Close\r\n\r\n"
    conn.send(bytes(headers, 'utf-8'))
    f = open(filename, "rb")
    
    while True:
        bytesRead = f.read(8192)
        conn.send(bytesRead)
        print(loops)
        if loops < 1:
            break
        loops -= 1
    print("made it outside loop")
    # thread.stop()

def uploadFile(conn, filename):
    f = open(filename, "wb")
    firstRead = conn.recv(1)#.decode('utf-8')
    f.write(firstRead)
    while True:
        bytesRead = conn.recv(1)#.decode('utf-8')
        f.write(bytesRead)
        if bytesRead < firstRead:
            break
    # thread.stop()

def handle_client(conn, addr):
    buf = ''
    buf2 = ''
    method = ""
    url = ""
    
    while True:
        req = conn.recv(256).decode('utf-8')
        buf += req
        if "\r\n\r\n" in buf:
            # print(buf)
            if "GET" in buf:
                method = "GET"
                # print("method:\n" + method)
            elif "POST" in buf:
                method = "POST"
                # print("method:\n" + method)
            break
    url = buf.split(" ")[1]
    # print("url:\n" + url)
    if method == "GET":
        if url == "/":
            filename = "index.html"
            writeFile(conn, filename)
        else:
            filename = url[1:]
            filename2 = filename + ".html"
            # print(filename2)
            if Path(filename).is_file():
                writeFile(conn, filename)
            elif Path(filename2).is_file():
                writeFile(conn, filename2)
            else:
                writeFile(conn, "404.html")
    elif method == "POST":
        while True:
            req2 = conn.recv(1).decode('utf-8')
            buf2 += req2
            if "\r\n\r\n" in buf2:
                # print(buf2)
                break
        req2Params = buf2.split("\n")
        # for i in req2Params:
            # print("this is i:\n" + i)

        req2Params2 = req2Params[1].split(" ")
        filename = req2Params2[3].split('"')
        filename = filename[1]
        print(filename)
        uploadFile(conn, filename)
        

def start():
    # signal(SIGPIPE, SIG_DFL)
    server.listen()
    ssock = context.wrap_socket(server, server_side=True)
    while True:
        conn, addr = ssock.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

print("server starting")
start()