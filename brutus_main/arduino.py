# Importing Libraries
import glob
import serial
import logging
import threading
import time
import re
import json


class Arduino:

    def __init__(self, name=""):
        # 
        self.serial = None
        self.name = name

        self.cmd_table = []
        self.msg_table = []

        self.cmd_cookie = 1
        self.cmd_lock = threading.Lock()
        self.cmd_queue = []

        self.response_regex = re.compile("^[#:][0-9]{2}:[0-9]{2}:")
        self.response_cmd_regex = re.compile("^#[0-9]{2}:[0-9]{2}:")
        self.response_msg_regex = re.compile("^:[0-9]{2}:[0-9]{2}:")

        # receive thread
        self.thread_recv = threading.Thread(target=self.thread_recv_func)
        self.thread_recv_event = threading.Event()
        self.thread_recv_running = True
        self.thread_recv.start()

        # try to open serial port when a name is given
        if name : 
            self.open(name)


    def __del__(self):
        self.thread_recv_running = False
        self.close()


    def open(self, name):
        if self.serial is not None:
            logging.error("arduino is already open")
            return False
        else:
            logging.info("scan for arduino as '" + name + "'") 

            ports = glob.glob('/dev/ttyUSB*')
            for port in ports:
                ser = serial.Serial()
                ser.port = port
                ser.baudrate = 57600
                ser.timeout = 0.5
                ser.open()
                time.sleep(2)

                self.serial = ser
                self.thread_recv_event.set()
                res, response = self.command("version", openquery=True)

                if res == 0 and name in str(response):
                    self.name = name
                    break
                else:
                    self.thread_recv_event.clear()
                    ser.close() 
                    self.serial = None

            # starting receive thread
            if self.serial is None:
                logging.error("open arduino as '" + name + "' failed") 
                return False
            else:
                logging.info("opened arduino at '" + self.serial.name + "' as '" + self.name + "'") 

                self.cmd_table = []
                res, response = self.command("info", "cmd", openquery=True)
                if res == 0:
                    response = json.loads(response)
                    for resp in response :
                        command = {   
                            "name":  resp[0],
                            "id": int(resp[1]),
                            "params":  resp[2],
                            "response":  resp[3],
                            "description":  resp[4],
                            "func":  None 
                        } 
                        self.cmd_table.append( command )

                self.msg_table = []
                res, response = self.command("info", "msg", openquery=True)
                if res == 0:
                    response = json.loads(response)
                    for resp in response :
                        message = {
                            "name": resp[0],
                            "id": int(resp[1]),
                            "response": resp[2],
                            "description": resp[3],
                            "func": None
                        }
                        self.msg_table.append( message ) 

                return True


    def close(self):
        if self.serial is None:
            logging.error("arduino is not opened")
            return False
        else:
            logging.info("close arduino at '" + self.serial.name + "' as '" + self.name + "'") 
            self.name = ""
            self.serial.close()
            self.serial = None
            self.thread_recv_event.set()
            self.thread_recv.join()
            self.cmd_table = []
            self.msg_table = []
            return True


    def is_open(self):
        if self.serial is None:
            logging.error("arduino is not open")
            return False
        else:
            return True


    def cmd_table_count(self):
        return len(self.cmd_table) 

    def cmd_table_get_list(self):
        return self.cmd_table

    def cmd_table_get_cmd(self, identifier):
        if isinstance(identifier, str):
            for c in self.cmd_table:
                if c["name"] == identifier:
                    return c
            return None 
        else :
            return self.cmd_table[identifier]

    def cmd_table_clear_func(self, identifier):
        c = self.cmd_table_get_cmd(identifier)
        if c is not None:
            c["func"] = None

    def cmd_table_assign_func(self, identifier, func):
        c = self.cmd_table_get_cmd(identifier)
        if c is not None:
            c["func"] = func


    def msg_table_count(self):
        return len(self.msg_table) 

    def msg_table_get_list(self):
        return self.msg_table

    def msg_table_get_msg(self, identifier):
        if isinstance(identifier, str):
            for m in self.msg_table:
                if m["name"] == identifier:
                    return m
            return None 
        else :
            return self.msg_table[identifier]

    def msg_table_clear_func(self, identifier):
        m = self.msg_table_get_msg(self, identifier)
        if m is not None:
            m["func"] = None

    def msg_table_register_func(self, identifier, func):
        m = self.msg_table_get_msg(self, identifier)
        if m is not None:
            m["func"] = func




    def command(self, cmd, *args, **kwargs):
        if self.serial is None:
            logging.error("arduino is not open")
            return (1, "")
        else:
            cmd_args = ""
            for arg in args:
                cmd_args += " " + str(arg)

            wait = True
            if "wait" in kwargs:
                wait = kwargs["wait"]

            timeout = 1000
            if "timeout" in kwargs:
                timeout = kwargs["timeout"]

            openquery = False
            if "openquery" in kwargs:
                openquery = kwargs["openquery"]

            if openquery:
                wait = True
            else:
                cmd_entry = self.cmd_table_get_cmd(cmd)
                if cmd_entry is None:
                    logging.error("command not found in cmd_list")
                    return (1, "")

            event = None
            func = None
            if wait:
                event = threading.Event()
            else:
                if "func" in kwargs:
                    func = kwargs["func"]
                elif cmd_entry["func"] is not None:
                    func = cmd_entry["func"]
                else :
                    logging.error("command can not be called asynchronous")
                    return (1, "")

            cookie = self.cmd_queue_push(cmd, cmd_args, event=event, func=func, timeout=timeout)

            if openquery:
                commandline = "\n" + f"#{cookie:02d}:" + cmd + " " + cmd_args + "\n"
            else :
                cmd_id = cmd_entry["id"]
                commandline = "\n" + f"#{cookie:02d}:{cmd_id:02d}:" + cmd_args + "\n"

            self.serial.write(bytes(commandline, 'utf-8'))

            if event is not None:
                logging.info( f"sync queued: {commandline}\n" )
                event.wait(timeout)
                cmd = self.cmd_queue_pop(cookie)
                return (cmd["res"], cmd["response"])
            else :
                logging.info( f"async queued: {commandline}\n" )
                return (1, "command queued")


    def thread_recv_func(self):
        while self.thread_recv_running :
            self.thread_recv_event.wait()
            if not self.thread_recv_running:
                return
            else:
                try:
                    line = self.serial.readline()
                except:
                    line = b""
                line = line.decode('utf-8')
                cookie = self.response_regex.search(line)
                if cookie is not None:
                    cookie = int(line[1:3])
                    res = int(line[4:6])
                    response = line[7:-1]
                    logging.info(f"parse: cookie: {cookie} res: {res} response: {response}")
                    msg = self.response_msg_regex.search(line)
                    if msg is not None:
                        # received line is a message
                        pass
                    else :
                        # received line is a commands
                        self.cmd_queue_process(cookie, res, response)


    def cmd_queue_push(self, cmd, cmd_args, event=None, func=None, timeout=1000):
        with self.cmd_lock:
            cookie = self.cmd_cookie
            self.cmd_cookie = 1 if cookie >= 99 else cookie + 1

        cmd_entry = {
            "cookie": cookie,
            "cmd": cmd,
            "args": cmd_args,
            "res": None,
            "response": None,
            "event": event,
            "func": func,
        }

        with self.cmd_lock:
            self.cmd_queue.append(cmd_entry)

        return cookie

    def cmd_queue_get(self, cookie):
        cmd = None
        with self.cmd_lock:
            for i, cmd in enumerate(self.cmd_queue):
                if cmd["cookie"] == cookie:
                    cmd = self.cmd_queue[i]
                    break
        return cmd

    def cmd_queue_pop(self, cookie):
        cmd = None
        with self.cmd_lock:
            for i, cmd in enumerate(self.cmd_queue):
                if cmd["cookie"] == cookie:
                    cmd = self.cmd_queue.pop(i)
                    break
        return cmd

    def cmd_queue_process(self, cookie, res, response):
        cmd = None
        func = None
        with self.cmd_lock:
            for i, cmd in enumerate(self.cmd_queue):
                if cmd["cookie"] == cookie:
                    cmd = self.cmd_queue[i]
                    break
            if cmd is not None:
                if cmd["event"] is not None:
                    cmd["res"] = res
                    cmd["response"] = response
                    cmd["event"].set()
                elif cmd["func"] is not None:
                    func = cmd["func"]
                    self.cmd_queue.pop(i)
        if func is not None:
            func(res, response)

