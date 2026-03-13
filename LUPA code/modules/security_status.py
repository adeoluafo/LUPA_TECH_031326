from __future__ import annotations

import pandas as pd


def build_security_status_frame(status_payload: dict) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"control": "Encryption", "status": status_payload["encryption_status"]},
            {"control": "Access Control", "status": status_payload["access_control_status"]},
            {"control": "Client Data Isolation", "status": status_payload["client_data_isolation_status"]},
            {"control": "Audit Logging", "status": status_payload["audit_logging_status"]},
        ]
    )
