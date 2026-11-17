/* ---------- slide 14: live demo against the model on OCI ---------- */
(function(){
  const API=new URLSearchParams(location.search).get('api')||(location.protocol==='file:'?'http://localhost:8000/api':'/api');
  const PHOTO={0:'equip',1:'corr',2:'mat',3:'exc',4:'nat',6:'oth',7:'op'};
  const rd=$('#lv-read'),st=$('#lv-status'),ta=$('#lv-text'),btn=$('#lv-go'),out=$('#lv-out'),exBox=$('#lv-ex'),wc=$('#lv-words');
  const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const argmax=a=>a.indexOf(Math.max(...a));
  const exOf=t=>OFFLINE.items.find(x=>x.text.trim()===t.trim());
  const LIVE_ENABLED=!!new URLSearchParams(location.search).get('api')||LIVE_API_ENABLED;
  let live=false,last=null;

  async function api(path,body,ms){
    const ac=new AbortController(),t=setTimeout(()=>ac.abort(),ms||20000);
    try{
      const r=await fetch(API+path,body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:ac.signal}:{signal:ac.signal});
      if(!r.ok){let m='';try{m=(await r.json()).detail}catch(e){} throw new Error(m||('HTTP '+r.status))}
      return await r.json();
    }finally{clearTimeout(t)}
  }
  function setLive(v){
    live=v;st.className='pill lv-st '+(v?'on':'off');
    st.innerHTML='<i></i>'+(v?'LIVE · model on Oracle Cloud':'SAVED RUN · real model output');
    ta.readOnly=!v;ta.placeholder=v?'e.g. a contractor using a backhoe struck the 12-inch transmission line while digging a trench...':'Choose a report above and it will appear here.';
    btn.hidden=!v;wc.hidden=!v;
    ta.hidden=!v;rd.hidden=v;
    if(!v&&!rd.dataset.set){rd.className='lv-read paper empty';rd.textContent='Choose a report above and it will appear here.'}
  }
  async function ping(){if(!LIVE_ENABLED){setLive(false);return}try{const h=await api('/health',null,6000);setLive(!!h.ok)}catch(e){setLive(false)}}

  const empty=()=>{out.innerHTML='<div class="lv-empty"><div><b>No report chosen yet</b>Choose a report on the left, and the model will stamp it with a cause.</div></div>'};
  const msg=m=>{$('#lv-act2').hidden=true;out.innerHTML='<p class="lv-msg">'+m+'</p>'};

  exBox.innerHTML=OFFLINE.items.map((x,i)=>`<button aria-pressed="false" data-i="${i}">${x.name}</button>`).join('');
  $$('button',exBox).forEach(b=>b.onclick=()=>{ta.value=OFFLINE.items[+b.dataset.i].text;sync();run()});
  function sync(){
    const n=ta.value.trim().split(/\s+/).filter(Boolean).length;
    wc.textContent=n+' words'; btn.disabled=!n;
    const e=exOf(ta.value);$$('button',exBox).forEach(b=>b.setAttribute('aria-pressed',!!e&&OFFLINE.items[+b.dataset.i]===e));
  }
  ta.addEventListener('input',sync);
  ta.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();run()}});
  btn.onclick=run;

  async function run(){
    const text=ta.value.trim(); if(!text)return;
    btn.disabled=true; msg('Reading the narrative...');
    let res;const saved=exOf(text);
    if(!LIVE_ENABLED&&saved)res={cleaned:saved.text,probs:saved.probs,top:argmax(saved.probs),titles:OFFLINE.titles};
    else try{res=await api('/predict',{text});setLive(true)}
    catch(e){
      setLive(false);
      if(!saved){msg('Cannot reach the model server ('+esc(e.message)+'). Pick one of the eight examples to replay its saved result.');sync();return}
      res={cleaned:saved.text,probs:saved.probs,top:argmax(saved.probs),titles:OFFLINE.titles};
    }
    last=res; draw(res); sync();
  }

  function draw(res){
    const top=res.top,C=OFFLINE.causes[top],pr=res.probs,ex=exOf(ta.value);
    const order=[...pr.keys()].sort((a,b)=>pr[b]-pr[a]);
    const photo=PHOTO[top]!==undefined?`<div class="frame"><img src="${IMG[PHOTO[top]]}" alt="${esc(C.title)}"></div>`:`<div class="frame"><div class="none">No photo for this cause</div></div>`;
    const badge=ex?`<span class="lv-badge">The recorded cause is <b>${esc(OFFLINE.titles[OFFLINE.labels.indexOf(ex.truth)])}</b>, and the model got it <b>${OFFLINE.labels.indexOf(ex.truth)===top?'right':'wrong'}</b>.</span>`:'';
    out.innerHTML=`
      <div class="lv-top"><div class="lv-hd"><div class="lv-stamp">${esc(C.title)}</div><div class="lv-conf"><span class="big">${Math.round(pr[top]*100)}%</span><span class="lab">model confidence</span></div></div>
        <figure class="lv-photo">${photo}<figcaption class="credit" title="${esc(C.caption||'')}">${esc(C.caption||'')}</figcaption></figure></div>
      <div class="lv-bars">${order.map((i,r)=>`<div class="lv-brow${r?'':' top'}"><span>${esc(res.titles[i])}</span><div class="tr"><div class="fl" data-w="${(pr[i]*100).toFixed(1)}"></div></div><span class="pc">${Math.round(pr[i]*100)}%</span></div>`).join('')}</div>
`;
    rd.dataset.set='1';rd.className='lv-read paper';rd.textContent=res.cleaned;
    $('#lv-act2').hidden=false;$('#lv-badge').innerHTML=badge;$('#lv-whyst').textContent='';$('#lv-why').disabled=false;
    requestAnimationFrame(()=>requestAnimationFrame(()=>$$('.fl',out).forEach(f=>f.style.width=f.dataset.w+'%')));
  }

  function shade(words,note){
    const mx=Math.max(...words.map(w=>Math.abs(w[1])),1e-9);
    rd.innerHTML=words.map(([w,v])=>{const a=Math.min(Math.abs(v)/mx,1)*.85;return `<span style="background:${v>0?`rgba(216,41,31,${a.toFixed(2)})`:`rgba(95,168,173,${a.toFixed(2)})`}" title="${v>=0?'+':''}${v.toFixed(3)}">${esc(w.trim())}</span>`}).join(' ');
    $('#lv-whyst').innerHTML='<span class="lv-legend"><span style="background:rgba(216,41,31,.6)">pushes toward</span><span style="background:rgba(95,168,173,.6)">pushes away</span></span>'+(note?` <span class="lab">${note}</span>`:'');
  }
  async function why(){
    const b=$('#lv-why'),s=$('#lv-whyst'),text=ta.value.trim(),ex=exOf(text); let sec=0;
    if(!live&&ex&&ex.words){shade(ex.words);return}
    b.disabled=true; s.textContent='Hiding words and re-scoring... 0 s';
    const tm=setInterval(()=>{s.textContent='Hiding words and re-scoring... '+(++sec)+' s'},1000);
    try{const r=await api('/explain',{text,evals:100},24000);clearInterval(tm);shade(r.words,'live SHAP')}
    catch(e){
      clearInterval(tm);
      if(ex&&ex.words)shade(ex.words,'saved SHAP result');
      else s.textContent='Explanation failed: '+e.message;
    }
    b.disabled=false;
  }

  $('#lv-why').onclick=why;
  empty(); sync(); ping().then(()=>{if(!live)setTimeout(ping,2000)});
  window._lvEnter=ping;
})();
