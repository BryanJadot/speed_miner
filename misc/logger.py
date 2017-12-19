from sys import stdout

def pr(text, prefix=None, stream=stdout):
    if prefix:
        assert isinstance(prefix, str)
        prefix = "\033[94m[%s] \033[0m" % prefix
    else:
        prefix = ""

    if isinstance(text, str):
        buf = stream
    elif isinstance(text, bytes):
        buf = stream.buffer
        prefix = bytes(prefix)

    buf.write(prefix + text)
    buf.flush()
