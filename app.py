import json
from pathlib import Path

import streamlit as st


# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="My Growth Journey",
    page_icon="💜",
    layout="wide"
)

DATA_FILE = Path(__file__).parent / "growth_data.json"

DEFAULT_SKILLS = {
    "Python": 60,
    "C": 45,
    "HTML & CSS": 70,
    "Java": 20,
    "Communication": 35,
}


# ---------------- DATA FUNCTIONS ----------------
def remove_duplicates(items):
    unique_items = []
    seen = set()

    for item in items:
        text = str(item).strip()
        normalized = text.casefold()

        if text and normalized not in seen:
            unique_items.append(text)
            seen.add(normalized)

    return unique_items


def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            saved_skills = data.get("skills", {})

            skills = {
                skill: saved_skills.get(skill, default_value)
                for skill, default_value in DEFAULT_SKILLS.items()
            }

            return {
                "goals": data.get("goals", []),
                "completed": remove_duplicates(
                    data.get("completed", [])
                ),
                "skills": skills,
            }

        except (json.JSONDecodeError, OSError, TypeError):
            pass

    return {
        "goals": [],
        "completed": [],
        "skills": DEFAULT_SKILLS.copy(),
    }


def save_data():
    data = {
        "goals": st.session_state.goals,
        "completed": remove_duplicates(
            st.session_state.completed
        ),
        "skills": st.session_state.skills,
    }

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


# ---------------- LOAD SAVED DATA ----------------
if "app_loaded" not in st.session_state:
    saved_data = load_data()

    st.session_state.goals = saved_data["goals"]
    st.session_state.completed = saved_data["completed"]
    st.session_state.skills = saved_data["skills"]

    st.session_state.app_loaded = True
    save_data()


# ---------------- DESIGN ----------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #101326, #211b3d);
        color: white;
    }

    h1, h2, h3, p, label {
        color: white !important;
    }

    div[data-testid="stMetric"] {
        background: #292541;
        border: 1px solid #514575;
        padding: 18px;
        border-radius: 14px;
    }

    div[data-testid="stMetricLabel"] {
        color: #d8d2f0 !important;
    }

    div[data-testid="stMetricValue"] {
        color: white !important;
    }

    .goal-card {
        background: #292541;
        border: 1px solid #514575;
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------- HEADER ----------------
st.title("💜 My Growth Journey")
st.write(
    "Track your skills, achieve your goals, "
    "and celebrate your progress!"
)
st.divider()


# ---------------- OVERVIEW ----------------
total_skills = len(st.session_state.skills)
active_goals = len(st.session_state.goals)
completed_goals = len(st.session_state.completed)

if total_skills:
    average_progress = round(
        sum(st.session_state.skills.values()) / total_skills
    )
else:
    average_progress = 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("📚 Skills", total_skills)
col2.metric("🎯 Active Goals", active_goals)
col3.metric("🏆 Goals Completed", completed_goals)
col4.metric("📈 Average Progress", f"{average_progress}%")


# ---------------- SKILLS ----------------
st.divider()
st.header("🌱 My Skills")
st.write("Update your progress as you learn.")

skill_columns = st.columns(2)

for index, (skill, current_value) in enumerate(
    st.session_state.skills.items()
):
    with skill_columns[index % 2]:
        new_value = st.slider(
            skill,
            min_value=0,
            max_value=100,
            value=int(current_value),
            key=f"skill_{skill}"
        )

        st.session_state.skills[skill] = new_value

        st.progress(new_value)
        st.caption(f"{new_value}% completed")

save_data()


# ---------------- LEARNING GOALS ----------------
st.divider()
st.header("🎯 My Learning Goals")
st.write("Add a goal and mark it as completed when you finish.")

with st.form("goal_form", clear_on_submit=True):
    new_goal = st.text_input(
        "Enter a learning goal",
        placeholder="Example: Complete Python basics"
    )

    add_goal = st.form_submit_button("➕ Add Goal")

    if add_goal:
        cleaned_goal = new_goal.strip()

        if not cleaned_goal:
            st.warning("Please enter a goal first.")

        elif any(
            goal.casefold() == cleaned_goal.casefold()
            for goal in st.session_state.goals
        ):
            st.info("This goal is already in your active goals.")

        else:
            st.session_state.goals.append(cleaned_goal)
            save_data()
            st.success("Your goal has been added!")
            st.rerun()


# ---------------- ACTIVE GOALS ----------------
st.subheader("📌 Active Goals")

if st.session_state.goals:
    for index, goal in enumerate(
        st.session_state.goals.copy()
    ):
        goal_col, button_col = st.columns([5, 1])

        with goal_col:
            st.markdown(
                f'<div class="goal-card">🎯 {goal}</div>',
                unsafe_allow_html=True
            )

        with button_col:
            if st.button(
                "✅ Done",
                key=f"done_{index}_{goal}"
            ):
                already_completed = any(
                    item.casefold() == goal.casefold()
                    for item in st.session_state.completed
                )

                if not already_completed:
                    st.session_state.completed.append(goal)

                st.session_state.goals.remove(goal)

                save_data()
                st.rerun()

else:
    st.info("No active goals yet. Add a new goal above!")


# ---------------- ACHIEVEMENTS ----------------
st.divider()
st.header("🏆 MY ACHIEVEMENTS")
st.write("Every completed goal is a step forward.")

st.session_state.completed = remove_duplicates(
    st.session_state.completed
)
save_data()

if st.session_state.completed:
    for achievement in st.session_state.completed:
        st.success(f"Completed: {achievement}")
else:
    st.info("Your completed goals will appear here.")


# ---------------- FOOTER ----------------
st.divider()
st.markdown(
    "<p style='text-align:center;'>"
    "Made with 💜 by Akshaya Aila"
    "</p>",
    unsafe_allow_html=True
)
