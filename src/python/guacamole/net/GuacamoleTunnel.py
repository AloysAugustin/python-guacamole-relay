#!/usr/bin/env python

import threading
import uuid


class GuacamoleTunnel(object):
    INTERNAL_DATA_OPCODE = ''

    def acquireReader(self):
        raise Exception("Not Implemented")

    def releaseReader():
        raise Exception("Not Implemented")

    def hasQueuedReaderThreads():
        raise Exception("Not Implemented")

    def acquireWriter():
        raise Exception("Not Implemented")

    def releaseWriter():
        raise Exception("Not Implemented")

    def getUUID():
        raise Exception("Not Implemented")

    def getSocket():
        raise Exception("Not Implemented")

    def close():
        raise Exception("Not Implemented")

    def isOpen():
        raise Exception("Not Implemented")


class AbstractGuacamoleTunnel(GuacamoleTunnel):
    def __init__(self):
        self.reader_lock = threading.Lock()
        self.writer_lock = threading.Lock()
        # Need to know if there's another thread waiting
        self.read_waiters = 0
        self.read_waiters_lock = threading.Lock()
        self.reader = ReaderGuacamoleReader(self.getSocket())
        self.writer = WriterGuacamoleWriter(self.getSocket())

    def acquireReader(self):
        with self.read_waiters_lock:
            self.read_waiters += 1

        self.reader_lock.acquire()
        with self.read_waiters_lock:
            self.read_waiters -= 1

        return self.reader

    def hasQueuedReaderThreads(self):
        with self.read_waiters_lock:
            return self.read_waiters > 0

    def releaseReader(self):
        self.reader_lock.release()

    def acquireWriter(self):
        self.writer_lock.acquire()
        return self.writer

    def releaseWriter(self):
        self.writer_lock.release()

    def isOpen(self):
        return self.getSocket().isOpen()

class SimpleGuacamoleTunnel(AbstractGuacamoleTunnel):
    def __init__(self, socket):
        self.uuid = str(uuid.uuid4())
        self.socket = socket
        super(SimpleGuacamoleTunnel, self).__init__()

    def getSocket(self):
        return self.socket

    def getUUID(self):
        return self.uuid

