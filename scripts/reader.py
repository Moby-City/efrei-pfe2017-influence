#!/usr/bin/env python3

import sys
import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

if len(sys.argv) < 2:
    print('Usage: reader.py <json data file> [optional out json file location]')
    sys.exit(1)

in_file = sys.argv[1]
out_file = in_file if len(sys.argv) == 2 else sys.argv[2]
my_path = os.path.dirname(os.path.realpath(__file__))

with open(in_file) as f:
    data = json.load(f)
    num_articles = len(data)
    num_checked = len([1 for a in data if a['is_confirmed'] is not None])

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            with open(os.path.join(my_path, 'reader.html'), 'rb') as f:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
        elif self.path == '/data':
            with open(os.path.join(in_file), 'rb') as f:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
        else:
            self.send_error(404, 'no such file %s, sorry' % self.path)

    def do_POST(self):
        if self.path == '/save':
            length = int(self.headers['Content-Length'])
            try:
                data = json.loads(self.rfile.read(length).decode('utf-8'))
            except ValueError:
                self.send_error(400, 'bad json, probably')
                return

            if not len(data) == num_articles:
                self.send_error(400, 'articles got dropped? invalid file')
                return
            if not len([1 for a in data if a['is_confirmed'] is not None]) > num_checked:
                self.send_error(400, 'less checked articles than before? invalid file')
                return

            with open(out_file, 'w') as f:
                json.dump(data, f, indent=2)
                f.close()
            self.send_response(200)
            self.end_headers()
        else:
            self.send_error(404, 'no such location, sorry')

httpd = HTTPServer(('', 8000), MyHandler)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
print('Bye!')
httpd.server_close()
