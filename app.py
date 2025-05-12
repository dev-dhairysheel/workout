import streamlit as st
from google import genai
from google.api_core import retry
import json
import re
import time
import urllib.parse

# --- Setup ---
client = genai.Client(api_key=st.secrets['API_KEY'])

# Retry handler for Gemini
is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})
if hasattr(genai.models.Models.generate_content, '__wrapped__'):
    genai.models.Models.generate_content = retry.Retry(predicate=is_retriable)(genai.models.Models.generate_content)

# --- Streamlit UI Config ---
st.set_page_config(page_title="AI Workout Planner", page_icon="💪", layout="centered")
st.title("💪 Personalized AI Workout Generator")

# --- Initialize session state variables ---
if 'page' not in st.session_state:
    st.session_state.page = "generator"
if 'current_exercise_idx' not in st.session_state:
    st.session_state.current_exercise_idx = 0
if 'current_set' not in st.session_state:
    st.session_state.current_set = 1
if 'workout_data' not in st.session_state:
    st.session_state.workout_data = None
if 'rest_timer' not in st.session_state:
    st.session_state.rest_timer = 0
if 'rest_active' not in st.session_state:
    st.session_state.rest_active = False
if 'rest_start_time' not in st.session_state:
    st.session_state.rest_start_time = 0
if 'workout_start_time' not in st.session_state:
    st.session_state.workout_start_time = 0
if 'set_start_time' not in st.session_state:
    st.session_state.set_start_time = 0
if 'timing_data' not in st.session_state:
    st.session_state.timing_data = []
if 'show_stop_analysis' not in st.session_state:
    st.session_state.show_stop_analysis = False

# --- Helper Function to Format Time ---
def format_time(seconds):
    if seconds >= 60:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"
    return f"{seconds:.1f}s"

# --- Function to Generate AI Insights ---
def generate_workout_insights(timing_data, total_workout_time, completed=True):
    # Summarize timing data
    summary = "Workout Summary:\n"
    exercise_times = {}
    for entry in timing_data:
        exercise = entry['exercise']
        set_time = entry['set_time']
        rest_time = entry['rest_time']
        set_num = entry['set_number']
        if exercise not in exercise_times:
            exercise_times[exercise] = {'sets': [], 'total_time': 0}
        exercise_times[exercise]['sets'].append({'set': set_num, 'set_time': set_time, 'rest_time': rest_time})
        exercise_times[exercise]['total_time'] += set_time + rest_time

    for exercise, data in exercise_times.items():
        avg_set_time = sum(s['set_time'] for s in data['sets']) / len(data['sets'])
        summary += f"- {exercise}: {len(data['sets'])} sets, Total Time: {format_time(data['total_time'])}, Avg Set Time: {format_time(avg_set_time)}\n"
    summary += f"Total Workout Time: {format_time(total_workout_time)}\n"
    summary += f"Status: {'Completed' if completed else 'Stopped Early'}\n"

    # AI Prompt for Insights
    prompt = f"""
    You are a professional fitness trainer analyzing a user's workout performance.

    Based on the following workout summary, provide insights and suggestions:
    - Comment on the speed of exercises (e.g., were sets completed quickly or slowly?).
    - Highlight any notable patterns (e.g., consistent pacing, long rest times).
    - Suggest improvements for future workouts (e.g., adjust reps, rest, or focus areas).
    - Provide motivational feedback to encourage the user.

    Workout Summary:
    {summary}

    Return your response in a clear, concise format with bullet points for insights and suggestions.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        return response.candidates[0].content.parts[0].text, exercise_times
    except Exception as e:
        return f"Error generating insights: {e}", exercise_times

# --- Page: Workout Generator ---
def render_generator_page():
    st.subheader("Workout Generator")

    # Collect user input
    fitness_level = st.selectbox("Your Fitness Level", ["Beginner", "Intermediate", "Advanced"])
    workout_type = st.selectbox("Preferred Workout Type", ["Strength", "Cardio", "HIIT", "Flexibility", "Endurance", "Full Body"])
    muscule_group = st.multiselect("Target Muscle Group(s)", ["Arms", "Back", "Chest", "Legs", "Core", "Shoulders", "Full Body"], default=["Full Body"])
    duration = st.slider("Workout Duration (minutes)", min_value=10, max_value=90, value=30, step=5)
    equipment = st.radio("Available Equipment", ["None", "Basic (dumbbells/mat)", "Full gym access"])
    goals = st.text_area("Fitness Goals", placeholder="e.g., lose weight, build muscle, increase stamina...")

    # --- Prompt Template ---
    prompt = f"""
    You are a professional fitness trainer who creates personalized workout plans.

    Generate a workout plan based on these user preferences:
    - Fitness level: {fitness_level}
    - Workout type: {workout_type}
    - Duration: {duration} minutes
    - Equipment available: {equipment}
    - Goals: {goals}
    - Target muscle group: {muscule_group}

    Return the workout strictly in this JSON format, with only three sections: "warmup", "main", and "cooldown". Do not include any extra commentary or text.

    Example format:
    {{
      "warmup": [
        {{"exercise": "Jumping Jacks", "sets": 1, "reps": 30, "rest": 30}}
      ],
      "main": [
        {{"exercise": "Push Ups", "sets": 3, "reps": 12, "rest": 60}}
      ],
      "cooldown": [
        {{"exercise": "Hamstring Stretch", "sets": 1, "reps": "30 seconds", "rest": 0}}
      ]
    }}
    Please fill in this format with a complete, personalized plan now.
    """

    # --- Generate Plan ---
    if st.button("Generate Workout Plan"):
        with st.spinner("Generating your personalized workout plan..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt
                )
                output = response.candidates[0].content.parts[0].text

                # Show raw text
                st.subheader("Raw Output")
                st.code(output)

                # Clean markdown and extract JSON
                cleaned = re.sub(r"^```json|```$", "", output.strip(), flags=re.MULTILINE).strip()
                json_match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
                if not json_match:
                    raise ValueError("No valid JSON found.")
                json_str = json_match.group(1)

                workout_data = json.loads(json_str)

                # Store workout data in session state
                st.session_state.workout_data = workout_data

                # Display structured workout plan
                st.success("Workout plan parsed and loaded successfully!")
                st.subheader("Workout Plan")

                for section, exercises in workout_data.items():
                    st.markdown(f"### 🏋️ {section.capitalize()}")
                    for idx, ex in enumerate(exercises, start=1):
                        ex_display = f"**{idx}. {ex.get('exercise', 'Unknown')}** — Sets: {ex.get('sets')}, Reps: {ex.get('reps')}, Rest: {ex.get('rest')}s"
                        if 'notes' in ex:
                            ex_display += f" (_{ex['notes']}_)"
                        elif 'description' in ex:
                            ex_display += f" (_{ex['description']}_)"
                        st.markdown(ex_display)

            except Exception as e:
                st.error(f"❌ Failed to parse workout plan. Error: {e}")

    # Start Workout Button
    if st.session_state.workout_data and st.button("Start Workout"):
        st.session_state.page = "tracker"
        st.session_state.current_exercise_idx = 0
        st.session_state.current_set = 1
        st.session_state.rest_timer = 0
        st.session_state.rest_active = False
        st.session_state.rest_start_time = 0
        st.session_state.workout_start_time = time.time()
        st.session_state.set_start_time = time.time()
        st.session_state.timing_data = []
        st.session_state.show_stop_analysis = False
        st.rerun()

# --- Page: Workout Tracker ---
def render_tracker_page():
    st.subheader("Workout Tracker")

    if not st.session_state.workout_data:
        st.error("No workout data. Returning to generator.")
        st.session_state.page = "generator"
        st.rerun()
        return

    if st.session_state.show_stop_analysis:
        # Display analysis after stopping workout
        st.subheader("Workout Stopped")
        st.info("You stopped the workout early. Below is the analysis of your performance.")

        # Calculate total workout time
        total_workout_time = time.time() - st.session_state.workout_start_time

        # Generate and display insights
        with st.spinner("Analyzing your workout..."):
            insights, exercise_times = generate_workout_insights(st.session_state.timing_data, total_workout_time, completed=False)

        st.markdown("### Timing Summary")
        for exercise, data in exercise_times.items():
            avg_set_time = sum(s['set_time'] for s in data['sets']) / len(data['sets'])
            st.markdown(f"- **{exercise}**: {len(data['sets'])} sets, Total Time: {format_time(data['total_time'])}, Avg Set Time: {format_time(avg_set_time)}")
        st.markdown(f"**Total Workout Time**: {format_time(total_workout_time)}")

        st.markdown("### AI Insights and Suggestions")
        st.markdown(insights)

        if st.button("Return to Generator"):
            # Reset session state
            st.session_state.page = "generator"
            st.session_state.current_exercise_idx = 0
            st.session_state.current_set = 1
            st.session_state.workout_data = None
            st.session_state.rest_timer = 0
            st.session_state.rest_active = False
            st.session_state.rest_start_time = 0
            st.session_state.workout_start_time = 0
            st.session_state.set_start_time = 0
            st.session_state.timing_data = []
            st.session_state.show_stop_analysis = False
            st.rerun()
        return

    exercises = (
        st.session_state.workout_data.get("warmup", []) +
        st.session_state.workout_data.get("main", []) +
        st.session_state.workout_data.get("cooldown", [])
    )
    
    if st.session_state.current_exercise_idx >= len(exercises):
        st.session_state.page = "completed"
        st.rerun()
        return

    current_exercise = exercises[st.session_state.current_exercise_idx]

    # Display current exercise and set information
    st.write(f"Now doing: **{current_exercise['exercise']}**")
    st.write(f"**Set**: {st.session_state.current_set} of {current_exercise['sets']} | **Reps**: {current_exercise['reps']} | **Rest**: {current_exercise['rest']}s")

    # YouTube search link for exercise tutorial
    exercise_name = current_exercise['exercise']
    encoded_exercise = urllib.parse.quote(f"how to do {exercise_name}")
    youtube_url = f"https://www.youtube.com/results?search_query={encoded_exercise}"
    st.markdown(
        f'<a href="{youtube_url}" target="_blank" style="text-decoration: none;">'
        '<button style="background-color: #FF0000; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer;">'
        'Watch Tutorial on YouTube 📺'
        '</button></a>',
        unsafe_allow_html=True
    )

    # Rest timer display
    rest_container = st.empty()
    if st.session_state.rest_active:
        elapsed_time = time.time() - st.session_state.rest_start_time
        remaining_time = max(0, st.session_state.rest_timer - int(elapsed_time))
        if remaining_time > 0:
            rest_container.markdown(f"**Resting**: {remaining_time} seconds remaining")
            time.sleep(1)
            st.rerun()
        else:
            # Rest is complete, prepare for next set or exercise
            st.session_state.rest_active = False
            rest_container.markdown("**Rest complete!**")
            rest_duration = int(current_exercise['rest'])
            st.session_state.timing_data[-1]['rest_time'] = rest_duration
            if st.session_state.current_set < current_exercise['sets']:
                # Move to next set
                st.session_state.current_set += 1
                st.session_state.set_start_time = time.time()
            else:
                # All sets complete, move to next exercise
                if st.session_state.current_exercise_idx < len(exercises) - 1:
                    st.session_state.current_exercise_idx += 1
                    st.session_state.current_set = 1
                    st.session_state.set_start_time = time.time()
                else:
                    # Workout complete
                    st.session_state.page = "completed"
            st.rerun()
    else:
        rest_container.markdown("Click 'Complete Set' to proceed.")

    # Complete Set Button
    if not st.session_state.rest_active and st.button("Complete Set", key="complete_set"):
        # Calculate and store set time
        set_time = time.time() - st.session_state.set_start_time
        st.session_state.timing_data.append({
            'exercise': current_exercise['exercise'],
            'set_number': st.session_state.current_set,
            'set_time': set_time,
            'rest_time': 0
        })

        rest_duration = int(current_exercise['rest'])
        if rest_duration > 0:
            st.session_state.rest_timer = rest_duration
            st.session_state.rest_active = True
            st.session_state.rest_start_time = time.time()
            rest_container.markdown(f"**Resting**: {rest_duration} seconds remaining")
        else:
            # No rest, check if more sets are left
            st.session_state.timing_data[-1]['rest_time'] = 0
            if st.session_state.current_set < current_exercise['sets']:
                # Move to next set
                st.session_state.current_set += 1
                st.session_state.set_start_time = time.time()
            else:
                # All sets complete, move to next exercise
                if st.session_state.current_exercise_idx < len(exercises) - 1:
                    st.session_state.current_exercise_idx += 1
                    st.session_state.current_set = 1
                    st.session_state.set_start_time = time.time()
                else:
                    # Workout complete
                    st.session_state.page = "completed"
        st.rerun()

    # Divider for visual separation
    st.markdown("---")

    # Stop Workout Button
    if st.button("Stop Workout", key="stop_workout"):
        st.session_state.show_stop_analysis = True
        st.rerun()

# --- Page: Workout Completed ---
def render_completed_page():
    st.subheader("Workout Completed")
    st.success("Congratulations! You've completed your workout!")

    # Calculate total workout time and generate insights
    total_workout_time = time.time() - st.session_state.workout_start_time
    with st.spinner("Analyzing your workout..."):
        insights, exercise_times = generate_workout_insights(st.session_state.timing_data, total_workout_time, completed=True)

    # Display timing summary and insights
    st.subheader("Workout Analysis")
    st.markdown("### Timing Summary")
    for exercise, data in exercise_times.items():
        avg_set_time = sum(s['set_time'] for s in data['sets']) / len(data['sets'])
        st.markdown(f"- **{exercise}**: {len(data['sets'])} sets, Total Time: {format_time(data['total_time'])}, Avg Set Time: {format_time(avg_set_time)}")
    st.markdown(f"**Total Workout Time**: {format_time(total_workout_time)}")

    st.markdown("### AI Insights and Suggestions")
    st.markdown(insights)

    if st.button("Create New Workout"):
        # Reset session state
        st.session_state.page = "generator"
        st.session_state.current_exercise_idx = 0
        st.session_state.current_set = 1
        st.session_state.workout_data = None
        st.session_state.rest_timer = 0
        st.session_state.rest_active = False
        st.session_state.rest_start_time = 0
        st.session_state.workout_start_time = 0
        st.session_state.set_start_time = 0
        st.session_state.timing_data = []
        st.session_state.show_stop_analysis = False
        st.rerun()

# --- Render the appropriate page ---
if st.session_state.page == "generator":
    render_generator_page()
elif st.session_state.page == "tracker":
    render_tracker_page()
elif st.session_state.page == "completed":
    render_completed_page()
