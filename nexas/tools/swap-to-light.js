const fs=require('fs'),path=require('path');
const dir=path.join(__dirname,'..','nexas');
const map={'01-home.png':'01-home-light.png','02-inspect.png':'02-inspect-light.png','04-emergency.png':'04-emergency-light.png'};
['index.html','for-business-owner.html'].forEach(f=>{
  const p=path.join(dir,f);
  let c=fs.readFileSync(p,'utf8');
  let n=0;
  Object.entries(map).forEach(([from,to])=>{
    const re=new RegExp('app-screenshots/'+from.replace('.','\\.'),'g');
    const before=c;
    c=c.replace(re,'app-screenshots/'+to);
    if(c!==before)n++;
  });
  fs.writeFileSync(p,c);
  console.log(f+': '+n+' replacements');
});
console.log('Done. git add -A && git commit -m "feat: app screenshots dark→light" && git push');
