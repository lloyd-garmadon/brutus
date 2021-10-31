import flask
import flask_limiter
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

        self.radar = False
        self.radar_scan = True
        self.radar_from = "-60"
        self.radar_to = "60"
        self.radar_pos = "0"


        @self.flask.route("/", methods=['GET', 'POST'])
        def entrypoint():
            if flask.request.method == 'GET':
                pass
            if flask.request.method == 'POST':
                if 'camera' in flask.request.form.keys():
                    self.cmd_table.command("camera_" + flask.request.form['camera'] )

                elif 'radar' in flask.request.form.keys():
                    if flask.request.form['radar'] == "start" and 'x' in flask.request.form.keys():
                        self.radar = True
                    if flask.request.form['radar'] == "stop" and 'x' in flask.request.form.keys():
                        self.radar = False
                    if 'range' in flask.request.form.keys() and 'pos' in flask.request.form.keys():
                        self.radar_scan = not self.radar_scan
                    if self.radar:
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
                                            camera=self.camera.is_running(),
                                            camera_fps=self.camera.get_fps(),
                                            radar=self.radar,
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
            return flask.Response(self.generate_video(), mimetype = "multipart/x-mixed-replace; boundary=frame")


    def generate_video(self):
        while True:
            # check if the output frame is available, otherwise skip
            image = self.camera.get_image()

            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(image) + b'\r\n')






