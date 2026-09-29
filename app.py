import json
from pathlib import Path
from datetime import date

import streamlit as st


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Growth Journey Dashboard",
    page_icon="🌷",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------- DATA FILE ----------------
DATA_FILE = Path(__file__).parent / "growth_data.json"

DEFAULT_SKILLS = {
    "Python": 0,
    "C Programming": 0,
    "HTML & CSS": 0,
    "Java": 0,
    "Communication": 0,
}


# ---------------- DATA MANAGEMENT ----------------
def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            data = {}
    else:
        data = {}

    if not isinstance(data, dict):
        data = {}

    data.setdefault("skills", DEFAULT_SKILLS.copy())
    data.setdefault("goals", [])
    data.setdefault("achievements", [])
    data.setdefault("study_plans", {})

    if not isinstance(data["skills"], dict):
        data["skills"] = DEFAULT_SKILLS.copy()

    for skill, value in DEFAULT_SKILLS.items():
        data["skills"].setdefault(skill, value)

    if not isinstance(data["goals"], list):
        data["goals"] = []

    if not isinstance(data["achievements"], list):
        data["achievements"] = []

    if not isinstance(data["study_plans"], dict):
        data["study_plans"] = {}

    return data


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def goal_text(goal):
    if isinstance(goal, dict):
        return goal.get("text", goal.get("title", "Untitled goal"))
    return str(goal)


def goal_done(goal):
    return isinstance(goal, dict) and bool(goal.get("done", False))


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


def task_text(task):
    if isinstance(task, dict):
        return task.get("topic", "Untitled task")
    return str(task)


def task_done(task):
    return isinstance(task, dict) and bool(task.get("done", False))


data = load_data()


# ---------------- ANIMATED DESIGN ----------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --purple: #7567e8;
        --deep-purple: #5143bd;
        --pink: #ed8fc5;
        --text: #292842;
        --muted: #85849d;
        --border: #e9e7f5;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, #f1edff 0%, transparent 28%),
            radial-gradient(circle at 100% 15%, #fff0f8 0%, transparent 25%),
            #f8f8fd;
        color: var(--text);
    }

    [data-testid="stSidebar"] {
        background: rgba(255,255,255,0.96);
        border-right: 1px solid #e9e7f5;
    }

    /* Sidebar text visibility fix */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #51436f !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #292842 !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label,
    [data-testid="stSidebar"] [role="radiogroup"] label p {
        color: #51436f !important;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        font-family: 'Manrope', sans-serif;
        color: var(--text);
    }

    .hero {
        position: relative;
        overflow: hidden;
        border-radius: 26px;
        padding: 32px;
        color: white;
        background: linear-gradient(120deg, #6254d9, #8d7cf4, #c49bf0);
        background-size: 200% 200%;
        animation: gradientShift 9s ease infinite;
        box-shadow: 0 14px 35px rgba(98, 84, 217, 0.22);
        margin-bottom: 27px;
    }

    .hero::after {
        content: "✦";
        position: absolute;
        right: 8%;
        top: 10%;
        font-size: 100px;
        color: rgba(255,255,255,0.15);
        animation: float 4s ease-in-out infinite;
    }

    .hero-tag {
        display: inline-block;
        padding: 7px 13px;
        border-radius: 30px;
        background: rgba(255,255,255,0.19);
        border: 1px solid rgba(255,255,255,0.25);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 13px;
    }

    .hero h1 {
        color: white;
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
        font-size: 23px;
        font-weight: 800;
        color: #292842;
        margin: 16px 0 5px 0;
    }

    .section-subtitle {
        color: var(--muted);
        font-size: 14px;
        margin-bottom: 18px;
    }

    .stat-card {
        position: relative;
        overflow: hidden;
        background: rgba(255,255,255,0.86);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.95);
        border-radius: 21px;
        padding: 21px;
        min-height: 145px;
        box-shadow: 0 7px 22px rgba(55, 48, 110, 0.06);
        transition: transform 0.3s ease,
                    box-shadow 0.3s ease,
                    border-color 0.3s ease;
        animation: fadeUp 0.65s ease both;
    }

    .stat-card:hover {
        transform: translateY(-8px) scale(1.015);
        box-shadow: 0 17px 35px rgba(98, 84, 217, 0.16);
        border-color: #c9c0ff;
    }

    .stat-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 60%;
        height: 100%;
        background: linear-gradient(
            110deg,
            transparent,
            rgba(255,255,255,0.55),
            transparent
        );
        transition: left 0.65s ease;
    }

    .stat-card:hover::before {
        left: 140%;
    }

    .stat-icon {
        font-size: 25px;
        margin-bottom: 10px;
        animation: float 4s ease-in-out infinite;
    }

    .stat-label {
        color: var(--muted);
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 7px;
    }

    .stat-value {
        color: #292842;
        font-family: 'Manrope', sans-serif;
        font-size: 30px;
        font-weight: 800;
    }

    .skill-name {
        font-weight: 700;
        color: #30304a;
        margin-bottom: 4px;
    }

    .goal-card {
        background: rgba(255,255,255,0.92);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 16px 18px;
        margin: 9px 0;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }

    .goal-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 22px rgba(98, 84, 217, 0.10);
    }

    .goal-done {
        background: #f0fbf5;
        border-color: #c6ead4;
    }

    .achievement-card {
        border: 1px solid #f4e5b6;
        border-radius: 19px;
        padding: 19px;
        min-height: 190px;
        margin-bottom: 15px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .achievement-card:hover {
        transform: translateY(-7px) rotate(-1deg);
        box-shadow: 0 14px 30px rgba(191, 145, 48, 0.16);
    }

    .achievement-icon {
        font-size: 30px;
        margin-bottom: 10px;
    }

    .achievement-title {
        font-weight: 800;
        color: #51401d;
        margin-bottom: 6px;
    }

    .achievement-text {
        color: #8c784c;
        font-size: 13px;
    }

    .planner-card {
        background: rgba(255,255,255,0.92);
        border: 1px solid #e9e7f5;
        border-radius: 18px;
        padding: 17px;
        margin-bottom: 12px;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }

    .planner-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 25px rgba(98, 84, 217, 0.10);
    }

    div.stButton > button {
        border-radius: 12px;
        font-weight: 700;
        min-height: 42px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(98, 84, 217, 0.15);
    }

    div[data-testid="stForm"] {
        background: rgba(255,255,255,0.92);
        border: 1px solid var(--border);
        border-radius: 19px;
        padding: 20px;
    }

    div[data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, #7668e8, #b99bf8, #ed9bc9);
        background-size: 200% 100%;
        animation: progressGlow 3s linear infinite;
        border-radius: 20px;
    }

    div[data-testid="stProgressBar"] > div {
        background: #eeedf7;
        border-radius: 20px;
    }

    .footer {
        text-align: center;
        color: #9998ad;
        font-size: 12px;
        padding-top: 30px;
    }

    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(15px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }

    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    @keyframes progressGlow {
        from { background-position: 0% 50%; }
        to { background-position: 200% 50%; }
    }

    @media (max-width: 768px) {
        .hero { padding: 24px; }
        .hero h1 { font-size: 27px; }
        .stat-value { font-size: 25px; }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🌷 Growth Journey")
    st.caption("Your personal learning space")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "My Skills",
            "My Goals",
            "Daily Planner",
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
        <h1>Welcome to your Growth Journey 🌷</h1>
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
        '<div class="section-subtitle">A little progress every day adds up to something amazing.</div>',
        unsafe_allow_html=True,
    )

    columns = st.columns(4)

    cards = [
        ("📚", "Skills tracked", len(skills)),
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
            '<div class="section-subtitle">Your learning levels so far.</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            for skill, value in skills.items():
                value = max(0, min(100, int(value or 0)))
                st.markdown(
                    f"<div class='skill-name'>{skill}</div>",
                    unsafe_allow_html=True,
                )
                st.progress(value / 100)
                st.caption(f"{value}% completed")

    with right:
        st.markdown(
            '<div class="section-title">🎯 Goal progress</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-subtitle">Keep moving toward your targets.</div>',
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
        '<div class="section-subtitle">Your next little wins are waiting.</div>',
        unsafe_allow_html=True,
    )

    if goals:
        for goal in goals[:3]:
            done = goal_done(goal)
            text = goal_text(goal)
            status = "✅ Completed" if done else "🕒 In progress"
            card_class = "goal-card goal-done" if done else "goal-card"

            st.markdown(
                f"""
                <div class="{card_class}">
                    <b>{text}</b><br>
                    <span style="color:#85849d;font-size:13px;">{status}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No goals yet. Add one in My Goals to get started.")


# ---------------- MY SKILLS ----------------
elif page == "My Skills":
    st.markdown(
        '<div class="section-title">💜 Build your skills</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">Update your levels as you learn and improve.</div>',
        unsafe_allow_html=True,
    )

    st.info("Move the sliders to update your progress. Your changes are saved automatically.")

    with st.container(border=True):
        for skill in list(data["skills"].keys()):
            current_value = max(
                0,
                min(100, int(data["skills"].get(skill, 0) or 0)),
            )

            st.markdown(f"### {skill}")

            new_value = st.slider(
                f"{skill} level",
                min_value=0,
                max_value=100,
                value=current_value,
                key=f"skill_slider_{skill}",
                format="%d%%",
            )

            if new_value != current_value:
                data["skills"][skill] = new_value
                save_data()

            st.progress(new_value / 100)
            st.caption(f"{new_value}% completed")
            st.divider()

    st.markdown("### ➕ Add another skill")

    with st.form("add_skill_form", clear_on_submit=True):
        new_skill = st.text_input(
            "Skill name",
            placeholder="Example: SQL",
        )
        submitted = st.form_submit_button(
            "Add skill",
            use_container_width=True,
        )

        if submitted:
            new_skill = new_skill.strip()

            if not new_skill:
                st.warning("Please enter a skill name.")
            elif new_skill in data["skills"]:
                st.warning("This skill is already in your list.")
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
        '<div class="section-subtitle">Make a plan, take action, and celebrate every win.</div>',
        unsafe_allow_html=True,
    )

    with st.form("add_goal_form", clear_on_submit=True):
        new_goal = st.text_input(
            "What do you want to achieve?",
            placeholder="Example: Complete Python basics",
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
                    {
                        "text": new_goal,
                        "done": False,
                    },
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
                if done:
                    st.markdown(f"~~{text}~~")
                    st.caption("Completed 🎉")
                else:
                    st.markdown(f"**{text}**")
                    st.caption("One step closer!")

            with col2:
                label = "Undo" if done else "Mark done"
                if st.button(label, key=f"complete_{index}"):
                    mark_goal_done(index)
                    st.rerun()

            with col3:
                if st.button("🗑️", key=f"delete_{index}"):
                    delete_goal(index)
                    st.rerun()

            st.divider()


# ---------------- DAILY STUDY PLANNER ----------------
elif page == "Daily Planner":
    st.markdown(
        '<div class="section-title">📅 Daily Study Planner</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Plan your study time, complete tasks, and track your daily progress.'
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
    st.caption(f"{round(daily_progress * 100)}% of today's tasks completed")

    st.write("")
    st.markdown("### ➕ Add a study task")

    with st.form("daily_study_form", clear_on_submit=True):
        subject = st.text_input(
            "Subject",
            placeholder="Example: Python",
        )

        topic = st.text_input(
            "Topic or task",
            placeholder="Example: Practice loops",
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

    st.write("")
    st.markdown("### 📝 Your study tasks")

    if not daily_tasks:
        st.info("No tasks planned for this date. Add your first task above.")
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
            subject_name = task.get("subject", "Study")
            topic_name = task.get("topic", "Untitled task")
            minutes = task.get("duration", 30)

            with st.container(border=True):
                col1, col2 = st.columns([5, 1.5])

                with col1:
                    if done:
                        st.markdown(f"### ~~{subject_name}~~")
                        st.markdown(f"~~{topic_name}~~")
                        st.caption(f"⏱️ {minutes} minutes · Completed 🎉")
                    else:
                        st.markdown(f"### {subject_name}")
                        st.write(topic_name)
                        st.caption(f"⏱️ Planned study time: {minutes} minutes")

                with col2:
                    st.write("")
                    button_text = "↩️ Undo" if done else "✅ Done"

                    if st.button(
                        button_text,
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

    st.write("")
    st.markdown("### 🌷 Study reminder")
    st.info(
        "Focus on one task at a time. Even 30 minutes of learning "
        "can make a difference!"
    )


# ---------------- ACHIEVEMENTS ----------------
elif page == "Achievements":
    st.markdown(
        '<div class="section-title">🏆 Your achievements</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">Every little achievement deserves a celebration.</div>',
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
            "description": "Reach 50% in any skill.",
            "unlocked": any(
                int(value or 0) >= 50
                for value in skills.values()
            ),
        },
        {
            "icon": "💎",
            "title": "Skill Star",
            "description": "Reach 100% in any skill.",
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
        item["unlocked"] for item in achievement_items
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
                background = "linear-gradient(145deg, #fffdf6, #fff1cf)"
            else:
                icon = "🔒"
                status = "LOCKED"
                background = "linear-gradient(145deg, #f7f7fb, #eeedf5)"

            st.markdown(
                f"""
                <div class="achievement-card"
                     style="background:{background};">
                    <div class="achievement-icon">{icon}</div>
                    <div class="achievement-title">{item["title"]}</div>
                    <div class="achievement-text">{item["description"]}</div>
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
        Made with 💜 for your learning journey · Keep growing, one step at a time.
    </div>
    """,
    unsafe_allow_html=True,
)
