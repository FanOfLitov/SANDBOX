"""Утилиты: загрузка/генерация флагов, поиск флага."""

from __future__ import annotations

import os
import random
import uuid
from collections import namedtuple
from pathlib import Path

FlagsRecord = namedtuple("FlagsRecord", ["flag", "service", "flag_type"])

FLAGS_FILE = Path("flags/flags.txt") #/opt/

# Кэшируем в память
_flags_cache: list[FlagsRecord] = []

# Статический список лабораторных (должно совпадать с compose)
LABS = [
    "dvwa",
    "juice-shop",
    "wordpress",
]

FLAG_TYPES = ["easy", "medium", "hard"]


#––––––––––––––––––––––––––––––––––––––––––––––––––
#   Генерация / чтение файла с флагами
#––––––––––––––––––––––––––––––––––––––––––––––––––

def _generate_flags() -> list[FlagsRecord]:
    """Случайно генерируем по 3 флага на сервис."""
    records: list[FlagsRecord] = []
    for lab in LABS:
        for t in FLAG_TYPES:
            rand = uuid.uuid4().hex[:12]
            flag = f"FLAG{{{rand}}}"
            records.append(FlagsRecord(flag=flag, service=lab, flag_type=t))
    return records


def load_flags(force_reload: bool = False) -> list[FlagsRecord]:
    """Читаем (или создаём) flags.txt, кладём в кэш."""
    global _flags_cache
    if _flags_cache and not force_reload:
        return _flags_cache

    # Создаём файл при первом запуске
    if not FLAGS_FILE.exists():
        FLAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        generated = _generate_flags()
        with FLAGS_FILE.open("w", encoding="utf-8") as fh:
            for rec in generated:
                fh.write(f"{rec.flag};{rec.service};{rec.flag_type}\n")
        _flags_cache = generated
        return _flags_cache

    # Читаем существующий файл
    records: list[FlagsRecord] = []
    with FLAGS_FILE.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                flag, service, flag_type = line.split(";", 2)
            except ValueError:
                continue  # пропускаем битые строки
            records.append(FlagsRecord(flag=flag, service=service, flag_type=flag_type))
    _flags_cache = records
    return _flags_cache


#––––––––––––––––––––––––––––––––––––––––––––––––––
#   Поиск флага
#––––––––––––––––––––––––––––––––––––––––––––––––––

def lookup_flag(flag: str) -> FlagsRecord | None:
    flag = flag.strip()
    if not flag:
        return None
    for rec in _flags_cache or load_flags():
        if rec.flag == flag:
            return rec
    return None

def generate_and_save_flags() -> list[FlagsRecord]:
    """Создаёт и сохраняет флаги, возвращает их."""
    flags = _generate_flags()
    FLAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with FLAGS_FILE.open("w", encoding="utf-8") as fh:
        for rec in flags:
            fh.write(f"{rec.flag};{rec.service};{rec.flag_type}\n")
    global _flags_cache
    _flags_cache = flags
    return flags
#––––––––––––––––––––––––––––––––––––––––––––––––––
#   Доп. утилки
#––––––––––––––––––––––––––––––––––––––––––––––––––

def total_flags() -> int:
    return len(_flags_cache or load_flags())



