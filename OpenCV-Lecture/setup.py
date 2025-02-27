import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["mediapipe", "cv2"],
    "include_files": [
        "windowsScripts",
        "ASL.py",
        "main.py"
    ]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Or "console" for terminal applications

setup(
    name="OpenCV Workshop",
    version="0.1",
    description="Make sure to get your shpoints",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, target_name="RockStar.exe")]
)
