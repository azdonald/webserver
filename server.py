import BaseHTTPServer, os

class ServerException:
    pass

class base_case:
    def handle_file(self, handler, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            handler.handle_error(msg)
    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        assert False, 'Not Implemented'
    
    def act(self, handler):
        assert False, 'Not Implemented'

    

class case_no_file(base_case):    

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))

class case_existing_file(base_case):
    
    def test(self, handler):
        return os.path.exists(handler.full_path)

    def act(self, handler):
        self.handle_file(handler,handler.full_path)

class case_always_fail(base_case):
    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))

class case_directory_index_file(base_case):
    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
        os.path.isfile(self.index_path(handler))
    
    def act(self, handler):
        self.handle_file(handler,self.index_path(handler))

class case_directory_no_index_file(base_case):
    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
        os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.list_dir(handler.full_path)

class case_cgi_file(base_case):
    def test(self, handler):
        print 'i got called'
        return os.path.isfile(handler.full_path) and \
        handler.full_path.endswith('.py')

    def act(self, handler):
        handler.run_cgi(handler.full_path)   

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    Cases = [case_no_file(), case_existing_file(),
            case_directory_index_file(),
            case_directory_no_index_file(), case_cgi_file(),
            case_always_fail()]


    def do_GET(self):
        try:
            self.full_path = os.getcwd() + self.path
            for case in self.Cases:
                handler = case
                if handler.test(self):
                    handler.act(self)
                    break

        except Exception as msg:
            self.handle_error(msg)
    
    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    Error_Page = """\
        <html>
        <body>
        <hi>Error accessing {path} </h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path,msg=msg)
        self.send_content(content, 404)

    def run_cgi(self, full_path):
        cmd = "Python " + full_path
        child_stdin, child_stdout = os.popen2(cmd)
        child_stdin.close()
        data = child_stdout.read()
        child_stdout.close()
        self.send_content(data)

    

if __name__ == '__main__':
    serverAddress = ('', 8090)
    server = BaseHTTPServer.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever();