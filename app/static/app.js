/* No frontend framework: render untrusted text with textContent or escaped HTML. */
const $ = (selector) => document.querySelector(selector);
const escapeHTML = (value) => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
let documents = [], config = null, currentAnswer = null, busy = false;
const titles = {search:'Ask your library', library:'Document library', quality:'Quality lab', about:'How it works'};
async function api(path, options = {}) {
  const response = await fetch(path, {...options, headers:{'Content-Type':'application/json', ...options.headers}});
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Please check your input and try again.');
  return data;
}
function showToast(message) { $('#toast').textContent = message; $('#toast').hidden = false; clearTimeout(showToast.timer); showToast.timer = setTimeout(() => $('#toast').hidden = true, 4500); }
function changeView(view) {
  if (!(view in titles)) return;
  document.querySelectorAll('.view').forEach(section => section.hidden = section.id !== `view-${view}`);
  document.querySelectorAll('.nav-item').forEach(button => { const active = button.dataset.view === view; button.classList.toggle('active', active); if(active) button.setAttribute('aria-current','page'); else button.removeAttribute('aria-current'); });
  $('#breadcrumb').textContent = titles[view];
  if (view === 'quality') loadQuality();
  if (view === 'library') renderLibrary();
  window.scrollTo({top:0, behavior:'instant'});
}
document.addEventListener('click', event => {
  const view = event.target.closest('[data-view]');
  if(view) changeView(view.dataset.view);
  const starter = event.target.closest('[data-question]');
  if(starter && !busy) { $('#question').value = starter.dataset.question; $('#category').value = 'All'; ask(); }
  const doc = event.target.closest('[data-document]');
  if(doc) openDocument(doc.dataset.document, doc.dataset.passage);
  const collection = event.target.closest('[data-collection]');
  if(collection) { $('#library-category').value = collection.dataset.collection; changeView('library'); }
});
document.addEventListener('keydown', event => {
  if(event.key === '/' && !['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName) && !$('#document-dialog').open) { event.preventDefault(); changeView('search'); $('#question').focus(); }
});
$('#question').addEventListener('keydown', event => { if(event.key === 'Enter' && !event.shiftKey) {event.preventDefault(); if(!busy) $('#ask-form').requestSubmit();} });
$('#ask-form').addEventListener('submit', event => { event.preventDefault(); ask(); });
async function ask() {
  if(busy) return;
  const question = $('#question').value.trim();
  if(question.length < 3) { $('#error').textContent='Please enter a question with at least three characters.'; $('#error').hidden=false; return; }
  busy=true; currentAnswer=null; $('#ask-button').disabled=true; $('#error').hidden=true;
  const area=$('#answer-area'); area.hidden=false; area.setAttribute('aria-busy','true');
  area.innerHTML='<div class="loading-card"><span class="spinner" aria-hidden="true"></span><div><strong>Following the paper trail…</strong><br><small>Looking for useful evidence in your library.</small></div></div>';
  try {
    currentAnswer=await api('/api/ask',{method:'POST',body:JSON.stringify({question,category:$('#category').value,method:$('#method').value})});
    renderAnswer(currentAnswer, question);
    area.scrollIntoView({block:'start',behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
  } catch(error) { area.hidden=true; $('#error').textContent=error.message; $('#error').hidden=false; }
  finally { busy=false; $('#ask-button').disabled=false; area.setAttribute('aria-busy','false'); }
}
function renderAnswer(answer, question) {
  const sourceNumbers = new Map(answer.sources.map((s,i)=>[s.id,i+1]));
  const title = answer.status === 'insufficient_evidence' ? 'The library doesn’t have enough evidence.' : answer.mode==='demo' ? 'Here’s what the documents say.' : 'An answer, with a paper trail.';
  const claims = answer.claims.map(claim => `<p class="claim">${escapeHTML(claim.text)} ${claim.source_ids.map(id => { const source=answer.sources.find(s=>s.id===id); return source ? `<button class="citation" data-document="${escapeHTML(source.document_id)}" data-passage="${escapeHTML(id)}" aria-label="Read source ${sourceNumbers.get(id)}">${sourceNumbers.get(id)}</button>`:''; }).join('')}</p>`).join('');
  const evidence = answer.sources.map((source,i)=>`<button class="source-button" data-document="${escapeHTML(source.document_id)}" data-passage="${escapeHTML(source.id)}"><strong>${i+1}. ${escapeHTML(source.title)}</strong><small>${escapeHTML(source.section)}${source.page ? ` · Page ${source.page}`:''}</small><p>${escapeHTML(source.text.slice(0,150))}${source.text.length>150?'…':''}</p></button>`).join('');
  $('#answer-area').innerHTML=`<div class="answer-layout"><article class="answer-card"><div class="answer-top"><span class="answer-badge">${answer.mode==='demo'?'SOURCE EXCERPTS':'AI SYNTHESIS'}</span><span class="answer-time">${answer.elapsed_ms<1000?`${answer.elapsed_ms} ms`:`${(answer.elapsed_ms/1000).toFixed(1)} s`}</span></div><h2>${title}</h2>${claims || '<p class="claim ui-empty-claim">Try a more specific question or another collection. Nearby passages, if any, are shown for inspection; they may not answer your question.</p>'}<div class="answer-disclaimer">${escapeHTML(answer.notice)}</div><div class="answer-actions"><span>Useful?</span><button class="action-button" id="feedback-yes" aria-label="This answer was helpful">Yes</button><button class="action-button" id="feedback-no" aria-label="This answer was not helpful">Not quite</button><button class="action-button copy-button" id="copy-answer">Copy ${answer.mode==='demo'?'excerpts':'answer'} ↗</button></div></article><aside class="evidence-panel"><h3>THE PAPER TRAIL <span> / ${answer.sources.length}</span></h3>${evidence || '<p class="evidence-note">No matching passages found.</p>'}<p class="evidence-note">Open a source to read it in context. Search ranking is not a confidence score.</p></aside></div>`;
  $('#feedback-yes').onclick=()=>feedback(true); $('#feedback-no').onclick=()=>feedback(false);
  $('#copy-answer').onclick=async()=>{ const text=[question,'',...answer.claims.map(c=>c.text+' '+c.source_ids.map(id=>'['+sourceNumbers.get(id)+']').join(' ')),'',...answer.sources.map((s,i)=>`[${i+1}] ${s.title} — ${s.section}`),'',answer.notice].join('\n'); try {await navigator.clipboard.writeText(text);showToast('Copied with source references.');} catch {showToast('Copy is unavailable in this browser. You can select the text instead.');} };
}
async function feedback(helpful) { if(!currentAnswer) return; try {await api('/api/feedback',{method:'POST',body:JSON.stringify({answer_id:currentAnswer.answer_id,helpful})});$('#feedback-yes').classList.toggle('selected',helpful);$('#feedback-no').classList.toggle('selected',!helpful);showToast('Thank you. Feedback is kept for this server session only.');}catch(error){showToast(error.message);} }
function renderLibrary() {
  const term=$('#library-search').value.toLowerCase(), category=$('#library-category').value;
  const matches=documents.filter(d=>(category==='All'||d.category===category)&&(d.title+' '+d.description).toLowerCase().includes(term));
  $('#library-grid').innerHTML=matches.map(d=>`<button class="doc-card" data-document="${escapeHTML(d.id)}"><span class="card-icon sage">▤</span><span class="doc-tag">${escapeHTML(d.category.toUpperCase())}</span><h2>${escapeHTML(d.title)}</h2><p>${escapeHTML(d.description.slice(0,100))}${d.description.length>100?'…':''}</p><span class="doc-meta">${d.format} · ${d.chunks} passages <b>↗</b></span></button>`).join('') || '<p class="empty">No documents match this filter. Try a different title or collection.</p>';
}
$('#library-search').addEventListener('input',renderLibrary);$('#library-category').addEventListener('change',renderLibrary);
async function openDocument(id, passageId) {
  const dialog=$('#document-dialog');
  $('#document-content').innerHTML='<p>Opening the source…</p>'; if(!dialog.open) dialog.showModal();
  try {
    const doc=await api('/api/documents/'+encodeURIComponent(id));
    $('#document-content').innerHTML=`<p class="document-category">${escapeHTML(doc.category.toUpperCase())} · FICTIONAL DEMO DOCUMENT</p><h2 class="document-title">${escapeHTML(doc.title)}</h2><a class="button-secondary" href="/api/documents/${encodeURIComponent(doc.id)}/original">Download original ${doc.format} ↓</a>${doc.passages.map(p=>`<section class="passage ${p.id===passageId?'highlight':''}" id="passage-${escapeHTML(p.id)}"><h3>${escapeHTML(p.section)}${p.page?` · Page ${p.page}`:''}</h3><p>${escapeHTML(p.text)}</p></section>`).join('')}`;
    if(passageId) document.getElementById('passage-'+passageId)?.scrollIntoView({block:'center'});
    else dialog.scrollTop=0;
  } catch(error) {$('#document-content').textContent=error.message;}
}
$('#close-dialog').onclick=()=>$('#document-dialog').close();
$('#document-dialog').addEventListener('click',event=>{if(event.target===$('#document-dialog')) {const rect=event.target.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom) event.target.close();}});
async function loadQuality() {
  try {
    const results=await api('/api/evaluation');
    if(results.status==='not_run'){ $('#quality-content').innerHTML='<div class="quality-note"><h2>Evaluation hasn’t run yet.</h2><p>The project includes a reproducible benchmark. See the evaluation guide to run it and publish actual results.</p></div>';return; }
    const pct=n=>(100*n).toFixed(1)+'%';
    $('#quality-content').innerHTML=`<div class="quality-stats"><div class="stat"><strong>${results.total_questions}</strong><small>Questions in this run</small></div><div class="stat"><strong>${pct(results.metrics.hit_at_5)}</strong><small>Supporting passage found in top 5</small></div><div class="stat"><strong>${results.method.toUpperCase()}</strong><small>Retrieval method measured</small></div></div><div class="quality-note"><h2>A benchmark, not a blanket promise.</h2><p>${escapeHTML(results.disclosure)}</p><p>Run: ${escapeHTML(results.generated_at)} · Split: ${escapeHTML(results.split)} · Answerable: ${results.answerable_questions} · Unanswerable: ${results.unanswerable_questions}</p><p>These results measure retrieval only. They do not establish AI answer accuracy, citation support, or safe refusal. Those require the separate human review worksheet.</p><a href="/guide/evaluation.html" target="_blank" rel="noopener">Read the evaluation method ↗</a></div><div class="table-scroll"><table class="quality-table"><thead><tr><th>Question</th><th>Expected</th><th>Top-5 evidence</th></tr></thead><tbody>${results.cases.map(c=>`<tr><td>${escapeHTML(c.question)}</td><td>${c.expected_ids.length?'Answerable':'Not in library'}</td><td>${c.expected_ids.length?(c.hit?'Found':'Missed'):'Not scored'}</td></tr>`).join('')}</tbody></table></div>`;
  } catch(error){$('#quality-content').textContent=error.message;}
}
async function init() {
  try {
    [config,documents]=await Promise.all([api('/api/config'),api('/api/documents')]);
    $('#nav-count').textContent=documents.length; $('#sidebar-status').textContent=`${documents.length} documents connected`;
    $('#mode-pill').textContent=config.mode==='demo'?'PUBLIC DEMO':'LIVE AI DEMO';
    $('#mode-note').innerHTML=config.mode==='demo'?'<span>◌</span> Demo mode · Real keyword search. Exact source excerpts. No AI key needed.':'<span>◌</span> Live mode · AI answers from a fictional library. Always check the sources.';
    for(const id of ['category','library-category']) for(const cat of config.categories) {const option=document.createElement('option');option.value=cat;option.textContent=cat;$('#'+id).append(option);}
    const names={bm25:'Keyword',semantic:'Semantic',hybrid:'Hybrid'};
    $('#method').innerHTML=config.methods.map(m=>`<option value="${m}">${names[m]}</option>`).join('');
    $('#collection-list').innerHTML=config.categories.map(cat=>`<button class="collection-chip" data-collection="${escapeHTML(cat)}"><span class="chip-symbol">▤</span><span><strong>${escapeHTML(cat)}</strong><small>${documents.filter(d=>d.category===cat).length} documents</small></span></button>`).join('');
  }catch(error){$('#error').textContent='The library could not load. Refresh to try again. '+error.message;$('#error').hidden=false;$('#sidebar-status').textContent='Library unavailable';$('#mode-note').textContent='Connection unavailable';}
}
init();
