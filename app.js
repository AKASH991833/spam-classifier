/* Spam Shield: Naive Bayes inference + evidence words */
(function(){
'use strict';
const M=NB_MODEL,VOC=new Set(M.vocab);
const tok=s=>(s.toLowerCase().match(/[a-z0-9']+/g)||[]);
function classify(text){
  const words=tok(text);
  let sS=M.prior.spam,sH=M.prior.ham;
  const contrib=[];
  for(const w of words){
    if(!VOC.has(w))continue;
    const ls=M.logpSpam[w]??M.default.spam, lh=M.logpHam[w]??M.default.ham;
    sS+=ls;sH+=lh;contrib.push({w,d:ls-lh});
  }
  const p=1/(1+Math.exp(sH-sS));
  return{p,contrib,known:contrib.length,total:words.length};
}
function render(){
  const text=$('#input').value.trim();
  if(!text){toast('Paste a message first');return}
  const{p,contrib,known,total}=classify(text);
  const pct=Math.round(p*100);
  const v=$('#verdict');v.style.display='flex';
  const spam=p>=0.5;
  $('#verdictLabel').innerHTML=spam?'🚨 Likely spam':'✅ Looks safe';
  $('#verdictLabel').style.color=spam?'var(--bad)':'var(--ok)';
  const gf=$('#gaugeFill');
  gf.style.width=Math.max(3,pct)+'%';
  gf.style.background=pct>75?'var(--bad)':pct>45?'var(--warn)':'var(--ok)';
  $('#verdictPct').textContent=pct+'% spam';
  // evidence
  const ev=$('#evidence');
  if(!contrib.length){
    ev.innerHTML=`<div class="note">None of the ${total} words appear in the training vocabulary, so this verdict rests on the class prior alone. Short or non-English messages score low-confidence by design.</div>`;
  }else{
    const top=[...contrib].sort((a,b)=>Math.abs(b.d)-Math.abs(a.d)).slice(0,8);
    const maxD=Math.max(...top.map(t=>Math.abs(t.d)),0.001);
    ev.innerHTML='';
    top.forEach(t=>{
      const spamW=t.d>0;
      const d=document.createElement('div');d.className='ev-item';
      d.innerHTML=`<span class="w">${esc(t.w)}</span><span class="bar"><i style="width:${Math.round(100*Math.abs(t.d)/maxD)}%;background:${spamW?'var(--bad)':'var(--ok)'}"></i></span><span class="v">${spamW?'spam +':'safe +'}${Math.abs(t.d).toFixed(1)}</span>`;
      ev.appendChild(d);
    });
    const note=document.createElement('div');note.style.cssText='font-size:.78rem;color:var(--ink-faint);margin-top:6px';
    note.textContent=`${known} of ${total} words matched the training vocabulary.`;
    ev.appendChild(note);
  }
}
$('#clsBtn').addEventListener('click',render);
$('#input').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.metaKey||e.ctrlKey))render()});
function example(label){
  const c=EXAMPLES.filter(e=>e.label===label);
  $('#input').value=c[Math.floor(Math.random()*c.length)].text;
  render();
}
$('#spamEx').addEventListener('click',()=>example('spam'));
$('#hamEx').addEventListener('click',()=>example('ham'));
// metrics panel
const m=M.metrics;
$('#mAcc').textContent=(m.accuracy*100).toFixed(1)+'%';
$('#mPrec').textContent=(m.precision*100).toFixed(1)+'%';
$('#mRec').textContent=(m.recall*100).toFixed(1)+'%';
$('#mVoc').textContent=M.vocab.length.toLocaleString();
$('#confMatrix').innerHTML=`
<div><span>Spam caught</span><b>${m.tp}</b></div><div><span>Spam missed</span><b>${m.fn}</b></div>
<div><span>Real kept</span><b>${m.tn}</b></div><div><span>False alarms</span><b>${m.fp}</b></div>`;
})();
