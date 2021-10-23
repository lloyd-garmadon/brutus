#!/usr/bin/env python3
 
# Importing Libraries
import logging
import json
import arduino
import command
import webapp

logging.basicConfig(level=logging.INFO)


arduino_drive = arduino.Arduino()
arduino_radar = arduino.Arduino()
brutus_cmd_table = command.CommandTable()
brutus_view_grabber = webapp.ViewGrabber()
brutus_webapp = webapp.Webapp(cmd_table=brutus_cmd_table, view_grabber=brutus_view_grabber)

def dump(*args):
    logging.info("dump:")
    logging.info(args)


if __name__ == "__main__":

    arduino_drive.open("brutus_drive")
    arduino_radar.open("brutus_radar")

    cmd_entry = arduino_radar.cmd_table_get_cmd("start")
    if cmd_entry is not None:
        brutus_cmd_table.cmd_table_insert( "radar_start",
                                            params = cmd_entry["params"],
                                            response = cmd_entry["response"],
                                            description = cmd_entry["description"],
                                            func = arduino_radar.command,
                                            func_args   = [ cmd_entry["name"] ],
                                            func_kwargs = { "wait": False, "func": dump } )

    cmd_entry = arduino_radar.cmd_table_get_cmd("stop")
    if cmd_entry is not None:
        brutus_cmd_table.cmd_table_insert( "radar_stop",
                                            params = cmd_entry["params"],
                                            response = cmd_entry["response"],
                                            description = cmd_entry["description"],
                                            func = arduino_radar.command,
                                            func_args   = [ cmd_entry["name"] ],
                                            func_kwargs = { "wait": False, "func": dump } )

    cmd_entry = arduino_radar.cmd_table_get_cmd("range")
    if cmd_entry is not None:
        brutus_cmd_table.cmd_table_insert( "radar_range",
                                            params = cmd_entry["params"],
                                            response = cmd_entry["response"],
                                            description = cmd_entry["description"],
                                            func = arduino_radar.command,
                                            func_args   = [ cmd_entry["name"] ],
                                            func_kwargs = { "wait": False, "func": dump } )

    cmd_entry = arduino_radar.cmd_table_get_cmd("pos")
    if cmd_entry is not None:
        brutus_cmd_table.cmd_table_insert( "radar_pos",
                                            params = cmd_entry["params"],
                                            response = cmd_entry["response"],
                                            description = cmd_entry["description"],
                                            func = arduino_radar.command,
                                            func_args   = [ cmd_entry["name"] ],
                                            func_kwargs = { "wait": False, "func": dump } )

    brutus_cmd_table.cmd_table_insert( "view_start",
                                        params = "",
                                        response = "",
                                        description = "opens the camera and start video transmission",
                                        func = brutus_view_grabber.start,
                                        func_args   = [ ],
                                        func_kwargs = { } )

    brutus_cmd_table.cmd_table_insert( "view_stop",
                                        params = "",
                                        response = "",
                                        description = "stops video transmission and closes camera",
                                        func = brutus_view_grabber.stop,
                                        func_args   = [ ],
                                        func_kwargs = { } )


    while (True) :
        cmd = input()
        cmd = cmd.split(" ")
        brutus_cmd_table.command(*cmd)
