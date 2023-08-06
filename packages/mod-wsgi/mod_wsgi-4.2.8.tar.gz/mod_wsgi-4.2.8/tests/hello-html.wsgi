def application(environ, start_response):
    status = '200 OK'
    output = b'<html><body>Hello World!</body></html>'

    #response_headers = [('Content-type', 'text/html'),
    #                    ('Content-Length', str(len(output)))]
    response_headers = [('Content-type', 'text/html')]
    start_response(status, response_headers)

    #yield output

    yield b'<html>'
    yield b'<head>'
    yield b'<meta charset="UTF-8">'
    yield b'<meta http-equiv="X-UA-Compatible" content="IE=edge">'
    yield b'</head>'
    yield b'<body>'
    yield b'Hello World!'
    yield b'</body>'
    yield b'</html>'
