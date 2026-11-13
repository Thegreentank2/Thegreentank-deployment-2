/* Static-host controls for the version 106 PDF readers and fuel publication. */
(() => {
  'use strict';
  document.querySelectorAll('button[aria-controls="complete-pdf-document"]').forEach(button => {
    const container = document.getElementById(button.getAttribute('aria-controls'));
    const link = button.parentElement.querySelector('a[href]');
    if (!container || !link) return;
    const preview = Array.from(container.childNodes);
    button.addEventListener('click', () => {
      const open = button.getAttribute('aria-expanded') !== 'true';
      button.setAttribute('aria-expanded', String(open));
      container.replaceChildren();
      button.textContent = open ? 'Close the reader −' : 'Read the complete PDF here +';
      if (!open) { container.append(...preview); return; }
      const frame = document.createElement('iframe');
      frame.src = link.href.split('#')[0] + '#view=FitH';
      frame.title = (document.querySelector('h1')?.textContent || 'Publication') + ' — complete PDF';
      frame.style.cssText = 'display:block;width:100%;height:85vh;min-height:600px;border:1px solid #172c23;background:white';
      container.append(frame);
    });
  });

  const demand = document.getElementById('demand');
  if (demand) {
    const fields = Array.from({length:6}, (_, i) => document.getElementById('fuel-input-' + i));
    const totalNode = demand.querySelector('[data-testid="fuel-total"]');
    const results = totalNode?.parentElement;
    const fmt = n => n.toLocaleString('en-GB', {maximumFractionDigits:1});
    const update = () => {
      const values = fields.map((field, i) => {
        let n = Number(field.value);
        if (!Number.isFinite(n)) n = Number(field.min);
        n = Math.min(Number(field.max), Math.max(Number(field.min), i === 0 ? Math.floor(n) : n));
        field.value = String(n);
        return n;
      });
      const [homes, distance, consumption, electricity, yieldPerLitre, share] = values;
      const vehicle = distance * consumption / 100;
      const generator = electricity / yieldPerLitre;
      const total = homes * (vehicle + generator);
      totalNode.textContent = fmt(total) + ' L';
      results.querySelector('p').textContent = fmt(vehicle) + ' L vehicle + ' + fmt(generator) + ' L generator per household';
      const components = results.querySelectorAll('b');
      components[0].textContent = fmt(total * share / 100) + ' L';
      components[1].textContent = fmt(total * (1 - share / 100)) + ' L';
      results.querySelectorAll('p')[1].textContent = fmt(total * 12) + ' L/year of finished fuel. Existing FAME in any base fuel must be included in the selected final fraction.';
    };
    if (fields.every(Boolean) && results) {
      fields.forEach(field => field.addEventListener('input', update));
      update();
    }
  }

  const videos = {
    'fuelpod': 'https://player.vimeo.com/video/7607669?dnt=1',
    'biopro-190': 'https://www.youtube-nocookie.com/embed/qnwSzJ9zTcE?rel=0',
    'greenergy': 'https://www.youtube-nocookie.com/embed/VeqWG8hVsXw?rel=0',
    'eni': 'https://www.youtube-nocookie.com/embed/mqInjUJSQi4?rel=0',
    'honeywell': 'https://play.vidyard.com/8T9vPw2PQRdXV5WmcjymgU.html',
    'kao-data': 'https://player.vimeo.com/video/894148325?dnt=1',
    'attenborough': 'https://player.vimeo.com/video/1039072811?dnt=1'
  };
  let active = null;
  const controls = Object.entries(videos).map(([id, url]) => {
    const button = document.querySelector('button[aria-controls="player-' + id + '"]');
    const container = document.getElementById('player-' + id);
    if (!button || !container) return null;
    return {button, container, url, preview:Array.from(container.childNodes)};
  }).filter(Boolean);
  const close = item => {
    item.container.replaceChildren(...item.preview);
    item.button.setAttribute('aria-expanded', 'false');
    item.button.textContent = 'Load video';
    item.button.setAttribute('aria-label', item.button.getAttribute('aria-label').replace(/^Close video:/, 'Load video:'));
  };
  controls.forEach(item => item.button.addEventListener('click', () => {
    const wasActive = active === item;
    if (active) close(active);
    active = wasActive ? null : item;
    if (!active) return;
    const frame = document.createElement('iframe');
    frame.src = item.url;
    frame.title = item.button.getAttribute('aria-label').replace(/^Load video: /, '');
    frame.allow = 'autoplay; encrypted-media; fullscreen; picture-in-picture';
    frame.allowFullscreen = true;
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    item.container.replaceChildren(frame);
    item.button.setAttribute('aria-expanded', 'true');
    item.button.textContent = 'Close player';
    item.button.setAttribute('aria-label', item.button.getAttribute('aria-label').replace(/^Load video:/, 'Close video:'));
  }));
})();
