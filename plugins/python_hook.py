class PythonHook:
    def __init__(self, hook, code, url):
        self.url = url
        self.hook = hook
        self.code = code
        self.local = {}
