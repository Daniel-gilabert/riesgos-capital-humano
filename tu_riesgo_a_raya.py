import base64
import hashlib
import os
import pathlib
import random
import runpy
import smtplib
import string
import sys
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText

import streamlit as st


APP_NAME = "TU RIESGO A RAYA FUNDACION PRODE"
BASE_DIR = pathlib.Path(__file__).resolve().parent
BUILDING_BG_URL = "https://www.prode.es/wp-content/uploads/2019/10/sedecordoba-portada.jpg"
CANVA_BG = BASE_DIR / "assets" / "login_canva.png"

# Ruta de la app de Worktime (carpeta externa)
DEFAULT_WORKTIME_APP = pathlib.Path(
    "C:/Users/ADMON121_/OneDrive - Fundación Prode/Escritorio/Herramienta analisis de fichaje/vertdent/app.py"
)

WORKTIME_DIR = DEFAULT_WORKTIME_APP.parent
WORKTIME_LOGO = WORKTIME_DIR / "assets" / "LOGO FUNDACION.png"
if not WORKTIME_LOGO.exists():
    WORKTIME_LOGO = WORKTIME_DIR / "assets" / "logo-prode.png"
if not WORKTIME_LOGO.exists():
    WORKTIME_LOGO = WORKTIME_DIR / "assets" / "logo-prode.jpg"

# Ruta de la app de Capital Humano (esta carpeta)
DEFAULT_CAPITAL_HUMANO_APP = BASE_DIR / "app.py"

MODULE_PREFIXES = (
    "config",
    "models",
    "services",
    "ui",
    "repositories",
    "utils",
)


def _clear_module_cache():
    for module_name in list(sys.modules.keys()):
        if any(
            module_name == prefix or module_name.startswith(prefix + ".")
            for prefix in MODULE_PREFIXES
        ):
            sys.modules.pop(module_name, None)


def _file_to_base64(path: pathlib.Path) -> str:
    if not path.exists():
        return ""
    data = path.read_bytes()
    return base64.b64encode(data).decode("utf-8")


def _render_hero_styles():
    background_css = (
        "linear-gradient(130deg, rgba(232, 236, 255, 0.42) 0%, rgba(223, 229, 250, 0.35) 45%, rgba(215, 225, 248, 0.30) 100%),"
        f"url('{BUILDING_BG_URL}')"
    )
    background_css = "".join(background_css)

    st.markdown(
        f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;700;800;900&family=Rye&display=swap');
          .stApp {{
            background: {background_css};
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
          }}
          [data-testid="stHeader"] {{
            background: transparent;
            border-bottom: none;
            box-shadow: none;
          }}
          [data-testid="stDecoration"] {{ display: none; }}
          [data-testid="stToolbar"] {{ right: 1rem; }}

          .main .block-container {{
            max-width: 1280px;
            padding-top: .7rem;
            padding-bottom: 1.2rem;
          }}

          .prode-top-left {{
            position: fixed;
            top: 18px;
            left: 30px;
            z-index: 30;
          }}
          .prode-top-left img {{
            width: 230px;
            height: auto;
            filter: drop-shadow(0 8px 16px rgba(255,255,255,.5));
          }}

          .login-shell {{
            margin-top: 2.6rem;
            background: rgba(245, 247, 253, 0.82);
            border-radius: 32px;
            border: 1px solid rgba(255,255,255,0.45);
            box-shadow: 0 24px 55px rgba(30,49,84,.22);
            min-height: 610px;
            padding: 2.4rem 2rem 2.2rem;
          }}

          .title-wrap {{
            text-align: center;
            margin-top: .2rem;
            margin-bottom: 2rem;
          }}
          .title-top {{
            font-family: "Montserrat", sans-serif;
            color: #17486f;
            font-weight: 800;
            letter-spacing: 9px;
            font-size: 2.9rem;
            transform: rotate(-7deg);
            margin: 0;
          }}
          .title-main {{
            font-family: "Rye", serif;
            color: #154a75;
            font-size: 5.5rem;
            line-height: .95;
            margin: .25rem 0 0;
            letter-spacing: 2px;
            text-shadow: 0 2px 0 #e8edf6, -2px 3px 0 rgba(20,70,112,0.27);
          }}

          .login-form-wrap {{
            max-width: 470px;
            margin: 0 auto;
          }}
          .stTextInput > label {{ display: none; }}
          .stTextInput > div > div > input {{
            border-radius: 999px;
            border: 1.6px solid #6f2bad;
            background: rgba(255,255,255,0.55);
            color: #2d3552;
            font-size: 1.05rem;
            padding: .7rem 1.1rem;
          }}
          .stForm [data-testid="stFormSubmitButton"] button {{
            border-radius: 999px;
            border: none;
            background: #4e0b86;
            color: #fff;
            font-weight: 700;
            font-size: 1rem;
            width: 100%;
            padding: .65rem 1rem;
          }}
          .stForm [data-testid="stFormSubmitButton"] button:hover {{
            background: #6314a4;
          }}
          .hint-links {{
            text-align: center;
            color: #7b7f8f;
            font-style: italic;
            margin: .4rem 0 .9rem;
            font-size: .92rem;
            letter-spacing: .4px;
          }}

          @media (max-width: 900px) {{
            .prode-top-left {{ position: static; text-align:center; margin-bottom:.3rem; }}
            .prode-top-left img {{ width: 185px; }}
            .login-shell {{ margin-top: .8rem; min-height: 0; padding: 1.2rem .8rem 1.6rem; border-radius: 20px; }}
            .title-top {{ font-size: 1.7rem; letter-spacing: 4px; transform: none; }}
            .title-main {{ font-size: 3rem; }}
            .login-form-wrap {{ max-width: 100%; }}
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _worktime_login(email: str):
    prev_sys_path = list(sys.path)
    prev_cwd = pathlib.Path.cwd()
    try:
        _clear_module_cache()
        os.chdir(WORKTIME_DIR)
        sys.path = [str(WORKTIME_DIR)] + [p for p in prev_sys_path if p != str(WORKTIME_DIR)]

        from config import load_runtime_env
        from services.auth_service import AuthService

        load_runtime_env()
        auth = AuthService()
        return auth.login(email)
    finally:
        os.chdir(prev_cwd)
        sys.path = prev_sys_path


def _normalize_email(value: str) -> str:
    email = (value or "").strip().lower()
    if email and "@" not in email:
        email = f"{email}@prode.es"
    return email


def _generate_access_code(size: int = 6) -> str:
    alphabet = string.digits
    return "".join(random.choice(alphabet) for _ in range(size))


def _get_supabase_client():
    from config import get_supabase_url, get_supabase_key
    import supabase

    url = get_supabase_url().strip()
    key = get_supabase_key().strip()
    if not url or not key:
        raise RuntimeError("Faltan SUPABASE_URL/SUPABASE_KEY para generar claves de acceso.")
    return supabase.create_client(url, key)


def _send_access_code_email(email: str, code: str) -> tuple[bool, str]:
    from config import (
        get_smtp_from,
        get_smtp_host,
        get_smtp_password,
        get_smtp_port,
        get_smtp_use_tls,
        get_smtp_user,
    )

    host = get_smtp_host()
    port = get_smtp_port()
    user = get_smtp_user()
    password = get_smtp_password()
    sender = get_smtp_from() or user

    if not host or not sender:
        return False, "SMTP no configurado. Define SMTP_HOST/SMTP_USER/SMTP_PASSWORD/SMTP_FROM."

    msg = MIMEText(
        (
            "Hola,\n\n"
            f"Tu clave de acceso para TU RIESGO A RAYA FUNDACION PRODE es: {code}\n"
            "La clave caduca en 10 minutos.\n\n"
            "Si no solicitaste esta clave, ignora este correo."
        ),
        "plain",
        "utf-8",
    )
    msg["Subject"] = "Clave de acceso - TU RIESGO A RAYA"
    msg["From"] = sender
    msg["To"] = email

    try:
        with smtplib.SMTP(host, port, timeout=20) as server:
            if get_smtp_use_tls():
                server.starttls()
            if user and password:
                server.login(user, password)
            server.sendmail(sender, [email], msg.as_string())
        return True, ""
    except Exception as exc:
        return False, str(exc)


def _create_access_key(email: str) -> tuple[bool, str]:
    from config import get_access_keys_table

    email = _normalize_email(email)
    if not email:
        return False, "Introduce un correo válido."

    code = _generate_access_code(6)
    code_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=10)

    sent_ok, sent_error = _send_access_code_email(email, code)

    try:
        client = _get_supabase_client()
        client.table(get_access_keys_table()).insert(
            {
                "email": email,
                "codigo": code,
                "codigo_hash": code_hash,
                "usado": False,
                "enviado_ok": sent_ok,
                "creado_en": now.isoformat(),
                "expira_en": expires.isoformat(),
                "metadata": {"origen": "landing", "smtp_error": sent_error if not sent_ok else None},
            }
        ).execute()
    except Exception as exc:
        return False, f"No se pudo guardar la clave en base de datos: {exc}"

    if not sent_ok:
        return False, f"Clave generada y guardada, pero no se pudo enviar correo: {sent_error}"
    return True, "Te hemos enviado una clave de acceso a tu correo."


def _verify_access_key(email: str, code_input: str) -> tuple[bool, str]:
    from config import get_access_keys_table

    email = _normalize_email(email)
    code = (code_input or "").strip()
    if not email or not code:
        return False, "Introduce correo y clave."

    code_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()
    now_iso = datetime.now(timezone.utc).isoformat()

    try:
        client = _get_supabase_client()
        table = client.table(get_access_keys_table())
        result = (
            table.select("id,codigo_hash,expira_en,usado")
            .eq("email", email)
            .eq("usado", False)
            .order("creado_en", desc=True)
            .limit(1)
            .execute()
        )
        rows = result.data or []
        if not rows:
            return False, "No hay clave activa para ese correo. Genera una nueva."

        row = rows[0]
        expira_en = row.get("expira_en")
        if expira_en and expira_en < now_iso:
            return False, "La clave ha caducado. Solicita otra."

        if row.get("codigo_hash") != code_hash:
            return False, "Clave incorrecta."

        table.update({"usado": True, "usado_en": now_iso}).eq("id", row["id"]).execute()
        return True, ""
    except Exception as exc:
        return False, f"Error validando clave: {exc}"


def _list_access_keys(limit: int = 100):
    from config import get_access_keys_table

    client = _get_supabase_client()
    result = (
        client.table(get_access_keys_table())
        .select("id,email,codigo,usado,enviado_ok,creado_en,expira_en,usado_en")
        .order("creado_en", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


def _revoke_access_key(key_id: str):
    from config import get_access_keys_table

    client = _get_supabase_client()
    client.table(get_access_keys_table()).update({"usado": True}).eq("id", key_id).execute()


def _run_app(script_path: pathlib.Path, app_name_env: str | None = None):
    if not script_path.exists():
        st.error(f"No se encontro el archivo de app: {script_path}")
        st.stop()

    prev_cwd = pathlib.Path.cwd()
    prev_app_name = os.environ.get("APP_NAME")
    prev_sys_path = list(sys.path)

    try:
        _clear_module_cache()
        os.chdir(script_path.parent)
        sys.path = [str(script_path.parent)] + [p for p in prev_sys_path if p != str(script_path.parent)]
        if app_name_env:
            os.environ["APP_NAME"] = app_name_env
        runpy.run_path(str(script_path), run_name="__main__")
    finally:
        os.chdir(prev_cwd)
        sys.path = prev_sys_path
        if prev_app_name is None:
            os.environ.pop("APP_NAME", None)
        else:
            os.environ["APP_NAME"] = prev_app_name


def _render_inicio():
    st.set_page_config(page_title=APP_NAME, layout="wide")
    _render_hero_styles()

    logo64 = _file_to_base64(WORKTIME_LOGO)
    if logo64:
        ext = "png" if WORKTIME_LOGO.suffix.lower() == ".png" else "jpeg"
        st.markdown(
            f'<div class="prode-top-left"><img src="data:image/{ext};base64,{logo64}" alt="Fundacion Prode"></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="login-shell">', unsafe_allow_html=True)
    st.markdown('<div class="title-wrap"><p class="title-top">TU RIESGO</p><p class="title-main">A RAYA</p></div>', unsafe_allow_html=True)

    left, center, right = st.columns([1.1, 1.55, 1.1])

    with center:
        st.markdown('<div class="login-form-wrap">', unsafe_allow_html=True)
        with st.form("login_unificado"):
            username = st.text_input("Username", placeholder="Username")
            access_key = st.text_input("Password", placeholder="Password", type="password")
            st.markdown('<p class="hint-links">Remember Me &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Forgot Password?</p>', unsafe_allow_html=True)
            col_send, col_login = st.columns(2)
            with col_send:
                send_key = st.form_submit_button("Enviar clave", use_container_width=True)
            with col_login:
                submit = st.form_submit_button("Log in", use_container_width=True)

        if send_key:
            ok, msg = _create_access_key(username)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

        if submit:
            email = _normalize_email(username)
            ok, msg = _verify_access_key(email, access_key)
            if not ok:
                st.error(msg)
            else:
                usuario = _worktime_login(email)
                if not usuario:
                    st.error("Clave valida, pero el usuario no tiene acceso en Worktime.")
                else:
                    st.session_state["auth_email"] = email
                    st.session_state["usuario"] = usuario
                    st.session_state["auth_ok"] = True
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def _render_selector():
    st.set_page_config(page_title=APP_NAME, layout="wide")
    _render_hero_styles()

    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.markdown(f"### {APP_NAME}")
        st.caption(f"Usuario: {st.session_state.get('auth_email', '')}")
    with top_r:
        if st.button("Cerrar sesion", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    usuario = st.session_state.get("usuario")
    if getattr(usuario, "es_admin", False) or getattr(usuario, "es_superadmin", False):
        with st.expander("Gestion de claves de acceso", expanded=False):
            col_refresh, col_revoke = st.columns([1, 2])
            with col_refresh:
                refresh = st.button("Actualizar", key="refresh_keys")
            with col_revoke:
                revoke_id = st.text_input("Revocar clave por ID", key="revoke_key_id")
                revoke = st.button("Revocar", key="revoke_key_btn")

            if revoke and revoke_id.strip():
                try:
                    _revoke_access_key(revoke_id.strip())
                    st.success("Clave revocada.")
                    refresh = True
                except Exception as exc:
                    st.error(f"No se pudo revocar: {exc}")

            try:
                keys = _list_access_keys(100)
                if keys:
                    st.dataframe(keys, use_container_width=True, hide_index=True)
                else:
                    st.info("Sin claves registradas todavia.")
            except Exception as exc:
                st.error(f"No se pudieron cargar claves: {exc}")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Worktime")
        st.write("Analisis de fichajes, responsables, historico y exportacion.")
        if st.button("Abrir Worktime", use_container_width=True, type="primary"):
            st.session_state["modulo_activo"] = "worktime"
            st.rerun()

    with col2:
        st.subheader("Capital Humano")
        st.write("Analisis de citas medicas y costos de riesgo.")
        if st.button("Abrir Capital Humano", use_container_width=True, type="primary"):
            st.session_state["modulo_activo"] = "capital_humano"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def main():
    if not st.session_state.get("auth_ok"):
        _render_inicio()
        return

    modulo = st.session_state.get("modulo_activo")
    if not modulo:
        _render_selector()
        return

    if modulo == "worktime":
        _run_app(DEFAULT_WORKTIME_APP)
        return

    if modulo == "capital_humano":
        _run_app(DEFAULT_CAPITAL_HUMANO_APP, app_name_env=APP_NAME)
        return

    st.session_state.pop("modulo_activo", None)
    _render_selector()


if __name__ == "__main__":
    main()
