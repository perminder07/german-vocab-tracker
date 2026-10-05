#!/usr/bin/env python3
"""Validate vocab.js (the vocabulary data file).

Usage:
    python3 validate_vocab.py                # check only, exit code 1 on errors
    python3 validate_vocab.py --assign-ids   # give new entries (no "id") the next free id, then check

Why this exists: progress is stored per entry id, so every entry needs a unique,
permanent id. Never edit or reuse an id; just add new entries without an id and run
--assign-ids.
"""
import json
import re
import sys
from pathlib import Path

VOCAB = Path(__file__).resolve().parent / "vocab.js"
CATS = ("nomen", "adjektive", "verben", "praepositionen")
PREFIX = {"nomen": "n", "adjektive": "a", "verben": "v", "praepositionen": "p"}
REQUIRED = {
    "nomen": ["id", "word", "genderClass", "meaning", "synonyms", "example"],
    "adjektive": ["id", "word", "meaning", "opposite", "example"],
    "verben": ["id", "word", "perfekt", "meaning", "example"],
    "praepositionen": ["id", "word", "prep", "meaning", "example"],
}
ID_RE = re.compile(r"^([navp])(\d{4,})$")
PREP_RE = re.compile(r"^(an|auf|aus|bei|für|in|mit|nach|über|um|unter|von|vor|zu) \+(Akk|Dat)$")


def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]*>", "", html).strip()


def load():
    text = VOCAB.read_text(encoding="utf8")
    m = re.match(r"\s*const VOCAB_DATABASE\s*=\s*(\{.*\})\s*;\s*$", text, re.S)
    if not m:
        sys.exit("vocab.js must look like: const VOCAB_DATABASE = { ... };")
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as e:
        sys.exit(f"vocab.js is not strict JSON (trailing comma? single quotes?): {e}")


def assign_ids(data):
    added = 0
    for cat in CATS:
        used = [int(ID_RE.match(e["id"]).group(2)) for e in data[cat]
                if isinstance(e.get("id"), str) and ID_RE.match(e["id"])]
        nxt = max(used, default=0) + 1
        for i, e in enumerate(data[cat]):
            if not e.get("id"):
                ne = {"id": f"{PREFIX[cat]}{nxt:04d}"}
                ne.update({k: v for k, v in e.items() if k != "id"})
                data[cat][i] = ne
                nxt += 1
                added += 1
    if added:
        VOCAB.write_text("const VOCAB_DATABASE = " + json.dumps(data, ensure_ascii=False, indent=4) + ";\n",
                         encoding="utf8")
    print(f"Assigned {added} new id(s).")


def check(data):
    errors, warnings = [], []
    seen_ids = {}
    for cat in CATS:
        if cat not in data:
            errors.append(f"missing category '{cat}'")
            continue
        pairs, words = set(), {}
        for idx, e in enumerate(data[cat]):
            where = f"{cat}[{idx}] ({strip_tags(str(e.get('word', '?')))})"
            for key in REQUIRED[cat]:
                if not isinstance(e.get(key), str) or not e[key].strip():
                    errors.append(f"{where}: missing or empty '{key}'")
            for key in e:
                if key not in REQUIRED[cat]:
                    warnings.append(f"{where}: unknown field '{key}'")
            eid = e.get("id", "")
            m = ID_RE.match(eid) if isinstance(eid, str) else None
            if not m:
                errors.append(f"{where}: bad id {eid!r} (expected like {PREFIX[cat]}0001)")
            else:
                if m.group(1) != PREFIX[cat]:
                    errors.append(f"{where}: id {eid} has wrong prefix for {cat}")
                if eid in seen_ids:
                    errors.append(f"{where}: duplicate id {eid} (also {seen_ids[eid]})")
                seen_ids[eid] = where
            word = strip_tags(str(e.get("word", "")))
            meaning = str(e.get("meaning", "")).strip().lower()
            if (word, meaning) in pairs:
                errors.append(f"{where}: exact duplicate of word + meaning")
            pairs.add((word, meaning))
            words.setdefault(word, []).append(meaning)
            if cat == "nomen":
                g = e.get("genderClass")
                if g not in ("der", "die", "das"):
                    errors.append(f"{where}: genderClass must be der/die/das")
                elif not word.lower().startswith(g + " "):
                    errors.append(f"{where}: genderClass '{g}' does not match the article")
            if cat == "verben" and not re.match(r"^(hat|ist)( sich)? \S", str(e.get("perfekt", ""))):
                warnings.append(f"{where}: perfekt should start with 'hat' or 'ist'")
            if cat == "praepositionen" and not PREP_RE.match(strip_tags(str(e.get("prep", "")))):
                warnings.append(f"{where}: unusual prep field {strip_tags(str(e.get('prep', '')))!r}")
        for w, ms in words.items():
            if len(ms) > 1:
                warnings.append(f"{cat}: '{w}' appears {len(ms)}x with different meanings: {' / '.join(ms)}")
    return errors, warnings


def main():
    data = load()
    if "--assign-ids" in sys.argv:
        assign_ids(data)
        data = load()
    errors, warnings = check(data)
    total = sum(len(data.get(c, [])) for c in CATS)
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("ERROR:  ", e)
    print(f"{total} entries, {len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
