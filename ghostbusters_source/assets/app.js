
function qs(x){return document.querySelector(x)}
document.addEventListener('DOMContentLoaded',()=>{let b=qs('#bigText'),c=qs('#contrast');if(b)b.addEventListener('click',()=>document.body.classList.toggle('large'));if(c)c.addEventListener('click',()=>document.body.classList.toggle('highcontrast'));});
function missingInfo(choice){const out=document.getElementById('missingResult');const map={hate:'That is one possible story, but the evidence is incomplete. Other explanations still fit.',busy:'Possible, but still a guess. We need more information.',happened:'Possible, but still a guess. We need more information.',unknown:'This answer preserves the uncertainty. It leaves room for evidence.'};out.textContent=map[choice];}
function revealCase(){document.getElementById('caseReveal').textContent='More information arrives: their phone battery failed during a family emergency. The silence was real; the first story was not necessarily the cause.';}
function confidence(v){let n=Number(v),t='I wonder';if(n>20)t='I think';if(n>45)t='Evidence suggests';if(n>70)t='I am fairly confident';if(n>90)t='I am very confident — but I should still say what evidence this rests on.';document.getElementById('confidenceResult').textContent=t;}


function setReadingMode(mode){
  document.body.classList.remove("simple-only","deep-only");
  if(mode==="simple") document.body.classList.add("simple-only");
  if(mode==="deep") document.body.classList.add("deep-only");
  try{localStorage.setItem("gb_reading_mode",mode);}catch(e){}
}
document.addEventListener("DOMContentLoaded",()=>{
  const b=document.getElementById("bigText"), c=document.getElementById("contrast");
  if(b) b.onclick=()=>document.body.classList.toggle("large");
  if(c) c.onclick=()=>document.body.classList.toggle("highcontrast");
  try{const m=localStorage.getItem("gb_reading_mode");if(m)setReadingMode(m)}catch(e){}
});
function missingInfo(choice){
  const out=document.getElementById("missingResult");
  const m={hate:"Possible, but the evidence is incomplete.",busy:"Possible, but still a guess.",happened:"Possible, but still a guess.",unknown:"This preserves uncertainty and leaves room for evidence."};
  if(out) out.textContent=m[choice];
}
function revealCase(){
 const el=document.getElementById("caseReveal");
 if(el) el.textContent="More information arrives: their phone battery failed during a family emergency. The silence was real; the first story was not necessarily the cause.";
}
function confidence(v){
 const el=document.getElementById("confidenceResult"); if(!el)return;
 const n=Number(v); let t="I wonder";
 if(n>20)t="I think"; if(n>45)t="Evidence suggests"; if(n>70)t="I am fairly confident"; if(n>90)t="I am very confident — and should still say what this rests on.";
 el.textContent=t;
}
