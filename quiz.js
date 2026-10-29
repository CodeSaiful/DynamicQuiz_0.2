(() => {
  const dataEl = document.getElementById('quiz-data');
  if (!dataEl) return;
  const data = JSON.parse(dataEl.textContent);
  const questions = data.questions;
  const count = questions.length;
  let index = 0;
  let answers = {...data.answers};
  let submitting = false;
  const text = document.getElementById('question-text'),
    options = document.getElementById('answer-options'),
    label = document.getElementById('question-label');
  const fill = document.getElementById('progress-fill'),
    numbers = [...document.querySelectorAll('.question-number')],
    prev = document.getElementById('prev-btn'),
    next = document.getElementById('next-btn'),
    answered = document.getElementById('answered-count'),
    status = document.getElementById('save-status');
  const timer = document.getElementById('timer'),
    deadline = Number(timer.dataset.deadline);
  let remaining = Math.max(0, Math.ceil(deadline - Date.now()/1000));

  function save(choice) {
    fetch('/save-answer', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({index,choice})
    })
      .then(r => r.json())
      .then(res => {
        if (!res.ok) status.textContent = 'Could not save this choice.';
        else status.textContent = 'Your choices are saved as you go.';
      })
      .catch(
        () =>
          (status.textContent =
            'Connection issue: your choice remains on this page.')
      );
  }

  function render() {
    const q = questions[index];
    label.textContent = `Question ${index+1}`;
    text.textContent = q.question;
    fill.style.width = `${((index+1)/count)*100}%`;
    options.innerHTML = '';
    q.options.forEach((answer, i) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className =
        'answer-option' + (answers[index] === answer ? ' selected' : '');
      btn.dataset.answer = answer;
      const letter = document.createElement('span');
      letter.className = 'answer-letter';
      letter.textContent = 'ABCD'[i] || '•';
      const val = document.createElement('span');
      val.textContent = answer;
      btn.append(letter, val);
      btn.addEventListener('click', () => {
        if (submitting) return;
        answers[index] = answer;
        render();
        save(answer);
      });
      options.append(btn);
    });
    prev.disabled = index === 0;
    next.textContent =
      index === count-1 ? 'Review & submit →' : 'Next question →';
    numbers.forEach((b, i) => {
      b.classList.toggle('current', i === index);
      b.classList.toggle('answered', answers[i] !== undefined);
    });
    answered.textContent = `${Object.keys(answers).length}/${count}`;
  }

  prev.addEventListener('click', () => {
    if (index > 0) {
      index--;
      render();
    }
  });
  next.addEventListener('click', () => {
    if (index < count-1) {
      index++;
      render();
    } else openModal();
  });
  numbers.forEach(b =>
    b.addEventListener('click', () => {
      index = Number(b.dataset.index);
      render();
    })
  );
  const modal = document.getElementById('submit-modal');
  function openModal() {
    const missing = count - Object.keys(answers).length;
    document.getElementById('submit-message').textContent = missing
      ? `You have ${missing} unanswered question${missing===1?'':'s'}. You can still go back and check your answers.`
      : 'All questions have an answer. Ready to see your results?';
    modal.hidden = false;
  }
  document.getElementById('submit-btn').addEventListener('click', openModal);
  document.getElementById('cancel-submit').addEventListener('click', () => modal.hidden = true);

  function tick() {
    remaining = Math.max(0, Math.ceil(deadline-Date.now()/1000));
    timer.textContent = `${remaining}s`;
    timer.classList.toggle('warning', remaining<=10);
    if (remaining<=0) {
      submitting = true;
      window.location.href = '/submit';
    }
  }
  tick();
  setInterval(tick, 250);
  render();
})();
