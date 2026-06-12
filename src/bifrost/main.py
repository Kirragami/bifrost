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
    for loader, name, is_pkg in pkgutil.iter_modules(bifrost.plugins.__path__):
        print(f"Checking in {bifrost.plugins.__path__}")
        print(name)
        module = importlib.import_module(f"bifrost.plugins.{name}")
        print("imported ig?")
        for func_name, func in inspect.getmembers(module, inspect.isfunction):
            if func.__module__ == module.__name__ and func_name == name:
                registry.register(func_name, func)
                print(f"[Main] Auto-registered: '{func_name}'")


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