# Nikari - Communication Classes
#
# Written by Martianmellow12

# General
import asyncio
import json
import socket

# Nikari
from ..nikari_logging import log


###################
# Comm Base Class #
###################

class __CommBase__:

    ##################
    # Helper Methods #
    ##################

    def get_ip_addr(self):
        # Return the interface that routes to the internet
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    
    def get_broadcast_addr(self, ip_addr, subnet_mask="255.255.255.0"):
        subnet_mask_list = [int(i) for i in subnet_mask.split(".")]
        ip_addr_list = [int(i) for i in ip_addr.split(".")]
        broadcast_addr_list = [256, 256, 256, 256]
        for i in range(0, 4):
            broadcast_addr_list[i] = subnet_mask_list[i] & ip_addr_list[i]
        return ".".join([str(i) for i in broadcast_addr_list])
    

################
# Client Class #
################

class Client(__CommBase__):

    ################
    # User Methods #
    ################

    def __init__(self, server_ip_addr=None, server_port=8080, subnet_mask="255.255.255.0"):
        self.server_ip_addr = server_ip_addr
        self.server_port = server_port
        self.subnet_mask = subnet_mask

        self.ip_addr = self.get_ip_addr()
        self.broadcast_addr = self.get_broadcast_addr(self.ip_addr, self.subnet_mask)

        if self.server_ip_addr == None:
            self.server_ip_addr = self.ip_addr

    def request(self, request_obj, get_reply=True):
        request_bytes = json.dumps(request_obj).encode()

        sock = socket.socket()
        sock.settimeout(5)
        sock.connect((self.server_ip_addr, self.server_port))
        sock.send(request_bytes)
        if get_reply:
            response_bytes = sock.recv(1024)
            response_obj = json.loads(response_bytes.decode())
        else:
            response_obj = None
        sock.close()

        return response_obj
    
    def discover(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(3)
        sock.bind((self.ip_addr, 8182))
        sock.sendto(b"NIKARI_DISCOVERY_REQUEST", (f"<broadcast>", 8181))

        response = sock.recvfrom(1024)
        if response[0] == b"NIKARI_DISCOVERY_RESPONSE":
            return response[1]
        else:
            return None


################
# Server Class #
################

class Server(__CommBase__):

    ##########################
    # Discovery Server Class #
    ##########################

    class Discovery(asyncio.DatagramProtocol):

        def __init__(self):
            super().__init__()
            self.__log_name__ = "Discovery Server"

        def connection_made(self, transport):
            log(self.__log_name__, "Listening for discovery messages")
            self.transport = transport

        def datagram_received(self, data, addr):
            if data == b"NIKARI_DISCOVERY_REQUEST":
                log(self.__log_name__, f"Responded to discovery message from {addr[0]}")
                self.transport.sendto(b"NIKARI_DISCOVERY_RESPONSE", addr)


    ####################
    # Internal Methods #
    ####################

    async def __default_callback__(self, data, addr):
        # TODO(martianmellow12): Implement this
        log(self.__log_name__, f"Default callback -> Received '{data}' from '{addr}'")
        return dict()

    async def __request_handler__(self, reader, writer):
        data_bytes = await reader.read(1024)
        data_obj = json.loads(data_bytes.decode())

        # TODO(martianmellow12): Kind of a hack; is there a better way?
        response_obj = await self.__callback__(data_obj, reader._transport.get_extra_info("peername"))
        
        response_bytes = json.dumps(response_obj).encode()
        await writer.write(response_bytes)
        writer.close()


    ################
    # User Methods #
    ################

    def __init__(self, ip_addr=None, port=8080, discovery_port=8181, client_limit=8, subnet_mask="255.255.255.0"):
        self.ip_addr = ip_addr if ip_addr else self.get_ip_addr()
        self.port = port
        self.discovery_port = discovery_port
        self.client_limit = client_limit
        self.subnet_mask = subnet_mask

        self.broadcast_addr = self.get_broadcast_addr(self.ip_addr, self.subnet_mask)
        self.__callback__ = self.__default_callback__
        self.__log_name__ = "Command Server"

    def set_callback(self, func=None):
        if func: self.__callback__ = func
        else: self.__callback__ = self.__default_callback__

    async def server_task(self):
        server = await asyncio.start_server(self.__request_handler__, self.ip_addr, self.port)
        async with server:
            await server.serve_forever()

    async def discovery_task(self):
        loop = asyncio.get_event_loop()
        await loop.create_datagram_endpoint(lambda: self.Discovery(), local_addr=(self.ip_addr, self.discovery_port))
        while True:
            await asyncio.sleep(1)
