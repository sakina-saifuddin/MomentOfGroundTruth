/* ---------- spotlight: the numbers we talk about pulse, and the weaker ones fade back ---------- */
function spotlight(id){
  const s=slides.find(x=>x.id===id); if(!s)return;
  $$('.auto',s).forEach(e=>e.classList.remove('pulse','dim','hotrow','auto'));
  const mark=(sel,cls)=>$$(sel,s).forEach(e=>e.classList.add(cls,'auto'));
  if(id==='s2')mark('.case .nums .big','pulse');
  if(id==='s3'){mark('#classbars .brow:first-child','hotrow');mark('#classbars .brow:last-child','hotrow')}
  if(id==='s6'||id==='s7'){
    // on a model slide, the run with the higher macro-F1 pulses and the other run fades back
    const tiles=$$('.tile',s);let best=-1,bi=-1;
    tiles.forEach((t,i)=>{const v=parseFloat($('.big',t).textContent);if(v>best){best=v;bi=i}});
    tiles.forEach((t,i)=>{if(i===bi)$('.big',t).classList.add('pulse','auto');else t.classList.add('dim','auto')});
  }
  if(id==='s9')mark('#pf,#pa,#pdelta b','pulse');
}
