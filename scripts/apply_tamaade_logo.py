#!/usr/bin/env python3
"""
Simple script to copy Tamaade logo over existing nxtbn logo files.
Run from repo root with: python scripts\apply_tamaade_logo.py
"""
import shutil
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / 'static' / 'images'

def apply():
    files = [
        ('tamaade.png', 'nxtbn_black.png'),
        ('tamaade.png', 'nxtbn_white.png'),
        ('tamaade_black.svg', 'nxtbn_black.svg')
    ]
    for src, dest in files:
        src_path = STATIC_DIR / src
        dest_path = STATIC_DIR / dest
        if src_path.exists():
            if dest_path.exists():
                shutil.copy(dest_path, str(dest_path) + '.bak')
            shutil.copy(src_path, dest_path)
            print(f'Copied {src_path} -> {dest_path}')
        else:
            print(f'Source missing: {src_path} (skipping)')

if __name__ == '__main__':
    apply()
