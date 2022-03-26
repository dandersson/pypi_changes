from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from rich.console import Console
from rich.table import Table

from ._cli import Options
from ._pkg import Package


class Reversor:
    def __init__(self, obj: str) -> None:
        self.obj = obj

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Reversor) and other.obj == self.obj

    def __lt__(self, other: Reversor) -> bool:
        return other.obj < self.obj


def get_sorted_pkg_list(distributions: Iterable[Package], options: Options, now: datetime) -> Iterable[Package]:
    if options.sort in ["a", "alphabetic"]:
        return sorted(distributions, key=lambda v: v.name.lower())
    return sorted(distributions, key=lambda v: (v.last_release_at or now, Reversor(v.name)), reverse=True)


def print_tree(distributions: Iterable[Package], options: Options) -> None:
    now = datetime.now(timezone.utc)
    table = Table()
    table.add_column("Package")
    table.add_column("Version", justify="right")
    table.add_column("Released", justify="center")
    table.add_column("Newest", justify="right")
    table.add_column("Released", justify="center")
    for pkg in get_sorted_pkg_list(distributions, options, now):
        row = [pkg.name, pkg.version]
        last_release = pkg.last_release
        if last_release is not None:  # pragma: no branch
            if last_release["version"] != pkg.version and pkg.info is not None:
                for a_version, releases in pkg.info["releases"].items():  # pragma: no branch
                    first_release_at = releases[0]["upload_time_iso_8601"]
                    if a_version == pkg.dist.version and first_release_at is not None:
                        row += [f"{first_release_at:%Y-%m-%d}"]
                        break
                row += [last_release['version']]
            if last_release["upload_time_iso_8601"] is not None:  # pragma: no branch
                row += [f"{last_release['upload_time_iso_8601']:%Y-%m-%d}"]
        table.add_row(*row)
    console = Console()
    console.print(table)


__all__ = [
    "print_tree",
]
