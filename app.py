import json
import time
import hashlib
import secrets
from pathlib import Path
from datetime import date
from html import escape

import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Growth Journey Dashboard",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# FILES
# ============================================================

BASE_DIR = Path(__file__).parent

LEGACY_DATA_FILE = BASE_DIR / "growth_data.json"
USERS_FILE = BASE_DIR / "users.json"


# ============================================================
# DEFAULT USER DATA
# ============================================================

def empty_user_data():
    return {
        "skills": {},
        "goals": [],
        "achievements": [],
        "study_plans": {},
    }


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password, salt=None):

    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()

    return {
        "salt": salt,
        "hash": password_hash,
    }


def verify_password(password, stored_password):

    if not isinstance(stored_password, dict):
        return False

    salt = stored_password.get("salt", "")
    saved_hash = stored_password.get("hash", "")

    if not salt or not saved_hash:
        return False

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()

    return secrets.compare_digest(
        password_hash,
        saved_hash,
    )


# ============================================================
# DATA CLEANING
# ============================================================

def clean_user_data(saved_data):

    if not isinstance(saved_data, dict):
        saved_data = empty_user_data()

    saved_data.setdefault("skills", {})
    saved_data.setdefault("goals", [])
    saved_data.setdefault("achievements", [])
    saved_data.setdefault("study_plans", {})

    if not isinstance(saved_data["skills"], dict):
        saved_data["skills"] = {}

    if not isinstance(saved_data["goals"], list):
        saved_data["goals"] = []

    if not isinstance(saved_data["achievements"], list):
        saved_data["achievements"] = []

    if not isinstance(saved_data["study_plans"], dict):
        saved_data["study_plans"] = {}

    cleaned_skills = {}

    for name, value in saved_data["skills"].items():

        try:
            cleaned_skills[str(name)] = max(
                0,
                min(100, int(value or 0)),
            )

        except (TypeError, ValueError):

            cleaned_skills[str(name)] = 0

    saved_data["skills"] = cleaned_skills

    return saved_data


# ============================================================
# LEGACY DATA
# ============================================================

def load_legacy_data():

    if not LEGACY_DATA_FILE.exists():
        return empty_user_data()

    try:

        with open(
            LEGACY_DATA_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            saved_data = json.load(file)

        return clean_user_data(saved_data)

    except (json.JSONDecodeError, OSError):

        return empty_user_data()


# ============================================================
# USER DATABASE
# ============================================================

def load_users():

    if not USERS_FILE.exists():

        return {
            "users": {}
        }

    try:

        with open(
            USERS_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            saved_users = json.load(file)

    except (json.JSONDecodeError, OSError):

        saved_users = {
            "users": {}
        }

    if not isinstance(saved_users, dict):

        saved_users = {
            "users": {}
        }

    saved_users.setdefault("users", {})

    if not isinstance(saved_users["users"], dict):

        saved_users["users"] = {}

    return saved_users


users_database = load_users()


def save_users():

    with open(
        USERS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            users_database,
            file,
            indent=4,
            ensure_ascii=False,
        )


# ============================================================
# USER HELPERS
# ============================================================

def normalize_username(username):

    return username.strip().lower()


def username_exists(username):

    username = normalize_username(username)

    return username in users_database["users"]


def create_user(
    display_name,
    username,
    password,
):

    username = normalize_username(username)

    if len(users_database["users"]) == 0:

        initial_data = load_legacy_data()

    else:

        initial_data = empty_user_data()

    password_data = hash_password(password)

    users_database["users"][username] = {
        "display_name": display_name.strip(),
        "password": password_data,
        "data": initial_data,
    }

    save_users()


def get_user_data(username):

    username = normalize_username(username)

    user = users_database["users"].get(username)

    if not user:
        return empty_user_data()

    if "data" not in user:

        user["data"] = empty_user_data()

    user["data"] = clean_user_data(
        user["data"]
    )

    return user["data"]


def save_current_user_data():

    username = st.session_state.get(
        "username"
    )

    if not username:
        return

    if username not in users_database["users"]:
        return

    users_database["users"][username]["data"] = (
        clean_user_data(
            st.session_state.user_data
        )
    )

    save_users()


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "display_name" not in st.session_state:
    st.session_state.display_name = ""

if "user_data" not in st.session_state:
    st.session_state.user_data = empty_user_data()

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "Login"


# ============================================================
# AUTHENTICATION PAGE
# ============================================================

if not st.session_state.logged_in:

    # --------------------------------------------------------
    # AUTH CSS
    # --------------------------------------------------------

    st.markdown(
        """
        <style>

        @import url(
            'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap'
        );

        :root {
            --bg: #151329;
            --panel: #211e3d;
            --purple: #a99aff;
            --pink: #ed9bc9;
            --text: #f5f2ff;
            --muted: #c2bbdf;
            --border: #403960;
        }

        html,
        body,
        [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 10% 0%,
                    #30275a 0%,
                    transparent 30%
                ),
                radial-gradient(
                    circle at 90% 10%,
                    #44284f 0%,
                    transparent 28%
                ),
                var(--bg);
        }

        [data-testid="stHeader"] {
            background: rgba(21, 19, 41, 0.96);
        }

        .cute-world {
            position: relative;
            width: 300px;
            height: 72px;
            margin: 8px auto 0 auto;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: visible;
        }

        .cute-item {
            position: absolute;
            left: 50%;
            top: 15px;

            font-size: 27px;

            opacity: 0;

            transform:
                translateX(-50%)
                translateY(12px)
                scale(0.65);

            animation:
                cuteSequence
                12s
                ease-in-out
                infinite;

            filter:
                drop-shadow(
                    0 5px 8px
                    rgba(0, 0, 0, 0.22)
                );
        }

        .cute1 {
            animation-delay: 0s;
        }

        .cute2 {
            animation-delay: 1.5s;
        }

        .cute3 {
            animation-delay: 3s;
        }

        .cute4 {
            animation-delay: 4.5s;
        }

        .cute5 {
            animation-delay: 6s;
        }

        .cute6 {
            animation-delay: 7.5s;
        }

        .cute7 {
            animation-delay: 9s;
        }

        .cute8 {
            animation-delay: 10.5s;
        }

        @keyframes cuteSequence {

            0% {
                opacity: 0;

                transform:
                    translateX(-50%)
                    translateY(12px)
                    scale(0.65)
                    rotate(-8deg);
            }

            4% {
                opacity: 1;

                transform:
                    translateX(-50%)
                    translateY(-2px)
                    scale(1)
                    rotate(4deg);
            }

            8% {
                opacity: 1;

                transform:
                    translateX(-50%)
                    translateY(-12px)
                    scale(1.08)
                    rotate(-4deg);
            }

            12% {
                opacity: 1;

                transform:
                    translateX(-50%)
                    translateY(-3px)
                    scale(1)
                    rotate(3deg);
            }

            16% {
                opacity: 0;

                transform:
                    translateX(-50%)
                    translateY(7px)
                    scale(0.75)
                    rotate(6deg);
            }

            100% {
                opacity: 0;
            }
        }

        .auth-wrapper {
            max-width: 520px;
            margin: 0 auto;
        }

        .auth-hero {
            text-align: center;
            padding: 2px 10px 20px 10px;
        }

        .auth-heart {
            font-size: 42px;
            margin-bottom: 4px;

            animation:
                heartBeat
                2s
                ease-in-out
                infinite;
        }

        @keyframes heartBeat {

            0%,
            100% {
                transform: scale(1);
            }

            50% {
                transform: scale(1.10);
            }
        }

        .auth-title {
            color: white;

            font-family:
                'Manrope',
                sans-serif;

            font-size: 34px;
            font-weight: 800;

            margin-bottom: 7px;
        }

        .auth-subtitle {
            color: #c2bbdf;
            font-size: 14px;
            line-height: 1.6;
        }

        div[data-testid="stForm"] {
            background:
                rgba(
                    33,
                    30,
                    61,
                    0.94
                );

            border:
                1px solid
                #403960;

            border-radius: 24px;

            padding: 28px;

            box-shadow:
                0 18px 45px
                rgba(0, 0, 0, 0.28);
        }

        input,
        textarea,
        [data-baseweb="input"],
        [data-baseweb="select"] > div {

            background-color:
                #292545 !important;

            color:
                #ffffff !important;

            border-color:
                #514a7c !important;
        }

        div.stButton > button,
        div[data-testid="stFormSubmitButton"] > button {

            border-radius: 13px;

            font-weight: 700;

            min-height: 44px;

            background: #7564d7;

            color: white;

            border:
                1px solid
                #9385ed;

            transition:
                all
                0.2s
                ease;
        }

        div.stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {

            background: #8a79ed;

            color: white;

            border-color:
                #b3a8ff;

            transform:
                translateY(-2px);
        }

        h1,
        h2,
        h3,
        h4,
        p,
        label {
            color: #f5f2ff;
        }

        .auth-footer {
            text-align: center;

            color: #a99ac7;

            font-family:
                Georgia,
                serif;

            font-style: italic;

            font-size: 13px;

            opacity: 0.70;

            padding-top: 28px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # CUTE EMOJIS
    # --------------------------------------------------------

    st.html(
        """
        <div class="cute-world">

            <div class="cute-item cute1">🐶</div>
            <div class="cute-item cute2">🧁</div>
            <div class="cute-item cute3">🍫</div>
            <div class="cute-item cute4">🌸</div>
            <div class="cute-item cute5">🍞</div>
            <div class="cute-item cute6">💜</div>
            <div class="cute-item cute7">🦋</div>
            <div class="cute-item cute8">🌷</div>

        </div>
        """
    )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    st.html(
        """
        <div class="auth-wrapper">

            <div class="auth-hero">

                <div class="auth-heart">
                    💜
                </div>

                <div class="auth-title">
                    Growth Journey
                </div>

                <div class="auth-subtitle">
                    A little space for your little progress.<br>
                    Learn · Plan · Grow · Repeat ✨
                </div>

            </div>

        </div>
        """
    )

    # ========================================================
    # LOGIN
    # ========================================================

    if st.session_state.auth_page == "Login":

        st.markdown(
            "### 🔐 Welcome back"
        )

        with st.form("login_form"):

            username = st.text_input(
                "Username",
                placeholder="Enter your username",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
            )

            submitted = st.form_submit_button(
                "💜 Login",
                use_container_width=True,
            )

            if submitted:

                username = normalize_username(
                    username
                )

                if not username or not password:

                    st.warning(
                        "Please enter both username and password."
                    )

                elif username not in users_database["users"]:

                    st.error(
                        "No account found with this username."
                    )

                else:

                    user = users_database[
                        "users"
                    ][username]

                    if verify_password(
                        password,
                        user.get(
                            "password",
                            {},
                        ),
                    ):

                        st.session_state.logged_in = True

                        st.session_state.username = (
                            username
                        )

                        st.session_state.display_name = (
                            user.get(
                                "display_name",
                                username,
                            )
                        )

                        st.session_state.user_data = (
                  clean_user_data(
                         get_user_data(
                             username
                        )
                 )
            )

                        st.session_state.page_navigation = (
                            "Dashboard"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Incorrect password. Please try again."
                        )

        st.write("")

        col1, col2, col3 = st.columns(
            [1, 2, 1]
        )

        with col2:

            if st.button(
                "✨ Create a new account",
                use_container_width=True,
            ):

                st.session_state.auth_page = (
                    "Register"
                )

                st.rerun()

    # ========================================================
    # REGISTER
    # ========================================================

    else:

        st.markdown(
            "### 🌸 Create your little space"
        )

        with st.form("register_form"):

            display_name = st.text_input(
                "Your name",
                placeholder="Example: Akshaya Aila",
            )

            username = st.text_input(
                "Create a username",
                placeholder="Example: akshaya",
            )

            password = st.text_input(
                "Create a password",
                type="password",
                placeholder="At least 6 characters",
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                placeholder="Enter the password again",
            )

            submitted = st.form_submit_button(
                "🌸 Create my account",
                use_container_width=True,
            )

            if submitted:

                display_name = display_name.strip()

                username = normalize_username(
                    username
                )

                if not display_name:

                    st.warning(
                        "Please enter your name."
                    )

                elif not username:

                    st.warning(
                        "Please create a username."
                    )

                elif len(username) < 3:

                    st.warning(
                        "Username must contain at least 3 characters."
                    )

                elif " " in username:

                    st.warning(
                        "Username cannot contain spaces."
                    )

                elif not password:

                    st.warning(
                        "Please create a password."
                    )

                elif len(password) < 6:

                    st.warning(
                        "Password must contain at least 6 characters."
                    )

                elif password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                elif username_exists(username):

                    st.error(
                        "That username is already registered."
                    )

                else:
                    create_user(
                        display_name,
                        username,
                        password,
                    )

                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.display_name = display_name

                    st.session_state.user_data = (
                        clean_user_data(
                            get_user_data(username)
                        )
                    )

                    st.session_state.page_navigation = (
                        "Dashboard"
                    )

                    st.success(
                        f"Welcome, {display_name}! 💜"
                    )

                    st.rerun()

        st.write("")

        col1, col2, col3 = st.columns(
            [1, 2, 1]
        )

        with col2:

            if st.button(
                "← Back to Login",
                use_container_width=True,
            ):

                st.session_state.auth_page = (
                    "Login"
                )

                st.rerun()

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    st.html(
        """
        <div class="auth-footer">
            Tiny steps still count. 💜
        </div>
        """
    )

    st.stop()


# ============================================================
# CURRENT USER DATA
# ============================================================

data = st.session_state.user_data


# ============================================================
# SAVE DATA
# ============================================================

def save_data():

    st.session_state.user_data = (
        clean_user_data(data)
    )

    save_current_user_data()


# ============================================================
# GOAL HELPERS
# ============================================================

def goal_text(goal):

    if isinstance(goal, dict):

        return goal.get(
            "text",
            goal.get(
                "title",
                "Untitled goal",
            ),
        )

    return str(goal)


def goal_done(goal):

    return (
        isinstance(goal, dict)
        and bool(
            goal.get(
                "done",
                False,
            )
        )
    )


def task_done(task):

    return (
        isinstance(task, dict)
        and bool(
            task.get(
                "done",
                False,
            )
        )
    )


def mark_goal_done(index):

    goal = data["goals"][index]

    if isinstance(goal, dict):

        goal["done"] = not goal.get(
            "done",
            False,
        )

    else:

        data["goals"][index] = {
            "text": str(goal),
            "done": True,
        }

    save_data()


def delete_goal(index):

    data["goals"].pop(index)

    save_data()


# ============================================================
# MAIN DARK THEME
# ============================================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap'
    );

    :root {
        --bg: #151329;
        --panel: #211e3d;
        --purple: #a99aff;
        --pink: #ed9bc9;
        --text: #f5f2ff;
        --muted: #c2bbdf;
        --border: #403960;
    }

    html,
    body,
    [class*="css"] {
        font-family:
            'DM Sans',
            sans-serif;
    }

    .stApp {

        background:
            radial-gradient(
                circle at 10% 0%,
                #30275a 0%,
                transparent 30%
            ),
            radial-gradient(
                circle at 100% 15%,
                #3a234d 0%,
                transparent 25%
            ),
            var(--bg);

        color:
            var(--text);
    }

    [data-testid="stHeader"] {
        background:
            rgba(
                21,
                19,
                41,
                0.96
            );
    }

    [data-testid="stSidebar"] {

        background:
            #201c3b;

        border-right:
            1px solid
            var(--border);
    }

    [data-testid="stSidebar"],
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"]
    [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"]
    [data-testid="stCaptionContainer"] {

        color:
            var(--text) !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {

        color:
            #ffffff !important;
    }

    .block-container {

        max-width:
            1450px;

        padding-top:
            2rem;

        padding-bottom:
            3rem;
    }

    h1,
    h2,
    h3,
    h4,
    p,
    label,
    li {

        color:
            var(--text);
    }

    .hero {

        border-radius:
            26px;

        padding:
            32px;

        color:
            white;

        background:
            linear-gradient(
                120deg,
                #5143a6,
                #7564d7,
                #925eaa
            );

        box-shadow:
            0 14px 35px
            rgba(0, 0, 0, 0.25);

        margin-bottom:
            27px;
    }

    .hero-tag {

        display:
            inline-block;

        padding:
            7px 13px;

        border-radius:
            30px;

        background:
            rgba(
                255,
                255,
                255,
                0.13
            );

        border:
            1px solid
            rgba(
                255,
                255,
                255,
                0.25
            );

        font-size:
            12px;

        font-weight:
            700;

        letter-spacing:
            1px;

        margin-bottom:
            13px;
    }

    .hero h1 {

        color:
            white;

        font-family:
            'Manrope',
            sans-serif;

        font-size:
            34px;

        font-weight:
            800;

        margin:
            0 0 9px 0;
    }

    .hero p {

        color:
            #f5f1ff;

        font-size:
            16px;

        margin:
            0;

        max-width:
            720px;
    }

    .section-title {

        font-family:
            'Manrope',
            sans-serif;

        font-size:
            24px;

        font-weight:
            800;

        color:
            var(--text);

        margin:
            16px 0 5px 0;
    }

    .section-subtitle {

        color:
            var(--muted);

        font-size:
            14px;

        margin-bottom:
            18px;
    }

    .stat-card {

        background:
            var(--panel);

        border:
            1px solid
            var(--border);

        border-radius:
            18px;

        padding:
            21px;

        min-height:
            145px;

        box-shadow:
            0 7px 22px
            rgba(0, 0, 0, 0.15);

        transition:
            transform
            0.25s
            ease;
    }

    .stat-card:hover {
        transform:
            translateY(-4px);
    }

    .stat-icon {

        font-size:
            25px;

        margin-bottom:
            10px;
    }

    .stat-label {

        color:
            var(--muted);

        font-size:
            13px;

        font-weight:
            600;

        margin-bottom:
            7px;
    }

    .stat-value {

        color:
            #ffffff;

        font-family:
            'Manrope',
            sans-serif;

        font-size:
            30px;

        font-weight:
            800;
    }

    .skill-row {

        background:
            #292545;

        border:
            1px solid
            var(--border);

        border-radius:
            14px;

        padding:
            15px 17px;

        margin-bottom:
            13px;
    }

    .skill-row-top {

        display:
            flex;

        justify-content:
            space-between;

        align-items:
            center;

        gap:
            12px;

        margin-bottom:
            10px;
    }

    .skill-row-name {

        color:
            #ffffff;

        font-weight:
            700;

        font-size:
            15px;
    }

    .skill-row-percent {

        color:
            #d8ceff;

        font-weight:
            800;

        font-size:
            15px;
    }

    .skill-track {

        height:
            12px;

        width:
            100%;

        background:
            #45405f;

        border-radius:
            20px;

        overflow:
            hidden;
    }

    .skill-fill {

        height:
            100%;

        border-radius:
            20px;

        background:
            linear-gradient(
                90deg,
                #8b7af0,
                #c19af3,
                #ed9bc9
            );
    }

    .goal-card {

        background:
            var(--panel);

        border:
            1px solid
            var(--border);

        border-radius:
            16px;

        padding:
            16px 18px;

        margin:
            9px 0;

        color:
            var(--text);
    }

    .goal-done {

        background:
            #203c37;

        border-color:
            #397a68;
    }

    .achievement-card {

        border:
            1px solid
            var(--border);

        border-radius:
            19px;

        padding:
            19px;

        min-height:
            190px;

        margin-bottom:
            15px;

        background:
            var(--panel);
    }

    .achievement-icon {

        font-size:
            30px;

        margin-bottom:
            10px;
    }

    .achievement-title {

        font-weight:
            800;

        color:
            #ffffff;

        margin-bottom:
            6px;
    }

    .achievement-text {

        color:
            var(--muted);

        font-size:
            13px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stForm"] {

        background:
            var(--panel);

        border:
            1px solid
            var(--border);

        border-radius:
            18px;
    }

    div[data-testid="stForm"] {
        padding:
            20px;
    }

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {

        border-radius:
            12px;

        font-weight:
            700;

        min-height:
            42px;

        background:
            #7564d7;

        color:
            white;

        border:
            1px solid
            #9385ed;
    }

    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {

        background:
            #8a79ed;

        color:
            white;

        border-color:
            #b3a8ff;
    }

    input,
    textarea,
    [data-baseweb="input"],
    [data-baseweb="select"] > div {

        background-color:
            #292545 !important;

        color:
            #ffffff !important;

        border-color:
            #514a7c !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"] {

        background:
            #292545 !important;

        color:
            white !important;
    }

    [data-testid="stMetric"] {

        background:
            var(--panel);

        border:
            1px solid
            var(--border);

        border-radius:
            15px;

        padding:
            15px;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {

        color:
            var(--text) !important;
    }

    [data-testid="stProgressBar"] > div {

        background:
            #39345f;

        border-radius:
            20px;
    }

    [data-testid="stProgressBar"] > div > div {

        background:
            linear-gradient(
                90deg,
                #8b7af0,
                #c19af3,
                #ed9bc9
            );

        border-radius:
            20px;
    }

    [data-testid="stAlert"] {

        background:
            #292545;

        color:
            var(--text);

        border:
            1px solid
            var(--border);
    }

    .timer-display {

        text-align:
            center;

        font-family:
            'Manrope',
            sans-serif;

        font-size:
            clamp(
                48px,
                8vw,
                86px
            );

        font-weight:
            800;

        color:
            #ffffff;

        padding:
            25px 10px;

        border-radius:
            22px;

        background:
            linear-gradient(
                135deg,
                #5143a6,
                #7564d7,
                #925eaa
            );

        border:
            1px solid
            #9385ed;

        margin:
            12px 0 20px 0;
    }

    .footer {

        text-align:
            center;

        color:
            var(--muted);

        font-size:
            12px;

        padding-top:
            30px;
    }

    .signature {

        text-align:
            center;

        color:
            #a99ac7;

        font-family:
            Georgia,
            serif;

        font-style:
            italic;

        font-size:
            13px;

        letter-spacing:
            0.3px;

        opacity:
            0.75;

        padding-top:
            6px;

        padding-bottom:
            10px;
    }

    .user-badge {

        background:
            rgba(
                169,
                154,
                255,
                0.10
            );

        border:
            1px solid
            #403960;

        border-radius:
            12px;

        padding:
            10px 12px;

        margin:
            10px 0;
    }

    .user-badge-name {

        color:
            white;

        font-weight:
            700;

        font-size:
            14px;
    }

    .user-badge-username {

        color:
            #c2bbdf;

        font-size:
            12px;
    }

    @media (max-width: 768px) {

        .hero {
            padding:
                24px;
        }

        .hero h1 {

            font-size:
                27px;
        }

        .stat-value {

            font-size:
                25px;
        }

        .cute-world {

            width:
                220px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## Growth Journey"
    )

    st.caption(
        "Your personal learning space"
    )

    st.divider()

    st.html(
        f"""
        <div class="user-badge">

            <div class="user-badge-name">
                💜 {escape(st.session_state.display_name)}
            </div>

            <div class="user-badge-username">
                @{escape(st.session_state.username)}
            </div>

        </div>
        """
    )

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "My Skills",
            "My Goals",
            "Daily Planner",
            "Study Timer",
            "Achievements",
        ],
        key="page_navigation",
    )

    st.divider()

    st.markdown(
        "### 💜 A little reminder"
    )

    st.write(
        "You don't have to be perfect. "
        "Just keep moving forward."
    )

    st.divider()

    st.caption(
        f"📅 {date.today().strftime('%d %B %Y')}"
    )

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True,
    ):

        save_current_user_data()

        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.display_name = ""
        st.session_state.user_data = empty_user_data()
        st.session_state.auth_page = "Login"

        timer_keys = [
            "timer_running",
            "timer_remaining",
            "timer_deadline",
            "timer_total",
            "timer_minutes",
        ]

        for key in timer_keys:

            if key in st.session_state:

                del st.session_state[key]

        st.rerun()


# ============================================================
# CALCULATIONS
# ============================================================

skills = data["skills"]
goals = data["goals"]

skill_values = [
    max(
        0,
        min(
            100,
            int(value or 0),
        ),
    )
    for value in skills.values()
]

average_skill = (
    round(
        sum(skill_values)
        / len(skill_values)
    )
    if skill_values
    else 0
)

total_goals = len(goals)

completed_goals = sum(
    goal_done(goal)
    for goal in goals
)

pending_goals = (
    total_goals
    - completed_goals
)

goal_completion = (
    round(
        completed_goals
        / total_goals
        * 100
    )
    if total_goals
    else 0
)


# ============================================================
# HERO
# ============================================================

st.html(
    f"""
    <div class="hero">

        <div class="hero-tag">
            YOUR PERSONAL GROWTH SPACE ✨
        </div>

        <h1>
            Welcome, {escape(st.session_state.display_name)}
        </h1>

        <p>
            Every small step matters. Keep learning,
            celebrate your progress, and become a little
            better every day.
        </p>

    </div>
    """
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.markdown(
        '<div class="section-title">'
        'Your progress at a glance'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'A little progress every day adds up to something amazing.'
        '</div>',
        unsafe_allow_html=True,
    )

    columns = st.columns(4)

    cards = [
        (
            "📚",
            "Subjects / skills tracked",
            len(skills),
        ),
        (
            "🎯",
            "Total goals",
            total_goals,
        ),
        (
            "✅",
            "Goals completed",
            completed_goals,
        ),
        (
            "📈",
            "Average skill level",
            f"{average_skill}%",
        ),
    ]

    for column, (
        icon,
        label,
        value,
    ) in zip(columns, cards):

        with column:

            st.html(
                f"""
                <div class="stat-card">

                    <div class="stat-icon">
                        {icon}
                    </div>

                    <div class="stat-label">
                        {escape(str(label))}
                    </div>

                    <div class="stat-value">
                        {escape(str(value))}
                    </div>

                </div>
                """
            )

    st.write("")

    left, right = st.columns(
        [1.15, 0.85],
        gap="large",
    )

    # --------------------------------------------------------
    # SKILLS OVERVIEW
    # --------------------------------------------------------

    with left:

        st.markdown(
            '<div class="section-title">'
            '💜 Skills overview'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Active learning levels. Completed items stay in My Skills.'
            '</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):

            active_skills = [
                (
                    name,
                    value,
                )
                for name, value
                in skills.items()
                if int(value or 0) < 100
            ]

            if not skills:

                st.info(
                    "First, add the subject or skill you want "
                    "to complete in My Skills. Your progress "
                    "bars will appear here."
                )

                if st.button(
                    "➕ Add your first subject / skill"
                ):

                    st.session_state.page_navigation = (
                        "My Skills"
                    )

                    st.rerun()

            elif not active_skills:

                st.success(
                    "All your tracked subjects / skills "
                    "are complete! 🎉 Add another whenever "
                    "you're ready."
                )

            else:

                for name, value in active_skills:

                    value = max(
                        0,
                        min(
                            100,
                            int(value or 0),
                        ),
                    )

                    st.html(
                        f"""
                        <div class="skill-row">

                            <div class="skill-row-top">

                                <span class="skill-row-name">
                                    {escape(str(name))}
                                </span>

                                <span class="skill-row-percent">
                                    {value}%
                                </span>

                            </div>

                            <div class="skill-track">

                                <div
                                    class="skill-fill"
                                    style="width:{value}%;">
                                </div>

                            </div>

                        </div>
                        """
                    )

    # --------------------------------------------------------
    # GOAL PROGRESS
    # --------------------------------------------------------

    with right:

        st.markdown(
            '<div class="section-title">'
            '🎯 Goal progress'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Keep moving toward your targets.'
            '</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):

            st.metric(
                "Goals completed",
                f"{completed_goals} / {total_goals}",
            )

            st.progress(
                goal_completion / 100
            )

            st.caption(
                f"{goal_completion}% of your goals completed"
            )

            st.write(
                f"🟢 Completed: **{completed_goals}**"
            )

            st.write(
                f"🕒 Remaining: **{pending_goals}**"
            )

            if total_goals == 0:

                st.info(
                    "Add your first goal in My Goals."
                )

    # --------------------------------------------------------
    # RECENT GOALS
    # --------------------------------------------------------

    st.write("")

    st.markdown(
        '<div class="section-title">'
        '🌟 Recent goals'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Your next little wins are waiting.'
        '</div>',
        unsafe_allow_html=True,
    )

    if goals:

        for goal in goals[:3]:

            done = goal_done(goal)

            goal_label = escape(
                goal_text(goal)
            )

            status = (
                "✅ Completed"
                if done
                else "🕒 In progress"
            )

            card_class = (
                "goal-card goal-done"
                if done
                else "goal-card"
            )

            st.html(
                f"""
                <div class="{card_class}">

                    <b>{goal_label}</b><br>

                    <span
                        style="
                            color:#c2bbdf;
                            font-size:13px;
                        "
                    >
                        {status}
                    </span>

                </div>
                """
            )

    else:

        st.info(
            "No goals yet. Add one in My Goals to get started."
        )


# ============================================================
# MY SKILLS
# ============================================================

elif page == "My Skills":

    st.markdown(
        '<div class="section-title">'
        '💜 My subjects & skills'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Add the subjects or skills you want to complete. '
        'You can add as many as you need.'
        '</div>',
        unsafe_allow_html=True,
    )

    if not data["skills"]:

        st.info(
            "Welcome! First, enter the subject or skill "
            "you want to complete. Nothing is pre-filled."
        )

    else:

        st.info(
            "Update progress with the sliders. At 100%, "
            "a skill is complete and its bar is hidden "
            "from Dashboard, but it stays here."
        )

        for name in list(
            data["skills"].keys()
        ):

            current_value = max(
                0,
                min(
                    100,
                    int(
                        data["skills"].get(
                            name,
                            0,
                        )
                        or 0
                    ),
                ),
            )

            with st.container(border=True):

                st.markdown(
                    f"### {escape(str(name))}"
                )

                if current_value == 100:

                    st.success(
                        "Completed 🎉"
                    )

                new_value = st.slider(
                    f"{name} progress",
                    min_value=0,
                    max_value=100,
                    value=current_value,
                    key=f"skill_slider_{name}",
                    format="%d%%",
                )

                if new_value != current_value:

                    data["skills"][name] = new_value

                    save_data()

                    st.rerun()

                st.progress(
                    new_value / 100
                )

                st.caption(
                    f"{new_value}% completed"
                )

                if st.button(
                    "🗑️ Remove",
                    key=f"remove_skill_{name}",
                ):

                    del data["skills"][name]

                    save_data()

                    st.rerun()

    st.markdown(
        "### ➕ Add a subject or skill"
    )

    with st.form(
        "add_skill_form",
        clear_on_submit=True,
    ):

        new_skill = st.text_input(
            "Subject or skill name",
            placeholder=(
                "Example: Biology, Algebra, "
                "Python, Drawing"
            ),
        )

        submitted = st.form_submit_button(
            "Add subject / skill",
            use_container_width=True,
        )

        if submitted:

            new_skill = new_skill.strip()

            existing_names = {
                name.casefold()
                for name in data["skills"]
            }

            if not new_skill:

                st.warning(
                    "Please enter a subject or skill name."
                )

            elif new_skill.casefold() in existing_names:

                st.warning(
                    "That subject or skill is already in your list."
                )

            else:

                data["skills"][new_skill] = 0

                save_data()

                st.success(
                    f"{new_skill} added!"
                )

                st.rerun()


# ============================================================
# MY GOALS
# ============================================================

elif page == "My Goals":

    st.markdown(
        '<div class="section-title">'
        '🎯 My learning goals'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Make a plan, take action, and celebrate every win.'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.form(
        "add_goal_form",
        clear_on_submit=True,
    ):

        new_goal = st.text_input(
            "What do you want to achieve?",
            placeholder="Example: Complete a chapter",
        )

        submitted = st.form_submit_button(
            "＋ Add goal",
            use_container_width=True,
        )

        if submitted:

            new_goal = new_goal.strip()

            if not new_goal:

                st.warning(
                    "Please enter a goal."
                )

            else:

                data["goals"].insert(
                    0,
                    {
                        "text": new_goal,
                        "done": False,
                    },
                )

                save_data()

                st.success(
                    "Your goal has been added!"
                )

                st.rerun()

    st.write("")

    st.markdown(
        "### Your goals"
    )

    if not data["goals"]:

        st.info(
            "You have no goals yet. "
            "Add your first goal above."
        )

    else:

        for index, goal in enumerate(
            data["goals"]
        ):

            text = goal_text(goal)

            done = goal_done(goal)

            col1, col2, col3 = st.columns(
                [5, 1.5, 0.8]
            )

            with col1:

                if done:

                    st.markdown(
                        f"~~{escape(str(text))}~~"
                    )

                else:

                    st.markdown(
                        f"**{escape(str(text))}**"
                    )

                st.caption(
                    "Completed 🎉"
                    if done
                    else "One step closer!"
                )

            with col2:

                if st.button(
                    "Undo"
                    if done
                    else "Mark done",
                    key=f"complete_{index}",
                ):

                    mark_goal_done(index)

                    st.rerun()

            with col3:

                if st.button(
                    "🗑️",
                    key=f"delete_{index}",
                ):

                    delete_goal(index)

                    st.rerun()

            st.divider()


# ============================================================
# DAILY PLANNER
# ============================================================

elif page == "Daily Planner":

    st.markdown(
        '<div class="section-title">'
        '📅 Daily Study Planner'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Plan your study time, complete tasks, and track daily progress.'
        '</div>',
        unsafe_allow_html=True,
    )

    selected_date = st.date_input(
        "Choose your study date",
        value=date.today(),
        key="planner_date",
    )

    date_key = selected_date.isoformat()

    if date_key not in data["study_plans"]:

        data["study_plans"][date_key] = []

    daily_tasks = data["study_plans"][date_key]

    if not isinstance(
        daily_tasks,
        list,
    ):

        daily_tasks = []

        data["study_plans"][date_key] = daily_tasks

        save_data()

    completed_tasks = sum(
        task_done(task)
        for task in daily_tasks
    )

    total_tasks = len(
        daily_tasks
    )

    daily_progress = (
        completed_tasks / total_tasks
        if total_tasks
        else 0
    )

    total_minutes = sum(
        int(
            task.get(
                "duration",
                0,
            )
            or 0
        )
        for task in daily_tasks
        if isinstance(
            task,
            dict,
        )
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "📚 Tasks planned",
        total_tasks,
    )

    col2.metric(
        "✅ Tasks completed",
        completed_tasks,
    )

    col3.metric(
        "⏱️ Planned study time",
        f"{total_minutes} min",
    )

    st.markdown(
        "### Today's progress"
    )

    st.progress(
        daily_progress
    )

    st.caption(
        f"{round(daily_progress * 100)}% "
        "of today's tasks completed"
    )

    st.markdown(
        "### ➕ Add a study task"
    )

    with st.form(
        "daily_study_form",
        clear_on_submit=True,
    ):

        subject = st.text_input(
            "Subject",
            placeholder="Example: Biology",
        )

        topic = st.text_input(
            "Topic or task",
            placeholder="Example: Revise chapter 1",
        )

        duration = st.number_input(
            "Study duration (minutes)",
            min_value=5,
            max_value=600,
            value=30,
            step=5,
        )

        submitted = st.form_submit_button(
            "Add to my plan",
            use_container_width=True,
        )

        if submitted:

            subject = subject.strip()

            topic = topic.strip()

            if not subject or not topic:

                st.warning(
                    "Please enter both a subject and a topic."
                )

            else:

                daily_tasks.append(
                    {
                        "subject": subject,
                        "topic": topic,
                        "duration": int(duration),
                        "done": False,
                    }
                )

                save_data()

                st.success(
                    "Study task added!"
                )

                st.rerun()

    st.markdown(
        "### 📝 Your study tasks"
    )

    if not daily_tasks:

        st.info(
            "No tasks planned for this date. "
            "Add your first task above."
        )

    else:

        for index, task in enumerate(
            daily_tasks
        ):

            if not isinstance(
                task,
                dict,
            ):

                task = {
                    "subject": "Study",
                    "topic": str(task),
                    "duration": 30,
                    "done": False,
                }

                daily_tasks[index] = task

            done = task_done(task)

            with st.container(
                border=True
            ):

                col1, col2 = st.columns(
                    [5, 1.5]
                )

                with col1:

                    st.markdown(
                        f"### {escape(str(task.get('subject', 'Study')))}"
                    )

                    topic_text = task.get(
                        "topic",
                        "Untitled task",
                    )

                    if done:

                        st.markdown(
                            f"~~{escape(str(topic_text))}~~"
                        )

                    else:

                        st.write(
                            topic_text
                        )

                    st.caption(
                        f"⏱️ {task.get('duration', 30)} minutes"
                        +
                        (
                            " · Completed 🎉"
                            if done
                            else ""
                        )
                    )

                with col2:

                    if st.button(
                        "↩️ Undo"
                        if done
                        else "✅ Done",
                        key=(
                            f"planner_done_"
                            f"{date_key}_{index}"
                        ),
                        use_container_width=True,
                    ):

                        task["done"] = not done

                        save_data()

                        st.rerun()

                    if st.button(
                        "🗑️ Delete",
                        key=(
                            f"planner_delete_"
                            f"{date_key}_{index}"
                        ),
                        use_container_width=True,
                    ):

                        daily_tasks.pop(index)

                        save_data()

                        st.rerun()

    st.markdown(
        "### Study reminder"
    )

    st.info(
        "Focus on one task at a time. Even 30 minutes "
        "of learning can make a difference!"
    )


# ============================================================
# STUDY TIMER
# ============================================================

elif page == "Study Timer":

    st.markdown(
        '<div class="section-title">'
        '⏱️ Study Timer'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Choose a study duration, focus on one task, '
        'and take a break when you finish.'
        '</div>',
        unsafe_allow_html=True,
    )

    timer_defaults = {
        "timer_running": False,
        "timer_remaining": 25 * 60,
        "timer_deadline": None,
        "timer_total": 25 * 60,
        "timer_minutes": 25,
    }

    for key, value in timer_defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value

    timer_minutes = st.select_slider(
        "Choose study duration",
        options=[
            5,
            10,
            15,
            20,
            25,
            30,
            45,
            60,
            90,
        ],
        value=st.session_state.timer_minutes,
        format_func=lambda value:
            f"{value} minutes",
        disabled=st.session_state.timer_running,
    )

    if not st.session_state.timer_running:

        st.session_state.timer_minutes = (
            timer_minutes
        )

        st.session_state.timer_remaining = (
            timer_minutes * 60
        )

        st.session_state.timer_total = (
            timer_minutes * 60
        )

    @st.fragment(run_every="1s")
    def show_timer():

        if st.session_state.timer_running:

            remaining = max(
                0,
                int(
                    st.session_state.timer_deadline
                    - time.time()
                ),
            )

            st.session_state.timer_remaining = (
                remaining
            )

            if remaining <= 0:

                st.session_state.timer_running = False

                st.session_state.timer_deadline = None

                st.session_state.timer_remaining = 0

        remaining = (
            st.session_state.timer_remaining
        )

        minutes = remaining // 60

        seconds = remaining % 60

        st.html(
            f"""
            <div class="timer-display">
                {minutes:02d}:{seconds:02d}
            </div>
            """
        )

        total_seconds = max(
            1,
            st.session_state.timer_total,
        )

        progress = (
            1
            -
            (
                remaining
                / total_seconds
            )
        )

        st.progress(
            max(
                0.0,
                min(
                    1.0,
                    progress,
                ),
            )
        )

        if remaining == 0:

            st.success(
                "🎉 Study session complete! Great job!"
            )

        elif st.session_state.timer_running:

            st.info(
                "Stay focused. You are doing great!"
            )

        else:

            st.caption(
                "Press Start when you are ready to focus."
            )

        col1, col2, col3 = st.columns(3)

        with col1:

            if st.button(
                "▶️ Start"
                if not st.session_state.timer_running
                else "⏳ Running",
                use_container_width=True,
                disabled=(
                    st.session_state.timer_running
                    or remaining == 0
                ),
            ):

                st.session_state.timer_running = True

                st.session_state.timer_deadline = (
                    time.time()
                    + remaining
                )

                st.rerun()

        with col2:

            if st.button(
                "⏸️ Pause",
                use_container_width=True,
                disabled=(
                    not st.session_state.timer_running
                ),
            ):

                st.session_state.timer_remaining = max(
                    0,
                    int(
                        st.session_state.timer_deadline
                        - time.time()
                    ),
                )

                st.session_state.timer_running = False

                st.session_state.timer_deadline = None

                st.rerun()

        with col3:

            if st.button(
                "🔄 Reset",
                use_container_width=True,
            ):

                st.session_state.timer_running = False

                st.session_state.timer_deadline = None

                st.session_state.timer_remaining = (
                    st.session_state.timer_minutes
                    * 60
                )

                st.session_state.timer_total = (
                    st.session_state.timer_minutes
                    * 60
                )

                st.rerun()

    show_timer()

    st.info(
        "Tip: Try 25 minutes of focused study followed "
        "by a short break. Keep your phone away and "
        "focus on one topic."
    )


# ============================================================
# ACHIEVEMENTS
# ============================================================

elif page == "Achievements":

    st.markdown(
        '<div class="section-title">'
        '🏆 Your achievements'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Every little achievement deserves a celebration.'
        '</div>',
        unsafe_allow_html=True,
    )

    achievement_items = [
        {
            "icon": "🌱",
            "title": "First Step",
            "description": "Add your first learning goal.",
            "unlocked": total_goals >= 1,
        },
        {
            "icon": "🎯",
            "title": "Goal Getter",
            "description": "Complete your first goal.",
            "unlocked": completed_goals >= 1,
        },
        {
            "icon": "🔥",
            "title": "Getting Started",
            "description": "Complete three goals.",
            "unlocked": completed_goals >= 3,
        },
        {
            "icon": "📚",
            "title": "Skill Builder",
            "description": (
                "Reach 50% in any subject or skill."
            ),
            "unlocked": any(
                int(value or 0) >= 50
                for value in skills.values()
            ),
        },
        {
            "icon": "💎",
            "title": "Skill Star",
            "description": (
                "Reach 100% in any subject or skill."
            ),
            "unlocked": any(
                int(value or 0) >= 100
                for value in skills.values()
            ),
        },
        {
            "icon": "🌟",
            "title": "Consistent Learner",
            "description": "Complete five goals.",
            "unlocked": completed_goals >= 5,
        },
    ]

    unlocked_count = sum(
        item["unlocked"]
        for item in achievement_items
    )

    st.metric(
        "Achievements unlocked",
        f"{unlocked_count} / {len(achievement_items)}",
    )

    st.progress(
        unlocked_count
        / len(achievement_items)
    )

    columns = st.columns(3)

    for index, item in enumerate(
        achievement_items
    ):

        with columns[index % 3]:

            if item["unlocked"]:

                icon = item["icon"]

                status = "UNLOCKED ✨"

                background = (
                    "linear-gradient("
                    "145deg, #3b3554, #51452f"
                    ")"
                )

            else:

                icon = "🔒"

                status = "LOCKED"

                background = (
                    "linear-gradient("
                    "145deg, #292545, #211e3d"
                    ")"
                )

            st.html(
                f"""
                <div
                    class="achievement-card"
                    style="background:{background};"
                >

                    <div class="achievement-icon">
                        {icon}
                    </div>

                    <div class="achievement-title">
                        {escape(item["title"])}
                    </div>

                    <div class="achievement-text">
                        {escape(item["description"])}
                    </div>

                    <br>

                    <small>
                        <b>{status}</b>
                    </small>

                </div>
                """
            )


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="footer">
        Made for your learning journey ·
        Keep growing, one step at a time.
    </div>
    """
)

st.html(
    """
    <div class="signature">
        Still growing. — Akshaya.Aila 💜
    </div>
    """
)
