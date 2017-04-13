#!/usr/bin/env python

import select

class GuacamoleReader(object):
    def available(self):
        raise Exception("Not Implemented")

    def read(self):
        raise Exception("Not Implemented")

    def readInstruction(self):
        raise Exception("Not Implemented")

# TODO cleanup
class ReaderGuacamoleReader(GuacamoleReader):
    def __init__(self, socket):
        self.socket = socket
        self.parseStart = 0
        self.buffer = bytearray(0)
        self.readPoller = select.poll()
        self.readPoller.register(socket, select.POLLIN)

    def available(self):
        ready = self.readPoller.poll(0)
        return len(ready) > 0 or len(self.buffer) > 0

    def read(self):
        while True:
            elementLength = 0
            i = self.parseStart
            while i < len(self.buffer):
                readChar = chr(self.buffer[i])
                i += 1
                if '0' <= readChar and readChar <= '9':
                    elementLength = elementLength * 10 + readChar - ord('0')
                elif readChar == '.':
                    if i + elementLength < len(self.buffer):
                        terminator = chr(self.buffer[i + elementLength])
                        i += elementLength + 1
                        elementLength = 0
                        self.parseStart = i
                        if terminator == ';':
                            instruction = bytearray(i)
                            instruction[:] = self.buffer[0:i]
                            self.buffer = self.buffer[i:]
                            self.parseStart = 0
                            return instruction
                        elif terminator != ',':
                            raise Exception("Element terminator of instruction was not ';' nor ','")
                    else:
                        break
                else:
                    raise Exception("Non-numeric character in element length.")
            chunk = bytearray(4096)
            numRead = self.socket.recv_into(chunk)
            if numRead == -1:
                return None
            self.buffer.append(chunk[:numRead])

