"""
JARVIS File & Folder Launcher
Phase 2.2 - Step 5.3
"""

from __future__ import annotations

import os
from pathlib import Path

from tools.path_resolver import PathResolver
from tools.path_searcher import PathSearcher


class FileLauncher:

    resolver = PathResolver()

    SPECIAL_FOLDERS = {
        # Desktop
        "desktop": Path.home() / "Desktop",

        # Downloads
        "downloads": Path.home() / "Downloads",
        "download": Path.home() / "Downloads",

        # Documents
        "documents": Path.home() / "Documents",
        "document": Path.home() / "Documents",

        # Pictures
        "pictures": Path.home() / "Pictures",
        "picture": Path.home() / "Pictures",
        "photos": Path.home() / "Pictures",
        "photo": Path.home() / "Pictures",

        # Videos
        "videos": Path.home() / "Videos",
        "video": Path.home() / "Videos",

        # Music
        "music": Path.home() / "Music",
        "songs": Path.home() / "Music",
    }

    @classmethod
    def open(cls, target: str):

        target = target.strip().strip('"').strip("'")

        if not target:
            return {
                "status": "error",
                "type": "file_launcher",
                "message": "No file or folder specified."
            }

        # -------------------------
        # Resolve target path
        # -------------------------

        resolved = cls.resolver.resolve(target)

        if resolved is not None:

            path = Path(resolved)

        else:

            # Backward-compatible fallback
            key = target.lower()

            if key in cls.SPECIAL_FOLDERS:

                path = cls.SPECIAL_FOLDERS[key]

            else:

                path = Path(
                    os.path.expandvars(
                        os.path.expanduser(target)
                    )
                )

        # -------------------------
        # Check existence
        # -------------------------

        if not path.exists():

            found_path = PathSearcher.find(target)

            if found_path is not None:
                path = found_path

            else:
                return {
                    "status": "error",
                    "type": "file_launcher",
                    "target": target,
                    "message": f"File or folder not found: {target}"
                }

        # -------------------------
        # Open with Windows
        # -------------------------

        try:

            os.startfile(str(path))

            return {
                "status": "success",
                "type": "file_launcher",
                "target": target,
                "path": str(path),
                "kind": (
                    "folder"
                    if path.is_dir()
                    else "file"
                )
            }

        except Exception as e:

            return {
                "status": "error",
                "type": "file_launcher",
                "target": target,
                "message": str(e)
            }