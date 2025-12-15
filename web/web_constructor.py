class WebConstructor:
    def __init__(self):
        self.index = []
        self.style = []
        self.script = []

    def include_index(self, index):
        self.index.append(index)

    def include_style(self, style):
        self.style.append(style)

    def include_script(self, script):
        self.script.append(script)

    def build(self) -> str:
        index = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link rel="icon" href="icon.ico" type="image/png">
        </head>
        <style>
        {'\n'.join(self.style)}
        </style>
        <body>
        {'\n'.join(self.index)}
        </body>
        <script>
        {'\n'.join(self.script)}
        </script>
        </html
        """
        return index