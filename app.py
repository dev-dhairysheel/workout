lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll, llllllllllllIlI, llllllllllllIIl, llllllllllllIII, lllllllllllIlll, lllllllllllIllI = sum, int, enumerate, ValueError, bool, len, max, Exception, isinstance, hasattr

from streamlit import multiselect as llIIllIlllIlII, code as IllIllIlllIIlI, slider as IlIlllIlIllIll, success as IlIIIlIIIllllI, rerun as IIlIIIIIlIIIll, subheader as IIIlIlIIIIlllI, radio as IIIlIlllIlIlIl, markdown as lIIIllllIllIIl, write as IlllllIIIIIIIl, error as llIllIIllllIIl, spinner as lIIIlIllIllllI, selectbox as IIIllIllllllll, title as IIIIlIIIIllIlI, button as IIIllIIllllllI, info as llIlIlIlIlIlIl, set_page_config as lllIIIIlIlIIlI, text_area as lIIllIllIIIIIl, session_state as IIllllIIlllIll, empty as lIllIIIlllIlIl
from streamlit.session_state import rest_timer as lIlIIlIIlIIIll, timing_data as llIIlllIIIIIII, current_exercise_idx as IIllllIllllIII, current_set as lllllIIIIllIlI, workout_start_time as IlIIIIlIIIIlII, rest_start_time as IIlllIIIIllIlI, page as lIlIlIIIlllIll, set_start_time as lIIlllIIlIIIlI, show_stop_analysis as llllIIlIIlIIII, workout_data as IIIIllllIIlIIl, rest_active as IlIIlllIlllllI
from re import sub as IlIlllIIIlIIlI, DOTALL as IllIllIllIIllI, MULTILINE as lIllIIIIIlIIlI, search as llIlllIIIlIlll
from json import loads as IlIIIlIllIllIl
from time import sleep as lllIlIIIIIlIIl, time as IllllllllIlIIl
from streamlit.session_state.workout_data import get as IlIIlIllIllIlI
from streamlit.session_state.timing_data import append as IlIIllIlIIllIl
from google import genai as lIlIllIllIIlII
from google.api_core import retry as IIIlllllllIlIl
llllllIIlIlIlIllll = lIlIllIllIIlII.Client(api_key=API_KEY)
IIlllIIllIlIllIIIl = lambda lIlIllllIllIIIIlIl: lllllllllllIlll(lIlIllllIllIIIIlIl, lIlIllIllIIlII.errors.APIError) and lIlIllllIllIIIIlIl.code in {429, 503}
if lllllllllllIllI(lIlIllIllIIlII.models.Models.generate_content, '__wrapped__'):
    lIlIllIllIIlII.models.Models.generate_content = IIIlllllllIlIl.Retry(predicate=IIlllIIllIlIllIIIl)(lIlIllIllIIlII.models.Models.generate_content)
lllIIIIlIlIIlI(page_title='AI Workout Planner', page_icon='💪', layout='centered')
IIIIlIIIIllIlI('💪 Personalized AI Workout Generator')
if 'page' not in IIllllIIlllIll:
    IIllIIllllIIllIlIl = 'generator'
if 'current_exercise_idx' not in IIllllIIlllIll:
    IIIllllIllIlIllIIl = 0
if 'current_set' not in IIllllIIlllIll:
    lIllIlIIIlIllIIIll = 1
if 'workout_data' not in IIllllIIlllIll:
    llIlllIIIIIIIlIlIl = None
if 'rest_timer' not in IIllllIIlllIll:
    llIIlIIllIlIlIllIl = 0
if 'rest_active' not in IIllllIIlllIll:
    IlIIlllIIIIIIlIIll = llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)
if 'rest_start_time' not in IIllllIIlllIll:
    IIllIIIllIIlIllIll = 0
if 'workout_start_time' not in IIllllIIlllIll:
    llIlIllIIlIllIlIll = 0
if 'set_start_time' not in IIllllIIlllIll:
    IIlllIlIIlllIIIllI = 0
if 'timing_data' not in IIllllIIlllIll:
    llIllIlllllIIIIlIl = []
if 'show_stop_analysis' not in IIllllIIlllIll:
    IIIIIIIIIllIlllIII = llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)

def IlIIIlIIllllIIlllI(IlllIlIIIlIllIIIII):
    if IlllIlIIIlIllIIIII >= 60:
        IlIllIllIIIlIlllIl = llllllllllllllI(IlllIlIIIlIllIIIII // 60)
        lllIllIIIlIllIIlII = IlllIlIIIlIllIIIII % 60
        return f'{IlIllIllIIIlIlllIl}m {lllIllIIIlIllIIlII:.1f}s'
    return f'{IlllIlIIIlIllIIIII:.1f}s'

def llIlIIllllIllIIIll(llIllIlllllIIIIlIl, lllIllllIlIIIllIII, lIlllllIIllIllIIlI=llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1)):
    IIlIIIlIIIlIIlIIIl = 'Workout Summary:\n'
    llIIlIlIIIIllllIll = {}
    for lIlIlllllIIlIIllIl in llIllIlllllIIIIlIl:
        IIIIIIIlllIIIlIllI = lIlIlllllIIlIIllIl['exercise']
        IllIIlIIIllIIIlIll = lIlIlllllIIlIIllIl['set_time']
        IIIIlIIllIIlIIIlll = lIlIlllllIIlIIllIl['rest_time']
        lIIlIlIlIIIIlIIlII = lIlIlllllIIlIIllIl['set_number']
        if IIIIIIIlllIIIlIllI not in llIIlIlIIIIllllIll:
            llIIlIlIIIIllllIll[IIIIIIIlllIIIlIllI] = {'sets': [], 'total_time': 0}
        llIIlIlIIIIllllIll[IIIIIIIlllIIIlIllI]['sets'].append({'set': lIIlIlIlIIIIlIIlII, 'set_time': IllIIlIIIllIIIlIll, 'rest_time': IIIIlIIllIIlIIIlll})
        llIIlIlIIIIllllIll[IIIIIIIlllIIIlIllI]['total_time'] += IllIIlIIIllIIIlIll + IIIIlIIllIIlIIIlll
    for (IIIIIIIlllIIIlIllI, llIIlIlIIIllIllIll) in llIIlIlIIIIllllIll.items():
        lIIIIllIIIIlIlIIIl = lllllllllllllll((s['set_time'] for s in llIIlIlIIIllIllIll['sets'])) / llllllllllllIlI(llIIlIlIIIllIllIll['sets'])
        IIlIIIlIIIlIIlIIIl += f"- {IIIIIIIlllIIIlIllI}: {llllllllllllIlI(llIIlIlIIIllIllIll['sets'])} sets, Total Time: {IlIIIlIIllllIIlllI(llIIlIlIIIllIllIll['total_time'])}, Avg Set Time: {IlIIIlIIllllIIlllI(lIIIIllIIIIlIlIIIl)}\n"
    IIlIIIlIIIlIIlIIIl += f'Total Workout Time: {IlIIIlIIllllIIlllI(lllIllllIlIIIllIII)}\n'
    IIlIIIlIIIlIIlIIIl += f"Status: {('Completed' if lIlllllIIllIllIIlI else 'Stopped Early')}\n"
    llIIIlIIIIIllIIlII = f"\n    You are a professional fitness trainer analyzing a user's workout performance.\n\n    Based on the following workout summary, provide insights and suggestions:\n    - Comment on the speed of exercises (e.g., were sets completed quickly or slowly?).\n    - Highlight any notable patterns (e.g., consistent pacing, long rest times).\n    - Suggest improvements for future workouts (e.g., adjust reps, rest, or focus areas).\n    - Provide motivational feedback to encourage the user.\n\n    Workout Summary:\n    {IIlIIIlIIIlIIlIIIl}\n\n    Return your response in a clear, concise format with bullet points for insights and suggestions.\n    "
    try:
        lIIllIllIlIlIllllI = llllllIIlIlIlIllll.models.generate_content(model='gemini-2.0-flash', contents=llIIIlIIIIIllIIlII)
        return (lIIllIllIlIlIllllI.candidates[0].content.parts[0].text, llIIlIlIIIIllllIll)
    except llllllllllllIII as lIlIllllIllIIIIlIl:
        return (f'Error generating insights: {lIlIllllIllIIIIlIl}', llIIlIlIIIIllllIll)

def IlIIIllIIIlllIIllI():
    IIIlIlIIIIlllI('Workout Generator')
    IlllIllllllIIllllI = IIIllIllllllll('Your Fitness Level', ['Beginner', 'Intermediate', 'Advanced'])
    IllIIlIllllIlIIlll = IIIllIllllllll('Preferred Workout Type', ['Strength', 'Cardio', 'HIIT', 'Flexibility', 'Endurance', 'Full Body'])
    IIlllIlIlllIlIIlll = llIIllIlllIlII('Target Muscle Group(s)', ['Arms', 'Back', 'Chest', 'Legs', 'Core', 'Shoulders', 'Full Body'], default=['Full Body'])
    lllllIIIlIIIlIIIII = IlIlllIlIllIll('Workout Duration (minutes)', min_value=10, max_value=90, value=30, step=5)
    llllllIllIlIlllIlI = IIIlIlllIlIlIl('Available Equipment', ['None', 'Basic (dumbbells/mat)', 'Full gym access'])
    IllllIIIlIlllIllII = lIIllIllIIIIIl('Fitness Goals', placeholder='e.g., lose weight, build muscle, increase stamina...')
    llIIIlIIIIIllIIlII = f'\n    You are a professional fitness trainer who creates personalized workout plans.\n\n    Generate a workout plan based on these user preferences:\n    - Fitness level: {IlllIllllllIIllllI}\n    - Workout type: {IllIIlIllllIlIIlll}\n    - Duration: {lllllIIIlIIIlIIIII} minutes\n    - Equipment available: {llllllIllIlIlllIlI}\n    - Goals: {IllllIIIlIlllIllII}\n    - Target muscle group: {IIlllIlIlllIlIIlll}\n\n    Return the workout strictly in this JSON format, with only three sections: "warmup", "main", and "cooldown". Do not include any extra commentary or text.\n\n    Example format:\n    {{\n      "warmup": [\n        {{"exercise": "Jumping Jacks", "sets": 1, "reps": 30, "rest": 30}}\n      ],\n      "main": [\n        {{"exercise": "Push Ups", "sets": 3, "reps": 12, "rest": 60}}\n      ],\n      "cooldown": [\n        {{"exercise": "Hamstring Stretch", "sets": 1, "reps": "30 seconds", "rest": 0}}\n      ]\n    }}\n    Please fill in this format with a complete, personalized plan now.\n    '
    if IIIllIIllllllI('Generate Workout Plan'):
        with lIIIlIllIllllI('Generating your personalized workout plan...'):
            try:
                lIIllIllIlIlIllllI = llllllIIlIlIlIllll.models.generate_content(model='gemini-2.0-flash', contents=llIIIlIIIIIllIIlII)
                IllIllIlIlllIllIIl = lIIllIllIlIlIllllI.candidates[0].content.parts[0].text
                IIIlIlIIIIlllI('Raw Output')
                IllIllIlllIIlI(IllIllIlIlllIllIIl)
                IIlllIIllIIllIIlIl = IlIlllIIIlIIlI('^```json|```$', '', IllIllIlIlllIllIIl.strip(), flags=lIllIIIIIlIIlI).strip()
                lllIlIlllllIllIlll = llIlllIIIlIlll('(\\{.*\\})', IIlllIIllIIllIIlIl, IllIllIllIIllI)
                if not lllIlIlllllIllIlll:
                    raise lllllllllllllII('No valid JSON found.')
                IllIIIIlIIlIIIlIlI = lllIlIlllllIllIlll.group(1)
                llIlllIIIIIIIlIlIl = IlIIIlIllIllIl(IllIIIIlIIlIIIlIlI)
                llIlllIIIIIIIlIlIl = llIlllIIIIIIIlIlIl
                IlIIIlIIIllllI('Workout plan parsed and loaded successfully!')
                IIIlIlIIIIlllI('Workout Plan')
                for (lllIIIIlIIIlIlIlII, lIIIIllIIIIllIIIIl) in llIlllIIIIIIIlIlIl.items():
                    lIIIllllIllIIl(f'### 🏋️ {lllIIIIlIIIlIlIlII.capitalize()}')
                    for (IIIIlllIlllIlIlIlI, IIlIlIIIIIlIIIllII) in lllllllllllllIl(lIIIIllIIIIllIIIIl, start=1):
                        llIllllIIlIllIIlII = f"**{IIIIlllIlllIlIlIlI}. {IIlIlIIIIIlIIIllII.get('exercise', 'Unknown')}** — Sets: {IIlIlIIIIIlIIIllII.get('sets')}, Reps: {IIlIlIIIIIlIIIllII.get('reps')}, Rest: {IIlIlIIIIIlIIIllII.get('rest')}s"
                        if 'notes' in IIlIlIIIIIlIIIllII:
                            llIllllIIlIllIIlII += f" (_{IIlIlIIIIIlIIIllII['notes']}_)"
                        elif 'description' in IIlIlIIIIIlIIIllII:
                            llIllllIIlIllIIlII += f" (_{IIlIlIIIIIlIIIllII['description']}_)"
                        lIIIllllIllIIl(llIllllIIlIllIIlII)
            except llllllllllllIII as lIlIllllIllIIIIlIl:
                llIllIIllllIIl(f'❌ Failed to parse workout plan. Error: {lIlIllllIllIIIIlIl}')
    if llIlllIIIIIIIlIlIl and IIIllIIllllllI('Start Workout'):
        IIllIIllllIIllIlIl = 'tracker'
        IIIllllIllIlIllIIl = 0
        lIllIlIIIlIllIIIll = 1
        llIIlIIllIlIlIllIl = 0
        IlIIlllIIIIIIlIIll = llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)
        IIllIIIllIIlIllIll = 0
        llIlIllIIlIllIlIll = IllllllllIlIIl()
        IIlllIlIIlllIIIllI = IllllllllIlIIl()
        llIllIlllllIIIIlIl = []
        IIIIIIIIIllIlllIII = llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)
        IIlIIIIIlIIIll()

def IIllIlllllIlIIlIII():
    IIIlIlIIIIlllI('Workout Tracker')
    if not llIlllIIIIIIIlIlIl:
        llIllIIllllIIl('No workout data. Returning to generator.')
        IIllIIllllIIllIlIl = 'generator'
        IIlIIIIIlIIIll()
        return
    if IIIIIIIIIllIlllIII:
        IIIlIlIIIIlllI('Workout Stopped')
        llIlIlIlIlIlIl('You stopped the workout early. Below is the analysis of your performance.')
        lllIllllIlIIIllIII = IllllllllIlIIl() - llIlIllIIlIllIlIll
        with lIIIlIllIllllI('Analyzing your workout...'):
            (lIlIlllIllIlIIIlIl, llIIlIlIIIIllllIll) = llIlIIllllIllIIIll(llIllIlllllIIIIlIl, lllIllllIlIIIllIII, completed=llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0))
        lIIIllllIllIIl('### Timing Summary')
        for (IIIIIIIlllIIIlIllI, llIIlIlIIIllIllIll) in llIIlIlIIIIllllIll.items():
            lIIIIllIIIIlIlIIIl = lllllllllllllll((s['set_time'] for s in llIIlIlIIIllIllIll['sets'])) / llllllllllllIlI(llIIlIlIIIllIllIll['sets'])
            lIIIllllIllIIl(f"- **{IIIIIIIlllIIIlIllI}**: {llllllllllllIlI(llIIlIlIIIllIllIll['sets'])} sets, Total Time: {IlIIIlIIllllIIlllI(llIIlIlIIIllIllIll['total_time'])}, Avg Set Time: {IlIIIlIIllllIIlllI(lIIIIllIIIIlIlIIIl)}")
        lIIIllllIllIIl(f'**Total Workout Time**: {IlIIIlIIllllIIlllI(lllIllllIlIIIllIII)}')
        lIIIllllIllIIl('### AI Insights and Suggestions')
        lIIIllllIllIIl(lIlIlllIllIlIIIlIl)
        if IIIllIIllllllI('Return to Generator'):
            IIllIIllllIIllIlIl = 'generator'
            IIIllllIllIlIllIIl = 0
            lIllIlIIIlIllIIIll = 1
            llIlllIIIIIIIlIlIl = None
            llIIlIIllIlIlIllIl = 0
            IlIIlllIIIIIIlIIll = llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)
            IIllIIIllIIlIllIll = 0
            llIlIllIIlIllIlIll = 0
            IIlllIlIIlllIIIllI = 0
            llIllIlllllIIIIlIl = []
            IIIIIIIIIllIlllIII = llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)
            IIlIIIIIlIIIll()
        return
    lIIIIllIIIIllIIIIl = IlIIlIllIllIlI('warmup', []) + IlIIlIllIllIlI('main', []) + IlIIlIllIllIlI('cooldown', [])
    if IIIllllIllIlIllIIl >= llllllllllllIlI(lIIIIllIIIIllIIIIl):
        IIllIIllllIIllIlIl = 'completed'
        IIlIIIIIlIIIll()
        return
    IllIIlIllIllIIlIll = lIIIIllIIIIllIIIIl[IIIllllIllIlIllIIl]
    IlllllIIIIIIIl(f"Now doing: **{IllIIlIllIllIIlIll['exercise']}**")
    IlllllIIIIIIIl(f"**Set**: {lIllIlIIIlIllIIIll} of {IllIIlIllIllIIlIll['sets']} | **Reps**: {IllIIlIllIllIIlIll['reps']} | **Rest**: {IllIIlIllIllIIlIll['rest']}s")
    IlIIIIIIllIlIIIlll = IllIIlIllIllIIlIll['exercise']
    llIlIlllIllIIlllIl = urllib.parse.quote(f'how to do {IlIIIIIIllIlIIIlll}')
    IllIIllIIllIIIlIll = f'https://www.youtube.com/results?search_query={llIlIlllIllIIlllIl}'
    lIIIllllIllIIl(f'<a href="{IllIIllIIllIIIlIll}" target="_blank" style="text-decoration: none;"><button style="background-color: #FF0000; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer;">Watch Tutorial on YouTube 📺</button></a>', unsafe_allow_html=llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1))
    IIIIIllllllIIIIlll = lIllIIIlllIlIl()
    if IlIIlllIIIIIIlIIll:
        lllIIlIlIIIIlIIlIl = IllllllllIlIIl() - IIllIIIllIIlIllIll
        lIlIIlIlIIlIlllIII = llllllllllllIIl(0, llIIlIIllIlIlIllIl - llllllllllllllI(lllIIlIlIIIIlIIlIl))
        if lIlIIlIlIIlIlllIII > 0:
            IIIIIllllllIIIIlll.markdown(f'**Resting**: {lIlIIlIlIIlIlllIII} seconds remaining')
            lllIlIIIIIlIIl(1)
            IIlIIIIIlIIIll()
        else:
            IlIIlllIIIIIIlIIll = llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)
            IIIIIllllllIIIIlll.markdown('**Rest complete!**')
            IIlllIIllIIIIIllII = llllllllllllllI(IllIIlIllIllIIlIll['rest'])
            llIllIlllllIIIIlIl[-1]['rest_time'] = IIlllIIllIIIIIllII
            if lIllIlIIIlIllIIIll < IllIIlIllIllIIlIll['sets']:
                lIllIlIIIlIllIIIll += 1
                IIlllIlIIlllIIIllI = IllllllllIlIIl()
            elif IIIllllIllIlIllIIl < llllllllllllIlI(lIIIIllIIIIllIIIIl) - 1:
                IIIllllIllIlIllIIl += 1
                lIllIlIIIlIllIIIll = 1
                IIlllIlIIlllIIIllI = IllllllllIlIIl()
            else:
                IIllIIllllIIllIlIl = 'completed'
            IIlIIIIIlIIIll()
    else:
        IIIIIllllllIIIIlll.markdown("Click 'Complete Set' to proceed.")
    if not IlIIlllIIIIIIlIIll and IIIllIIllllllI('Complete Set', key='complete_set'):
        IllIIlIIIllIIIlIll = IllllllllIlIIl() - IIlllIlIIlllIIIllI
        IlIIllIlIIllIl({'exercise': IllIIlIllIllIIlIll['exercise'], 'set_number': lIllIlIIIlIllIIIll, 'set_time': IllIIlIIIllIIIlIll, 'rest_time': 0})
        IIlllIIllIIIIIllII = llllllllllllllI(IllIIlIllIllIIlIll['rest'])
        if IIlllIIllIIIIIllII > 0:
            llIIlIIllIlIlIllIl = IIlllIIllIIIIIllII
            IlIIlllIIIIIIlIIll = llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1)
            IIllIIIllIIlIllIll = IllllllllIlIIl()
            IIIIIllllllIIIIlll.markdown(f'**Resting**: {IIlllIIllIIIIIllII} seconds remaining')
        else:
            llIllIlllllIIIIlIl[-1]['rest_time'] = 0
            if lIllIlIIIlIllIIIll < IllIIlIllIllIIlIll['sets']:
                lIllIlIIIlIllIIIll += 1
                IIlllIlIIlllIIIllI = IllllllllIlIIl()
            elif IIIllllIllIlIllIIl < llllllllllllIlI(lIIIIllIIIIllIIIIl) - 1:
                IIIllllIllIlIllIIl += 1
                lIllIlIIIlIllIIIll = 1
                IIlllIlIIlllIIIllI = IllllllllIlIIl()
            else:
                IIllIIllllIIllIlIl = 'completed'
        IIlIIIIIlIIIll()
    lIIIllllIllIIl('---')
    if IIIllIIllllllI('Stop Workout', key='stop_workout'):
        IIIIIIIIIllIlllIII = llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1)
        IIlIIIIIlIIIll()

def IlIIIlIlIIlIllIllI():
    IIIlIlIIIIlllI('Workout Completed')
    IlIIIlIIIllllI("Congratulations! You've completed your workout!")
    lllIllllIlIIIllIII = IllllllllIlIIl() - llIlIllIIlIllIlIll
    with lIIIlIllIllllI('Analyzing your workout...'):
        (lIlIlllIllIlIIIlIl, llIIlIlIIIIllllIll) = llIlIIllllIllIIIll(llIllIlllllIIIIlIl, lllIllllIlIIIllIII, completed=llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1))
    IIIlIlIIIIlllI('Workout Analysis')
    lIIIllllIllIIl('### Timing Summary')
    for (IIIIIIIlllIIIlIllI, llIIlIlIIIllIllIll) in llIIlIlIIIIllllIll.items():
        lIIIIllIIIIlIlIIIl = lllllllllllllll((s['set_time'] for s in llIIlIlIIIllIllIll['sets'])) / llllllllllllIlI(llIIlIlIIIllIllIll['sets'])
        lIIIllllIllIIl(f"- **{IIIIIIIlllIIIlIllI}**: {llllllllllllIlI(llIIlIlIIIllIllIll['sets'])} sets, Total Time: {IlIIIlIIllllIIlllI(llIIlIlIIIllIllIll['total_time'])}, Avg Set Time: {IlIIIlIIllllIIlllI(lIIIIllIIIIlIlIIIl)}")
    lIIIllllIllIIl(f'**Total Workout Time**: {IlIIIlIIllllIIlllI(lllIllllIlIIIllIII)}')
    lIIIllllIllIIl('### AI Insights and Suggestions')
    lIIIllllIllIIl(lIlIlllIllIlIIIlIl)
    if IIIllIIllllllI('Create New Workout'):
        IIllIIllllIIllIlIl = 'generator'
        IIIllllIllIlIllIIl = 0
        lIllIlIIIlIllIIIll = 1
        llIlllIIIIIIIlIlIl = None
        llIIlIIllIlIlIllIl = 0
        IlIIlllIIIIIIlIIll = llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)
        IIllIIIllIIlIllIll = 0
        llIlIllIIlIllIlIll = 0
        IIlllIlIIlllIIIllI = 0
        llIllIlllllIIIIlIl = []
        IIIIIIIIIllIlllIII = llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)
        IIlIIIIIlIIIll()
if IIllIIllllIIllIlIl == 'generator':
    IlIIIllIIIlllIIllI()
elif IIllIIllllIIllIlIl == 'tracker':
    IIllIlllllIlIIlIII()
elif IIllIIllllIIllIlIl == 'completed':
    IlIIIlIlIIlIllIllI()
