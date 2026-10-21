module.exports.run = async (page, base, shot) => {
  const out=[];
  await page.evaluate(()=>document.querySelector('#spamEx').click());
  await new Promise(r=>setTimeout(r,300));
  out.push(['spam example verdict', await page.evaluate(()=>document.querySelector('#verdictLabel').textContent+' @ '+document.querySelector('#verdictPct').textContent)]);
  await page.evaluate(()=>document.querySelector('#hamEx').click());
  await new Promise(r=>setTimeout(r,300));
  out.push(['ham example verdict', await page.evaluate(()=>document.querySelector('#verdictLabel').textContent+' @ '+document.querySelector('#verdictPct').textContent)]);
  // classic scam
  await page.evaluate(()=>{document.querySelector('#input').value='URGENT! Your account will be suspended. Click here now to claim your FREE prize worth $1000 cash. Text WIN to 80123';document.querySelector('#clsBtn').click()});
  await new Promise(r=>setTimeout(r,300));
  out.push(['scam verdict', await page.evaluate(()=>document.querySelector('#verdictLabel').textContent+' @ '+document.querySelector('#verdictPct').textContent)]);
  out.push(['evidence rows', await page.evaluate(()=>document.querySelectorAll('.ev-item').length)]);
  out.push(['metrics shown', await page.evaluate(()=>document.querySelector('#mAcc').textContent)]);
  await page.screenshot({path:shot});
  return out;
};
