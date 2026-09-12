import os
import subprocess
import sys
import PyInstaller.__main__


def build_ui(base_dir: str):
    ui_file = os.path.join(base_dir, "app/vcalc.ui")
    ui_py = os.path.join(base_dir, "app/vcalc_ui.py")
    qrc_file = os.path.join(base_dir, "app/vcalc.qrc")
    rc_py = os.path.join(base_dir, "app/vcalc_rc.py")

    print(f"Compiling UI: {ui_file} -> {ui_py}")
    subprocess.check_call([sys.executable, "-m", "PyQt5.uic.pyuic", ui_file, "-o", ui_py])

    print(f"Compiling resources: {qrc_file} -> {rc_py}")
    subprocess.check_call([sys.executable, "-m", "PyQt5.pyrcc_main", qrc_file, "-o", rc_py])


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    # print(f"Using base directory: {base_dir}")
    # build_ui(base_dir)

    print("Building application with PyInstaller...")
    spec_path = os.path.join(base_dir, "main.spec")
    args = [spec_path, "--noconfirm"] + sys.argv[1:]
    PyInstaller.__main__.run(args)


if __name__ == "__main__":
    main()
