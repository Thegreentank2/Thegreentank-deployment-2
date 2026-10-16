/* Static mirror controls for the approved settlement and recycling publications. */
(function () {
  'use strict';
  const prefix = '/Thegreentank-deployment-2';
  const path = location.pathname.replace(/\/$/, '');
  const local = value => value.startsWith(prefix + '/') ? value : prefix + value;

  function installDocumentViewer() {
    const button = document.querySelector('button[aria-controls="publication-embedded-document"]');
    const container = document.getElementById('publication-embedded-document');
    if (!button || !container) return;
    const link = button.parentElement.querySelector('a[href]');
    if (!link) return;
    const preview = Array.from(container.childNodes);
    let open = false;
    button.addEventListener('click', () => {
      open = !open;
      container.replaceChildren();
      if (open) {
        const frame = document.createElement('iframe');
        frame.src = link.href;
        frame.title = document.querySelector('h1').textContent.trim();
        if (new URL(link.href).pathname.endsWith('.html')) frame.setAttribute('sandbox', 'allow-scripts allow-downloads');
        frame.style.cssText = 'display:block;width:100%;height:82vh;min-height:620px;border:1px solid #172c23;background:white;margin-top:32px';
        container.append(frame);
      } else preview.forEach(node => container.append(node));
      button.setAttribute('aria-expanded', String(open));
      button.textContent = open ? 'Close −' : (new URL(link.href).pathname.endsWith('.html') ? 'Load the interactive map +' : 'Read the PDF here +');
    });
  }

  async function installStoryReader() {
    const top = document.getElementById('comic-page-top');
    const bottom = document.getElementById('comic-page-bottom');
    if (!top || !bottom) return;
    const response = await fetch(local('/assets/settlement-reader-data.json'));
    if (!response.ok) throw new Error('Story data unavailable');
    const stories = await response.json();
    const story = stories.find(item => path.endsWith('/stories/' + item.slug));
    if (!story) throw new Error('Unknown story');
    const caption = Array.from(document.querySelectorAll('figcaption[aria-live]')).find(node => node.textContent.includes(story.title));
    const image = caption.parentElement.querySelector('img');
    const details = Array.from(document.querySelectorAll('details')).find(node => /^Read the text from page/.test(node.querySelector('summary')?.textContent || ''));
    const full = Array.from(document.querySelectorAll('a[href]')).find(node => new URL(node.href).pathname.includes('/stories/' + story.slug + '/page-'));
    const controls = [top, bottom].map(select => ({ select, buttons: select.closest('label').parentElement.querySelectorAll('button') }));
    let current = 0;
    function turn(index, changeHash = true) {
      current = Math.max(0, Math.min(story.readerPages.length - 1, index));
      const page = story.readerPages[current];
      image.src = local(page.src);
      image.width = page.width; image.height = page.height;
      image.alt = story.title + ', page ' + (current + 1) + '. The page text is available below the reader.';
      caption.textContent = story.title + ' · Page ' + (current + 1) + ' of ' + story.pages + ' · Includes the original notes and references.';
      controls.forEach(control => {
        control.select.value = String(current);
        control.buttons[0].disabled = current === 0;
        control.buttons[1].disabled = current === story.readerPages.length - 1;
      });
      if (details) {
        details.querySelector('summary').textContent = 'Read the text from page ' + (current + 1);
        details.querySelector('pre').textContent = page.text || 'This page contains illustration without extractable text.';
      }
      if (full) full.href = local(page.src);
      if (changeHash) history.replaceState(null, '', '#page-' + (current + 1));
    }
    controls.forEach(control => {
      control.select.addEventListener('change', () => turn(Number(control.select.value)));
      control.buttons[0].addEventListener('click', () => turn(current - 1));
      control.buttons[1].addEventListener('click', () => turn(current + 1));
    });
    function readHash() {
      const match = location.hash.match(/^#page-(\d+)$/);
      turn(match ? Number(match[1]) - 1 : 0, false);
    }
    window.addEventListener('hashchange', readHash);
    readHash();
  }

  function installRecyclingSlides() {
    const viewer = document.querySelector('.local-recycling-viewer');
    if (!viewer) return;
    const choices = Array.from(viewer.querySelectorAll('.local-recycling-slide-index button'));
    const titles = choices.map(button => button.querySelector('strong').textContent);
    const buttons = viewer.querySelectorAll('.local-recycling-controls button');
    const heading = viewer.querySelector('.local-recycling-viewer-heading .eyebrow');
    const title = document.getElementById('local-recycling-viewer-title');
    const image = viewer.querySelector('.local-recycling-current-slide img');
    const links = viewer.querySelectorAll('.local-recycling-current-slide a');
    let current = 0;
    function turn(index) {
      current = Math.max(0, Math.min(titles.length - 1, index));
      const src = local('/climate-change-technology/local-recycling-and-manufacturing/slides/slide-' + (current + 1) + '.webp');
      heading.textContent = 'The complete introduction · slide ' + (current + 1) + ' of ' + titles.length;
      title.textContent = titles[current]; image.src = src;
      image.alt = 'Slide ' + (current + 1) + ' of ' + titles.length + ': ' + titles[current];
      links.forEach(link => { link.href = src; });
      links[0].setAttribute('aria-label', 'Open slide ' + (current + 1) + ' full size: ' + titles[current]);
      buttons[0].disabled = current === 0; buttons[1].disabled = current === titles.length - 1;
      choices.forEach((button, index) => {
        button.classList.toggle('is-current', index === current);
        if (index === current) button.setAttribute('aria-current', 'true'); else button.removeAttribute('aria-current');
      });
    }
    buttons[0].addEventListener('click', () => turn(current - 1));
    buttons[1].addEventListener('click', () => turn(current + 1));
    choices.forEach((button, index) => button.addEventListener('click', () => turn(index)));
    viewer.addEventListener('keydown', event => {
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') { event.preventDefault(); turn(current + (event.key === 'ArrowLeft' ? -1 : 1)); }
    });
    turn(0);
  }

  async function installMaterialsExplorer() {
    const root = document.querySelector('.local-recycling-explorer');
    if (!root) return;
    const response = await fetch(local('/research/UK_Materials_Inventory_2026-10-09.json'));
    if (!response.ok) throw new Error('Material data unavailable');
    const data = await response.json();
    const query = root.querySelector('input[type="search"]');
    const domain = root.querySelector('select');
    const count = root.querySelector('.local-recycling-result-count');
    const list = root.querySelector('.local-recycling-material-list');
    let more = root.querySelector('.local-recycling-more');
    if (!more) { more = document.createElement('button'); more.type = 'button'; more.className = 'local-recycling-more'; more.textContent = 'Show more materials ↓'; root.append(more); }
    let limit = 18;
    function render() {
      const term = query.value.trim().toLowerCase();
      const found = data.materials.filter(item => (domain.value === 'All' || item.domain === domain.value) && [item.name, item.code, item.family, item.record_level].join(' ').toLowerCase().includes(term));
      list.replaceChildren();
      found.slice(0, limit).forEach(item => {
        const article = document.createElement('article');
        const label = document.createElement('span'); label.textContent = item.id + ' · ' + item.domain + ' · ' + item.record_level;
        const title = document.createElement('h3'); title.textContent = item.name;
        if (item.code) { const code = document.createElement('small'); code.textContent = ' ' + item.code; title.append(code); }
        const detail = document.createElement('p'); detail.textContent = item.family + ' · ' + item.uk_evidence;
        article.append(label, title, detail); list.append(article);
      });
      count.textContent = 'Showing ' + Math.min(limit, found.length) + ' of ' + found.length + ' matching records';
      more.hidden = found.length <= limit;
      if (!found.length) { const empty = document.createElement('p'); empty.textContent = 'No matching records. Try another name or category.'; list.append(empty); }
    }
    query.addEventListener('input', () => { limit = 18; render(); });
    domain.addEventListener('change', () => { limit = 18; render(); });
    more.addEventListener('click', () => { limit += 30; render(); });
    render();
  }

  installDocumentViewer(); installRecyclingSlides();
  installStoryReader().catch(error => console.error(error));
  installMaterialsExplorer().catch(error => console.error(error));
}());
