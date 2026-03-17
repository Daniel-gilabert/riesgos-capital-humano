import os
import pathlib

# Default configuration values
DEFAULT_LOGO_PATH = "assets/logo.png"
DEFAULT_APP_NAME = "TU RIESGO A RAYA FUNDACION PRODE"
DEFAULT_DATA_SOURCE = "worktime"  # excel | worktime | mixed
DEFAULT_WORKTIME_TABLE = "worktime_citas"
DEFAULT_WORKTIME_EMPLOYEES_TABLE = "trrfp_empleados"
DEFAULT_ANALISIS_TABLE = "trrfp_analisis"
DEFAULT_CITAS_DETALLE_TABLE = "trrfp_citas_analizadas"
DEFAULT_ACCESS_KEYS_TABLE = "trrfp_access_keys"

def load_runtime_env() -> None:
    """Load environment variables from .env files and Streamlit secrets"""
    try:
        import streamlit as st
        secrets = st.secrets
        for key in (
            "APP_NAME",
            "LOGO_PATH", 
            "DATA_SOURCE",
            "SUPABASE_URL",
            "SUPABASE_KEY",
            "SUPABASE_SERVICE_KEY",
            "WORKTIME_TABLE",
            "WORKTIME_DATE_COLUMN",
            "WORKTIME_EMPLOYEE_COLUMN",
            "WORKTIME_ATTENDANCE_COLUMN",
            "WORKTIME_CANCELED_COLUMN",
            "WORKTIME_LIMIT",
            "ANALISIS_TABLE",
            "CITAS_DETALLE_TABLE",
            "ACCESS_KEYS_TABLE",
            "SMTP_HOST",
            "SMTP_PORT",
            "SMTP_USER",
            "SMTP_PASSWORD",
            "SMTP_FROM",
            "SMTP_USE_TLS",
            "LOG_LEVEL",
        ):
            if key in secrets and key not in os.environ:
                os.environ[key] = str(secrets[key])
    except Exception:
        pass

    base = pathlib.Path(__file__).resolve().parent
    candidates = [base / name for name in (".env", "1.env")]

    # Fallback: reutilizar credenciales del proyecto Worktime
    external_env = os.environ.get(
        "WORKTIME_ENV_PATH",
        "C:/Users/ADMON121_/OneDrive - Fundación Prode/Escritorio/Herramienta analisis de fichaje/vertdent/key.env",
    )
    if external_env:
        candidates.append(pathlib.Path(external_env))

    for candidate in candidates:
        if candidate.exists():
            with open(candidate, encoding="utf-8-sig") as file:
                for raw_line in file:
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value
            return

def get_app_name() -> str:
    load_runtime_env()
    return os.environ.get("APP_NAME", DEFAULT_APP_NAME)

def get_logo_path() -> str:
    load_runtime_env()
    return os.environ.get("LOGO_PATH", DEFAULT_LOGO_PATH)

def get_data_source() -> str:
    load_runtime_env()
    return os.environ.get("DATA_SOURCE", DEFAULT_DATA_SOURCE)

def get_worktime_table() -> str:
    load_runtime_env()
    return os.environ.get("WORKTIME_TABLE", DEFAULT_WORKTIME_TABLE)

def get_worktime_employees_table() -> str:
    load_runtime_env()
    return os.environ.get("WORKTIME_EMPLOYEES_TABLE", DEFAULT_WORKTIME_EMPLOYEES_TABLE)

def get_worktime_date_column() -> str:
    load_runtime_env()
    return os.environ.get("WORKTIME_DATE_COLUMN", "fecha")

def get_worktime_employee_column() -> str:
    load_runtime_env()
    return os.environ.get("WORKTIME_EMPLOYEE_COLUMN", "persona_trabajadora")

def get_worktime_attendance_column() -> str:
    load_runtime_env()
    return os.environ.get("WORKTIME_ATTENDANCE_COLUMN", "asistencia")

def get_worktime_canceled_column() -> str:
    load_runtime_env()
    return os.environ.get("WORKTIME_CANCELED_COLUMN", "anulada")

def get_worktime_limit() -> int:
    load_runtime_env()
    raw = os.environ.get("WORKTIME_LIMIT", "5000")
    try:
        return max(int(raw), 1)
    except (TypeError, ValueError):
        return 5000

def get_analisis_table() -> str:
    load_runtime_env()
    return os.environ.get("ANALISIS_TABLE", DEFAULT_ANALISIS_TABLE)

def get_citas_detalle_table() -> str:
    load_runtime_env()
    return os.environ.get("CITAS_DETALLE_TABLE", DEFAULT_CITAS_DETALLE_TABLE)

def get_access_keys_table() -> str:
    load_runtime_env()
    return os.environ.get("ACCESS_KEYS_TABLE", DEFAULT_ACCESS_KEYS_TABLE)

def get_smtp_host() -> str:
    load_runtime_env()
    return os.environ.get("SMTP_HOST", "")

def get_smtp_port() -> int:
    load_runtime_env()
    raw = os.environ.get("SMTP_PORT", "587")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 587

def get_smtp_user() -> str:
    load_runtime_env()
    return os.environ.get("SMTP_USER", "")

def get_smtp_password() -> str:
    load_runtime_env()
    return os.environ.get("SMTP_PASSWORD", "")

def get_smtp_from() -> str:
    load_runtime_env()
    return os.environ.get("SMTP_FROM", "")

def get_smtp_use_tls() -> bool:
    load_runtime_env()
    raw = os.environ.get("SMTP_USE_TLS", "true").strip().lower()
    return raw in {"1", "true", "yes", "si", "sí", "y"}

def get_supabase_url() -> str:
    load_runtime_env()
    return os.environ.get("SUPABASE_URL", "")

def get_supabase_key() -> str:
    load_runtime_env()
    return os.environ.get("SUPABASE_KEY", "")

def get_supabase_service_key() -> str:
    load_runtime_env()
    return os.environ.get("SUPABASE_SERVICE_KEY", "")
