import streamlit as st
from typing import Optional
import base64
import hashlib
import secrets
from urllib.parse import quote


def _get_query_params():
    try:
        return dict(st.query_params)
    except Exception:
        return st.experimental_get_query_params()


def _clear_query_params():
    try:
        st.query_params.clear()
    except Exception:
        st.experimental_set_query_params()


def _get_app_base_url():
    base = st.secrets.get("APP_BASE_URL")
    if base:
        return str(base).rstrip("/")
    return "http://localhost:8502"


@st.cache_resource
def _pkce_store():
    return {}


def _base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _new_pkce_pair():
    verifier = secrets.token_urlsafe(64)
    challenge = _base64url(hashlib.sha256(verifier.encode("utf-8")).digest())
    return verifier, challenge


def _build_google_authorize_url(redirect_to: str, state: str, code_challenge: str) -> str:
    supabase_url = str(st.secrets.get("SUPABASE_URL", "")).rstrip("/")
    return (
        f"{supabase_url}/auth/v1/authorize"
        f"?provider=google"
        f"&redirect_to={quote(redirect_to, safe='')}"
        f"&code_challenge={quote(code_challenge, safe='')}"
        f"&code_challenge_method=s256"
        f"&state={quote(state, safe='')}"
    )


def get_supabase_client():
    try:
        from supabase import create_client
    except Exception:
        return None

    supabase_url = st.secrets.get("SUPABASE_URL")
    supabase_anon_key = st.secrets.get("SUPABASE_ANON_KEY")
    if not supabase_url or not supabase_anon_key:
        return None
    if str(supabase_anon_key).startswith("sb_secret_"):
        st.session_state["auth_error"] = "Do not use Supabase Secret key here. Use the anon/publishable key from Project Settings → API."
        return None

    try:
        return create_client(str(supabase_url), str(supabase_anon_key))
    except Exception:
        return None


def _extract_user(auth_response):
    user = getattr(auth_response, "user", None)
    if user:
        return user
    data = getattr(auth_response, "data", None)
    if data:
        user = getattr(data, "user", None)
        if user:
            return user
    if isinstance(auth_response, dict):
        return auth_response.get("user") or auth_response.get("data", {}).get("user")
    return None


def _extract_oauth_url(oauth_response):
    url = getattr(oauth_response, "url", None)
    if url:
        return url
    data = getattr(oauth_response, "data", None)
    if data:
        url = getattr(data, "url", None)
        if url:
            return url
    if isinstance(oauth_response, dict):
        return oauth_response.get("url") or (oauth_response.get("data") or {}).get("url")
    return None


def handle_auth_callback():
    params = _get_query_params()

    code = params.get("code") or params.get("auth_code")
    if isinstance(code, list):
        code = code[0] if code else None

    state = params.get("state")
    if isinstance(state, list):
        state = state[0] if state else None

    error_desc = params.get("error_description") or params.get("error")
    if isinstance(error_desc, list):
        error_desc = error_desc[0] if error_desc else None

    if error_desc:
        st.session_state["auth_error"] = str(error_desc)
        _clear_query_params()
        return

    if not code:
        return

    supabase = get_supabase_client()
    if not supabase:
        st.session_state["auth_error"] = "Supabase is not configured."
        _clear_query_params()
        return

    if "supabase_user" in st.session_state:
        _clear_query_params()
        return

    try:
        store = _pkce_store()
        stored = store.get(state) if state else None
        code_verifier = None
        post_login_page = None
        if isinstance(stored, dict):
            code_verifier = stored.get("code_verifier")
            post_login_page = stored.get("post_login_page")
        if not code_verifier:
            st.session_state["auth_error"] = "invalid request: missing PKCE code_verifier. Please click 'Continue with Google' again."
            _clear_query_params()
            return

        redirect_to = f"{_get_app_base_url()}/"
        auth_response = supabase.auth.exchange_code_for_session(
            {"auth_code": code, "code_verifier": code_verifier, "redirect_to": redirect_to}
        )
        user = _extract_user(auth_response)
        st.session_state["supabase_user"] = user
        if post_login_page and "post_login_page" not in st.session_state:
            st.session_state["post_login_page"] = post_login_page
        if state and state in store:
            del store[state]
        if "oauth_url" in st.session_state:
            del st.session_state["oauth_url"]
        _clear_query_params()
        st.rerun()
    except Exception as e:
        st.session_state["auth_error"] = str(e)
        _clear_query_params()


def render_auth_sidebar():
    user = st.session_state.get("supabase_user")
    if not user:
        return

    email = getattr(user, "email", None)
    if not email and isinstance(user, dict):
        email = user.get("email")

    st.sidebar.markdown("---")
    st.sidebar.caption("Signed in")
    st.sidebar.write(email or "User")

    if st.sidebar.button("Logout", use_container_width=True):
        supabase = get_supabase_client()
        if supabase:
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
        for k in ["supabase_user", "oauth_url", "post_login_page", "auth_error", "openrouter_messages", "messages"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()


def require_login(post_login_page: Optional[str] = None):
    handle_auth_callback()

    supabase = get_supabase_client()
    if not supabase:
        st.error("Supabase auth is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY in .streamlit/secrets.toml")
        st.stop()

    auth_error = st.session_state.get("auth_error")
    if auth_error:
        st.warning(f"Login issue: {str(auth_error)[:200]}")
        del st.session_state["auth_error"]

    if st.session_state.get("supabase_user"):
        return

    st.title("🔐 Sign in required")
    st.write("Continue with Google to access AquaSense AI.")

    if post_login_page and "post_login_page" not in st.session_state:
        st.session_state["post_login_page"] = post_login_page

    redirect_to = f"{_get_app_base_url()}/"

    if st.button("Continue with Google", type="primary", use_container_width=True):
        try:
            store = _pkce_store()
            state = secrets.token_urlsafe(16)
            code_verifier, code_challenge = _new_pkce_pair()
            store[state] = {"code_verifier": code_verifier, "post_login_page": post_login_page}
            st.session_state["oauth_url"] = _build_google_authorize_url(
                redirect_to=redirect_to, state=state, code_challenge=code_challenge
            )
        except Exception as e:
            st.error(f"Could not start Google login: {str(e)[:200]}")

    url = st.session_state.get("oauth_url")
    if url:
        st.link_button("Open Google Login", url, use_container_width=True)
        st.caption("After login, you will be redirected back automatically.")

    st.stop()


def redirect_after_login(default_page: str):
    if not st.session_state.get("supabase_user"):
        return

    target = st.session_state.pop("post_login_page", None) or default_page
    try:
        st.switch_page(target)
    except Exception:
        return
