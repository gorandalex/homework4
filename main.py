from http.server import HTTPServer, BaseHTTPRequestHandler
import mimetypes
import pathlib
import udp_client
import udp_server
from threading import Thread
import urllib.parse

HOST = 'localhost'
PORT = 5000


class HttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print("Get HTTP request")
        pr_url = urllib.parse.urlparse(self.path)
        match pr_url.path:
            case '/':
                self.send_html_file('index.html')
            case '/message.html':
                self.send_html_file('message.html')
            case _:
                if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                    self.send_static()
                else:
                    self.send_html_file('error.html', 404)

    def do_POST(self):
        print("Post HTTP request")
        data_input: bytes = self.rfile.read(int(self.headers['Content-Length']))
        data_decode: str = urllib.parse.unquote_plus(data_input.decode())
        data: dict = urllib.parse.parse_qs(data_decode)
        code = udp_client.run_client(HOST, PORT, data)
        self.send_response(code)
        match code:
            case 302:
                self.send_header('Location', '/')
            case _:
                self.send_header('Location', '/error.html')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    print("run")
    path_data = pathlib.Path.joinpath(pathlib.Path().absolute(), 'storage')
    print(path_data.absolute())
    if not path_data.exists():
        print('Creating directory')
        pathlib.Path.mkdir(path_data)
        print('Creating file')
    path_data = pathlib.Path.joinpath(path_data, 'data.json')
    print(path_data.absolute())
    if not path_data.exists():
        path_data.touch(exist_ok=True)
        path_data.write_text('{}')
        print('File is saved')
    if not path_data.exists():
        print('File is not created')
    else:
        print('File is created')
    server_address = ('localhost', 3000)
    http = server_class(server_address, handler_class)
    try:
#        http.serve_forever()
        server = Thread(target=udp_server.udp_server, args=(HOST, PORT))
        http_server = Thread(target=http.serve_forever)
        print(f'{http =}')
#        http_server.daemon = True
        server.start()
        http_server.start()
        print('Server is running')
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    print('main')
    run()
