from datetime import date

from marketing_pipeline.connectors.simulated import SimulatedAdConnector


def test_simulated_connector_is_deterministic_and_labeled():
    connector = SimulatedAdConnector("google_ads", seed=7)
    first = connector.extract(date(2026, 1, 1), date(2026, 1, 2)).rows
    second = connector.extract(date(2026, 1, 1), date(2026, 1, 2)).rows
    assert first == second
    assert len(first) == 4
    assert all(row["is_simulated"] for row in first)

