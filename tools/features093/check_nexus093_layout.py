"""Render local publication preview in isolated headless Chrome, no publishing."""
from pathlib import Path
import argparse, html, json, os, re, subprocess

ROOT=Path(__file__).resolve().parents[2]

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('preview',type=Path);parser.add_argument('out',type=Path);a=parser.parse_args()
    out=a.out.resolve();assert out.is_relative_to(ROOT/'BetaGwent/build') and not out.exists();out.mkdir(parents=True)
    chrome=Path('C:/Program Files/Google/Chrome/Application/chrome.exe');assert chrome.is_file()
    probe='''<script>addEventListener('load',async()=>{await document.fonts.ready;const result=[];for(const a of articles){choose(a.dataset.lang);for(const d of a.querySelectorAll('details'))d.open=true;result.push({language:a.dataset.lang,width:innerWidth,scroll:document.documentElement.scrollWidth,details:a.querySelectorAll('details').length,version:a.querySelector('.eyebrow').textContent,commands:a.textContent.includes('bg_clean_confirm'),bugLog:a.textContent.includes('scriptslog.txt')});for(const d of a.querySelectorAll('details'))d.open=false;}choose('ru');parent.postMessage({kind:'nexus-qa',result},'*');});</script>'''
    child=a.preview.read_text('utf8').replace('</body>',probe+'</body>');reports=[]
    for label,width,height in [('desktop',1440,1100),('mobile',390,1000)]:
        # Desktop Chrome enforces a minimum browser innerWidth near500 even
        # when its screenshot is390px. An explicit same-document frame gives
        # the page a real390px viewport; asserting that size prevents false QA.
        file=out/(label+'-probe.html')
        wrapper='<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0;overflow:hidden"><script>addEventListener("message",e=>{if(e.data.kind!=="nexus-qa")return;const p=document.createElement("pre");p.id="qa-result";p.style.display="none";p.textContent=JSON.stringify(e.data.result);document.body.append(p);});</script><iframe style="border:0;display:block" width="'+str(width)+'" height="'+str(height)+'" srcdoc="'+html.escape(child,quote=True)+'"></iframe></body></html>'
        file.write_text(wrapper,'utf8')
        cmd=[str(chrome),'--headless','--disable-gpu','--no-first-run','--no-default-browser-check','--disable-extensions','--hide-scrollbars','--force-device-scale-factor=1',f'--user-data-dir={out/(label+"-profile")}',f'--window-size={width},{height}','--virtual-time-budget=1500',f'--screenshot={out/(label+".png")}','--dump-dom',file.as_uri()]
        r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=50,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        (out/(label+'-browser.log')).write_text(r.stderr[-4000:],'utf8');assert r.returncode==0,r.stderr[-1000:]
        match=re.search(r'<pre id="qa-result"[^>]*>(.*?)</pre>',r.stdout,re.S);assert match,'DOM probe did not finish'
        result=json.loads(html.unescape(match[1]));assert len(result)==13 and len({x['language'] for x in result})==13
        for x in result:assert x['width']==width and x['scroll']<=x['width'] and x['details']==3 and x['commands'] and x['bugLog'] and '0.9.3' in x['version'],x
        assert (out/(label+'.png')).is_file();reports.append(dict(layout=label,records=result))
    (out/'report.json').write_text(json.dumps(dict(complete=True,layouts=reports,retailOrNexusRenderingVerified=False),ensure_ascii=False,indent=2)+'\n','utf8');print('PASS13languages at desktop/mobile widths; no horizontal overflow; all operational sections present')

if __name__=='__main__':main()
