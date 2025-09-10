#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fstree.py - Exporta o reconstruye estructuras de directorios estilo 'tree'.
Programador Eidy EV <eidyev@gmail.com>
"""
from __future__ import annotations
import os
import sys
import re
import argparse
from typing import List, Tuple, Dict, Set

DEFAULT_CONTENT = {
    ".php": "<?php\n\n",
    ".yaml": "# YAML configuration\n",
    ".yml": "# YAML configuration\n",
    ".json": "{\n}\n",
    ".html": "<!DOCTYPE html>\n<html>\n<head>\n</head>\n<body>\n</body>\n</html>\n",
    ".twig": "{# Twig template #}\n",
    ".md": "# Document\n",
    ".txt": "",
    ".py": "#!/usr/bin/env python3\n\n",
    ".sh": "#!/bin/bash\n\n",
    ".bat": "@echo off\n",
    "": ""
}

DEFAULT_EXCLUDES = {".git", "node_modules", "vendor", "__pycache__"}

def normalize_relpath(parts: List[str]) -> str:
    return os.path.normpath(os.path.join(*parts)) if parts else ""

def parse_tree_file(file_path: str) -> Tuple[List[str], Dict[str, str]]:
    """Parses the tree-style file and returns paths and optional file contents."""
    paths: List[str] = []
    contents: Dict[str, str] = {}
    stack: List[str] = []
    collecting = False
    buffer: List[str] = []
    current_file_rel: str | None = None
    connector_re = re.compile(r'(├──|└──)\s*(.*)$')

    with open(file_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            if line.strip() == ">>>":
                collecting = True
                buffer = []
                continue
            if line.strip() == "<<<":
                collecting = False
                if current_file_rel:
                    contents[current_file_rel] = "\n".join(buffer) + ("\n" if buffer and not buffer[-1].endswith("\n") else "")
                current_file_rel = None
                buffer = []
                continue
            if collecting:
                idx = line.find("    ")
                content_line = line[idx + 4 :] if idx >= 0 else line.lstrip()
                buffer.append(content_line)
                continue
            no_comment = line.split("#", 1)[0].rstrip()
            if not no_comment.strip():
                continue
            idxs = [i for i in (no_comment.find("├"), no_comment.find("└")) if i >= 0]
            if idxs:
                conn_idx = min(idxs)
                depth = (conn_idx // 4) + 1
                m = connector_re.search(no_comment)
                name = m.group(2) if m else no_comment[conn_idx + 1 :].strip()
            else:
                depth = 0
                name = no_comment.strip()
            name = name.rstrip()
            if len(stack) > depth:
                stack = stack[:depth]
            if name.endswith("/"):
                part = name.rstrip("/")
                parts = stack + [part] if part else stack[:]
                rel = normalize_relpath(parts) + os.sep
                paths.append(rel)
                stack = stack + [part] if part else stack
            else:
                parts = stack + [name]
                rel = normalize_relpath(parts)
                paths.append(rel)
                current_file_rel = rel
    return paths, contents

def create_structure(paths: List[str], base_dir: str, contents: Dict[str, str], verbose: bool = False, overwrite: bool = False):
    """Crea directorios y archivos a partir de la lista de paths y contenidos."""
    def get_content_for(rel: str) -> str | None:
        for k in [rel, rel.replace(os.sep, "/"), rel.replace("/", os.sep), os.path.normpath(rel)]:
            if k in contents:
                return contents[k]
        return None

    for rel in paths:
        target = os.path.normpath(os.path.join(base_dir, rel))
        if rel.endswith(os.sep):
            os.makedirs(target, exist_ok=True)
            if verbose:
                print(f"[DIR] {target}")
        else:
            parent = os.path.dirname(target)
            if parent and not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)
            exists = os.path.exists(target)
            should_write = (not exists) or overwrite
            if should_write:
                content = get_content_for(rel)
                if content is None:
                    _, ext = os.path.splitext(rel.lower())
                    content = DEFAULT_CONTENT.get(ext, "")
                with open(target, "w", encoding="utf-8") as f:
                    f.write(content)
                if verbose:
                    print(f"[WRITE] {'OVERWRITE' if exists and overwrite else 'CREATE'} {target}")
            elif verbose:
                print(f"[SKIP] {target} (ya existe)")

def dump_structure(base_dir: str, output_file: str, excludes: Set[str], with_content: bool = False, verbose: bool = False, dirs_only: bool = False, max_level: int | None = None):
    """Exporta la estructura de un directorio a un archivo de texto."""
    def list_entries(path: str) -> List[str]:
        try:
            return sorted([e for e in os.listdir(path) if e not in excludes])
        except Exception:
            return []

    with open(output_file, "w", encoding="utf-8") as out:
        root_name = os.path.basename(os.path.normpath(base_dir)) or os.path.normpath(base_dir)
        out.write(f"{root_name}/\n")
        if verbose:
            print(f"[ROOT] {base_dir}")

        def walk(dir_path: str, prefix: str = "", current_level: int = 0):
            if max_level is not None and current_level >= max_level:
                return
            entries = list_entries(dir_path)
            if dirs_only:
                entries = [e for e in entries if os.path.isdir(os.path.join(dir_path, e))]
            total = len(entries)
            for idx, entry in enumerate(entries):
                full = os.path.join(dir_path, entry)
                connector = "└── " if idx == total - 1 else "├── "
                is_dir = os.path.isdir(full)
                name_out = f"{entry}/" if is_dir else entry
                out.write(f"{prefix}{connector}{name_out}\n")
                if verbose:
                    print(f"[SCAN] {full}")
                if is_dir:
                    extension = "    " if idx == total - 1 else "│   "
                    walk(full, prefix + extension, current_level + 1)
                elif with_content and not dirs_only:
                    try:
                        with open(full, "r", encoding="utf-8") as rf:
                            content = rf.read().rstrip("\n")
                        if content != "":
                            out.write(f"{prefix}    >>>\n")
                            for cl in content.split("\n"):
                                out.write(f"{prefix}    {cl}\n")
                            out.write(f"{prefix}    <<<\n")
                    except Exception as e:
                        if verbose:
                            print(f"[WARN] no se pudo leer {full}: {e}", file=sys.stderr)

        walk(base_dir)

def load_excludes(exclude_list: str | None, exclude_file: str | None) -> Set[str]:
    excludes = set(DEFAULT_EXCLUDES)
    if exclude_file and os.path.isfile(exclude_file):
        with open(exclude_file, "r", encoding="utf-8") as f:
            for ln in f:
                name = ln.split("#", 1)[0].strip()
                if name:
                    excludes.add(name)
    if exclude_list:
        for name in exclude_list.split(","):
            n = name.strip()
            if n:
                excludes.add(n)
    return excludes

def test_process(mode: str, entrada: str, salida: str, verbose: bool = False, dirs_only: bool = False, max_level: int | None = None):
    """Valida el proceso dump o build."""
    errors = []

    if mode == "build":
        paths, _ = parse_tree_file(entrada)
        for rel in paths:
            path_check = os.path.join(salida, rel)
            if not os.path.exists(path_check):
                errors.append(f"No existe: {path_check}")
            elif verbose:
                print(f"[CHECK] Existe: {path_check}")

    elif mode == "dump":
        actual_paths = []
        for root, dirs, files in os.walk(entrada):
            level = root.replace(entrada, "").count(os.sep)
            if max_level is not None and level >= max_level:
                dirs[:] = []
            if dirs_only:
                files = []
            for d in dirs:
                actual_paths.append(os.path.relpath(os.path.join(root, d), entrada) + os.sep)
            for f in files:
                actual_paths.append(os.path.relpath(os.path.join(root, f), entrada))
        gen_paths, _ = parse_tree_file(salida)
        missing_in_file = [p for p in actual_paths if p not in gen_paths]
        extra_in_file = [p for p in gen_paths if p not in actual_paths]

        if missing_in_file:
            errors.append(f"Faltan en archivo generado: {missing_in_file}")
        if extra_in_file:
            errors.append(f"Sobran en archivo generado: {extra_in_file}")
        if verbose:
            print(f"[CHECK] Paths reales: {len(actual_paths)}")
            print(f"[CHECK] Paths en archivo: {len(gen_paths)}")

    if errors:
        print("TEST: Se encontraron errores:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("TEST: Todo correcto ✅")
        return True

def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fstree",
        usage=(
            "fstree [MODE] [OPTION]... SOURCE DEST\n"
            "  or: fstree [MODE] [OPTION]... -t DEST SOURCE...\n"
            "Modos:\n"
            "  dump    Exporta un directorio a un archivo .txt\n"
            "  build   Reconstruye un directorio desde un archivo .txt\n"
            "  test    Valida un proceso build o dump"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Muestra acciones detalladas")
    parser.add_argument("--overwrite", action="store_true", help="Sobrescribir archivos existentes (solo build)")
    parser.add_argument("--with-content", action="store_true", help="Incluir contenido de archivos (solo dump)")
    parser.add_argument("-d", "--dirs-only", action="store_true", help="Listar solo directorios (omitirá archivos) en dump")
    parser.add_argument("-L", "--level", type=int, default=None, help="Limitar profundidad de directorios (solo dump)")
    parser.add_argument("--exclude", help="Lista separada por comas de nombres a excluir (ej: .git,node_modules)")
    parser.add_argument("--exclude-file", help="Archivo que contiene nombres de exclusión")
    parser.add_argument("mode", choices=["dump", "build", "test"], help="Modo de operación: dump, build o test")
    parser.add_argument("entrada", help="Archivo de entrada o directorio según el modo")
    parser.add_argument("salida", help="Archivo de salida o directorio según el modo")
    parser.add_argument("--test-mode", choices=["dump","build"], default="build", help="Indica qué proceso validar cuando se usa --mode test")
    return parser

def main():
    parser = build_cli()
    args = parser.parse_args()

    excludes = load_excludes(args.exclude, args.exclude_file)

    if args.mode == "dump":
        dump_structure(
            base_dir=args.entrada,
            output_file=args.salida,
            excludes=excludes,
            with_content=args.with_content,
            verbose=args.verbose,
            dirs_only=args.dirs_only,
            max_level=args.level
        )
    elif args.mode == "build":
        paths, contents = parse_tree_file(args.entrada)
        create_structure(paths, args.salida, contents, verbose=args.verbose, overwrite=args.overwrite)
    elif args.mode == "test":
        success = test_process(
            mode=args.test_mode,
            entrada=args.entrada,
            salida=args.salida,
            verbose=args.verbose,
            dirs_only=args.dirs_only,
            max_level=args.level
        )
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
