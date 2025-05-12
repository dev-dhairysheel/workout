import streamlit as s
from google import g
from google.api_core import r
import json as j
import re as _r
import time as t
import urllib.parse as u


c = g.Client(api_key=API_KEY)

i = lambda e: (isinstance(e, g.errors.APIError) and e.code in {429, 503})
if hasattr(g.models.Models.generate_content, '__wrapped__'):
    g.models.Models.generate_content = r.Retry(predicate=i)(g.models.Models.generate_content)

s.set_page_config(page_title="AI Workout Planner", page_icon="💪", layout="centered")
s.title("💪 Personalized AI Workout Generator")

if 'pg' not in s.session_state:
    s.session_state.pg = "generator"
if 'ce_idx' not in s.session_state:
    s.session_state.ce_idx = 0
if 'cs' not in s.session_state:
    s.session_state.cs = 1
if 'wd' not in s.session_state:
    s.session_state.wd = None
if 'rt' not in s.session_state:
    s.session_state.rt = 0
if 'ra' not in s.session_state:
    s.session_state.ra = False
if 'rst' not in s.session_state:
    s.session_state.rst = 0
if 'wst' not in s.session_state:
    s.session_state.wst = 0
if 'sst' not in s.session_state:
    s.session_state.sst = 0
if 'td' not in s.session_state:
    s.session_state.td = []
if 'ssa' not in s.session_state:
    s.session_state.ssa = False


def fmt_time(s):
    if s >= 60:
        m = int(s // 60)
        r = s % 60
        return f"{m}m {r:.1f}s"
    return f"{s:.1f}s"


def gen_wi(td, t_w, c=True):

    sm = "Workout Summary:\n"
    ex_times = {}
    for e in td:
        ex = e['exercise']
        st = e['set_time']
        rt = e['rest_time']
        sn = e['set_number']
        if ex not in ex_times:
            ex_times[ex] = {'sets': [], 'total_time': 0}
        ex_times[ex]['sets'].append({'set': sn, 'set_time': st, 'rest_time': rt})
        ex_times[ex]['total_time'] += st + rt

    for ex, d in ex_times.items():
        avg_st = sum(s['set_time'] for s in d['sets']) / len(d['sets'])
        sm += f"- {ex}: {len(d['sets'])} sets, Total Time: {fmt_time(d['total_time'])}, Avg Set Time: {fmt_time(avg_st)}\n"
    sm += f"Total Workout Time: {fmt_time(t_w)}\n"
    sm += f"Status: {'Completed' if c else 'Stopped Early'}\n"


    pr = f"""
    You are a professional fitness trainer analyzing a user's workout performance.

    Based on the following workout summary, provide insights and suggestions:
    - Comment on the speed of exercises (e.g., were sets completed quickly or slowly?).
    - Highlight any notable patterns (e.g., consistent pacing, long rest times).
    - Suggest improvements for future workouts (e.g., adjust reps, rest, or focus areas).
    - Provide motivational feedback to encourage the user.

    Workout Summary:
    {sm}

    Return your response in a clear, concise format with bullet points for insights and suggestions.
    """

    try:
        res = c.models.generate_content(
            model='gemini-2.0-flash',
            contents=pr
        )
        return res.candidates[0].content.parts[0].text, ex_times
    except Exception as e:
        return f"Error generating insights: {e}", ex_times


def r_pg():
    s.subheader("Workout Generator")


    fl = s.selectbox("Your Fitness Level", ["Beginner", "Intermediate", "Advanced"])
    wt = s.selectbox("Preferred Workout Type", ["Strength", "Cardio", "HIIT", "Flexibility", "Endurance", "Full Body"])
    mg = s.multiselect("Target Muscle Group(s)", ["Arms", "Back", "Chest", "Legs", "Core", "Shoulders", "Full Body"], default=["Full Body"])
    dur = s.slider("Workout Duration (minutes)", min_value=10, max_value=90, value=30, step=5)
    eq = s.radio("Available Equipment", ["None", "Basic (dumbbells/mat)", "Full gym access"])
    gl = s.text_area("Fitness Goals", placeholder="e.g., lose weight, build muscle, increase stamina...")


    pr = f"""
    You are a professional fitness trainer who creates personalized workout plans.

    Generate a workout plan based on these user preferences:
    - Fitness level: {fl}
    - Workout type: {wt}
    - Duration: {dur} minutes
    - Equipment available: {eq}
    - Goals: {gl}
    - Target muscle group: {mg}

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


    if s.button("Generate Workout Plan"):
        with s.spinner("Generating your personalized workout plan..."):
            try:
                res = c.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=pr
                )
                out = res.candidates[0].content.parts[0].text


                cl = _r.sub(r"^```json|```$", "", out.strip(), flags=_r.MULTILINE).strip()
                jm = _r.search(r"(\{.*\})", cl, _r.DOTALL)
                if not jm:
                    raise ValueError("No valid JSON found.")
                js = jm.group(1)

                wd = j.loads(js)


                s.session_state.wd = wd

                s.success("Workout plan parsed and loaded successfully!")
                s.subheader("Workout Plan")

                for sec, exs in wd.items():
                    s.markdown(f"### 🏋️ {sec.capitalize()}")
                    for idx, ex in enumerate(exs, start=1):
                        ex_disp = f"**{idx}. {ex.get('exercise', 'Unknown')}** — Sets: {ex.get('sets')}, Reps: {ex.get('reps')}, Rest: {ex.get('rest')}s"
                        if 'notes' in ex:
                            ex_disp += f" (_{ex['notes']}_)"
                        elif 'description' in ex:
                            ex_disp += f" (_{ex['description']}_)"
                        s.markdown(ex_disp)

            except Exception as e:
                s.error(f"❌ Failed to parse workout plan. Error: {e}")


    if s.session_state.wd and s.button("Start Workout"):
        s.session_state.pg = "tracker"
        s.session_state.ce_idx = 0
        s.session_state.cs = 1
        s.session_state.rt = 0
        s.session_state.ra = False
        s.session_state.rst = 0
        s.session_state.wst = t.time()
        s.session_state.sst = t.time()
        s.session_state.td = []
        s.session_state.ssa = False
        s.rerun()


def r_tp():
    s.subheader("Workout Tracker")

    if not s.session_state.wd:
        s.error("No workout data. Returning to generator.")
        s.session_state.pg = "generator"
        s.rerun()
        return

    if s.session_state.ssa:

        s.subheader("Workout Stopped")
        s.info("You stopped the workout early. Below is the analysis of your performance.")


        twt = t.time() - s.session_state.wst


        with s.spinner("Analyzing your workout..."):
            in_s, ex_times = gen_wi(s.session_state.td, twt, c=False)

        s.markdown("### Timing Summary")
        for ex, data in ex_times.items():
            avg_st = sum(s['set_time'] for s in data['sets']) / len(data['sets'])
            s.markdown(f"- **{ex}**: {len(data['sets'])} sets, Total Time: {fmt_time(data['total_time'])}, Avg Set Time: {fmt_time(avg_st)}")
        s.markdown(f"**Total Workout Time**: {fmt_time(twt)}")

        s.markdown("### AI Insights and Suggestions")
        s.markdown(in_s)

        if s.button("Return to Generator"):
            # Reset session state
            s.session_state.pg = "generator"
            s.session_state.ce_idx = 0
            s.session_state.cs = 1
            s.session_state.wd = None
            s.session_state.rt = 0
            s.session_state.ra = False
            s.session_state.rst = 0
            s.session_state.wst = 0
            s.session_state.sst = 0
            s.session_state.td = []
            s.session_state.ssa = False
            s.rerun()
        return

    exs = (
        s.session_state.wd.get("warmup", []) +
        s.session_state.wd.get("main", []) +
        s.session_state.wd.get("cooldown", [])
    )
    
    if s.session_state.ce_idx >= len(exs):
        s.session_state.pg = "completed"
        s.rerun()
        return

    ce = exs[s.session_state.ce_idx]


    s.write(f"Now doing: **{ce['exercise']}**")
    s.write(f"**Set**: {s.session_state.cs} of {ce['sets']} | **Reps**: {ce['reps']} | **Rest**: {ce['rest']}s")


    en = ce['exercise']
    enc = u.quote(f"how to do {en}")
    yt_url = f"https://www.youtube.com/results?search_query={enc}"
    s.markdown(
        f'<a href="{yt_url}" target="_blank" style="text-decoration: none;">'
        '<button style="background-color: #FF0000; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer;">'
        'Watch Tutorial on YouTube 📺'
        '</button></a>',
        unsafe_allow_html=True
    )

    rest_ctn = s.empty()
    if s.session_state.ra:
        elapsed_t = t.time() - s.session_state.rst
        remaining_t = max(0, s.session_state.rt - int(elapsed_t))
        if remaining_t > 0:
            rest_ctn.markdown(f"**Resting**: {remaining_t} seconds remaining")
            t.sleep(1)
            s.rerun()
        else:

            s.session_state.ra = False
            rest_ctn.markdown("**Rest complete!**")
            rd = int(ce['rest'])
            s.session_state.td[-1]['rest_time'] = rd
            if s.session_state.cs < ce['sets']:

                s.session_state.cs += 1
                s.session_state.sst = t.time()
            else:

                if s.session_state.ce_idx < len(exs) - 1:
                    s.session_state.ce_idx += 1
                    s.session_state.cs = 1
                    s.session_state.sst = t.time()
                else:

                    s.session_state.pg = "completed"
            s.rerun()
    else:
        rest_ctn.markdown("Click 'Complete Set' to proceed.")


    if not s.session_state.ra and s.button("Complete Set", key="complete_set"):
        # Calculate and store set time
        st_t = t.time() - s.session_state.sst
        s.session_state.td.append({
            'exercise': ce['exercise'],
            'set_number': s.session_state.cs,
            'set_time': st_t,
            'rest_time': 0
        })

        rd = int(ce['rest'])
        if rd > 0:
            s.session_state.rt = rd
            s.session_state.ra = True
            s.session_state.rst = t.time()
            rest_ctn.markdown(f"**Resting**: {rd} seconds remaining")
        else:

            s.session_state.td[-1]['rest_time'] = 0
            if s.session_state.cs < ce['sets']:
           
                s.session_state.cs += 1
                s.session_state.sst = t.time()
            else:

                if s.session_state.ce_idx < len(exs) - 1:
                    s.session_state.ce_idx += 1
                    s.session_state.cs = 1
                    s.session_state.sst = t.time()
                else:

                    s.session_state.pg = "completed"
        s.rerun()


    s.markdown("---")


    if s.button("Stop Workout", key="stop_workout"):
        s.session_state.ssa = True
        s.rerun()

def r_cp():
    s.subheader("Workout Completed")
    s.success("Congratulations! You've completed your workout!")

    twt = t.time
