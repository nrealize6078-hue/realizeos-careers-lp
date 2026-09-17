/* Native details preserve keyboard/touch behavior, including when JavaScript is off. */
(() => {
  const links = document.querySelectorAll('a[href^="#"]');
  links.forEach((link) => {
    link.addEventListener('click', () => {
      const id = link.getAttribute('href');
      if (!id || id.length < 2) return;
      const destination = document.getElementById(id.slice(1));
      if (!destination) return;
      // Transfer keyboard focus to the destination without disrupting anchor scrolling.
      if (!destination.hasAttribute('tabindex')) destination.setAttribute('tabindex', '-1');
      window.setTimeout(() => destination.focus({ preventScroll: true }), 20);
    });
  });
})();
