import flask
import threading
import cv2
import os
import sys
import glob
import logging

import command


logging.basicConfig(level=logging.INFO)

path = os.path.dirname(os.path.realpath(__file__))


class ViewGrabber():

    def __init__(self, camera_name=None):
        if not camera_name:
            camera_name = "/dev/video0"

        self.camera_name = None
        devices = glob.glob('/dev/video*')
        for device in devices:
            if camera_name == device:
                self.camera_name = camera_name
                continue

        self.camera = None

        self.image_lock = threading.Lock()
        self.image_off = cv2.imread(path + '/static/view_off.jpg')
        self.image = self.image_off.copy()

        self.running = False

        self.grabber = threading.Thread(target=self.grabber_func)
        self.grabber_event = threading.Event()
        self.grabber_running = True if self.camera_name is not None else False
        self.grabber.start()


    def start(self):
        self.running = True
        self.grabber_event.set()


    def stop(self):
        self.running = False
        self.grabber_event.clear()
        if self.camera is not None:
            self.camera.release()


    def is_running(self):
        return self.running


    def grabber_func(self):
        while self.grabber_running :
            self.grabber_event.wait()
            if not self.grabber_running:
                return
            else:
                if self.camera is None:
                    self.camera = cv2.VideoCapture(self.camera_name)
                if not self.camera.isOpened():
                    self.camera = None
                    continue
                
                ret, cameraframe = self.camera.read()

                if ret:
                    with self.image_lock:
                        self.image = cameraframe.copy()

        if self.camera is not None:
            self.camera.release()









class Webapp():

    def __init__(self, webapp_name=None, cmd_table=None, view_grabber=None):
        if not webapp_name:
            webapp_name = __name__

        self.view_grabber = view_grabber
        self.cmd_table = cmd_table
        
        self.radar = False
        self.radar_scan = True
        self.radar_from = "-60"
        self.radar_to = "60"
        self.radar_pos = "0"

        self.flask = flask.Flask(webapp_name)

        self.thread_flask = threading.Thread(target=self.flask.run, kwargs={"host":"0.0.0.0"} )
        self.thread_flask.start()

        

        @self.flask.route("/", methods = ['GET', 'POST'] )
        def webapp_route_index():
            # return the rendered template
            if flask.request.method == 'GET':
                pass
            if flask.request.method == 'POST':
                if 'view' in flask.request.form.keys():
                    self.cmd_table.command("view_" + flask.request.form['view'] )

                if 'left' in flask.request.form.keys():
                    pass
                if 'right' in flask.request.form.keys():
                    pass
                if 'center' in flask.request.form.keys():
                    pass

                if 'forward' in flask.request.form.keys():
                    pass
                if 'backward' in flask.request.form.keys():
                    pass
                if 'stop' in flask.request.form.keys():
                    pass

                if 'radar' in flask.request.form.keys():
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

            return flask.render_template("index.html",
                                            view=self.view_grabber.is_running(),
                                            radar=self.radar,
                                            radar_scan=self.radar_scan,
                                            radar_from=self.radar_from,
                                            radar_to=self.radar_to,
                                            radar_pos=self.radar_pos,
                                        )

        @self.flask.route("/view")
        def webapp_route_view():
            return flask.Response(self.generate_view(), mimetype = "multipart/x-mixed-replace; boundary=frame")


    def generate_view(self):
        while True:
            # check if the output frame is available, otherwise skip
            with self.view_grabber.image_lock:
                if self.view_grabber.running:
                    output_image = self.view_grabber.image
                else :
                    output_image = self.view_grabber.image_off

                # encode the frame in JPEG format
                (flag, encodedImage) = cv2.imencode(".jpg", output_image)

                # ensure the frame was successfully encoded
                if not flag:
                    continue

            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

