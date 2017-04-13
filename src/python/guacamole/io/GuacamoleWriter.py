

class GuacamoleWriter(object):
    def write(self, chunk):
        raise Exception("Not Implemented")

    def writeInstruction(self, instruction):
        raise Exception("Not Implemented")


class WriterGuacamoleWriter(GuacamoleWriter):
    def __init__(self, socket):
        self.socket = socket

    def write(self, chunk):
        if self.socket.sendall(chunk):
            raise Exception("Send error")

