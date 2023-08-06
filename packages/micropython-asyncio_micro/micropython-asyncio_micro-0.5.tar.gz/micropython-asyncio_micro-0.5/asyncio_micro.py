import __main__
import time
import heapq
import errno
import logging


log = logging.getLogger("asyncio")

type_gen = type((lambda: (yield))())

class EventLoop:

    def __init__(self):
        self.q = []
        self.cnt = 0

    def time(self):
        return time.time()

    def call_soon(self, callback, *args):
        self.call_at(0, callback, *args)

    def call_later(self, delay, callback, *args):
        self.call_at(self.time() + delay, callback, *args)

    def call_at(self, time, callback, *args):
        # Including self.cnt is a workaround per heapq docs
        log.debug("Scheduling %s", (time, self.cnt, callback, args))
        heapq.heappush(self.q, (time, self.cnt, callback, args))
#        print(self.q)
        self.cnt += 1

    def wait(self, delay):
        # Default wait implementation, to be overriden in subclasses
        # with IO scheduling
        log.debug("Sleeping for: %s", delay)
        time.sleep(delay)

    def run_forever(self):
        while True:
            if self.q:
                t, cnt, cb, args = heapq.heappop(self.q)
                log.debug("Next coroutine to run: %s", (t, cnt, cb, args))
#                __main__.mem_info()
                tnow = self.time()
                delay = t - tnow
                if delay > 0:
                    self.wait(delay)
            else:
                self.wait(-1)
                # Assuming IO completion scheduled some tasks
                continue
            if callable(cb):
                cb(*args)
            else:
                delay = 0
                try:
                    if args == ():
                        args = (None,)
                    log.debug("Coroutine %s send args: %s", cb, args)
                    ret = cb.send(*args)
                    log.debug("Coroutine %s yield result: %s", cb, ret)
                    if isinstance(ret, SysCall):
                        arg = ret.args[0]
                        if isinstance(ret, Sleep):
                            delay = arg
                        elif isinstance(ret, IORead):
#                            self.add_reader(ret.obj.fileno(), lambda self, c, f: self.call_soon(c, f), self, cb, ret.obj)
#                            self.add_reader(ret.obj.fileno(), lambda c, f: self.call_soon(c, f), cb, ret.obj)
                            self.add_reader(arg.fileno(), lambda cb, f: self.call_soon(cb, f), cb, arg)
                            continue
                        elif isinstance(ret, IOWrite):
                            self.add_writer(arg.fileno(), lambda cb, f: self.call_soon(cb, f), cb, arg)
                            continue
                        elif isinstance(ret, IOReadDone):
                            self.remove_reader(arg.fileno())
                        elif isinstance(ret, IOWriteDone):
                            self.remove_writer(arg.fileno())
                    elif isinstance(ret, type_gen):
                        self.call_soon(ret)
                    elif ret is None:
                        # Just reschedule
                        pass
                    else:
                        assert False, "Unsupported coroutine yield value: %r (of type %r)" % (ret, type(ret))
                except StopIteration as e:
                    log.debug("Coroutine finished: %s", cb)
                    continue
                self.call_later(delay, cb, *args)

    def run_until_complete(self, coro):
        val = None
        while True:
            try:
                ret = coro.send(val)
            except StopIteration as e:
                print(e)
                break
            print("ret:", ret)
            if isinstance(ret, SysCall):
                ret.handle()

    def close(self):
        pass


import select

class EpollEventLoop(EventLoop):

    def __init__(self):
        EventLoop.__init__(self)
        self.poller = select.epoll(1)

    def add_reader(self, fd, cb, *args):
        log.debug("add_reader%s", (fd, cb, args))
        self.poller.register(fd, select.EPOLLIN, (cb, args))

    def remove_reader(self, fd):
        log.debug("remove_reader(%s)", fd)
        self.poller.unregister(fd)

    def add_writer(self, fd, cb, *args):
        log.debug("add_writer%s", (fd, cb, args))
        self.poller.register(fd, select.EPOLLOUT, (cb, args))

    def remove_writer(self, fd):
        log.debug("remove_writer(%s)", fd)
        self.poller.unregister(fd)

    def wait(self, delay):
        log.debug("epoll.wait(%d)", delay)
        if delay == -1:
            res = self.poller.poll(-1)
        else:
            res = self.poller.poll(int(delay * 1000))
        log.debug("epoll result: %s", res)
        for cb, ev in res:
            log.debug("Calling IO callback: %s%s", cb[0], cb[1])
            cb[0](*cb[1])


class SysCall:

    def __init__(self, *args):
        self.args = args

    def handle(self):
        raise NotImplementedError

class Sleep(SysCall):
    pass

class IORead(SysCall):
    pass

class IOWrite(SysCall):
    pass

class IOReadDone(SysCall):
    pass

class IOWriteDone(SysCall):
    pass


def get_event_loop():
    return EpollEventLoop()

def coroutine(f):
    return f

def async(coro):
    # We don't have Task bloat, so op is null
    return coro

def sleep(secs):
    yield Sleep(secs)


import microsocket as _socket

class StreamReader:

    def __init__(self, s):
        self.s = s

    def read(self, n=-1):
        s = yield IORead(self.s)
        while True:
            res = self.s.read(n)
            if res is not None:
                break
            log.warn("Empty read")
        if not res:
            yield IOReadDone(self.s)
        return res

    def readline(self):
        log.debug("StreamReader.readline()")
        s = yield IORead(self.s)
        log.debug("StreamReader.readline(): after IORead: %s", s)
        while True:
            res = self.s.readline()
            if res is not None:
                break
            log.warn("Empty read")
        if not res:
            yield IOReadDone(self.s)
        log.debug("StreamReader.readline(): res: %s", res)
        return res


class StreamWriter:

    def __init__(self, s):
        self.s = s

    def awrite(self, buf):
        # This method is called awrite (async write) to not proliferate
        # incompatibility with original asyncio. Unlike original asyncio
        # whose .write() method is both not a coroutine and guaranteed
        # to return immediately (which means it has to buffer all the
        # data), this method is a coroutine.
        sz = len(buf)
        while True:
            res = self.s.write(buf)
            # If we spooled everything, return immediately
            if res == sz:
                log.debug("StreamWriter.awrite(): completed spooling %d bytes", res)
                return
            if res is None:
                res = 0
            log.debug("StreamWriter.awrite(): spooled partial %d bytes", res)
            buf = buf[res:]
            sz -= res
            s = yield IOWrite(self.s)
            log.debug("StreamWriter.awrite(): can write more")

    def close(self):
        yield IOWriteDone(self.s)
        self.s.close()


def open_connection(host, port):
    log.debug("open_connection(%s, %s)", host, port)
    s = _socket.socket()
    s.setblocking(False)
    ai = _socket.getaddrinfo(host, port)
    addr = ai[0][4]
    try:
        s.connect(addr)
    except OSError as e:
        if e.args[0] != errno.EINPROGRESS:
            raise
    log.debug("open_connection: After connect")
    s = yield IOWrite(s)
    log.debug("open_connection: After iowait: %s", s)
    return StreamReader(s), StreamWriter(s)


def start_server(client_coro, host, port):
    log.debug("start_server(%s, %s)", host, port)
    s = _socket.socket()
    s.setblocking(False)

    ai = _socket.getaddrinfo(host, port)
    addr = ai[0][4]
    s.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(10)
    while True:
        log.debug("start_server: Before accept")
        yield IORead(s)
        log.debug("start_server: After iowait")
        s2, client_addr = s.accept()
        s2.setblocking(False)
        log.debug("start_server: After accept: %s", s2)
        yield client_coro(StreamReader(s2), StreamWriter(s2))
