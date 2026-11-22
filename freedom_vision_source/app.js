/* Freedom Vision v0.6 — a low-demand public-archive gateway.
 * No trackers, no analytics, no preloading, no autoplay, no video proxy.
 * Browsers contact only the provider APIs the visitor explicitly searches.
 */
(() => {
  'use strict';
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => Array.from(document.querySelectorAll(selector));
  const providers = [
    {id:'ia', name:'Internet Archive', monogram:'IA', media:'Video · Audio · Books', desc:'Classic cinema, vintage animation, historical recordings and digital books.',url:'https://archive.org/',kind:'search',donate:'https://archive.org/donate',tag:'audiobook'},
    {id:'commons',name:'Wikimedia Commons',monogram:'WC',media:'Video · Audio',desc:'Free-licensed cultural, historical and educational recordings.',url:'https://commons.wikimedia.org/',kind:'search'},
    {id:'gutenberg',name:'Project Gutenberg',monogram:'PG',media:'Books',desc:'Free ebooks; catalogue discovery uses the independent Gutendex API.',url:'https://www.gutenberg.org/',kind:'search'},
    {id:'librivox',name:'LibriVox',monogram:'LV',media:'Audiobooks',desc:'Public-domain audiobooks read by volunteers. Requests are carefully paced.',url:'https://librivox.org/',kind:'search',tag:'audiobook'},
    {id:'lit2go',name:'Lit2Go · Free Audiobooks',monogram:'L2',media:'Stories · Poetry · Audio MP3',desc:'University of South Florida narrated classics, stories, poetry and read-along PDFs. Limited noncommercial reuse only; external link.',url:'https://etc.usf.edu/lit2go/',kind:'external',donate:'https://etc.usf.edu/lit2go/giving/',tag:'audiobook'},
    {id:'storybookscanada',name:'Storybooks Canada',monogram:'SC',media:'Multilingual · Illustrated Audio Stories',desc:'Free illustrated stories with multilingual text and some MP3 narration. Audio varies by language and has track-specific CC licences.',url:'https://storybookscanada.ca/',kind:'external',tag:'audiobook,culture'},
    {id:'globalstorybooks',name:'Global Storybooks',monogram:'GS',media:'Languages · Children’s Audio Stories',desc:'Free illustrated stories and narration in many languages. Reuse requires checking CC BY and CC BY-NC file permissions.',url:'https://globalstorybooks.net/',kind:'external',tag:'audiobook,culture'},
    {id:'peertube',name:'PeerTube',monogram:'PT',media:'Video',desc:'Independent video instances. Embeds require individual server checks.',url:'https://joinpeertube.org/',kind:'external'},
    {id:'blender',name:'Blender Open Movies',monogram:'BF',media:'Animation',desc:'Openly licensed animated films; credited copies need suitable low-res sources.',url:'https://studio.blender.org/films/',kind:'external'},
    {id:'loc',name:'Library of Congress',monogram:'LC',media:'Film · Audio',desc:'National Screening Room and historical moving-image collections.',url:'https://www.loc.gov/collections/national-screening-room/',kind:'external'},
    {id:'bfi',name:'BFI Replay',monogram:'BFI',media:'British TV · Film',desc:'Free historic British films and television; embedded rights not cleared.',url:'https://replay.bfi.org.uk/',kind:'external'},
    {id:'nfb',name:'NFB Canada',monogram:'NFB',media:'Animation · Film',desc:'Freely viewable Canadian films. Third-party embeds require terms review.',url:'https://www.nfb.ca/',kind:'external'},
    {id:'audius',name:'Audius',monogram:'AU',media:'Music',desc:'Independent music catalogue; integration needs API and advert checks.',url:'https://audius.co/',kind:'external'},
    {id:'funkwhale',name:'Funkwhale',monogram:'FW',media:'Music',desc:'Decentralised music collections with instance-specific access rules.',url:'https://www.funkwhale.audio/',kind:'external'},
    {id:'jamendo',name:'Jamendo',monogram:'JA',media:'Music',desc:'Independent Creative Commons recordings; player and API terms to check.',url:'https://www.jamendo.com/',kind:'external'},
    {id:'ccmixter',name:'ccMixter',monogram:'CC',media:'Music',desc:'Openly licensed music and remixes, subject to track-by-track rights.',url:'https://ccmixter.org/',kind:'external'},
    {id:'dogmazic',name:'Dogmazic',monogram:'DZ',media:'Music',desc:'Free-licence music archive with its own catalogue.',url:'https://dogmazic.net/',kind:'external'},
    {id:'openlibrary',name:'Open Library',monogram:'OL',media:'Books',desc:'Book discovery and permitted reading; some titles have borrowing restrictions.',url:'https://openlibrary.org/',kind:'external'},
    {id:'oapen',name:'OAPEN',monogram:'OA',media:'Academic Books',desc:'Open-access scholarly book discovery.',url:'https://www.oapen.org/',kind:'external'},
    {id:'doab',name:'DOAB',monogram:'DB',media:'Academic Books',desc:'Directory of Open Access Books; reading depends on publishers.',url:'https://www.doabooks.org/',kind:'external'},
    {id:'europeana',name:'Europeana',monogram:'EU',media:'Culture · Books',desc:'European cultural collections, with varied provider licences.',url:'https://www.europeana.eu/',kind:'external'},
    {id:'nasa',name:'NASA Media Library',monogram:'NA',media:'Science · Film',desc:'Space imagery and film, with resource-specific usage rules.',url:'https://images.nasa.gov/',kind:'external'},
    {id:'fiaf',name:'FIAF Film Archives Online',monogram:'FI',media:'World Cinema',desc:'Global catalogue of free archive films; English subtitles are available for some works. External links only.',url:'https://www.fiafnet.org/filmsonline',kind:'external',tag:'worldfilm'},
    {id:'jff',name:'JFF Theater',monogram:'JF',media:'Japan · World Cinema',desc:'Free Japanese movies and dramas with subtitles; separate free account and regional restrictions. External viewing only.',url:'https://en.jff.jpf.go.jp/',kind:'external',tag:'worldfilm'},
    {id:'nfaj',name:'Japanese Animated Film Classics',monogram:'NF',media:'Japan · Animation',desc:'64 early Japanese animated films, some English-subtitled. Embedding expressly prohibited; link to official site.',url:'https://animation.filmarchives.jp/en/index.html',kind:'external',tag:'worldfilm'},
    {id:'kofa',name:'Korean Film Archive KMDb',monogram:'KO',media:'Korea · Cinema',desc:'Official Korean classic-film catalogue and on-site VOD. Check subtitles and rights per item.',url:'https://www.kmdb.or.kr/vod',kind:'external',tag:'worldfilm'},
    {id:'cfc',name:'Chinese Film Classics',monogram:'CF',media:'China · Film History',desc:'Academic film-history research and English subtitle information. Video delivery depends on YouTube and is not embedded.',url:'https://chinesefilmclassics.org/',kind:'external',tag:'worldfilm'},
    {id:'hkfa',name:'Hong Kong Film Archive',monogram:'HK',media:'Hong Kong · Film Culture',desc:'Archive information and licensed screenings, not a verified free film stream.',url:'https://www.filmarchive.gov.hk/',kind:'external',tag:'worldfilm'},
    {id:'languageguide',name:'LanguageGuide.org',monogram:'LG',media:'Language Learning',desc:'Free nonprofit interactive vocabulary, listening and pronunciation lessons. External course link.',url:'https://www.languageguide.org/',kind:'external',tag:'culture'},
    {id:'openlearn',name:'OpenLearn',monogram:'OU',media:'Language Learning',desc:'Free Open University courses in languages and culture. Embedded course reuse not established.',url:'https://www.open.edu/openlearn/languages/free-courses',kind:'external',tag:'culture'},
    {id:'tv5',name:'TV5MONDE Apprendre',monogram:'TV',media:'French · Language Video',desc:'Free and advertising-free French video lessons and exercises. Link to official teaching platform.',url:'https://apprendre.tv5monde.com/en',kind:'external',tag:'culture'},
    {id:'nhkjp',name:'NHK Easy Japanese',monogram:'NH',media:'Japanese · Language Audio',desc:'Free Japanese language lessons with listening exercises and cultural context.',url:'https://www.nhk.or.jp/lesson/en/',kind:'external',tag:'culture,audio'},
    {id:'librelingo',name:'LibreLingo',monogram:'LL',media:'Open Source · Language Learning',desc:'AGPLv3 language app; course content needs separate licence checks.',url:'https://github.com/LibreLingoCommunity/LibreLingo',kind:'external',tag:'culture'},
    {id:'tatoeba',name:'Tatoeba',monogram:'TT',media:'Language Text · Translation',desc:'Open multilingual sentence and translation datasets; attribution and audio permissions vary.',url:'https://tatoeba.org/en/',kind:'external',tag:'culture'},
    {id:'lingualibre',name:'Lingua Libre',monogram:'LI',media:'Speech · Language Heritage',desc:'Wikimedia France project preserving recorded pronunciation and endangered-language speech.',url:'https://lingualibre.org/',kind:'external',tag:'culture'},
    {"id":"languagetransfer","name":"Language Transfer · Audio Courses","monogram":"LT","media":"Language · Audio MP3","desc":"Free downloadable language audio courses. Original site only; no SoundCloud or YouTube embeds.","url":"https://www.languagetransfer.org/courses","kind":"external","tag":"culture,audio"},
    {"id":"mitquantum","name":"MIT OpenCourseWare · Quantum Physics I","monogram":"MIT","media":"Quantum · Video Lectures","desc":"Free quantum mechanics lectures, downloadable video and written course materials. Original course link only pending permissions and bitrate checks.","url":"https://ocw.mit.edu/courses/8-04-quantum-physics-i-spring-2016/","kind":"external","tag":"science"},
    {"id":"yalephys1","name":"Open Yale · Fundamentals of Physics I","monogram":"Y1","media":"Physics · MP3 · Video","desc":"Mechanics, relativity and waves. Official MP3 lectures, low-bandwidth video and transcripts.","url":"https://oyc.yale.edu/physics/phys-200","kind":"external","tag":"science,audio"},
    {"id":"yalephys2","name":"Open Yale · Fundamentals of Physics II","monogram":"Y2","media":"Quantum · MP3 · Video","desc":"Electricity, optics and quantum mechanics, with official audio MP3, low-bandwidth video and transcripts.","url":"https://oyc.yale.edu/physics/phys-201","kind":"external","tag":"science,audio"},
    {"id":"yalechem","name":"Open Yale · Organic Chemistry","monogram":"YC","media":"Chemistry · MP3 · Video","desc":"University-level chemistry lectures with audio-only options and course resources.","url":"https://oyc.yale.edu/chemistry/chem-125a","kind":"external","tag":"science,audio"},
    {"id":"yalebio","name":"Open Yale · Evolution and Biology","monogram":"YB","media":"Biology · MP3 · Video","desc":"Evolution, ecology and behaviour lectures with audio and course resources.","url":"https://oyc.yale.edu/ecology-and-evolutionary-biology/eeb-122","kind":"external","tag":"science,audio"},
    {"id":"cernedu","name":"CERN · Educational Physics Videos","monogram":"CE","media":"Particle Physics · Video","desc":"Official physics videos and animations about particles, accelerators and wave-particle phenomena. Source playback only.","url":"https://educational-resources.web.cern.ch/videos-and-animations/","kind":"external","tag":"science"},
    {"id":"pirsa","name":"PIRSA · Theoretical Physics Archive","monogram":"PI","media":"Quantum Theory · Seminars","desc":"Perimeter Institute free searchable research seminars. Embed rights and low-bitrate versions not verified.","url":"https://pirsa.org/","kind":"external","tag":"science"},
    {"id":"phet","name":"PhET · Interactive Science","monogram":"PH","media":"Physics · Chemistry · Maths","desc":"Free interactive science simulations with official embed codes, subject to attribution and non-commercial licence conditions.","url":"https://phet.colorado.edu/","kind":"external","tag":"science"},
    {"id":"geogebra","name":"GeoGebra · Geometry and Maths","monogram":"GG","media":"Geometry · Maths","desc":"Free interactive geometry and maths materials. Non-commercial licence and attribution apply.","url":"https://www.geogebra.org/math/geometry?lang=en","kind":"external","tag":"science"},
    {"id":"openstax","name":"OpenStax · Science Textbooks","monogram":"OS","media":"Physics · Chemistry · Biology · Maths","desc":"Free online textbooks and PDFs; reuse licences must be checked per edition.","url":"https://openstax.org/higher-education","kind":"external","tag":"science"},
    {"id":"openlearnscience","name":"OpenLearn · Science and Maths","monogram":"OU","media":"Physics · Chemistry · Biology · Audio","desc":"Free Open University science and mathematics courses, videos and audio resources.","url":"https://www.open.edu/openlearn/science-maths-technology/free-courses","kind":"external","tag":"science,audio"},
    {"id":"nasapodcast","name":"NASA · Podcasts and Audio","monogram":"NA","media":"Space · Science Audio","desc":"NASA official free podcasts, science stories and sonifications. Opens original source, with no third-party player.","url":"https://www.nasa.gov/podcasts-and-audio/","kind":"external","tag":"science,audio"}
  ];
  // This directory is *not* a list of authorised embeddable players.
  // External services are discovery links only, not part of unified playback.
  const collectionSettings = {
    film: {mode:'watch', query:'',archiveCollection:'feature_films',label:'Classic cinema'},
    cartoons: {mode:'watch',query:'',archiveCollection:'animationandcartoons',label:'Vintage cartoons'},
    tv: {mode:'watch',query:'',archiveCollection:'classic_tv',label:'Classic series'},
    music:{mode:'listen',query:'music',label:'Music & sound'},
    books:{mode:'read',query:'fiction',label:'Books & stories'},
    news:{mode:'news',query:'',label:'World news'}
  };
  const state={mode:'all',sourceFilter:'all',activeItem:null,searching:false,currentController:null};
  const cache=new Map();
  const lastRequest=new Map();
  const cooldownUntil=new Map();
  const TTL=7*60*1000;
  const WAIT={ia:6500,commons:6000,gutenberg:5000,librivox:10000};
  const MIN_GAP={ia:3000,commons:3000,gutenberg:4000,librivox:9000};
  const archiveSearchLink='https://archive.org/';
  const typeIcon={video:'▰',audio:'◉',book:'▤',other:'◇'};

  function textNode(tag,txt,cls){const e=document.createElement(tag);if(cls)e.className=cls;e.textContent=String(txt??'');return e}
  function externalLink(url,text,cls){const a=textNode('a',text,cls);a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.referrerPolicy='no-referrer';return a}
  function clean(value, max=420){
    const str=Array.isArray(value)?value.join(' '):String(value??'');
    const parsed=new DOMParser().parseFromString(str,'text/html');
    return (parsed.body.textContent||'').replace(/\s+/g,' ').trim().slice(0,max);
  }
  function providerById(id){return providers.find(x=>x.id===id)||providers[0]}
  function setMode(mode){
    state.mode=mode;
    $$('.nav-link').forEach(b=>{const current=b.dataset.mode===mode;b.classList.toggle('active',current);if(current)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current')});
    $('#search-input').placeholder=({all:'Search classic films, music, books...',watch:'Search films, cartoons, documentaries...',listen:'Search music, recordings, audiobooks...',read:'Search books, authors, documents...',news:'Explore international news sources...',worldcinema:'Find world film sources...',culture:'Find language learning sources...',science:'Find science course sources...',audiolessons:'Find free audio lesson sources...',audiobooks:'Search audiobook titles and narrated stories...'})[mode];
    if(mode==='news')showNews();
    if(['culture','worldcinema','science','audiolessons','audiobooks'].includes(mode))showDirectory(mode);
  }
  function showDirectory(mode,term=''){
    const settings={
      culture:{tag:'culture',title:'Culture & languages · Free learning',notice:'Official free language-learning resources. Lesson audio is not copied, streamed or embedded without permission.'},
      worldcinema:{tag:'worldfilm',title:'World cinema · International collections',notice:'Official film-archive resources. Subtitles, availability, advertising and embed rights vary; no video loaded automatically.'},
      science:{tag:'science',title:'Science & mathematics · Free courses',notice:'University lectures, physics seminars, simulations and science books. Open original provider sites until low-bandwidth reuse rights are verified.'},
      audiolessons:{tag:'audio',title:'Free audio lessons · Listen and learn',notice:'Language audio courses, university MP3 lectures and official science podcasts. These are source links, not centrally hosted audio.'},
      audiobooks:{tag:'audiobook',title:'Free audiobooks & stories',notice:'Find public-domain audiobooks and multilingual storytelling resources. To search for a story title, type it above and select Search; results come from LibriVox and Internet Archive. Other sources open at their official sites.'}
    };
    const cfg=settings[mode];if(!cfg)return;
    const needle=String(term||'').trim().toLocaleLowerCase();
    const matches=providers.filter(p=>String(p.tag||'').split(',').includes(cfg.tag)).filter(p=>!needle||[p.name,p.desc,p.media].join(' ').toLocaleLowerCase().includes(needle));
    const section=$('#results-section');section.hidden=false;
    $('#results-title').textContent=cfg.title;
    $('#search-status').textContent=cfg.notice+(needle?' Filtered the local source directory for “'+term+'”, with no provider API calls.':'')+' '+matches.length+' source'+(matches.length===1?'':'s')+' listed.';
    const grid=$('#results-grid');grid.replaceChildren();
    matches.forEach(p=>{const card=createResult({id:p.id,kind:'other',provider:p.id,url:p.url,title:p.name,desc:p.desc});card.querySelector('.result-actions button')?.remove();grid.append(card)});
    $('#search-errors').replaceChildren();section.scrollIntoView({behavior:'smooth',block:'start'});
  }
  function showNews(){
    const s=$('#results-section');s.hidden=false;
    $('#results-title').textContent='World news · Official sources';
    $('#search-status').textContent='These are external broadcaster websites, not embedded Freedom Vision streams. Their sites may contain adverts or regional restrictions. No live video is loaded here until permissions and the 480p rule can be verified.';
    const grid=$('#results-grid');grid.replaceChildren();
    [
      {title:'NHK WORLD-JAPAN',desc:'International news and cultural programming from Japan. Opens the broadcaster’s official website; live video is not embedded here.',kind:'other',provider:'nhk',url:'https://www3.nhk.or.jp/nhkworld/en/live/',id:'nhk'},
      {title:'Deutsche Welle',desc:'Germany-based international reporting and current affairs. External official broadcaster link only.',kind:'other',provider:'dw',url:'https://www.dw.com/en/live-tv/channel-english',id:'dw'},
      {title:'France 24',desc:'International news in multiple languages. External official broadcaster link only.',kind:'other',provider:'f24',url:'https://www.france24.com/en/live',id:'f24'}
    ].forEach(result=>{const card=createResult(result);card.querySelector('.result-actions button')?.remove();grid.append(card)});
    $('#search-errors').replaceChildren();s.scrollIntoView({behavior:'smooth',block:'start'});
  }

  function renderProviders(){
    const grid=$('#provider-grid');grid.replaceChildren();
    const visible=providers.filter(p=>state.sourceFilter==='all'||p.kind===state.sourceFilter);
    visible.forEach(p=>{
      const card=document.createElement('article');card.className='provider-card';
      const top=document.createElement('div');top.className='provider-top';top.append(textNode('div',p.monogram,'provider-monogram'));
      const heading=document.createElement('div');heading.append(textNode('h3',p.name),textNode('div',p.media,'provider-types'));top.append(heading);card.append(top);
      card.append(textNode('p',p.desc,'provider-desc'));
      const foot=document.createElement('div');foot.className='provider-bottom';
      foot.append(textNode('span',p.kind==='search'?'Search API':'Source link','provider-status '+(p.kind==='external'?'external':'')),externalLink(p.url,'Visit ↗'));
      card.append(foot);grid.append(card);
    });
  }
  function showError(container,name,message,link){const box=textNode('div',name+': '+message,'search-error');if(link)box.append(externalLink(link,'Open archive ↗'));container.append(box)}
  async function getJSON(id,url){
    const key=id+':'+url,now=Date.now(),existing=cache.get(key);
    if(existing&&now-existing.time<TTL)return existing.data;
    const waitUntil=cooldownUntil.get(id)||0;
    if(waitUntil>now)throw new Error('Requests are paused to protect this source. Please use its official website or try again later.');
    const gap=MIN_GAP[id]||4000;
    const remaining=(lastRequest.get(id)||0)+gap-now;
    if(remaining>0)await new Promise(resolve=>setTimeout(resolve,remaining));
    if((cooldownUntil.get(id)||0)>Date.now())throw new Error('The archive has requested slower traffic. No more requests will be sent now.');
    lastRequest.set(id,Date.now());
    const ctrl=new AbortController();const timeout=setTimeout(()=>ctrl.abort(),WAIT[id]||7000);
    try{
      const response=await fetch(url,{signal:ctrl.signal,mode:'cors',credentials:'omit',referrerPolicy:'no-referrer',headers:{Accept:'application/json'}});
      if(response.status===429||response.status===503){
        const retry=Number(response.headers.get('Retry-After'));
        cooldownUntil.set(id,Date.now()+(Number.isFinite(retry)&&retry>0?Math.min(retry*1000,600000):120000));
        throw new Error('The source is limiting requests or temporarily unavailable. Freedom Vision has stopped asking it for more data.');
      }
      if(!response.ok)throw new Error('The source returned HTTP '+response.status+'. Further automatic requests have been stopped.');
      const data=await response.json();cache.set(key,{data,time:Date.now()});return data;
    }catch(error){if(error.name==='AbortError')throw new Error('The source did not respond within our safety timeout. No automatic retries were made.');if(error instanceof TypeError)throw new Error('The request was blocked or the archive is unreachable. This may be a browser connection restriction; the exact cause is unknown.');throw error}
    finally{clearTimeout(timeout)}
  }
  function safeTerm(str){return String(str||'').replace(/["\\()[\]{}*:^~|]/g,' ').replace(/\s+/g,' ').trim().slice(0,80)}
  function resultForIA(d){return {id:d.identifier,provider:'ia',kind:d.mediatype==='audio'?'audio':d.mediatype==='texts'?'book':'video',title:clean(d.title||d.identifier,150),desc:clean(d.description||'Open the original item to learn more.',330),url:'https://archive.org/details/'+encodeURIComponent(d.identifier)}}
  async function searchIA(term,mode,collection){
    const q=safeTerm(term),mediatype=mode==='listen'?'audio':mode==='read'?'texts':mode==='watch'?'movies':null;
    const clauses=[];
    if(q)clauses.push('(title:"'+q+'" OR description:"'+q+'")');
    if(mediatype)clauses.push('mediatype:'+mediatype);
    if(collection)clauses.push('collection:'+collection);
    if(!clauses.length)clauses.push('(mediatype:movies OR mediatype:audio OR mediatype:texts)');
    const params=new URLSearchParams({q:clauses.join(' AND '),rows:'9',page:'1',output:'json'});
    ['identifier','title','description','mediatype'].forEach(f=>params.append('fl[]',f));
    const data=await getJSON('ia','https://archive.org/advancedsearch.php?'+params.toString());
    return (data?.response?.docs||[]).filter(d=>d.identifier).map(resultForIA);
  }
  async function searchCommons(term){
    if(!safeTerm(term))return [];
    const params=new URLSearchParams({action:'query',format:'json',origin:'*',generator:'search',gsrsearch:safeTerm(term)+' filetype:video',gsrnamespace:'6',gsrlimit:'6',prop:'info|imageinfo',inprop:'url',iiprop:'extmetadata',iilimit:'1'});
    const data=await getJSON('commons','https://commons.wikimedia.org/w/api.php?'+params.toString());
    return Object.values(data?.query?.pages||{}).filter(x=>x.fullurl).map(p=>({id:p.pageid,provider:'commons',kind:'video',title:clean(p.title.replace(/^File:/,''),160),desc:clean(p.imageinfo?.[0]?.extmetadata?.ImageDescription?.value||'Wikimedia Commons recording. View the original page for the licence and attribution.',300),url:p.fullurl}));
  }
  async function searchGutenberg(term){
    if(!safeTerm(term))return [];
    const data=await getJSON('gutenberg','https://gutendex.com/books/?search='+encodeURIComponent(safeTerm(term)));
    return (data?.results||[]).slice(0,6).map(b=>({id:b.id,provider:'gutenberg',kind:'book',title:clean(b.title,160),desc:'Free ebook catalogue entry'+(b.authors?.length?' by '+clean(b.authors.map(x=>x.name).join('; '),130):'')+'. Open the official book page for the available formats and rights information.',url:'https://www.gutenberg.org/ebooks/'+encodeURIComponent(b.id)}));
  }
  async function searchLibriVox(term){
    if(!safeTerm(term))return [];
    const params=new URLSearchParams({title:safeTerm(term),format:'json',limit:'6'});
    const data=await getJSON('librivox','https://librivox.org/api/feed/audiobooks/?'+params.toString());
    return (data?.books||[]).slice(0,6).map(b=>({id:b.id,provider:'librivox',kind:'audio',title:clean(b.title,160),desc:clean(b.description||'Volunteer-read public-domain audiobook.',330),url:String(b.url_librivox||'https://librivox.org/')}));
  }
  async function performSearch({term,mode,collection}={}){
    if(state.searching)return;
    mode=mode||state.mode;term=safeTerm(term===undefined?$('#search-input').value:term);
    if(mode==='news'){showNews();return}
    if(['culture','worldcinema','science','audiolessons'].includes(mode)){showDirectory(mode,term);return}
    if(mode==='audiobooks')mode='listen';
    if(!term&&!collection){$('#search-input').focus();return}
    state.searching=true;$('#search-button').disabled=true;$('#search-button').textContent='Searching…';
    const section=$('#results-section');section.hidden=false;
    $('#results-title').textContent=collection?collectionSettings[Object.keys(collectionSettings).find(k=>collectionSettings[k].archiveCollection===collection)]?.label||'Archive collection':'Found in the archives';
    $('#search-status').textContent='Requesting a small set of metadata results. No videos or audio are being loaded.';
    $('#results-grid').replaceChildren();$('#search-errors').replaceChildren();
    section.scrollIntoView({behavior:'smooth',block:'start'});
    const tasks=[{id:'ia',name:'Internet Archive',run:()=>searchIA(term,mode,collection)}];
    if(!collection&&mode==='watch'&&term)tasks.push({id:'commons',name:'Wikimedia Commons',run:()=>searchCommons(term)});
    if(!collection&&(mode==='read'||mode==='all')&&term)tasks.push({id:'gutenberg',name:'Project Gutenberg',run:()=>searchGutenberg(term)});
    if(!collection&&mode==='listen'&&term)tasks.push({id:'librivox',name:'LibriVox',run:()=>searchLibriVox(term)});
    const answers=await Promise.allSettled(tasks.map(x=>x.run()));
    const all=[];let broken=0;
    answers.forEach((r,i)=>{if(r.status==='fulfilled')all.push(...r.value);else{broken++;showError($('#search-errors'),tasks[i].name,String(r.reason?.message||'Unavailable'),providerById(tasks[i].id).url)}});
    const uniques=new Map();all.forEach(r=>uniques.set(r.provider+':'+r.id,r));
    const results=Array.from(uniques.values()).slice(0,18);
    results.forEach(r=>$('#results-grid').append(createResult(r)));
    $('#search-status').textContent=results.length?results.length+' item'+(results.length===1?'':'s')+' found in '+(tasks.length-broken)+' responding source'+(tasks.length-broken===1?'':'s')+'. Select an item to inspect its source and permitted playback.':'No results received. Try different terms or visit the original collections directly.';
    state.searching=false;$('#search-button').disabled=false;$('#search-button').replaceChildren(document.createTextNode('Search '),textNode('span','↗'));
  }
  function createResult(item){
    const el=document.createElement('article');el.className='result-card';
    el.append(textNode('div',typeIcon[item.kind]+'   '+({video:'WATCH',audio:'LISTEN',book:'READ',other:'SOURCE'})[item.kind],'result-kind'));
    el.append(textNode('h3',item.title),textNode('p',item.desc));
    const actions=document.createElement('div');actions.className='result-actions';
    const details=textNode('button','View details ↗');details.type='button';details.addEventListener('click',()=>openViewer(item));actions.append(details,externalLink(item.url,'Original source ↗'));el.append(actions);
    return el;
  }
  function showMessage(msg){const e=$('#viewer-message');e.hidden=false;e.textContent=msg}
  function openViewer(item){
    const provider=providerById(item.provider);state.activeItem=item;
    $('#viewer-title').textContent=item.title;$('#viewer-desc').textContent=item.desc;
    $('#viewer-provider').textContent='Original provider: '+provider.name;
    $('#viewer-source').href=item.url;
    const donate=$('#viewer-donate');
    if(provider.donate){donate.hidden=false;donate.href=provider.donate;donate.textContent='Donate directly to '+provider.name+' ↗';}else donate.hidden=true;
    $('#viewer-licence').textContent='Rights are item-specific. Public archive access alone does not establish public-domain status. Reproductions, restorations and soundtracks may have additional restrictions.';
    const check=$('#viewer-check');check.disabled=item.provider!=='ia';check.hidden=item.provider!=='ia';
    check.textContent='Check available playback';$('#player-shell').replaceChildren();$('#player-shell').hidden=true;
    if(item.provider==='ia')showMessage('No media loaded. Select “Check available playback” to request only this item’s metadata and inspect its existing file options.');
    else showMessage('A safe in-page player has not yet been verified for this source. Use “View original archive” to access the collection directly.');
    $('#viewer-dialog').showModal();
  }
  function durationSecs(v){const s=String(v||'');if(/^\d+(\.\d+)?$/.test(s))return Number(s);if(/^\d+:\d{1,2}(:\d{1,2})?$/.test(s)){return s.split(':').map(Number).reduce((a,b)=>a*60+b,0)}return 0}
  function openlyLicenced(meta){
    const m=meta?.metadata||{};
    const t=clean([m.licenseurl,m.rights,m.license,m.usage].flat().join(' '),2000).toLowerCase();
    return /creativecommons\.org\/(licenses|publicdomain)\/|public domain|cc[\s-]?by(?:[\s-]|$)|cc0/.test(t)
  }
  function chooseMedia(meta,kind){
    const files=Array.isArray(meta.files)?meta.files:[];
    const candidates=[];
    for(const f of files){
      const name=String(f.name||''),size=Number(f.size),seconds=durationSecs(f.length),bitrate=seconds>0?size*8/seconds:Infinity;
      if(!name||!Number.isFinite(size)||size<=0||!seconds)continue;
      if(kind==='video'){
        // Require BOTH measured dimensions and a measured low bitrate; never fetch a high-res source to downscale it.
        const h=Number(f.height),w=Number(f.width);
        if(!/\.(mp4|webm)$/i.test(name)||!h||h>480||h<120||!w||w>960||bitrate>1250000)continue;
      }else if(kind==='audio'){
        if(!/\.mp3$/i.test(name)||bitrate>160000)continue;
      }else if(kind==='book'){
        if(!/\.pdf$/i.test(name)||size>10000000)continue;
      }else continue;
      candidates.push({name,size,seconds,bitrate});
    }
    candidates.sort((a,b)=>a.bitrate-b.bitrate||a.size-b.size);
    return candidates[0]||null;
  }
  function fileURL(identifier,name){return 'https://archive.org/download/'+encodeURIComponent(identifier)+'/'+name.split('/').map(encodeURIComponent).join('/')}
  async function checkPlayback(){
    const item=state.activeItem;if(!item||item.provider!=='ia')return;
    const button=$('#viewer-check');button.disabled=true;button.textContent='Checking…';
    $('#player-shell').replaceChildren();$('#player-shell').hidden=true;
    showMessage('Requesting the item’s metadata only. The media file has not been loaded.');
    try{
      const meta=await getJSON('ia','https://archive.org/metadata/'+encodeURIComponent(item.id));
      if(!openlyLicenced(meta)){
        showMessage('We could not verify an open licence or public-domain declaration for this exact item. Freedom Vision will not embed it. You can review the original archive page and its rights information.');return;
      }
      const file=chooseMedia(meta,item.kind);
      if(!file){showMessage(item.kind==='video'?'No existing file has both verified dimensions at or below 480p and a bitrate within our limit. We will not request a higher-resolution file or ask the archive to transcode one.':'No existing file met our conservative size and bitrate limits. Freedom Vision has not loaded media.');return}
      const shell=$('#player-shell'),url=fileURL(item.id,file.name);
      let media;
      if(item.kind==='video'){media=document.createElement('video');media.controls=true;media.preload='none';media.playsInline=true;media.disablePictureInPicture=true;media.setAttribute('aria-label',item.title);}
      else if(item.kind==='audio'){media=document.createElement('audio');media.controls=true;media.preload='none';media.setAttribute('aria-label',item.title);}
      else if(item.kind==='book'){media=document.createElement('iframe');media.title=item.title+' document reader';media.loading='lazy';media.referrerPolicy='no-referrer';}
      if(!media){showMessage('This media type is not supported in the safe viewer.');return}
      media.src=url;media.addEventListener('error',()=>showMessage('The archive file could not be loaded. The original archive link remains available.'),{once:true});
      shell.append(media);shell.hidden=false;
      showMessage('Selected an existing '+(item.kind==='video'?'≤480p, low-bitrate video':item.kind==='audio'?'low-bitrate audio':'small PDF')+' file. Playback is manual. This content is delivered directly from the original archive; no proxy or conversion is used.');
      $('#viewer-licence').textContent='Archive metadata contains an open-licence or public-domain declaration. That is a catalogue claim, not independent territorial rights clearance; consult the original item for details.';
    }catch(error){showMessage('Playback check stopped: '+String(error.message||error)+' No automatic retry will be made.');}
    finally{button.disabled=false;button.textContent='Check available playback'}
  }
  function closeViewer(){
    $('#player-shell').replaceChildren();$('#player-shell').hidden=true;state.activeItem=null;
    $('#viewer-dialog').close();
  }
  // Static curated discovery stays readable without a network connection.
  $('#search-form').addEventListener('submit',e=>{e.preventDefault();performSearch()});
  $$('.nav-link').forEach(b=>b.addEventListener('click',()=>setMode(b.dataset.mode)));
  $$('.quick-searches button').forEach(b=>b.addEventListener('click',()=>{$('#search-input').value=b.dataset.quick;performSearch({term:b.dataset.quick})}));
  $$('.collection-card').forEach(b=>b.addEventListener('click',()=>{
    if(['culture','worldcinema','science','audiolessons','audiobooks'].includes(b.dataset.collection)){setMode(b.dataset.collection);return}
    const c=collectionSettings[b.dataset.collection];setMode(c.mode);$('#search-input').value=c.query;
    if(c.mode==='news'){showNews();return}
    performSearch({term:c.query,mode:c.mode,collection:c.archiveCollection});
  }));
  $$('.source-filter').forEach(b=>b.addEventListener('click',()=>{state.sourceFilter=b.dataset.sourceFilter;$$('.source-filter').forEach(x=>x.classList.toggle('active',x===b));renderProviders()}));
  $('#clear-results').addEventListener('click',()=>{$('#results-section').hidden=true;$('#results-grid').replaceChildren();$('#search-errors').replaceChildren()});
  $('#viewer-check').addEventListener('click',checkPlayback);$('#viewer-close').addEventListener('click',closeViewer);
  $('#viewer-dialog').addEventListener('click',e=>{if(e.target===$('#viewer-dialog'))closeViewer()});
  $('#viewer-dialog').addEventListener('close',()=>{$('#player-shell').replaceChildren();$('#player-shell').hidden=true;state.activeItem=null});
  renderProviders();
})();