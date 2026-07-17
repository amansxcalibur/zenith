import sys
import subprocess
from pathlib import Path
from loguru import logger
from PIL import Image

from .helpers import get_screen_resolution_i3

from config.config import config
from config.info import ROOT_DIR, CACHE_DIR as cache_dir_str

CACHE_DIR = Path(cache_dir_str)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOCKSCREEN_RESOURCE_DIR = Path(CACHE_DIR) / "lockscreen"
LOCKSCREEN_IMG_FILE = LOCKSCREEN_RESOURCE_DIR / "lockscreen.png"


def lock_screen():
    import os

    if config.system.LOCKSCREEN == "zenith":
        current_env = os.environ.copy()
        current_env["PYTHONPATH"] = (
            str(ROOT_DIR) + os.pathsep + current_env.get("PYTHONPATH", "")
        )

        lock_path = ROOT_DIR / "lock"

        if lock_path.exists():
            subprocess.Popen(
                [sys.executable, "-m", "lock"],
                env=current_env,
                start_new_session=True,
            )
    else:
        lock_with_i3lock()


def get_cached_lockscreen(
    wallpaper: Path,
) -> Path:
    # width, height = get_screen_resolution()

    # mtime = int(wallpaper.stat().st_mtime)
    # cache_name = f"lock_{mtime}_{width}x{height}.png"
    # cached = CACHE_DIR / cache_name

    # if cached.exists():
    #     return cached

    if LOCKSCREEN_IMG_FILE.exists():
        return LOCKSCREEN_IMG_FILE
    else:
        # maybe I shouldn't do this (causes delay)
        return generate_lockscreen_image(wallpaper)


def lock_with_i3lock() -> None:
    from modules.wallpaper import WallpaperService

    wallpaper = Path(WallpaperService().get_wallpaper_path())
    cached_img = get_cached_lockscreen(wallpaper)

    subprocess.Popen(
        ["i3lock", "-i", str(cached_img)],
        start_new_session=True,
    )


def generate_lockscreen_image(image_path: str | Path) -> Path | None:
    try:
        LOCKSCREEN_RESOURCE_DIR.mkdir(parents=True, exist_ok=True)

        tmp = LOCKSCREEN_IMG_FILE.with_suffix(".tmp")
        width, height = get_screen_resolution_i3()

        with Image.open(image_path) as img:
            img = img.convert("RGB")
            iw, ih = img.size

            scale = max(width / iw, height / ih)
            new_size = (int(iw * scale), int(ih * scale))
            img = img.resize(new_size, Image.LANCZOS)

            # Center crop
            left = (img.width - width) // 2
            top = (img.height - height) // 2
            right = left + width
            bottom = top + height

            img = img.crop((left, top, right, bottom))

            LOCKSCREEN_IMG_FILE.parent.mkdir(parents=True, exist_ok=True)
            img.save(tmp, "PNG")

        tmp.replace(LOCKSCREEN_IMG_FILE)

        # returning in case we do hashing and caching later
        return LOCKSCREEN_IMG_FILE

    except Exception as e:
        logger.error(f"Lockscreen generation failed for {image_path}: {e}")
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise
