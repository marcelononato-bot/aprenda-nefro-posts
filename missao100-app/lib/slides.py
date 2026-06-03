"""
Carrossel de 10 slides (1080x1080) do Missão 100% — diagramação por itens.
Cada parágrafo do 'corpo' (separado por \n) vira um item com MARCADOR dourado;
o rótulo antes de ':' sai em dourado (destaque ao mudar de parágrafo).
Auto-ajuste de fonte e distribuição vertical para preencher o slide.
Identidade: navy #16213E (fundo), ouro #FDC535, branco no corpo.
"""
import json, pathlib
from PIL import Image, ImageDraw, ImageFont

BASE = pathlib.Path(__file__).parents[1]
NAVY=(22,33,62); GOLD=(253,197,53); WHITE=(238,240,247); MUT=(150,160,186); RULE=(54,68,108)
FB="/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
FR="/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"
W=H=1080; MX=72

def _f(p,s): return ImageFont.truetype(p,s)

def _wrap(d,txt,font,maxw):
    out=[]
    for w in txt.split():
        t=(out[-1]+" "+w).strip() if out else w
        if out and d.textlength(t,font=font)<=maxw: out[-1]=t
        else: out.append(w)
    return out

def _split_lead(text):
    head=text.split(":",1)
    if len(head)==2 and len(head[0])<=54 and len(head[0].split())<=8 and head[1].strip():
        return head[0].strip()+":", head[1].strip()
    return None, text

def _item(d,x,y,width,text,bf,lf,blh,draw=True):
    """Renderiza/mede um item com marcador + rótulo dourado + texto branco (indent pendurado)."""
    indent=34; tx=x+indent; right=tx+(width-indent)
    lead,rest=_split_lead(text)
    if draw: d.rectangle([x,y+int(blh*0.30),x+13,y+int(blh*0.30)+13],fill=GOLD)
    cx=tx; cy=y
    if lead:
        if draw: d.text((cx,cy),lead+" ",font=lf,fill=GOLD)
        cx+=d.textlength(lead+" ",font=lf)
    for w in rest.split():
        ww=d.textlength(w+" ",font=bf)
        if cx+ww>right and cx>tx: cx=tx; cy+=blh
        if draw: d.text((cx,cy),w+" ",font=bf,fill=WHITE)
        cx+=ww
    return (cy+blh)-y

def _chrome(d,img,ep,idx):
    sym=BASE/"assets"/"simbolo-missao100-ouro.png"
    if not sym.exists(): sym=BASE.parent/"simbolo-missao100-ouro.png"
    if sym.exists():
        s=Image.open(sym).convert("RGBA"); s.thumbnail((112,112)); img.paste(s,(W-112-MX,54),s)
    d.text((MX,60),"MISSÃO 100% APROVAÇÃO",font=_f(FB,28),fill=GOLD)
    d.text((MX,98),f"Episódio {ep['episodio']}/100  ·  faltam {ep['faltam']} dias",font=_f(FR,24),fill=MUT)
    d.text((MX,H-66),"@aprendanefro",font=_f(FB,26),fill=MUT)
    n=f"{idx:02d}/10"; d.text((W-MX-d.textlength(n,font=_f(FB,26)),H-66),n,font=_f(FB,26),fill=GOLD)

def _capa(d,img,titulo,ep):
    maxw=W-2*MX
    for size in range(86,52,-1):
        f=_f(FB,size); lines=_wrap(d,titulo,f,maxw)
        if len(lines)*int(size*1.10)<=470: break
    lh=int(size*1.10); y=(H-len(lines)*lh)//2-50
    for ln in lines: d.text((MX,y),ln,font=f,fill=WHITE); y+=lh
    d.text((MX,y+22),f"Revisão · Episódio {ep['episodio']}",font=_f(FR,32),fill=GOLD)
    d.rectangle([MX,y+92,MX+96,y+98],fill=GOLD)

def _conteudo(d,titulo,corpo,ep):
    maxw=W-2*MX
    # título
    for ts in range(46,34,-1):
        tf=_f(FB,ts); tl=_wrap(d,titulo,tf,maxw)
        if len(tl)*int(ts*1.12)<=140: break
    tlh=int(ts*1.12); ty=170
    for ln in tl: d.text((MX,ty),ln,font=tf,fill=GOLD); ty+=tlh
    ty+=12; d.rectangle([MX,ty,MX+96,ty+5],fill=GOLD); ty+=30
    # itens
    items=[s.strip() for s in corpo.split("\n") if s.strip()]
    top=ty; bot=H-104; avail=bot-top
    for size in range(34,23,-1):
        bf=_f(FR,size); lf=_f(FB,size); blh=int(size*1.30); gap=int(size*0.60)
        hs=[_item(d,MX,0,maxw,it,bf,lf,blh,draw=False) for it in items]
        total=sum(hs)+gap*(len(items)-1)
        if total<=avail: break
    slack=max(0,avail-total)
    extra=min(slack//max(1,len(items)-1), int(size*1.1)) if len(items)>1 else 0
    y=top
    for it,h in zip(items,hs):
        _item(d,MX,y,maxw,it,bf,lf,blh,draw=True); y+=h+gap+extra

def _slide(idx,titulo,corpo,ep,capa=False):
    img=Image.new("RGB",(W,H),NAVY); d=ImageDraw.Draw(img); _chrome(d,img,ep,idx)
    if capa: _capa(d,img,titulo,ep)
    else: _conteudo(d,titulo,corpo,ep)
    return img

def render(ep_num):
    out=BASE/"saida"/f"dia-{ep_num:03d}"
    data=json.load(open(out/"conteudo.json")); ep=data["_meta"]; paths=[]
    for i,sl in enumerate(data["carrossel"][:10],1):
        img=_slide(i,sl.get("titulo",""),sl.get("corpo",""),ep,capa=(i==1))
        p=out/f"slide-{i:02d}.png"; img.save(p); paths.append(str(p))
    return paths

if __name__=="__main__":
    import sys; print("\n".join(render(int(sys.argv[1]))))
