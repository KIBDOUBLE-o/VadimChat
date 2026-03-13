class PythonHook:
    def __init__(self, hook, code, url):
        self.url = url
        self.hook = hook
        self.code = code
        self.local = {}
        self.load()

    def load(self):
        try:
            exec(self.code, self.local, self.local)
        except: pass
