import re
from datetime import datetime
from typing import Dict, Any, List


# -----------------------------
# Helpers
# -----------------------------

def _normalize_ssn(ssn: str) -> str:
    """
    Normalize SSN to XXX-XX-XXXX if possible.
    """
    if not ssn:
        return ""

    digits = re.sub(r"\D", "", ssn)
    if len(digits) == 9:
        return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"
    return ssn


def _calculate_age_from_dob(dob: str) -> int:
    """
    Calculates age if DOB is valid.
    """
    try:
        dob_dt = datetime.strptime(dob, "%m/%d/%Y")
        today = datetime.today()
        return today.year - dob_dt.year - (
            (today.month, today.day) < (dob_dt.month, dob_dt.day)
        )
    except Exception:
        return 0


def _is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, list) and len(value) == 0:
        return True
    return False


# -----------------------------
# Core Validator
# -----------------------------

def validate_extracted_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Soft validator:
    - Normalizes fields
    - Adds warnings instead of deleting data
    - Keeps ALL fields
    """

    warnings: List[str] = []

    identity = data.get("identity", {})

    # ---- Name ----
    if _is_empty(identity.get("name")):
        warnings.append("identity.name is missing")

    # ---- DOB & Age ----
    dob = identity.get("dob", "")
    age = identity.get("age", 0)

    if dob:
        calculated_age = _calculate_age_from_dob(dob)
        if calculated_age > 0:
            if age == 0 or abs(calculated_age - age) > 1:
                warnings.append(
                    f"Age mismatch: provided={age}, calculated={calculated_age}"
                )
                identity["age"] = calculated_age
    else:
        if age:
            warnings.append("Age present but DOB missing")

    # ---- SSN ----
    identity["ssn"] = _normalize_ssn(identity.get("ssn", ""))

    # ---- DL ----
    if identity.get("DL") and len(identity["DL"]) < 4:
        warnings.append("DL looks suspiciously short")

    # ---- Addresses sanity ----
    addresses = data.get("addresses_timeline", [])
    for i, addr in enumerate(addresses):
        if _is_empty(addr.get("place")):
            warnings.append(f"addresses_timeline[{i}] missing place")

    # ---- Phones ----
    phones = data.get("contacts", {}).get("phones", [])
    for p in phones:
        digits = re.sub(r"\D", "", p)
        if len(digits) < 10:
            warnings.append(f"Invalid phone detected: {p}")

    # ---- Emails ----
    emails = data.get("contacts", {}).get("emails", [])
    for e in emails:
        if "@" not in e:
            warnings.append(f"Invalid email detected: {e}")

    # ---- Credit KPIs sanity ----
    kpis = data.get("kpis", {})
    if kpis.get("open_accounts", 0) < 0:
        warnings.append("open_accounts < 0")
    if kpis.get("current_total_balance", 0) < 0:
        warnings.append("Negative balance detected")

    # ---- Criminal history sanity ----
    crime = data.get("criminal_history", {}).get("crime", "")
    if crime and len(crime) < 3:
        warnings.append("Crime field too short to be meaningful")

    # -----------------------------
    # Attach validation metadata
    # -----------------------------

    data["_validation"] = {
        "status": "ok" if not warnings else "needs_review",
        "warning_count": len(warnings),
        "warnings": warnings,
        "validated_at": datetime.utcnow().isoformat() + "Z"
    }

    return data
