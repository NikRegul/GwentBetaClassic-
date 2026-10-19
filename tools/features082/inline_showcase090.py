"""Adapt the offline publication proof for the conversation's inline viewer."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'docs/releases/0.9.0/nexus/preview.html'
DEST = Path('C:/Users/NikR/.codex/visualizations/2026/10/18/01a14ffb-0a16-7c13-9668-8978c60fa5c1/gwent-description.html')
source = SOURCE.read_text('utf8')
css = re.search(r'<style>(.*?)</style>', source, re.S)[1]
body = re.search(r'<body>(.*?)<script>', source, re.S)[1]
banner = re.search(r'const BANNER=(.*?);const select=', source, re.S)[1]
# CSS scoping preserves the existing design without affecting host controls.
css = css.replace(':root', ':scope').replace('html', ':scope')
css = re.sub(r'\bbody\b', '.gwent-surface', css)
css = re.sub(r'--(paper|muted|gold|line|panel|tint|accent)\b', r'--gwent-\1', css)
css = css.replace('position:sticky;top:0;', 'position:relative;')
css += '\n:scope{display:block;max-width:100%;overflow-wrap:anywhere}.gwent-surface{padding-top:6px}header{z-index:1}.nav{padding-right:110px}@media(max-width:560px){.nav{padding-right:18px;padding-top:45px}}\n'
script = r'''
(() => {
  const root = document.getElementById('gwent-showcase');
  const select = root.querySelector('select');
  const articles = [...root.querySelectorAll('[data-lang]')];
  const valid = new Set(articles.map(el => el.dataset.lang));
  const banner = BANNER_VALUE;
  root.querySelectorAll('[data-banner]').forEach(img => { img.src = banner; });
  function choose(language) {
    const lang = valid.has(language) ? language : 'ru';
    articles.forEach(article => { article.hidden = article.dataset.lang !== lang; });
    root.setAttribute('lang', articles.find(article => article.dataset.lang === lang).getAttribute('lang'));
    select.value = lang;
  }
  choose(window.openai?.widgetState?.modelContent?.language);
  select.addEventListener('change', () => {
    choose(select.value);
    window.openai?.setWidgetState?.({modelContent:{language:select.value},privateContent:null})?.catch(() => {});
  });
  window.addEventListener('openai:set_globals', event => {
    const state = event.detail?.globals?.widgetState;
    if (state?.modelContent?.language) choose(state.modelContent.language);
  });
  root.querySelectorAll('.button').forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault();
      root.querySelector(link.getAttribute('href')).scrollIntoView({block:'start'});
    });
  });
})();
'''.replace('BANNER_VALUE', banner)
result = '<div id="gwent-showcase" lang="ru">\n<style>\n@scope (#gwent-showcase) {\n' + css + '\n}\n</style>\n<div class="gwent-surface">\n' + body + '\n</div>\n</div>\n<script>\n' + script + '\n</script>\n'
assert len(result.encode('utf8')) < 1_000_000
assert not re.search(r'<(?:html|head|body)\b|<!doctype', result, re.I)
assert 'fetch(' not in result and 'XMLHttpRequest' not in result
DEST.write_text(result, encoding='utf8')
readback = DEST.read_text('utf8')
assert '<div id="gwent-showcase" lang="ru">\n<style>' in readback
print(DEST)
print(len(readback.encode('utf8')))
