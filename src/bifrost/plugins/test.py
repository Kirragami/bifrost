from bifrost.core.registry import plugin

@plugin
def test(client, devices):
    print(devices)
    

def printer():
    print("This is test endpoint")