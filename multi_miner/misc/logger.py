from sys import stdout

from threading import Lock

_pr_lock = Lock()

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
        prefix = prefix.encode("utf-8")
    else:
        raise Exception("Unsupported input of type: %s", str(type(text)))

    with _pr_lock:
        buf.write(prefix + text)
        buf.flush()
