#!/usr/bin/env python3
 
# Importing Libraries
import logging
import json
import arduino
import command
import brutus_camera
import brutus_radar
import webapp

logging.basicConfig(level=logging.INFO)


arduino_drive = arduino.Arduino()
arduino_radar = arduino.Arduino()

brutus_cmd_table = command.CommandTable()

brutus_camera = brutus_camera.Camera()
brutus_radar = brutus_radar.Radar(arduino_radar)

brutus_webapp = webapp.Webapp(camera=brutus_camera, radar=brutus_radar)

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

    brutus_cmd_table.cmd_table_insert( "camera_start",
                                        params = "",
                                        response = "",
                                        description = "opens the camera and start video transmission",
                                        func = brutus_camera.start,
                                        func_args   = [ ],
                                        func_kwargs = { } )

    brutus_cmd_table.cmd_table_insert( "camera_stop",
                                        params = "",
                                        response = "",
                                        description = "stops video transmission and closes camera",
                                        func = brutus_camera.stop,
                                        func_args   = [ ],
                                        func_kwargs = { } )

    while (True) :
        cmd = input()
        cmd = cmd.split(" ")
        brutus_cmd_table.command(*cmd)
