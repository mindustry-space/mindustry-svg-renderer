import logging
from os import remove
from pathlib import Path
from shutil import rmtree
from subprocess import Popen
from time import sleep
from typing import Any, Iterable
from xml.etree import ElementTree

from PIL import Image
from pynput.keyboard import Controller, Key
from rich.logging import RichHandler


logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

inkscape_path = Path("~/.config/inkscape").expanduser()

IGNORED_KEYS = ["id", "height", "version", "width"]
NAMESPACE = "http://www.w3.org/2000/svg"


def bundle_svgs(paths: Iterable[Path], out: Path) -> None:
    bundle = ElementTree.Element("svg")
    for key in ["xmlns", "xmlns:svg"]:
        bundle.set(key, NAMESPACE)

    for path in paths:
        tree = ElementTree.parse(path)
        root = tree.getroot()

        symbol = ElementTree.SubElement(bundle, "symbol")
        for key, value in root.attrib.items():
            if key not in IGNORED_KEYS:
                symbol.set(key, value)
        symbol.set("id", path.stem)

        for svg_path in root.findall(".//{" + NAMESPACE + "}path"):
            symbol_path = ElementTree.SubElement(symbol, "path")
            for key, value in svg_path.attrib.items():
                if key not in IGNORED_KEYS:
                    symbol_path.set(key, value)

    ElementTree.canonicalize(ElementTree.tostring(bundle), out=out.open("w"))


def count_colours(image: Image) -> int:
    # https://stackoverflow.com/a/51388568
    return len(
        {
            image.getpixel((x, y))
            for x in range(image.size[0])
            for y in range(image.size[1])
        }
    )


def get_svg_path(path: Path) -> Path:
    return path.parent / (path.stem + ".svg")


def tap_multiple(keyboard: Controller, keys: Iterable[Key]) -> None:
    for action in [keyboard.press, keyboard.release]:
        for key in keys:
            action(key)


def render(path: Path, *args: Any, **kwargs: Any) -> None:
    if inkscape_path.exists():
        rmtree(inkscape_path)

    svg_path = get_svg_path(path)
    if svg_path.exists():
        log.warn(f"Replacing file {svg_path}")
        remove(svg_path)

    colours = count_colours(Image.open(path))
    if colours > 16:
        log.warn(f"{path} has {colours} colours. Has anti-aliasing been disabled?")

    keyboard = Controller()
    with Popen(["inkscape", str(path)], *args, **kwargs):
        sleep(1)

        # Image Import Type: Embed
        keyboard.tap(Key.tab)
        keyboard.tap(Key.up)
        # Image DPI: Default import resolution
        keyboard.tap(Key.tab)
        keyboard.tap(Key.down)
        # Image Rendering Mode: Blocky
        keyboard.tap(Key.tab)
        keyboard.tap(Key.down)
        keyboard.tap(Key.down)
        # OK
        keyboard.tap(Key.enter)
        sleep(3)

        # Select all
        tap_multiple(keyboard, [Key.ctrl, "a"])

        # Trace Bitmap
        tap_multiple(keyboard, [Key.alt, Key.shift, "b"])
        sleep(1)
        # Multicolor
        keyboard.tap(Key.right)
        # Detection mode: Colors
        keyboard.tap(Key.tab)
        keyboard.tap(Key.enter)
        keyboard.tap(Key.down)
        keyboard.tap(Key.enter)
        # Scans
        keyboard.tap(Key.tab)
        keyboard.tap(Key.tab)
        keyboard.type(str(colours))
        # Stack: True
        keyboard.tap(Key.tab)
        keyboard.tap(Key.tab)
        keyboard.tap(Key.enter)
        # Remove background: False
        keyboard.tap(Key.tab)
        # All details: False
        for i in range(3):
            for _ in range(1 if i == 0 else 3):
                keyboard.tap(Key.tab)
            keyboard.tap(Key.enter)
        # Apply
        for _ in range(8):
            keyboard.tap(Key.tab)
        keyboard.tap(Key.enter)
        sleep(1)

        # Delete original image
        # Invert selection
        keyboard.tap("!")
        # Delete
        keyboard.tap(Key.delete)

        # Export...
        tap_multiple(keyboard, [Key.ctrl, Key.shift, "e"])
        sleep(1)
        # png -> svg
        keyboard.tap(Key.tab)
        keyboard.tap(Key.tab)
        keyboard.tap(Key.enter)
        keyboard.tap(Key.down)
        keyboard.tap(Key.enter)
        # Export
        keyboard.tap(Key.tab)
        keyboard.tap(Key.enter)
        sleep(3)

        # Quit
        tap_multiple(keyboard, [Key.ctrl, "q"])
        sleep(1)
        # Close without saving
        keyboard.tap(Key.tab)
        keyboard.tap(Key.enter)
