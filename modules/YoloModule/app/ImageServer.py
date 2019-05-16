# Base on work from https://github.com/Bronkoknorb/PyImageStream
import trollius as asyncio
import tornado.ioloop
import tornado.web
import tornado.websocket
import threading
import base64
import os

class ImageStreamHandler(tornado.websocket.WebSocketHandler):

    def initialize(self, videoCapture):
        self.clients = []
        self.videoCapture = videoCapture

    def check_origin(self, origin):
        return True

    def open(self):
        self.clients.append(self)
        print("Image Server Connection::opened")

    def on_message(self, msg):
        if msg == 'next':
            frame = self.videoCapture.get_display_frame()
            if frame != None:
                encoded = base64.b64encode(frame)
                self.write_message(encoded, binary=False)

    def on_close(self):
        self.clients.remove(self)
        print("Image Server Connection::closed")

class ImageServer(threading.Thread):

    def __init__(self, port, videoCapture):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.port = port
        self.videoCapture = videoCapture

    def run(self):
        print ('ImageServer::run() : Started Image Server')
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop( loop )

            indexPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
            app = tornado.web.Application([
                (r"/stream", ImageStreamHandler, {'videoCapture': self.videoCapture}),
                (r"/(.*)", tornado.web.StaticFileHandler, {'path': indexPath, 'default_filename': 'index.html'})
            ])
            app.listen(self.port)
            print ('ImageServer::Started.')

            tornado.ioloop.IOLoop.instance().start()
        except Exception as e:
            print('ImageServer::exited run loop. Exception - '+ str(e))

    def close(self):
        print ('ImageServer::close()')