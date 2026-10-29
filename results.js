(() => {
  const tabs = [...document.querySelectorAll('.filter-tabs button')];
  const cards = [...document.querySelectorAll('.review-card')];
  tabs.forEach(tab =>
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.toggle('active', t === tab));
      cards.forEach(
        card =>
          (card.hidden =
            tab.dataset.filter !== 'All' &&
            card.dataset.status !== tab.dataset.filter)
      );
    })
  );
})();
