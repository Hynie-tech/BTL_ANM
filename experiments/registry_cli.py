"""Quan ly phien ban mo hinh:  python experiments/registry_cli.py list | promote <model> <vN> | rollback <model>"""
import sys

from _common import *  # noqa: F401,F403


def main():
    cfg, _ = setup("registry")
    reg = registry(cfg)
    a = sys.argv[1:]
    if not a or a[0] == "list":
        for name, vs in reg._read()["models"].items():
            for e in vs:
                m = e["metrics"]
                print(f"{name:14s} {e['version']:3s} {e['stage']:10s} F1={m.get('f1', float('nan')):.4f} "
                      f"parent={e['parent_version']} | {e['notes']}")
    elif a[0] == "promote" and len(a) == 3:
        reg.promote(a[1], a[2]); print("OK")
    elif a[0] == "rollback" and len(a) == 2:
        print("Rolled back to", reg.rollback(a[1]))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
