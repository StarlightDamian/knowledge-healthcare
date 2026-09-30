"""Keep the shared static site and proxy only /healthcare to its loopback API."""
import argparse
from functools import partial
from http.client import HTTPConnection
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit

HOP_HEADERS = {'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
               'te', 'trailer', 'transfer-encoding', 'upgrade'}


class GatewayHandler(SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def __init__(self, *args, backend_port=11004, **kwargs):
        self.backend_port = backend_port
        super().__init__(*args, **kwargs)

    def end_headers(self):
        path = self.path.split('?', 1)[0]
        if path == '/fitness' or path.startswith('/fitness/'):
            self.send_header('Cache-Control', 'public, no-cache, no-transform')
        super().end_headers()

    def route(self):
        path = urlsplit(self.path).path
        medical = path == '/healthcare' or path.startswith('/healthcare/')
        decoded = unquote(path)
        if not medical and (decoded == '/healthcare' or decoded.startswith('/healthcare/')):
            self.send_error(404)
            return True
        if not medical:
            return False
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            self.send_error(400)
            return True
        if length < 0 or length > 2_000_000 or self.headers.get('Transfer-Encoding'):
            self.send_error(413)
            self.close_connection = True
            return True
        body = self.rfile.read(length) if length else None
        headers = {key: value for key, value in self.headers.items()
                   if key.lower() not in HOP_HEADERS | {'accept-encoding', 'cookie', 'authorization'}}
        upstream = HTTPConnection('127.0.0.1', self.backend_port, timeout=60)
        started = False
        try:
            upstream.request(self.command, self.path, body=body, headers=headers)
            response = upstream.getresponse()
            self.send_response(response.status)
            for key, value in response.getheaders():
                if key.lower() not in HOP_HEADERS | {'server', 'date', 'cache-control'}:
                    self.send_header(key, value)
            self.send_header('Cache-Control', 'no-store, no-transform')
            self.send_header('Connection', 'close')
            self.end_headers()
            started = True
            if self.command != 'HEAD':
                while chunk := response.read(65536):
                    self.wfile.write(chunk)
        except (OSError, TimeoutError):
            if not started:
                self.send_error(502, 'Healthcare service unavailable')
        finally:
            upstream.close()
            self.close_connection = True
        return True

    def do_GET(self):
        if not self.route():
            super().do_GET()

    def do_HEAD(self):
        if not self.route():
            super().do_HEAD()

    def do_POST(self):
        if not self.route():
            self.send_error(405)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('port', type=int, nargs='?', default=11003)
    parser.add_argument('--bind', default='127.0.0.1')
    parser.add_argument('--directory', required=True)
    parser.add_argument('--backend-port', type=int, default=11004)
    args = parser.parse_args()
    handler = partial(GatewayHandler, directory=args.directory, backend_port=args.backend_port)
    with ThreadingHTTPServer((args.bind, args.port), handler) as server:
        server.serve_forever()


if __name__ == '__main__':
    main()
