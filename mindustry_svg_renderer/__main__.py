from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from subprocess import check_output

from rich.progress import track

from . import get_svg_path, render


log = getLogger(__name__)

parser = ArgumentParser()
parser.add_argument("source", nargs="+", type=Path)
parser.add_argument("-l", "--log-to", default=Path("inkscape.log"), type=Path)
parser.add_argument("-s", "--skip-existing", action='store_true')


def main() -> None:
    args = parser.parse_args()

    expected_version = "Inkscape 1.2"
    version = check_output(["inkscape", "--version"]).decode().strip()
    if version.startswith("Inkscape " + expected_version):
        log.warn(
            "You may be running an unsupported version of inkscape. "
            + f"Expected {expected_version}, found {version}"
        )

    log.info(f"Redirecting Inkscape's STDOUT and STDERR to {args.log_to}")
    with open(args.log_to, "wb") as log_to:
        for path in track(args.source):
            if args.skip_existing and get_svg_path(path).exists():
                continue
            render(path, stdout=log_to, stderr=log_to)


if __name__ == "__main__":
    main()
