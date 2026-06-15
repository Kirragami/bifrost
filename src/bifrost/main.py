import pkgutil
import importlib
import inspect
import socket
import os
import bifrost.plugins
from bifrost.core.bridge import Bridge
from bifrost.core.registry import Registry


def register_plugins(registry):
    importlib.invalidate_caches()
    importlib.reload(bifrost.plugins)
    registry.clear()
    for loader, name, is_pkg in pkgutil.iter_modules(bifrost.plugins.__path__):
        print(f"Checking in {bifrost.plugins.__path__}")
        print(name)
        module = importlib.import_module(f"bifrost.plugins.{name}")
        print("imported ig?")
        for func_name, func in inspect.getmembers(module, inspect.isfunction):
            if getattr(func, "_is_plugin", False):
                registry.register(func.__name__, func)
                print(f"[Main] Registered plugin: '{func.__name__}'")


def start_daemon():
    bridge = Bridge()
    registry = Registry(bridge)
    register_plugins(registry)
    
    print("[Bifrost] Starting daemon...")
    
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    socket_path = "/tmp/bifrost.sock"
    
    import os
    if os.path.exists(socket_path):
        os.remove(socket_path)
        
    sock.bind(socket_path)
    sock.listen(1)
    
    while True:
        conn, _ = sock.accept()
        data = conn.recv(1024).decode().strip()
        print(f"[Bifrost] Received command: {data}")
        if data == 'reload':
            register_plugins(registry)
        else:
            registry.execute(data)
        conn.close()

if __name__ == "__main__":
    start_daemon()