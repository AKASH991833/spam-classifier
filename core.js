/* Shared: theme, toast, PWA */
(function(){
  const root=document.documentElement;
  const saved=localStorage.getItem('theme');
  const pref=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
  root.dataset.theme=saved||pref;
  window.toggleTheme=function(){
    root.dataset.theme=root.dataset.theme==='dark'?'light':'dark';
    localStorage.setItem('theme',root.dataset.theme);
  };
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change',e=>{
    if(!localStorage.getItem('theme'))root.dataset.theme=e.matches?'dark':'light';
  });
  window.toast=function(msg,ms=2200){
    let t=document.querySelector('.toast');
    if(!t){t=document.createElement('div');t.className='toast';document.body.appendChild(t);}
    t.textContent=msg;t.classList.add('show');
    clearTimeout(t._h);t._h=setTimeout(()=>t.classList.remove('show'),ms);
  };
  if('serviceWorker' in navigator && location.protocol.startsWith('http')){
    navigator.serviceWorker.register('sw.js').catch(()=>{});
  }
  window.$=s=>document.querySelector(s);window.$$=s=>[...document.querySelectorAll(s)];
  window.esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
})();
