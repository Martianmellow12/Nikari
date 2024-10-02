# Nikari Voice Command Library
#
# Written by Martianmellow12

import asyncio
import json
import picovoice, pvrecorder

from shared import nikari_logging

# TODO(martianmellow12): DO NOT COMMIT
PV_KEY = "TEMP"

########################
# Voice Command Server #
########################

class VoiceCmdServer:

    class DatagramServer(asyncio.DatagramProtocol):

        def __init__(self):
            super().__init__()
            self.__log_name__ = "Voice Command Server"

            self.__connections__ = dict()
            self.__response_queue__ = dict()

        def __init_connection__(self, addr):
            nikari_logging.log(self.__log_name__, f"Beginning exchange with {addr[0]}")
            self.__connections__[addr[0]] = list()
            loop = asyncio.get_event_loop()
            loop.create_task(self.__process_thread__(addr))

        def __wake_callback__(self, addr):
            print(f"WOKE {addr}")
            self.transport.sendto(b"WOKE", addr)

        def __inference_callback__(self, addr, inference):
            print(f"INFERENCE {addr}: {inference}")
            self.transport.sendto(b"INF", addr)

        async def __process_thread__(self, addr):
            nikari_logging.log(self.__log_name__, f"Thread for {addr[0]} started")

            pv = picovoice.Picovoice(access_key=PV_KEY,
                                     keyword_path="wake.ppn",
                                     wake_word_callback=lambda: self.__wake_callback__(addr),
                                     context_path="inference.rhn",
                                     inference_callback=lambda i: self.__inference_callback__(addr, i))

            while True:
                while len(self.__connections__[addr[0]]) == 0:
                    await asyncio.sleep(0.1)
                pv.process(self.__connections__[addr[0]].pop(0))
                #self.transport.sendto(b"OK", addr)
                

        def connection_made(self, transport):
            nikari_logging.log(self.__log_name__, "Ready to receive data")
            self.transport = transport

        def datagram_received(self, data, addr):
            try:
                frame = json.loads(data.decode("utf-8"))
            except Exception:
                nikari_logging.log(self.__log_name__, f"Received bad frame from {addr[0]}")
            else:
                if not addr[0] in self.__connections__.keys():
                    self.__init_connection__(addr)
                self.__connections__[addr[0]].append(frame)

    def __init__(self):
        pass

    async def voice_server_task(self):
        loop = asyncio.get_event_loop()
        # TODO(martianmellow12): Get IP address/port selection working
        await loop.create_datagram_endpoint(lambda: self.DatagramServer(), local_addr=("10.0.1.38", 9090))
        while True:
            await asyncio.sleep(1)


########################
# Voice Command Client #
########################

class VoiceCmdClient:

    def __init__(self):
        pass