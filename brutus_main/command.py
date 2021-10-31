# Importing Libraries
import logging
import json

class CommandTable:

    def __init__(self, ):
        self.cmd_table = []
        self.cmd_table_insert( "cmd_if",
                                params = "",
                                response = "",
                                description = "returns a list of all implemented commands",
                                func = self.cmd_if,
                                func_args   = [ ],
                                func_kwargs = { } )

    def cmd_table_count(self):
        return len(self.cmd_table) 

    def cmd_table_get_list(self):
        return self.cmd_table

    def cmd_table_insert(self, cmd, params=None, response=None, description=None, func=None, func_args=None, func_kwargs=None):
        command = {
            "name": cmd,
            "params":  params,
            "response":  response,
            "description":  description,
            "func":  func,
            "func_args": func_args,
            "func_kwargs": func_kwargs
        }
        self.cmd_table.append( command )

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

    def cmd_if(self):
        for cmd_entry in self.cmd_table:
            logging.info( f"Command:")
            logging.info( f"  {cmd_entry['name']}")
            if cmd_entry['description']:
                logging.info( f"Description:")
                logging.info( f"  {cmd_entry['description']}")
            if cmd_entry['params']:
                logging.info( f"Parameter:")
                logging.info( f"  {cmd_entry['params']}")
            if cmd_entry['response']:
                logging.info( f"Response:")
                logging.info( f"  {cmd_entry['response']}")
            logging.info( "")

    def command(self, cmd, *args):
        for cmd_entry in self.cmd_table:
            if cmd_entry["name"] == cmd:
                if cmd_entry["func"] is not None:
                    return cmd_entry["func"]( *cmd_entry["func_args"], *args, **cmd_entry["func_kwargs"] )
        logging.error("unknown command")
        return False 
