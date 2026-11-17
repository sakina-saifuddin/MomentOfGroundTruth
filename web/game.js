/* ---------- audience game: live votes + reveal ---------- */
(function(){
  const GAME=new URLSearchParams(location.search).get('game')||'/.netlify/functions/game';
  const qs=new URLSearchParams(location.search);
  if(qs.get('host'))try{localStorage.setItem('mogHost',qs.get('host'))}catch(e){}
  let HOSTKEY='mog-host';try{HOSTKEY=localStorage.getItem('mogHost')||HOSTKEY}catch(e){}
  const SHORT=['Equipment','Corrosion','Material','Excavation','Natural force','Other outside','Other cause','Incorrect op'];
  const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  let st=null,timer=0,online=false;

  async function call(action,body){
    const ac=new AbortController(),t=setTimeout(()=>ac.abort(),8000);
    try{
      const r=body?await fetch(GAME,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action,...body}),signal:ac.signal}):await fetch(GAME+'?action='+action,{signal:ac.signal});
      return await r.json();
    }finally{clearTimeout(t)}
  }
  function setOnline(v){
    online=v;
    ['#gm-online','#gm-online2'].forEach(id=>{const e=$(id);if(e){e.className='pill lv-st '+(v?'on':'off');e.innerHTML='<i></i>'+(v?'LIVE · votes counting':'GAME SERVER OFFLINE')}});
  }
  async function poll(){
    try{st=await call('state');if(!st.ok)throw new Error();setOnline(true);drawVote();drawRes()}
    catch(e){setOnline(false)}
  }
  window.gameEnter=function(){clearInterval(timer);poll();timer=setInterval(poll,2000)};
  window.gameLeave=function(){clearInterval(timer);timer=0};

  /* slide 13: who is in */
  function drawVote(){
    if(!st)return;
    $('#gv-voters').textContent=st.voters;
    const mx=Math.max(1,st.voters);
    $('#gv-rounds').innerHTML=st.rounds.length===1?'':st.rounds.map((r,i)=>`<div class="gv-rrow"><span>Report ${i+1}</span><div class="tr"><div class="fl" style="width:${Math.round(100*r.total/mx)}%"></div></div><b>${r.total}</b></div>`).join('');
  }

  /* slide 14: live bars, then the reveal */
  const ROUNDS=GAME_ROUNDS;
  let shownVerdict='';
  function drawRes(){
    if(!st)return;
    const rev=st.revealed&&st.answers;
    const one=ROUNDS.length===1;$('#gr-cols').className='gr-cols'+(one?' one':'');
    const cols=ROUNDS.map((rd,i)=>{
      const c=st.rounds[i],tot=c.total,mx=Math.max(1,...c.counts),a=rev?st.answers[i]:null;
      const top=c.counts.indexOf(Math.max(...c.counts));
      const rows=c.counts.map((n,k)=>{
        const pct=tot?Math.round(100*n/tot):0,isT=a&&a.truth===k,isM=a&&a.model===k;
        return `<div class="gr-row${isT?' truth':''}${tot&&k===top?' top':''}"><span class="n">${SHORT[k]}</span><div class="tr"><div class="fl" style="width:${Math.round(100*n/mx)}%"></div></div><span class="p">${pct}%</span><span class="mk">${isT?'<i class="t">✓</i>':''}${isM?'<i class="m">M</i>':''}</span></div>`;
      }).join('');
      const res=a?`Crowd right: <b>${tot?Math.round(100*c.counts[a.truth]/tot):0}%</b> · Model: <b>${a.model===a.truth?'right':'wrong'}</b> (${Math.round(a.conf*100)}% sure)`:'';
      const card=one?`<div class="gr-rep paper"><div class="lab" style="color:#5a5143">The report · what caused it?</div><p>${esc(rd.text)}</p></div>`:'';
      return card+`<div class="gr-col"><div class="gr-h"><b>${one?'The votes':'Report '+(i+1)}</b><span class="lab">${tot} answers</span></div>${one?'':`<p class="gr-ex">${esc(rd.excerpt)}</p>`}<div><div class="gr-rows">${rows}</div><div class="gr-res" style="margin-top:.5rem">${res}</div></div></div>`;
    }).join('');
    $('#gr-cols').innerHTML=cols;
    const btn=$('#gm-reveal');btn.textContent=rev?'Hide answers':'Reveal answers';
    const score=$('#gr-score'),vd=$('#gr-verdict');
    if(!rev){score.textContent=st.voters+' people voting';vd.innerHTML='';shownVerdict='';return}
    let model=0,crowd=0,avg=0;
    st.answers.forEach((a,i)=>{
      const c=st.rounds[i];if(a.model===a.truth)model++;
      if(c.total&&c.counts.indexOf(Math.max(...c.counts))===a.truth)crowd++;
      avg+=c.total?c.counts[a.truth]/c.total:0;
    });
    const n=st.answers.length;
    score.textContent=n===1?`${Math.round(100*avg)}% of the room got it right · the model got it ${model?'right':'wrong'}`:`Crowd vote ${crowd}/${n} · Model ${model}/${n} · average person ${Math.round(100*avg/n)}% right`;
    const v=crowd>model?'The crowd wins':crowd<model?'The model wins':n===1?(model?'Both got it':'Both fooled'):'Dead heat';
    if(v!==shownVerdict){vd.innerHTML=`<span class="gm-stamp">${v}</span>`;shownVerdict=v}
  }
  async function toggleReveal(){
    if(!st)return;
    try{
      const r=await call('reveal',{key:HOSTKEY,value:!st.revealed});
      if(!r.ok)alert('Reveal refused: '+(r.error||'unknown')+'. Open the deck once with ?host=YOUR_KEY.');
    }catch(e){}
    poll();
  }
  $('#gm-reveal').onclick=toggleReveal;
  $('#gm-refresh').onclick=poll;
  addEventListener('keydown',e=>{
    if(e.metaKey||e.ctrlKey||e.altKey||e.target.matches('input,textarea'))return;
    if(slides[cur]&&slides[cur].id==='sr'){
      if(e.key==='v'||e.key==='V')toggleReveal();
      if(e.key==='X'&&e.shiftKey&&confirm('Delete ALL votes and start a fresh game?'))call('reset',{key:HOSTKEY}).then(poll);
    }
  });
  drawRes();
})();

