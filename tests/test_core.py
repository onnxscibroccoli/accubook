"""
Basic tests for Accubook core.
Run: python tests/test_core.py
"""

import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.accubook import AccubookWorkspace


def test_pricebook_suggest_and_insert():
    with tempfile.TemporaryDirectory() as tmp:
        ws = AccubookWorkspace(tmp)
        ws.save_csv("pricebook", [
            {"id": "1", "item": "Synthetic Oil", "unit": "qt", "cost": "5", "sell_price": "10", "trade_tag": "auto"},
        ])
        suggestions = ws.pricebook_suggest("oil")
        assert len(suggestions) == 1
        line = ws.insert_pricebook_line("job1", "1", qty=2)
        assert line["description"] == "Synthetic Oil"
        assert line["sell_price"] == "10"
        assert float(line["qty"]) == 2


def test_change_order_flow():
    with tempfile.TemporaryDirectory() as tmp:
        ws = AccubookWorkspace(tmp)
        co = ws.create_change_order("job1", [
            {"description": "Extra labor", "qty": "1", "sell_price": "100", "cost": "0"},
        ])
        assert co["status"] == "proposed"
        assert float(co["delta_total"]) == 100
        ws.acknowledge_change_order(co["id"])
        cos = ws.load_csv("change_orders")
        assert cos[0]["status"] == "acknowledged"


def test_feature_flags():
    with tempfile.TemporaryDirectory() as tmp:
        ws = AccubookWorkspace(tmp)
        assert ws.feature_enabled("enable_change_orders") is True
        ws.config["enable_change_orders"] = False
        ws.save_config()
        assert ws.feature_enabled("enable_change_orders") is False


if __name__ == "__main__":
    test_pricebook_suggest_and_insert()
    test_change_order_flow()
    test_feature_flags()
    print("All tests passed.")
