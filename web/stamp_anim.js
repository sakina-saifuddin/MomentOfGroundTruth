/* ---------- title stamp: slam in ---------- */
let _actx=null;
function thump(){
  try{
    _actx=_actx||new (window.AudioContext||window.webkitAudioContext)();
    if(_actx.state!=='running')return;            // browsers keep audio locked until the first click or key
    const t=_actx.currentTime,o=_actx.createOscillator(),g=_actx.createGain();
    o.type='sine';o.frequency.setValueAtTime(150,t);o.frequency.exponentialRampToValueAtTime(38,t+.28);
    g.gain.setValueAtTime(.9,t);g.gain.exponentialRampToValueAtTime(.001,t+.4);
    o.connect(g).connect(_actx.destination);o.start(t);o.stop(t+.42);
    const n=_actx.createBuffer(1,_actx.sampleRate*.12,_actx.sampleRate),d=n.getChannelData(0);
    for(let i=0;i<d.length;i++)d[i]=(Math.random()*2-1)*Math.pow(1-i/d.length,3);
    const s=_actx.createBufferSource(),ng=_actx.createGain();s.buffer=n;ng.gain.value=.5;s.connect(ng).connect(_actx.destination);s.start(t);
  }catch(e){}
}
let _stT=0;
function playStamp(){
  const w=$('.s-title .stampwrap'),s=$('#s1'); if(!w||!s)return;
  clearTimeout(_stT);
  w.classList.remove('slam');s.classList.remove('hit');void w.offsetWidth;
  _stT=setTimeout(()=>{
    w.classList.add('slam');
    _stT=setTimeout(()=>{s.classList.add('hit');thump();setTimeout(()=>s.classList.remove('hit'),950)},620);
  },reduce?0:450);
}
['pointerdown','keydown'].forEach(ev=>addEventListener(ev,()=>{try{_actx=_actx||new (window.AudioContext||window.webkitAudioContext)();_actx.resume()}catch(e){}},{once:true}));
addEventListener('keydown',e=>{if((e.key==='r'||e.key==='R')&&cur===0&&!e.metaKey&&!e.ctrlKey&&!e.target.matches('input,textarea'))playStamp()});
$('.s-title .stampwrap').addEventListener('click',playStamp);

