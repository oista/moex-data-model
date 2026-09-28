"""Fail-closed publish gate CLI — delegates to moex_model_cli.gates."""

from __future__ import annotations

from moex_model_cli.gates.publish_gate import main

if __name__ == "__main__":
    raise SystemExit(main())
