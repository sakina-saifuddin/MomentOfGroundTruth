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
  enterFx(id);
}

/* ---------- entry effects: every slide brings its main number in with a different move, so the slides feel different ----------
   They use the Web Animations API on the separate translate/rotate/scale properties, so they never fight the pulse. */
const FX={
  zoom:  [{scale:'3.2',opacity:0},{scale:'1',opacity:1}],
  slam:  [{scale:'4',opacity:0,translate:'0 -2rem'},{scale:'.9',opacity:1,translate:'0 .2rem',offset:.55},{scale:'1.05',translate:'0 0',offset:.75},{scale:'1',opacity:1,translate:'0 0'}],
  flipX: [{rotate:'x 90deg',opacity:0},{rotate:'x 0deg',opacity:1}],
  flipY: [{rotate:'y -90deg',opacity:0},{rotate:'y 0deg',opacity:1}],
  spin:  [{rotate:'360deg',scale:'.2',opacity:0},{rotate:'0deg',scale:'1',opacity:1}],
  drop:  [{translate:'0 -4rem',opacity:0},{translate:'0 .6rem',opacity:1,offset:.6},{translate:'0 0',opacity:1}],
  rise:  [{translate:'0 3rem',opacity:0},{translate:'0 0',opacity:1}],
  left:  [{translate:'-7rem 0',opacity:0},{translate:'0 0',opacity:1}],
  right: [{translate:'7rem 0',opacity:0},{translate:'0 0',opacity:1}],
  wipe:  [{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0 0 0)'}],
  track: [{letterSpacing:'.6em',opacity:0},{letterSpacing:'0em',opacity:1}],
  jelly: [{scale:'0',opacity:0},{scale:'1.25 .8',opacity:1,offset:.5},{scale:'.9 1.1',offset:.7},{scale:'1',opacity:1}]
};
/* slide id -> [effect of the main number, count it up?, other elements, their effect] */
const ENTER={
  s2: ['zoom',  true,  '.case',            'left'],
  s3: ['jelly', true,  '#classbars .brow', 'wipe'],
  s4: ['jelly', false, '.cc',              'rise'],
  s5: ['flipY', false, '.sb-train,.sb-val,.sb-test', 'drop'],
  e1: ['slam',  false, '.xr',              'left'],
  e2: ['spin',  true,  '.xr',              'wipe'],
  s6: ['flipX', false, '.tile',            'rise'],
  s7: ['right', false, '.tile',            'left'],
  s8: ['drop',  false, '.tile',            'jelly'],
  s9: ['track', false, '.pc',              'rise'],
  s10:['slam',  false, '.hrow,.hbar',      'left'],
  s16:['zoom',  true,  '.wcard',           'jelly']
};
function tweenNum(el,ms){
  const raw=el.textContent.trim(),m=raw.match(/^([+]?)([\d,]*\.?\d+)(.*)$/);if(!m)return;
  const dec=(m[2].split('.')[1]||'').length,comma=m[2].includes(','),to=parseFloat(m[2].replace(/,/g,'')),t0=performance.now();
  (function step(t){
    const k=Math.min((t-t0)/ms,1),v=to*(1-Math.pow(1-k,3));
    let s=v.toFixed(dec);if(comma)s=Number(s).toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec});
    el.textContent=m[1]+s+m[3];
    if(k<1)requestAnimationFrame(step);else el.textContent=raw;
  })(t0);
}
/* every number gets a highlighter marker behind it (a soft colour, so the text stays easy to read) and its own entry move */
const HLC=['rgba(242,183,5,.5)','rgba(216,41,31,.26)','rgba(31,157,85,.3)','rgba(31,111,214,.26)'];
const HL_MODEL={s6:0,s7:3,s8:2};   /* BiGRU yellow, BiLSTM blue, BERT green */
const FXLIST=['zoom','flipX','jelly','slam','spin','drop','left','track','flipY','rise','right'];
const NUMSEL='.big,.rank,.v,#pf,#pa,#pdelta b';
function enterFx(id){
  const s=slides.find(x=>x.id===id),c=ENTER[id];
  if(!s||!c)return;
  const calm=matchMedia('(prefers-reduced-motion:reduce)').matches,si=slides.indexOf(s);
  const nums=$$(NUMSEL,s);if(!nums.some(e=>e.classList.contains('big'))){const e=$('h2 em',s);if(e)nums.unshift(e)}
  nums.forEach((e,i)=>{
    if(!e.classList.contains('rank')&&e.tagName!=='EM'){
      e.classList.add('hl');
      e.style.setProperty('--hlc',HLC[id in HL_MODEL?HL_MODEL[id]:(i+si)%HLC.length]);
    }
    if(calm)return;
    const fx=FX[i===0?c[0]:FXLIST[(i*3+si)%FXLIST.length]];
    e.animate(fx,{duration:900,delay:i*90,easing:'cubic-bezier(.2,.8,.2,1)',fill:'backwards'});
    if(e.classList.contains('hl'))e.animate([{backgroundSize:'0% 100%'},{backgroundSize:'100% 100%'}],{duration:700,delay:350+i*90,easing:'ease-out',fill:'backwards'});
    if(c[1]&&i===0&&!e.hasAttribute('data-count'))tweenNum(e,1100);
  });
  if(!calm)$$(c[2],s).forEach((e,i)=>e.animate(FX[c[3]],{duration:700,delay:200+i*90,easing:'cubic-bezier(.2,.8,.2,1)',fill:'backwards'}));
}
