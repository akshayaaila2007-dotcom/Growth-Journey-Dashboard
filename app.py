import json
import time
from pathlib import Path
from datetime import date
from html import escape

import streamlit as st


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Growth Journey Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------- DATA FILE ----------------
DATA_FILE = Path(__file__).parent / "growth_data.json"


# ---------------- DATA MANAGEMENT ----------------
def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                saved_data = json.load(file)
        except (json.JSONDecodeError, OSError):
            saved_data = {}
    else:
        saved_data = {}

    if not isinstance(saved_data, dict):
        saved_data = {}

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

    # Preserve saved skills and progress without adding preset subjects.
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


data = load_data()


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def goal_text(goal):
    if isinstance(goal, dict):
        return goal.get("text", goal.get("title", "Untitled goal"))
    return str(goal)


def goal_done(goal):
    return isinstance(goal, dict) and bool(goal.get("done", False))


def task_done(task):
    return isinstance(task, dict) and bool(task.get("done", False))


def mark_goal_done(index):
    goal = data["goals"][index]

    if isinstance(goal, dict):
        goal["done"] = not goal.get("done", False)
    else:
        data["goals"][index] = {
            "text": str(goal),
            "done": True,
        }

    save_data()


def delete_goal(index):
    data["goals"].pop(index)
    save_data()


# ---------------- DARK THEME ----------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #151329;
        --panel: #211e3d;
        --purple: #a99aff;
        --pink: #ed9bc9;
        --text: #f5f2ff;
        --muted: #c2bbdf;
        --border: #403960;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, #30275a 0%, transparent 30%),
            radial-gradient(circle at 100% 15%, #3a234d 0%, transparent 25%),
            var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(21, 19, 41, 0.96);
    }

    [data-testid="stSidebar"] {
        background: #201c3b;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"],
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: var(--text) !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4, p, label, li {
        color: var(--text);
    }

    .hero {
        border-radius: 26px;
        padding: 32px;
        color: white;
        background: linear-gradient(120deg, #5143a6, #7564d7, #925eaa);
        box-shadow: 0 14px 35px rgba(0, 0, 0, 0.25);
        margin-bottom: 27px;
    }

    .hero-tag {
        display: inline-block;
        padding: 7px 13px;
        border-radius: 30px;
        background: rgba(255,255,255,0.13);
        border: 1px solid rgba(255,255,255,0.25);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 13px;
    }

    .hero h1 {
        color: white;
        font-family: 'Manrope', sans-serif;
        font-size: 34px;
        font-weight: 800;
        margin: 0 0 9px 0;
    }

    .hero p {
        color: #f5f1ff;
        font-size: 16px;
        margin: 0;
        max-width: 720px;
    }

    .section-title {
        font-family: 'Manrope', sans-serif;
        font-size: 24px;
        font-weight: 800;
        color: var(--text);
        margin: 16px 0 5px 0;
    }

    .section-subtitle {
        color: var(--muted);
        font-size: 14px;
        margin-bottom: 18px;
    }

    .stat-card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 21px;
        min-height: 145px;
        box-shadow: 0 7px 22px rgba(0, 0, 0, 0.15);
        transition: transform 0.25s ease;
    }

    .stat-card:hover {
        transform: translateY(-4px);
    }

    .stat-icon {
        font-size: 25px;
        margin-bottom: 10px;
    }

    .stat-label {
        color: var(--muted);
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 7px;
    }

    .stat-value {
        color: #ffffff;
        font-family: 'Manrope', sans-serif;
        font-size: 30px;
        font-weight: 800;
    }

    .skill-row {
        background: #292545;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 15px 17px;
        margin-bottom: 13px;
    }

    .skill-row-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-bottom: 10px;
    }

    .skill-row-name {
        color: #ffffff;
        font-weight: 700;
        font-size: 15px;
    }

    .skill-row-percent {
        color: #d8ceff;
        font-weight: 800;
        font-size: 15px;
    }

    .skill-track {
        height: 12px;
        width: 100%;
        background: #45405f;
        border-radius: 20px;
        overflow: hidden;
    }

    .skill-fill {
        height: 100%;
        border-radius: 20px;
        background: linear-gradient(90deg, #8b7af0, #c19af3, #ed9bc9);
    }

    .goal-card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 16px 18px;
        margin: 9px 0;
        color: var(--text);
    }

    .goal-done {
        background: #203c37;
        border-color: #397a68;
    }

    .achievement-card {
        border: 1px solid var(--border);
        border-radius: 19px;
        padding: 19px;
        min-height: 190px;
        margin-bottom: 15px;
        background: var(--panel);
    }

    .achievement-icon {
        font-size: 30px;
        margin-bottom: 10px;
    }

    .achievement-title {
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 6px;
    }

    .achievement-text {
        color: var(--muted);
        font-size: 13px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stForm"] {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 18px;
    }

    div[data-testid="stForm"] {
        padding: 20px;
    }

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        border-radius: 12px;
        font-weight: 700;
        min-height: 42px;
        background: #7564d7;
        color: white;
        border: 1px solid #9385ed;
    }

    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        background: #8a79ed;
        color: white;
        border-color: #b3a8ff;
    }

    input, textarea,
    [data-baseweb="input"],
    [data-baseweb="select"] > div {
        background-color: #292545 !important;
        color: #ffffff !important;
        border-color: #514a7c !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"] {
        background: #292545 !important;
        color: white !important;
    }

    [data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 15px;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        color: var(--text) !important;
    }

    [data-testid="stProgressBar"] > div {
        background: #39345f;
        border-radius: 20px;
    }

    [data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, #8b7af0, #c19af3, #ed9bc9);
        border-radius: 20px;
    }

    [data-testid="stAlert"] {
        background: #292545;
        color: var(--text);
        border: 1px solid var(--border);
    }

    .timer-display {
        text-align: center;
        font-family: 'Manrope', sans-serif;
        font-size: clamp(48px, 8vw, 86px);
        font-weight: 800;
        color: #ffffff;
        padding: 25px 10px;
        border-radius: 22px;
        background: linear-gradient(135deg, #5143a6, #7564d7, #925eaa);
        border: 1px solid #9385ed;
        margin: 12px 0 20px 0;
    }

    .footer {
        text-align: center;
        color: var(--muted);
        font-size: 12px;
        padding-top: 30px;
    }

    @media (max-width: 768px) {
        .hero { padding: 24px; }
        .hero h1 { font-size: 27px; }
        .stat-value { font-size: 25px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("##  Growth Journey")
    st.caption("Your personal learning space")
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
    st.markdown("### 💜 A little reminder")
    st.write("You don't have to be perfect. Just keep moving forward.")
    st.divider()
    st.caption(f"📅 {date.today().strftime('%d %B %Y')}")


# ---------------- CALCULATIONS ----------------
skills = data["skills"]
goals = data["goals"]

skill_values = [
    max(0, min(100, int(value or 0)))
    for value in skills.values()
]

average_skill = (
    round(sum(skill_values) / len(skill_values))
    if skill_values
    else 0
)

total_goals = len(goals)
completed_goals = sum(goal_done(goal) for goal in goals)
pending_goals = total_goals - completed_goals

goal_completion = (
    round(completed_goals / total_goals * 100)
    if total_goals
    else 0
)


# ---------------- HERO ----------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-tag">YOUR PERSONAL GROWTH SPACE ✨</div>
        <h1>Welcome to your Growth Journey</h1>
        <p>
            Every small step matters. Keep learning, celebrate your progress,
            and become a little better every day.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.markdown(
        '<div class="section-title">Your progress at a glance</div>',
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
        ("📚", "Subjects / skills tracked", len(skills)),
        ("🎯", "Total goals", total_goals),
        ("✅", "Goals completed", completed_goals),
        ("📈", "Average skill level", f"{average_skill}%"),
    ]

    for column, (icon, label, value) in zip(columns, cards):
        with column:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-icon">{icon}</div>
                    <div class="stat-label">{label}</div>
                    <div class="stat-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown(
            '<div class="section-title">💜 Skills overview</div>',
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
                (name, value)
                for name, value in skills.items()
                if int(value or 0) < 100
            ]

            if not skills:
                st.info(
                    "First, add the subject or skill you want to complete "
                    "in My Skills. Your progress bars will appear here."
                )

                if st.button("➕ Add your first subject / skill"):
                    st.session_state.page_navigation = "My Skills"
                    st.rerun()

            elif not active_skills:
                st.success(
                    "All your tracked subjects / skills are complete! 🎉 "
                    "Add another whenever you're ready."
                )

            else:
                for name, value in active_skills:
                    value = max(0, min(100, int(value or 0)))

                    st.markdown(
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
                                <div class="skill-fill"
                                     style="width:{value}%;">
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    with right:
        st.markdown(
            '<div class="section-title">🎯 Goal progress</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-subtitle">'
            'Keep moving toward your targets.'
            '</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.metric("Goals completed", f"{completed_goals} / {total_goals}")
            st.progress(goal_completion / 100)
            st.caption(f"{goal_completion}% of your goals completed")
            st.write(f"🟢 Completed: **{completed_goals}**")
            st.write(f"🕒 Remaining: **{pending_goals}**")

            if total_goals == 0:
                st.info("Add your first goal in My Goals.")

    st.write("")
    st.markdown(
        '<div class="section-title">🌟 Recent goals</div>',
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
            text = escape(goal_text(goal))
            status = "✅ Completed" if done else "🕒 In progress"
            card_class = "goal-card goal-done" if done else "goal-card"

            st.markdown(
                f"""
                <div class="{card_class}">
                    <b>{text}</b><br>
                    <span style="color:#c2bbdf;font-size:13px;">
                        {status}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No goals yet. Add one in My Goals to get started.")


# ---------------- MY SKILLS ----------------
elif page == "My Skills":
    st.markdown(
        '<div class="section-title">💜 My subjects & skills</div>',
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
            "Welcome! First, enter the subject or skill you want "
            "to complete. Nothing is pre-filled."
        )
    else:
        st.info(
            "Update progress with the sliders. At 100%, a skill is "
            "complete and its bar is hidden from Dashboard, but it "
            "stays here."
        )

        for name in list(data["skills"].keys()):
            current_value = max(
                0,
                min(100, int(data["skills"].get(name, 0) or 0)),
            )

            with st.container(border=True):
                st.markdown(f"### {escape(str(name))}")

                if current_value == 100:
                    st.success("Completed 🎉")

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

                st.progress(new_value / 100)
                st.caption(f"{new_value}% completed")

                if st.button(
                    "🗑️ Remove",
                    key=f"remove_skill_{name}",
                ):
                    del data["skills"][name]
                    save_data()
                    st.rerun()

    st.markdown("### ➕ Add a subject or skill")

    with st.form("add_skill_form", clear_on_submit=True):
        new_skill = st.text_input(
            "Subject or skill name",
            placeholder="Example: Biology, Algebra, Python, Drawing",
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
                st.warning("Please enter a subject or skill name.")

            elif new_skill.casefold() in existing_names:
                st.warning("That subject or skill is already in your list.")

            else:
                data["skills"][new_skill] = 0
                save_data()
                st.success(f"{new_skill} added!")
                st.rerun()


# ---------------- MY GOALS ----------------
elif page == "My Goals":
    st.markdown(
        '<div class="section-title">🎯 My learning goals</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Make a plan, take action, and celebrate every win.'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.form("add_goal_form", clear_on_submit=True):
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
                st.warning("Please enter a goal.")
            else:
                data["goals"].insert(
                    0,
                    {"text": new_goal, "done": False},
                )
                save_data()
                st.success("Your goal has been added!")
                st.rerun()

    st.write("")
    st.markdown("### Your goals")

    if not data["goals"]:
        st.info("You have no goals yet. Add your first goal above.")
    else:
        for index, goal in enumerate(data["goals"]):
            text = goal_text(goal)
            done = goal_done(goal)

            col1, col2, col3 = st.columns([5, 1.5, 0.8])

            with col1:
                st.markdown(
                    f"~~{text}~~" if done else f"**{text}**"
                )
                st.caption(
                    "Completed 🎉" if done else "One step closer!"
                )

            with col2:
                if st.button(
                    "Undo" if done else "Mark done",
                    key=f"complete_{index}",
                ):
                    mark_goal_done(index)
                    st.rerun()

            with col3:
                if st.button("🗑️", key=f"delete_{index}"):
                    delete_goal(index)
                    st.rerun()

            st.divider()


# ---------------- DAILY PLANNER ----------------
elif page == "Daily Planner":
    st.markdown(
        '<div class="section-title">📅 Daily Study Planner</div>',
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

    if not isinstance(daily_tasks, list):
        daily_tasks = []
        data["study_plans"][date_key] = daily_tasks
        save_data()

    completed_tasks = sum(task_done(task) for task in daily_tasks)
    total_tasks = len(daily_tasks)
    daily_progress = (
        completed_tasks / total_tasks
        if total_tasks
        else 0
    )

    total_minutes = sum(
        int(task.get("duration", 0) or 0)
        for task in daily_tasks
        if isinstance(task, dict)
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("📚 Tasks planned", total_tasks)
    col2.metric("✅ Tasks completed", completed_tasks)
    col3.metric("⏱️ Planned study time", f"{total_minutes} min")

    st.markdown("### Today's progress")
    st.progress(daily_progress)
    st.caption(
        f"{round(daily_progress * 100)}% of today's tasks completed"
    )

    st.markdown("### ➕ Add a study task")

    with st.form("daily_study_form", clear_on_submit=True):
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
                st.warning("Please enter both a subject and a topic.")
            else:
                daily_tasks.append({
                    "subject": subject,
                    "topic": topic,
                    "duration": int(duration),
                    "done": False,
                })
                save_data()
                st.success("Study task added!")
                st.rerun()

    st.markdown("### 📝 Your study tasks")

    if not daily_tasks:
        st.info(
            "No tasks planned for this date. Add your first task above."
        )
    else:
        for index, task in enumerate(daily_tasks):
            if not isinstance(task, dict):
                task = {
                    "subject": "Study",
                    "topic": str(task),
                    "duration": 30,
                    "done": False,
                }
                daily_tasks[index] = task

            done = task_done(task)

            with st.container(border=True):
                col1, col2 = st.columns([5, 1.5])

                with col1:
                    st.markdown(f"### {task.get('subject', 'Study')}")
                    topic_text = task.get("topic", "Untitled task")

                    if done:
                        st.markdown(f"~~{topic_text}~~")
                    else:
                        st.write(topic_text)

                    st.caption(
                        f"⏱️ {task.get('duration', 30)} minutes"
                        + (" · Completed 🎉" if done else "")
                    )

                with col2:
                    if st.button(
                        "↩️ Undo" if done else "✅ Done",
                        key=f"planner_done_{date_key}_{index}",
                        use_container_width=True,
                    ):
                        task["done"] = not done
                        save_data()
                        st.rerun()

                    if st.button(
                        "🗑️ Delete",
                        key=f"planner_delete_{date_key}_{index}",
                        use_container_width=True,
                    ):
                        daily_tasks.pop(index)
                        save_data()
                        st.rerun()

    st.markdown("###  Study reminder")
    st.info(
        "Focus on one task at a time. Even 30 minutes of learning "
        "can make a difference!"
    )


# ---------------- STUDY TIMER ----------------
elif page == "Study Timer":
    st.markdown(
        '<div class="section-title">⏱️ Study Timer</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Choose a study duration, focus on one task, and take a break '
        'when you finish.'
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
        options=[5, 10, 15, 20, 25, 30, 45, 60, 90],
        value=st.session_state.timer_minutes,
        format_func=lambda value: f"{value} minutes",
        disabled=st.session_state.timer_running,
    )

    if not st.session_state.timer_running:
        st.session_state.timer_minutes = timer_minutes
        st.session_state.timer_remaining = timer_minutes * 60
        st.session_state.timer_total = timer_minutes * 60

    @st.fragment(run_every="1s")
    def show_timer():
        if st.session_state.timer_running:
            remaining = max(
                0,
                int(st.session_state.timer_deadline - time.time()),
            )
            st.session_state.timer_remaining = remaining

            if remaining <= 0:
                st.session_state.timer_running = False
                st.session_state.timer_deadline = None
                st.session_state.timer_remaining = 0

        remaining = st.session_state.timer_remaining
        minutes = remaining // 60
        seconds = remaining % 60

        st.markdown(
            f'<div class="timer-display">{minutes:02d}:{seconds:02d}</div>',
            unsafe_allow_html=True,
        )

        total_seconds = max(1, st.session_state.timer_total)
        progress = 1 - (remaining / total_seconds)
        st.progress(max(0.0, min(1.0, progress)))

        if remaining == 0:
            st.success("🎉 Study session complete! Great job!")
        elif st.session_state.timer_running:
            st.info("Stay focused. You are doing great!")
        else:
            st.caption("Press Start when you are ready to focus.")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                "▶️ Start" if not st.session_state.timer_running else "⏳ Running",
                use_container_width=True,
                disabled=st.session_state.timer_running or remaining == 0,
            ):
                st.session_state.timer_running = True
                st.session_state.timer_deadline = time.time() + remaining
                st.rerun()

        with col2:
            if st.button(
                "⏸️ Pause",
                use_container_width=True,
                disabled=not st.session_state.timer_running,
            ):
                st.session_state.timer_remaining = max(
                    0,
                    int(st.session_state.timer_deadline - time.time()),
                )
                st.session_state.timer_running = False
                st.session_state.timer_deadline = None
                st.rerun()

        with col3:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.timer_running = False
                st.session_state.timer_deadline = None
                st.session_state.timer_remaining = (
                    st.session_state.timer_minutes * 60
                )
                st.session_state.timer_total = (
                    st.session_state.timer_minutes * 60
                )
                st.rerun()

    show_timer()

    st.info(
        "Tip: Try 25 minutes of focused study followed by a short break. "
        "Keep your phone away and focus on one topic."
    )


# ---------------- ACHIEVEMENTS ----------------
elif page == "Achievements":
    st.markdown(
        '<div class="section-title">🏆 Your achievements</div>',
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
            "description": "Reach 50% in any subject or skill.",
            "unlocked": any(
                int(value or 0) >= 50
                for value in skills.values()
            ),
        },
        {
            "icon": "💎",
            "title": "Skill Star",
            "description": "Reach 100% in any subject or skill.",
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
    st.progress(unlocked_count / len(achievement_items))

    columns = st.columns(3)

    for index, item in enumerate(achievement_items):
        with columns[index % 3]:
            if item["unlocked"]:
                icon = item["icon"]
                status = "UNLOCKED ✨"
                background = "linear-gradient(145deg, #3b3554, #51452f)"
            else:
                icon = "🔒"
                status = "LOCKED"
                background = "linear-gradient(145deg, #292545, #211e3d)"

            st.markdown(
                f"""
                <div class="achievement-card"
                     style="background:{background};">
                    <div class="achievement-icon">{icon}</div>
                    <div class="achievement-title">{item["title"]}</div>
                    <div class="achievement-text">
                        {item["description"]}
                    </div>
                    <br>
                    <small><b>{status}</b></small>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------- FOOTER ----------------
st.markdown(
    """
    <div class="footer">
        Made for your learning journey · Keep growing, one step at a time.
    </div>
    """,
    unsafe_allow_html=True,
)
