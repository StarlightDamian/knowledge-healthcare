"""Exercise exact-prefix routing against two real local HTTP servers."""
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from src.ops.serve_gateway import GatewayHandler


class GatewayTests(unittest.TestCase):
    def test_prefix_stream_and_unrelated_static_routes(self):
        received = []
        class Backend(BaseHTTPRequestHandler):
            def do_GET(self):
                received.append((self.path, self.headers.get('Host'), b''))
                self.send_response(200); self.send_header('Content-Length', '7'); self.end_headers()
                self.wfile.write(b'medical')
            def do_POST(self):
                body = self.rfile.read(int(self.headers['Content-Length']))
                received.append((self.path, self.headers.get('Host'), body))
                self.send_response(200); self.send_header('Content-Type', 'text/csv'); self.end_headers()
                self.wfile.write(body)
            def log_message(self, *args): pass
        class QuietGateway(GatewayHandler):
            def log_message(self, *args): pass
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'home').mkdir(); (root/'home/index.html').write_text('homepage')
            (root/'fitness').mkdir(); (root/'fitness/index.html').write_text('fitness')
            backend = ThreadingHTTPServer(('127.0.0.1', 0), Backend)
            gateway = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietGateway, directory=directory, backend_port=backend.server_port))
            threads = [threading.Thread(target=s.serve_forever, daemon=True) for s in (backend, gateway)]
            for t in threads: t.start()
            base = f'http://127.0.0.1:{gateway.server_port}'
            try:
                with urlopen(base+'/home/') as response: self.assertEqual(response.read(), b'homepage')
                with urlopen(base+'/fitness/') as response:
                    self.assertEqual(response.read(), b'fitness')
                    self.assertIn('no-transform', response.headers['Cache-Control'])
                with urlopen(base+'/healthcare/api/v1/catalog?release_id=test') as response:
                    self.assertEqual(response.read(), b'medical')
                    self.assertEqual(response.headers['Cache-Control'], 'no-store, no-transform')
                # A selected set near full-catalog size must not hit a smaller gateway body cap.
                body = b'ids=' + b'a' * 100000
                with urlopen(Request(base+'/healthcare/api/v1/exports/conditions.csv',data=body)) as response:
                    self.assertEqual(response.read(), body)
                self.assertEqual(received[0][0], '/healthcare/api/v1/catalog?release_id=test')
                self.assertEqual(received[0][1], f'127.0.0.1:{gateway.server_port}')
                for path in ('/healthcare-other/', '/%68ealthcare/', '/missing/'):
                    with self.assertRaises(HTTPError) as caught: urlopen(base+path)
                    self.assertEqual(caught.exception.code,404)
                self.assertEqual(len(received), 2)
            finally:
                for s in (gateway, backend): s.shutdown(); s.server_close()
                for t in threads: t.join(timeout=3)


if __name__ == '__main__': unittest.main()
