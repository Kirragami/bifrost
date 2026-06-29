# Bifrost

A Python wrapper around [OpenRGB](https://openrgb.org/) that turns your RGB hardware into something you can actually script. Write lighting effects as plugins, then trigger them from anywhere on your system with a single bash command.

Bifrost runs as a user-level systemd daemon. It manages the OpenRGB server, watches your USB devices, and exposes a small CLI so your shell, cron jobs, and desktop scripts can talk to your keyboard, mouse, and whatever else glows on your desk.

**Linux only for now.** macOS and Windows are not supported.

---

## How it works

```
  Terminal                    Bifrost daemon                 OpenRGB
  ────────                    ──────────────                 ───────

  bifrost call notiflash  →   loads plugin, passes       →   sets LED colors
                              client + devices                 on your hardware
```

1. You install Bifrost. It sets up a virtualenv, links the `bifrost` command into your `$PATH`, and starts a systemd user service.
2. You write plugins — plain Python functions decorated with `@plugin`.
3. You call them with `bifrost call <plugin_name>`. The CLI sends the command over a Unix socket to the running daemon, which executes your function with a live OpenRGB client and a dict of matched devices.

That's the whole model. Everything else is convenience around that loop.

---

## Prerequisites

- **Linux**
- **Python 3** with venv
- **lsusb**
- **USB permissions** for your RGB devices

---

## Installation

Pick one method. Both install Bifrost to `~/.local/share/bifrost`, link the `bifrost` binary to `~/.local/bin`, and enable a user-level systemd service.

### One-liner

```bash
curl -sSL https://bifrost.kirragami.com | bash
```

### From source

```bash
git clone https://github.com/Kirragami/bifrost.git
cd bifrost
./scripts/install.sh
```

Make sure `~/.local/bin` is on your `$PATH`. After install, the daemon starts automatically and you can run `bifrost` from any terminal.

### Uninstall

```bash
./scripts/uninstall.sh
```

This stops the service, removes the binary link, and deletes `~/.local/share/bifrost`.

---

## Quick start

```bash
# See available commands
bifrost help

# Set up a local dev workspace (symlinks to settings + plugins)
bifrost link

# Trigger a built-in plugin
bifrost call test

# Reload plugins after editing
bifrost reload
```

The `link` command creates a `bifrost/` directory in your current working directory with symlinks to the installed settings file and plugins folder. Edit files there without digging through `~/.local/share/bifrost`.

---

## CLI reference

| Command | Description |
|---|---|
| `bifrost help` | Print available commands |
| `bifrost link` | Create a `bifrost/` workspace with symlinks to settings and plugins |
| `bifrost call <name>` | Run a plugin by function name |
| `bifrost reload` | Tell the daemon to re-import all plugins |
| `bifrost setudev` | Interactive tool to write udev rules for USB devices |

---

## Writing plugins

### The basics

A plugin is a Python function in `plugins/` with two parameters and the `@plugin` decorator:

```python
from bifrost.core.registry import plugin

@plugin
def hello(client, devices):
    print(f"Connected devices: {list(devices.keys())}")
```

The function name becomes the plugin name. Call it with:

```bash
bifrost call hello
```

After adding or editing a plugin, reload:

```bash
bifrost reload
```

### Parameters

Every plugin receives the same two arguments:

| Parameter | Type | Description |
|---|---|---|
| `client` | `OpenRGBClient` | A connected OpenRGB client, ready to use |
| `devices` | `dict[str, Device]` | Devices successfully matched from your settings (see below) |

The `devices` dict is keyed by the aliases you define in `settings.py`. If a device isn't plugged in or OpenRGB can't find it, it simply won't appear in the dict — your plugin should handle that gracefully.

### Configuring devices

Edit `settings.py` (or the symlinked copy in your `bifrost/` workspace) to map friendly names to the exact device names OpenRGB reports:

```python
DEVICES = {
    "mouse": "Logitech G203 Lightsync",
    "keyboard": "Keychron K8 Pro",
}
```

Run `bifrost call test` to print whatever devices were matched:

```python
@plugin
def test(client, devices):
    print(devices)
```

Use the aliases as keys when writing effects:

```python
@plugin
def red_mouse(client, devices):
    mouse = devices.get("mouse")
    if mouse:
        mouse.set_color(255, 0, 0)
```

### Startup plugins

Want something to run automatically when the daemon starts (or when a device is hot-plugged)? Stack `@startup` on top of `@plugin`:

```python
from bifrost.core.registry import plugin, startup

@plugin
@startup
def load(client, devices):
    client.load_profile("my-profile-name")
```

Startup tasks run once at daemon boot and again whenever Bifrost detects a USB device connect/disconnect and rescans hardware.

### A real example: notification flash

The included `notiflash` plugin listens for a trigger, runs a ripple effect on the keyboard, and stops when `noticleared` is called:

```python
from bifrost.core.registry import plugin

@plugin
def notiflash(client, devices):
    kb = devices.get("keyboard")
    if kb:
        kb.set_mode("direct")
        # ... start ripple effect in a background thread

@plugin
def noticleared(client, devices):
    # ... signal the ripple thread to stop
    pass
```

Hook these up from your notification daemon, a desktop script, whatever:

```bash
bifrost call notiflash      # notification arrived
bifrost call noticleared    # notification dismissed
```

### Using OpenRGB directly

Inside a plugin you have full access to the `openrgb-python` API. Set colors, switch modes, load profiles — anything OpenRGB supports:

```python
from bifrost.core.registry import plugin
from openrgb.utils import RGBColor

@plugin
def rainbow_keys(client, devices):
    kb = devices.get("keyboard")
    if not kb:
        return
    kb.set_mode("direct")
    colors = [RGBColor(i * 10, 255 - i * 10, 128) for i in range(len(kb.leds))]
    kb.set_colors(colors)
```

---

## Device permissions

OpenRGB needs read/write access to your USB devices. Bifrost includes a helper:

```bash
bifrost setudev
```

This lists your USB devices, lets you pick them by number (comma-separated), and writes udev rules to `/etc/udev/rules.d/99-bifrost.rules`. You'll be prompted for your sudo password.

Example session:

```
Detected USB devices:
[0] Logitech, Inc. G203 (046d:c084)
[1] Keychron K8 Pro (3434:0280)
...

Enter the numbers of devices to setup (comma separated, e.g., 0, 2): 0, 1
```

Alternatively, add rules manually following the same pattern the tool generates.

---

## Logs

Bifrost logs through systemd journal. Follow live output with:

```bash
journalctl -t bifrost -f
```

Useful when a plugin throws an error or a device isn't being detected.

---

## Sample plugins

| Plugin | File | What it does |
|---|---|---|
| `test` | `plugins/test.py` | Prints matched devices — good sanity check |
| `notiflash` / `noticleared` | `plugins/notiflash.py` | Keyboard ripple on notification, stop on clear |

Read through these before writing your own. They cover the common patterns: device lookup, direct mode, and background threads.

---

## Troubleshooting

**"Bifrost daemon is not running."**
The systemd service isn't up. Check with `systemctl --user status bifrost` and start it with `systemctl --user start bifrost`.

**Device not in `devices` dict.**
Confirm the name in `settings.py` matches what OpenRGB reports (run `bifrost call test` to see what's matched). Check udev permissions with `bifrost setudev`.

**Plugin changes not taking effect.**
Run `bifrost reload` after every edit. The daemon caches imported modules.

**Permission denied on USB device.**
Run `bifrost setudev` or add udev rules manually, then unplug and replug the device.

---

## License

Bifrost is open source and free software. Use it, modify it, share it — no strings attached.
