from config.info import IS_WAYLAND

if IS_WAYLAND:
    from .wayland import run
else:
    from .x11 import run

if __name__ == "__main__":
    run()
