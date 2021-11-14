import flask
import threading
import cv2
import os
import sys
import glob
import logging

import command
import brutus_camera
import brutus_radar


logging.basicConfig(level=logging.INFO)

class Webapp():

    def __init__(self, webapp_name=None, camera=None, radar=None):
        if not webapp_name:
            webapp_name = __name__

        self.flask = flask.Flask(webapp_name)

        self.thread_flask = threading.Thread(target=self.flask.run, kwargs={"host":"0.0.0.0"} )
        self.thread_flask.start()

        self.radar = radar
        self.radar_active = False
        self.radar_scan = True
        self.radar_from = "-60"
        self.radar_to = "60"
        self.radar_pos = "0"

        self.camera = camera



        @self.flask.route("/", methods=['GET', 'POST'])
        def entrypoint():
            if flask.request.method == 'GET':
                pass
            if flask.request.method == 'POST':
                if 'camera' in flask.request.form.keys():
                    if flask.request.form['camera'] == "start"  or  flask.request.form['camera'] == "update":
                        self.camera.start()
                    elif flask.request.form['camera'] == "stop":
                        self.camera.stop()

                elif 'radar' in flask.request.form.keys():
                    if flask.request.form['radar'] == "start"  or  flask.request.form['radar'] == "update":
                        curr_range_from, curr_range_to = self.radar.get_range()
                        curr_static_pos = self.radar.get_pos()
                        curr_mode = self.radar.get_mode()
                        form_range_from = int(flask.request.form['range_from'])
                        form_range_to = int(flask.request.form['range_to'])
                        form_static_pos = int(flask.request.form['static_pos'])
                        form_mode = flask.request.form['radar_mode']

                        self.radar.set_range( form_range_from, form_range_to )
                        self.radar.set_pos( form_static_pos )
                        self.radar.set_mode( form_mode )
                        self.radar.clear_screen()
                        if flask.request.form['radar'] == "start":
                            self.radar.start()
                        if flask.request.form['radar'] == "update":
                            if curr_range_from != form_range_from or curr_range_to != form_range_to or curr_static_pos != form_static_pos or curr_mode != form_mode :
                                self.radar.start()

                    elif flask.request.form['radar'] == "stop":
                        self.radar.stop()
                else:
                    pass 

            range_from, range_to = self.radar.get_range()
            return flask.render_template("index.html",
                                            camera_active=self.camera.is_running(),
                                            camera_fps=self.camera.get_fps(),
                                            radar_active=self.radar.is_running(),
                                            radar_mode=self.radar.get_mode(),
                                            range_from=range_from,
                                            range_to=range_to,
                                            static_pos=self.radar.get_pos(),
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

        @self.flask.route("/radar")
        def entrypoint_radar():
            return flask.Response(self.radar.generate_image(), mimetype = "multipart/x-mixed-replace; boundary=frame")







