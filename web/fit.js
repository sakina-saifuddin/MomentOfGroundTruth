/* ---------- keep slide content clear of the footer bar ---------- */
function fitAll(){
  const hud=$('#hud'); if(!hud)return;
  const narrow=innerWidth<=900;
  slides.forEach(s=>{
    const b=$('.body',s); if(!b)return;
    b.style.zoom='';
    if(narrow)return;
    const was=s.className;
    s.classList.add('measure');
    const limit=hud.getBoundingClientRect().top-12;
    for(let pass=0;pass<3;pass++){
      const top=b.getBoundingClientRect().top;
      let worst=0;
      b.querySelectorAll('*').forEach(e=>{
        if(e.closest('.stampwrap')||e.closest('.lv-out'))return;
        const r=e.getBoundingClientRect(); if(r.width<2||r.height<2)return;
        const cs=getComputedStyle(e); if(cs.display==='none'||cs.visibility==='hidden')return;
        if(r.bottom>worst)worst=r.bottom;
      });
      if(worst<=limit||worst<=top)break;
      const cur=parseFloat(b.style.zoom||'1');
      b.style.zoom=Math.max(.55,cur*(limit-top)/(worst-top)).toFixed(3);
    }
    s.className=was;
  });
}
let _fitT=0;
addEventListener('resize',()=>{clearTimeout(_fitT);_fitT=setTimeout(fitAll,150)});
addEventListener('load',fitAll);
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(fitAll);

