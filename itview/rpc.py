import json
import os
import socket
import struct
import sys
import threading
import traceback
try:
    from PySide2 import QtCore, QtWidgets
except:
    from PySide6 import QtCore, QtWidgets


MESSAGE_TYPE_RPC = b"RPC" # remote procedure call (non-blocking calls)
MESSAGE_TYPE_RFC = b"RFC" # remote function call (blocking calls)
MESSAGE_TYPE_RES = b"RES" # result of the remote function call
MESSAGE_TYPE_EXC = b"EXC" # exception raised within the remote function call

def message_color(sending, type):
    if sending:
        return "\033[97m"
    elif type == MESSAGE_TYPE_EXC:
        return "\033[91m"
    elif type == MESSAGE_TYPE_RES:
        return "\033[92m"
    return "\033[94m"


class RpcEvent(QtCore.QEvent):
    __event_type = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, type, data):
        super().__init__(self.__event_type)
        self.type = type
        self.data = data


class Rpc(QtCore.QObject):

    def __init__(self, entry_point, server_port=None, port=None, use_rpc=False, debug=False):
        super().__init__()
        self.__entry_point = entry_point
        self.__port = port
        server_port = 0 if server_port is None else server_port
        self.__defaul_call = self.__rpc if use_rpc else self.__rfc
        self.__debug = debug
        self.__running = False
        self.__server_socket = None
        self.__client_socket = None
        self.__thread = threading.Thread(target=self.__thread)
        self.__event = threading.Event()
        self.__response = None
        self.__qapp = QtWidgets.QApplication.instance()

        if self.is_server:
            self.__server_socket = socket.socket()
            self.__server_socket.bind(("", server_port))
            self.__server_socket.listen()

    def __del__(self):
        self.stop()

    @property
    def port(self):
        return self.__server_socket.getsockname()[1] if self.is_server else self.__port

    @property
    def is_server(self):
        return self.__port is None

    def start(self):
        if self.__running:
            return
        self.__running = True
        if self.is_server:
            if self.__debug:
                print("Server Started", self.port)
            self.__client_socket, _ = self.__server_socket.accept()
        else:
            if self.__debug:
                print("Client Started", self.port)
            self.__client_socket = socket.socket()
            self.__client_socket.connect(("localhost", self.__port))
        self.__thread.start()

    def stop(self):
        if not self.__running:
            return

        self.__client_socket.shutdown(socket.SHUT_RDWR)
        self.__client_socket.close()
        self.__thread.join()
        if self.is_server:
            self.__server_socket.close()
        self.__running = False

    def __thread(self):
        while True:
            try:
                type, data = self.__recvmsg()
                if not data:
                    break
                if type in (MESSAGE_TYPE_RPC, MESSAGE_TYPE_RFC):
                    self.__qapp.postEvent(self, RpcEvent(type, data))
                elif type in (MESSAGE_TYPE_RES, MESSAGE_TYPE_EXC):
                    self.__response = (type, data)
                    self.__event.set()
            except Exception as e:
                print(str(e), file=sys.stderr)
                break

    def __recvall(self, size):
        data = bytearray()
        while len(data) < size:
            part = self.__client_socket.recv(size - len(data))
            if not part:
                break
            data.extend(part)
        return bytes(data)

    def __recvmsg(self):
        data = self.__recvall(7)
        if not data:
            return None, None
        size, type = struct.unpack("!I3s", data)
        data = self.__recvall(size)
        if not data:
            return None, None
        if self.__debug:
            os.write(1, bytes(f"{message_color(False, type)}RECV {str(type, 'utf-8')}: {str(data, 'utf-8')}\033[0m\n", "utf-8"))
        return type, data

    def __sendmsg(self, type, data):
        if self.__debug:
            os.write(1, bytes(f"{message_color(True, type)}SEND {str(type, 'utf-8')}: {str(data, 'utf-8')}\033[0m\n", "utf-8"))
        message = bytearray()
        message.extend(struct.pack("!I3s", len(data), type))
        message.extend(data)
        self.__client_socket.sendall(bytes(message))

    def send_result(self, res):
        self.__sendmsg(MESSAGE_TYPE_RES, bytes(json.dumps(res), "utf-8"))

    def customEvent(self, event):
        if isinstance(event, RpcEvent):
            self.__process_call(event.type, event.data)

    def __process_call(self, type, data):
        try:
            res = self.__entry_point
            for item in json.loads(data):
                if isinstance(item, str):
                    res = getattr(res, item)
                else:
                    args, kwargs = item
                    if args and kwargs:
                        res = res(*args, **kwargs)
                    elif args:
                        res = res(*args)
                    elif kwargs:
                        res = res(**kwargs)
                    else:
                        res = res()
            if type == MESSAGE_TYPE_RFC:
                self.__sendmsg(MESSAGE_TYPE_RES, bytes(json.dumps(res), "utf-8"))
        except Exception as e:
            if type == MESSAGE_TYPE_RFC:
                self.__sendmsg(MESSAGE_TYPE_EXC,
                    bytes("Remote procedure call raised an exception\nRemote " + traceback.format_exc().strip(), "utf-8"))

    def __rpc(self, data):
        self.__sendmsg(MESSAGE_TYPE_RPC, data)

    @property
    def rpc(self):
        return Call(self.__rpc)

    def __rfc(self, data):
        self.__event.clear()
        self.__sendmsg(MESSAGE_TYPE_RFC, data)
        self.__event.wait()
        type, data = self.__response
        if type == MESSAGE_TYPE_EXC:
            raise RuntimeError(str(data, "utf-8"))
        return json.loads(data)

    @property
    def rfc(self):
        return Call(self.__rfc)

    def __getattr__(self, attr):
        return Call(self.__defaul_call, data=[attr])


class Call:

    def __init__(self, call, data=None):
        self.__call = call
        self.__data = [] if data is None else data

    def __getattr__(self, attr):
        self.__data.append(attr)
        return self

    def __call__(self, *args, **kwargs):
        self.__data.append([args, kwargs])
        return self.__call(bytes(json.dumps(self.__data), "utf-8"))


def get_available_ports(num_of_ports):
    temp_sockets = []
    ports = []
    for _ in range(num_of_ports):
        s = socket.socket()
        s.bind(("", 0))
        ports.append(s.getsockname()[1])
        temp_sockets.append(s)

    for s in temp_sockets:
        s.close()
    return ports