(() => {
  const toggle = document.querySelector('.menu-toggle');
  const navigation = document.querySelector('#site-navigation');

  if (toggle && navigation) {
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      navigation.classList.toggle('is-open', !open);
      document.body.classList.toggle('menu-open', !open);
    });
  }

  document.querySelectorAll('[data-carousel]').forEach((carousel) => {
    const track = carousel.querySelector('.carousel-track');
    const previous = carousel.querySelector('.previous');
    const next = carousel.querySelector('.next');
    const current = carousel.querySelector('.carousel-count span');
    const slides = [...carousel.querySelectorAll('.carousel-slide')];

    const step = () => {
      if (!slides.length) return 0;
      const gap = Number.parseFloat(getComputedStyle(track).columnGap || 0);
      return slides[0].getBoundingClientRect().width + gap;
    };

    const update = () => {
      const size = step();
      if (!size) return;
      const index = Math.min(slides.length - 1, Math.max(0, Math.round(track.scrollLeft / size)));
      current.textContent = String(index + 1);
      previous.disabled = index === 0;
      next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 4;
    };

    previous.addEventListener('click', () => track.scrollBy({ left: -step(), behavior: 'smooth' }));
    next.addEventListener('click', () => track.scrollBy({ left: step(), behavior: 'smooth' }));
    track.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    update();
  });
})();
