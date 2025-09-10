#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de instalación de fstree.py como comando del sistema
Compatible Linux y Windows
Programador Eidy EV <eidyev@gmail.com>
"""
import os
import sys
import shutil
import stat

SRC_SCRIPT = os.path.join(os.path.dirname(__file__), "fstree.py")
CMD_NAME = "fstree"

def install():
    if not os.path.exists(SRC_SCRIPT):
        print(f"[ERROR] No se encontró {SRC_SCRIPT}")
        sys.exit(1)

    if os.name == "nt":
        target_dir = os.path.join(os.environ["USERPROFILE"], "Scripts")
        os.makedirs(target_dir, exist_ok=True)
        target = os.path.join(target_dir, CMD_NAME + ".py")
    else:
        target_dir = "/usr/local/bin"
        target = os.path.join(target_dir, CMD_NAME)

    shutil.copy2(SRC_SCRIPT, target)
    if os.name != "nt":
        st = os.stat(target)
        os.chmod(target, st.st_mode | stat.S_IEXEC)

    print(f"[OK] Instalado {CMD_NAME} en {target}")

def uninstall():
    if os.name == "nt":
        target = os.path.join(os.environ["USERPROFILE"], "Scripts", CMD_NAME + ".py")
    else:
        target = os.path.join("/usr/local/bin", CMD_NAME)

    if os.path.exists(target):
        os.remove(target)
        print(f"[OK] Desinstalado {CMD_NAME} desde {target}")
    else:
        print(f"[WARN] No se encontró {target}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Instala o desinstala fstree.py")
    parser.add_argument("--uninstall", action="store_true", help="Desinstalar fstree")
    args = parser.parse_args()

    if args.uninstall:
        uninstall()
    else:
        install()

if __name__ == "__main__":
    main()

