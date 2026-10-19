import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
const topic=(process.env.VIDEO_TOPIC||"Long Handle Floor Scrub Brush with Squeegee").trim().slice(0,180);
const price=(process.env.VIDEO_PRODUCT_PRICE||"£14.99").trim().slice(0,32);
const url=(process.env.VIDEO_PRODUCT_URL||"https://atlasgoodsstore.co.uk/products/long-handle-floor-scrub-brush-with-squeegee").trim().replace(/\/$/,"");
const image=(process.env.VIDEO_PRODUCT_IMAGE_URL||"https://cdn.shopify.com/s/files/1/0833/5284/6562/files/long-handle-floor-scrub-brush.png?v=1789778185").trim();
const out="video-output";fs.mkdirSync(out,{recursive:true});
if(!/^https:\/\/atlasgoodsstore\.co\.uk\/products\/[a-z0-9-]+$/i.test(url))throw Error("Invalid Atlas product URL");
let title=topic,actualPrice=price,img=image;
const response=await fetch(url+".js",{signal:AbortSignal.timeout(12000)}).catch(()=>null);
if(response?.ok){const p=await response.json();if(p.title)title=String(p.title).slice(0,180);if(typeof p.price==="number")actualPrice=new Intl.NumberFormat("en-GB",{style:"currency",currency:"GBP"}).format(p.price/100);if(p.images?.[0])img=String(p.images[0]);}
if(!/^https:\/\/cdn\.shopify\.com\//i.test(img))throw Error("Only Shopify CDN product images are allowed");
const ir=await fetch(img,{signal:AbortSignal.timeout(15000)});if(!ir.ok)throw Error("Product image HTTP "+ir.status);
const type=(ir.headers.get("content-type")||"").toLowerCase(),ext=type.includes("png")?"png":type.includes("webp")?"webp":"jpg";
const imagePath=out+"/product."+ext;fs.writeFileSync(imagePath,Buffer.from(await ir.arrayBuffer()));
const esc=s=>s.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;");
const scenes=[
["A BETTER CLEANING ROUTINE",title],
["BRUSH + SQUEEGEE","Two functions in one handy design"],
["TAKE A CLOSER LOOK","See product details on our store"],
[actualPrice,"Check the listing for current details"],
["FREE UK SHIPPING","Shop Atlas Goods Store"],
["YOUR HOME. YOUR WAY.","Explore the range at Atlas Goods Store"]
];
const clips=[];
for(let i=0;i<scenes.length;i++){
 const [head,sub]=scenes[i];
 const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#101828"/><stop offset="1" stop-color="#34465e"/></linearGradient></defs><rect width="1080" height="1920" fill="url(#g)"/><text x="540" y="130" text-anchor="middle" font-family="DejaVu Sans" font-size="29" letter-spacing="5" fill="#e4c879">ATLAS GOODS STORE</text><rect x="65" y="200" width="950" height="1110" rx="38" fill="#fff"/><text x="540" y="1400" text-anchor="middle" font-family="DejaVu Sans" font-size="48" font-weight="bold" fill="#e4c879">${esc(head)}</text><text x="540" y="1485" text-anchor="middle" font-family="DejaVu Sans" font-size="34" fill="#fff" stroke="#101828" stroke-width="1" paint-order="stroke">${esc(sub.slice(0,58))}</text><text x="540" y="1770" text-anchor="middle" font-family="DejaVu Sans" font-size="27" fill="#e4c879">FREE UK SHIPPING</text><text x="540" y="1830" text-anchor="middle" font-family="DejaVu Sans" font-size="24" fill="#fff">ATLASGOODSSTORE.CO.UK</text></svg>`;
 const svgPath=`${out}/scene-${i}.svg`,png=`${out}/scene-${i}.png`,mp4=`${out}/scene-${i}.mp4`;
 fs.writeFileSync(svgPath,svg);execFileSync("rsvg-convert",["-o",png,svgPath]);
 const filter="[0:v]scale=1080:1920[bg];[1:v]scale=900:1000:force_original_aspect_ratio=decrease,pad=900:1000:(ow-iw)/2:(oh-ih)/2:color=white,zoompan=z='min(zoom+0.001,1.04)':d=75:s=900x1000:fps=25,setsar=1[product];[bg][product]overlay=90:255,format=yuv420p[v]";
 execFileSync("ffmpeg",["-y","-loop","1","-i",png,"-loop","1","-i",imagePath,"-filter_complex",filter,"-map","[v]","-t","3","-an","-r","25","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",mp4],{stdio:"inherit"});
 clips.push(mp4);
}
const list=out+"/concat.txt";fs.writeFileSync(list,clips.map(p=>`file '${path.basename(p)}'`).join("\n"));
execFileSync("ffmpeg",["-y","-f","concat","-safe","0","-i",list,"-c","copy","-movflags","+faststart",out+"/atlas-video-draft.mp4"],{stdio:"inherit"});
fs.writeFileSync(out+"/CAPTION.txt",title+" — "+actualPrice+"\n\nView product details: "+url+"\n\nFree UK shipping from Atlas Goods Store.\n\n#AtlasGoodsStore #UKShopping #HomeEssentials\n\nDRAFT ONLY: visual-first edit with no synthetic narration. Verify price, stock and delivery terms before publishing.\n");
console.log("Created silent visual-first product video");
