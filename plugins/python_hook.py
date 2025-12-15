class PythonHook:
    def __init__(self, hook, code):
        self.hook = hook
        self.code = code
        self.local = {}
