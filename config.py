import os
import pathlib

# Default configuration values
DEFAULT_LOGO_PATH = "assets/logo.png"
DEFAULT_APP_NAME = "Riesgos de Capital Humano"
DEFAULT_DATA_SOURCE = "local"  # or "supabase", "api", etc.

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
            "LOG_LEVEL",
        ):
            if key in secrets and key not in os.environ:
                os.environ[key] = str(secrets[key])
    except Exception:
        pass

    base = pathlib.Path(__file__).resolve().parent
    for name in (".env", "1.env"):
        candidate = base / name
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

def get_supabase_url() -> str:
    load_runtime_env()
    return os.environ.get("SUPABASE_URL", "")

def get_supabase_key() -> str:
    load_runtime_env()
    return os.environ.get("SUPABASE_KEY", "")

def get_supabase_service_key() -> str:
    load_runtime_env()
    return os.environ.get("SUPABASE_SERVICE_KEY", "")