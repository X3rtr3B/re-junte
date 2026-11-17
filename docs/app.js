/* Sin dependencias, peticiones de confirmación, almacenamiento ni seguimiento. */
'use strict';
(() => {
  const $ = (id) => document.getElementById(id);
  if (!window.REJUNTE) {
    $('notice').hidden = false;
    $('notice').textContent = 'No se pudieron cargar los datos. Recarga la página o vuelve a abrir el enlace.';
    return;
  }
  const { evento: event, invitados: guests } = window.REJUNTE;
  const selector = $('selector');
  const invitation = $('invitation');
  const dialog = $('response-dialog');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const date = new Date(event.fecha + 'T12:00:00');
  const dateLabel = new Intl.DateTimeFormat('es-BO', {day:'numeric', month:'long', year:'numeric'}).format(date);
  let previousFocus = null;
  let confettiTimer;
  document.title = `${event.titulo} ${date.getFullYear()} · ${event.festividad} en ${event.ciudad}`;
  if (event.opciones_visuales?.animaciones === false) document.body.classList.add('no-motion');
  document.querySelectorAll('[data-event]').forEach(el => { el.textContent = event[el.dataset.event]; });
  document.querySelectorAll('.event-date').forEach(el => { el.textContent = dateLabel; });
  document.querySelectorAll('.event-year').forEach(el => { el.textContent = String(date.getFullYear()); });
  $('event-day').textContent = String(date.getDate()).padStart(2, '0');
  $('event-month').textContent = new Intl.DateTimeFormat('es-BO', {month:'long'}).format(date).toUpperCase() + ' · ' + date.getFullYear();
  $('invite-title').firstChild.textContent = event.titulo.toUpperCase();
  const coverParts = event.titulo.split('-');
  if (coverParts.length === 2) {
    const title = document.querySelector('.cover-title');
    title.setAttribute('aria-label', event.titulo);
    title.children[0].firstChild.textContent = coverParts[0].toUpperCase();
    title.children[1].firstChild.textContent = coverParts[1].toUpperCase();
  } else {
    document.querySelector('.cover-title').textContent = event.titulo.toUpperCase();
  }
  $('invitation-copy').textContent = event.texto.convocatoria;
  $('antecedents').textContent = event.texto.antecedentes;
  $('reserve-copy').textContent = event.texto.reserva;
  $('details-copy').textContent = event.texto.detalles;
  $('closing-line').textContent = event.texto.cierre;
  $('legal-copy').textContent = event.texto.aviso;
  function guestButtons(filter = '') {
    const fragment = document.createDocumentFragment();
    const normalized = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('es');
    const visible = guests.filter(g => normalized(g.nombre).includes(normalized(filter)));
    visible.forEach(guest => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'guest-button';
      button.textContent = guest.nombre;
      const arrow = document.createElement('span');
      arrow.textContent = '↗';
      arrow.setAttribute('aria-hidden', 'true');
      button.append(arrow);
      button.addEventListener('click', () => navigate(guest.id));
      fragment.append(button);
    });
    $('guest-list').replaceChildren(fragment);
    $('no-results').hidden = visible.length > 0;
  }
  guestButtons();
  $('search-wrap').hidden = guests.length < 10;
  $('guest-search').addEventListener('input', e => guestButtons(e.target.value));
  function stopVideo() { $('event-video').pause(); }
  function clearCelebration() { clearTimeout(confettiTimer); $('confetti').replaceChildren(); }
  function render(moveFocus = false) {
    stopVideo();
    if (dialog.open) dialog.close();
    clearCelebration();
    const id = new URLSearchParams(location.search).get('i');
    const guest = guests.find(g => g.id === id);
    const invalid = id !== null && !guest;
    $('notice').hidden = !invalid;
    $('notice').textContent = invalid ? 'Ese identificador no está en la lista. Elige tu nombre para continuar.' : '';
    selector.hidden = Boolean(guest);
    invitation.hidden = !guest;
    if (guest) {
      $('guest-name').textContent = guest.nombre;
      $('guest-alias').textContent = [guest.articulo_alias, guest.apodo].filter(Boolean).join(' ');
      $('guest-obligation').textContent = guest.forma_obligacion;
    }
    const view = guest ? invitation : selector;
    view.classList.remove('view-enter');
    void view.offsetWidth;
    view.classList.add('view-enter');
    if (moveFocus) {
      window.scrollTo({top:0, behavior:'instant'});
      (guest ? $('invite-title') : $('selector-heading')).focus({preventScroll:true});
    }
  }
  function navigate(id) {
    const url = new URL(location.href);
    if (id) url.searchParams.set('i', id); else url.searchParams.delete('i');
    history.pushState(null, '', url);
    render(true);
  }
  $('change-guest').addEventListener('click', () => navigate(null));
  document.querySelector('.brand').addEventListener('click', e => { e.preventDefault(); navigate(null); });
  window.addEventListener('popstate', () => render(true));
  function addParagraph(text, strong = false) {
    const p = document.createElement('p');
    if (strong) { const b = document.createElement('strong'); b.textContent = text; p.append(b); }
    else p.textContent = text;
    $('response-body').append(p);
  }
  function celebrate() {
    if (reduced.matches || event.opciones_visuales?.animaciones === false || event.opciones_visuales?.confeti === false) return;
    clearCelebration();
    const fragment = document.createDocumentFragment();
    for (let i = 0; i < 34; i++) {
      const piece = document.createElement('i');
      piece.style.left = `${Math.random() * 100}%`;
      piece.style.background = ['#e94e3a','#f4b942','#1c9c91','#fff3db'][i % 4];
      piece.style.animationDelay = `${Math.random() * .5}s`;
      fragment.append(piece);
    }
    $('confetti').append(fragment);
    confettiTimer = setTimeout(clearCelebration, 2500);
  }
  function response(accepted) {
    previousFocus = document.activeElement;
    stopVideo();
    dialog.classList.toggle('denied', !accepted);
    $('response-title').textContent = accepted ? 'DESTINO ACEPTADO' : 'IMPUGNACIÓN DENEGADA';
    $('response-body').replaceChildren();
    $('dialog-symbol').textContent = accepted ? '✳︎' : '§';
    if (accepted) {
      addParagraph('Su disposición a cumplir con sus obligaciones sociales ha sido debidamente reconocida.');
      addParagraph(`Nos vemos en ${event.ciudad}.`, true);
    } else {
      addParagraph('El comité ha considerado que su recurso carece de fundamentos.');
      addParagraph('Motivo: La última reunión colectiva data de 2023.');
      addParagraph(`Resolución: Preséntese el ${dateLabel}.`);
      addParagraph('Contra esta resolución no procede recurso alguno.', true);
    }
    $('close-dialog').textContent = accepted ? 'VOLVER A LA INVITACIÓN' : 'ENTENDIDO, NI MODO';
    dialog.showModal();
    $('response-title').focus();
    if (accepted) celebrate();
  }
  $('accept').addEventListener('click', () => response(true));
  $('negotiate').addEventListener('click', () => response(false));
  $('close-dialog').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => { clearCelebration(); if (previousFocus && !invitation.hidden) previousFocus.focus({preventScroll:true}); });
  dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
  // <dialog>.showModal gestiona el fondo inerte, Escape y el ciclo de Tab nativamente.
  if (event.video_habilitado) {
    $('video-panel').hidden = false;
    $('event-video').src = event.video_archivo;
    $('video-captions').src = event.video_subtitulos;
    $('event-video').addEventListener('error', () => { $('video-error').hidden = false; });
  }
  $('skip-video').addEventListener('click', () => { stopVideo(); $('antecedents').focus(); $('antecedents').scrollIntoView({block:'center', behavior:reduced.matches ? 'instant':'smooth'}); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopVideo(); });
  render(new URLSearchParams(location.search).has('i'));
})();
