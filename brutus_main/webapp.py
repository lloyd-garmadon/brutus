import flask
import threading
import cv2
import os
import sys
import glob
import logging

import command
import camera


logging.basicConfig(level=logging.DEBUG)

class Webapp():

    def __init__(self, webapp_name=None, cmd_table=None, camera=None):
        if not webapp_name:
            webapp_name = __name__

        self.cmd_table = cmd_table
        self.camera = camera

        self.flask = flask.Flask(webapp_name)

        self.thread_flask = threading.Thread(target=self.flask.run, kwargs={"host":"0.0.0.0"} )
        self.thread_flask.start()

        self.radar_active = False
        self.radar_scan = True
        self.radar_from = "-60"
        self.radar_to = "60"
        self.radar_pos = "0"

        self.camera_active = False
        self.camera_fps = self.camera.get_fps()



        @self.flask.route("/", methods=['GET', 'POST'])
        def entrypoint():
            if flask.request.method == 'GET':
                pass
            if flask.request.method == 'POST':
                if 'camera' in flask.request.form.keys():
                    if flask.request.form['camera'] == "start":
                        self.camera_active = True
                        self.cmd_table.command("camera_fps", int(flask.request.form['fps']) )
                        self.cmd_table.command("camera_start" )
                        self.camera_fps = self.camera.get_fps()
                    if flask.request.form['camera'] == "stop":
                        if int(flask.request.form['fps']) != self.camera_fps and self.camera_active:
                            self.cmd_table.command("camera_fps", int(flask.request.form['fps']) )
                            self.camera_fps = self.camera.get_fps()
                        else:
                            self.camera_active = False
                            self.cmd_table.command("camera_stop" )

                elif 'radar' in flask.request.form.keys():
                    if flask.request.form['radar'] == "start" and 'x' in flask.request.form.keys():
                        self.radar_active = True
                    if flask.request.form['radar'] == "stop" and 'x' in flask.request.form.keys():
                        self.radar_active = False
                    if 'range' in flask.request.form.keys() and 'pos' in flask.request.form.keys():
                        self.radar_scan = not self.radar_scan
                    if self.radar_active:
                        if self.radar_scan:
                            # set range and start
                            #self.cmd_table.command("radar_range", flask.request.form['radar_from'], flask.request.form['radar_to'] )
                            pass
                        else:
                            #self.cmd_table.command("radar_pos", flask.request.form['radar_pos'] )
                            pass
                    #self.cmd_table.command("radar_" + flask.request.form['radar'] )
                else:
                    pass 

            return flask.render_template("index.html",
                                            camera_active=self.camera_active,
                                            camera_fps=self.camera_fps,
                                            radar_active=self.radar_active,
                                            radar_scan=self.radar_scan,
                                            radar_from=self.radar_from,
                                            radar_to=self.radar_to,
                                            radar_pos=self.radar_pos,
                                        )


        @self.flask.route("/control", methods=['GET', 'POST'])
        def entrypoint_control():
            cmd = ""
            args = ""
            if flask.request.method == 'POST':
                cmd = "drive"
                if 'left' in flask.request.form.keys():
                    args = "left"
                elif 'right' in flask.request.form.keys():
                    args = "right"
                elif 'center' in flask.request.form.keys():
                    args = "center"
                elif 'forward' in flask.request.form.keys():
                    args = "faster"
                elif 'backward' in flask.request.form.keys():
                    args = "slower"
                elif 'stop' in flask.request.form.keys():
                    args = "stop"
                else:
                    cmd = "Unknown Command"

            return flask.render_template("output.html", cmd=cmd, args=args)


        @self.flask.route("/video")
        def entrypoint_video():
            return flask.Response(self.camera.generate_image(), mimetype = "multipart/x-mixed-replace; boundary=frame")








