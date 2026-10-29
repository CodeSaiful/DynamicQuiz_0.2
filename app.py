from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pathlib import Path
import json, random, time

app = Flask(__name__)
app.secret_key = 'change-this-development-secret-key'
BASE_DIR = Path(__file__).resolve().parent
QUESTION_FILE = BASE_DIR / 'questions.json'
ALLOWED_COUNTS = {10, 15, 30}
ALLOWED_DIFFICULTIES = {'Easy', 'Medium', 'Hard'}

with QUESTION_FILE.open(encoding='utf-8') as f:
    QUESTION_BANK = json.load(f)

TOPICS = {
    'python': 'Python',
    'cpp': 'C++',
    'c': 'C Programming',
    'html': 'HTML',
    'css': 'CSS',
    'javascript': 'JavaScript',
    'computer-systems': 'Computer Systems',
    'dsa': 'Data Structures & Algorithms',
    'general': 'General Computer Knowledge',
    'mixed': 'Mixed Topics'
}


def get_questions(topic, difficulty, count):
    pool = []
    if topic == 'mixed':
        for topic_key, items in QUESTION_BANK.items():
            pool.extend([
                dict(q, topic=topic_key)
                for q in items
                if q['difficulty'] == difficulty
            ])
    else:
        pool = [
            dict(q, topic=topic)
            for q in QUESTION_BANK.get(topic, [])
            if q['difficulty'] == difficulty
        ]
    # If a particular level has fewer questions than requested, supplement from other levels.
    if len(pool) < count:
        if topic == 'mixed':
            extra = [
                dict(q, topic=k)
                for k, items in QUESTION_BANK.items()
                for q in items
                if q['difficulty'] != difficulty
            ]
        else:
            extra = [
                dict(q, topic=topic)
                for q in QUESTION_BANK.get(topic, [])
                if q['difficulty'] != difficulty
            ]
        seen = {q['id'] for q in pool}
        pool.extend(q for q in extra if q['id'] not in seen)
    # Keep the requested question count even while the sample bank is small.
    # When a topic has too few examples, top up from the wider bank and label each item by its actual topic.
    if len(pool) < count and topic != 'mixed':
        seen = {q['id'] for q in pool}
        extra = [
            dict(q, topic=k)
            for k, items in QUESTION_BANK.items()
            if k != topic
            for q in items
        ]
        pool.extend(q for q in extra if q['id'] not in seen)
    random.shuffle(pool)
    selected = pool[:count]
    for q in selected:
        q['options'] = list(q['options'])
        random.shuffle(q['options'])
    return selected


@app.route('/')
def index():
    return render_template('index.html', topics=TOPICS)


@app.post('/start')
def start_quiz():
    topic = request.form.get('topic', 'python')
    difficulty = request.form.get('difficulty', 'Easy').title()
    try:
        count = int(request.form.get('count', '10'))
        seconds_per_question = int(request.form.get('seconds_per_question', '30'))
    except ValueError:
        return redirect(url_for('index'))
    if (
        topic not in TOPICS
        or difficulty not in ALLOWED_DIFFICULTIES
        or count not in ALLOWED_COUNTS
        or seconds_per_question not in {15, 30, 60}
    ):
        return redirect(url_for('index'))
    questions = get_questions(topic, difficulty, count)
    if not questions:
        return redirect(url_for('index'))
    session['quiz'] = {
        'topic': topic,
        'difficulty': difficulty,
        'count': len(questions),
        'seconds_per_question': seconds_per_question,
        'started_at': time.time(),
        'deadline': time.time() + len(questions) * seconds_per_question,
        'questions': questions,
        'answers': {}
    }
    return redirect(url_for('quiz'))


@app.route('/quiz')
def quiz():
    quiz_data = session.get('quiz')
    if not quiz_data:
        return redirect(url_for('index'))
    # Keep answer keys on the server; only send public question data.
    public_questions = [
        {k: q[k] for k in ('id', 'question', 'options', 'explanation')}
        for q in quiz_data['questions']
    ]
    return render_template(
        'quiz.html',
        quiz=quiz_data,
        questions=public_questions,
        topic_name=TOPICS.get(quiz_data['topic'], 'Mixed Topics')
    )


@app.post('/save-answer')
def save_answer():
    quiz_data = session.get('quiz')
    if not quiz_data:
        return jsonify({'ok': False, 'error': 'No active quiz'}), 400
    data = request.get_json(silent=True) or {}
    try:
        index = int(data.get('index'))
    except (ValueError, TypeError):
        return jsonify({'ok': False, 'error': 'Invalid question'}), 400
    if (
        index < 0
        or index >= len(quiz_data['questions'])
        or time.time() >= quiz_data['deadline']
    ):
        return jsonify({'ok': False, 'error': 'Quiz expired or question invalid'}), 400
    choice = data.get('choice')
    q = quiz_data['questions'][index]
    if choice is not None and choice not in q['options']:
        return jsonify({'ok': False, 'error': 'Invalid choice'}), 400
    answers = quiz_data.get('answers', {})
    if choice is None:
        answers.pop(str(index), None)
    else:
        answers[str(index)] = choice
    quiz_data['answers'] = answers
    session['quiz'] = quiz_data
    session.modified = True
    return jsonify({'ok': True, 'answered': len(answers)})


@app.route('/submit', methods=['POST', 'GET'])
def submit_quiz():
    quiz_data = session.get('quiz')
    if not quiz_data:
        return redirect(url_for('index'))
    answers = quiz_data.get('answers', {})
    review = []
    correct = 0
    for i, q in enumerate(quiz_data['questions']):
        chosen = answers.get(str(i))
        is_correct = chosen == q['answer']
        if is_correct:
            correct += 1
        review.append({
            'number': i + 1,
            'topic': TOPICS.get(q.get('topic', quiz_data['topic']), 'Mixed Topics'),
            'difficulty': q['difficulty'],
            'question': q['question'],
            'options': q['options'],
            'your_answer': chosen,
            'correct_answer': q['answer'],
            'correct': is_correct,
            'explanation': q['explanation'],
            'status': 'Unanswered' if chosen is None else ('Correct' if is_correct else 'Incorrect')
        })
    total = len(quiz_data['questions'])
    elapsed = min(int(time.time() - quiz_data['started_at']), total * quiz_data['seconds_per_question'])
    result = {
        'topic': quiz_data['topic'],
        'topic_name': TOPICS.get(quiz_data['topic'], 'Mixed Topics'),
        'difficulty': quiz_data['difficulty'],
        'total': total,
        'correct': correct,
        'incorrect': sum(
            1
            for r in review
            if r['your_answer'] is not None and not r['correct']
        ),
        'unanswered': sum(1 for r in review if r['your_answer'] is None),
        'percentage': round(correct / total * 100) if total else 0,
        'elapsed': elapsed,
        'average': round(elapsed / total) if total else 0,
        'review': review,
        'finished_at': int(time.time())
    }
    history = session.get('history', [])
    history.insert(
        0,
        {
            k: result[k]
            for k in (
                'topic_name',
                'difficulty',
                'total',
                'correct',
                'percentage',
                'elapsed',
                'finished_at'
            )
        }
    )
    session['history'] = history[:30]
    session['result'] = result
    session.pop('quiz', None)
    return redirect(url_for('results'))


@app.route('/results')
def results():
    result = session.get('result')
    if not result:
        return redirect(url_for('index'))
    return render_template('results.html', result=result)


@app.route('/history')
def history():
    return render_template('history.html', history=session.get('history', []))


@app.route('/about')
def about():
    return render_template('about.html')


@app.post('/clear-history')
def clear_history():
    session['history'] = []
    return redirect(url_for('history'))


if __name__ == '__main__':
    app.run(debug=True)
