class Registry:
    def __init__(self, bridge):
        self.bridge = bridge
        self._endpoints = {}
    
    def register(self, name, func) :
        self._endpoints[name] = func

    def execute(self, name):
        if name in self._endpoints:
            self._endpoints[name](self.bridge.client, self.bridge.devices)
        else:
            print(f"[Registry] Error: Plugin '{name}' not found")

    def clear(self):
        self._endpoints.clear()

def plugin(func):
        func._is_plugin = True
        return func