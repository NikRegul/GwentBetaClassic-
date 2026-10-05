"""Prepare isolated local HD preview build runners; does not publish."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for name in ('build_presentation','package_presentation'):
 source=(ROOT/'tools'/(name+'92.py')).read_text('utf8')
 for old,new in [('stage92','stage93'),('release92','release93'),('stage=92','stage=93'),("'92'","'93'"),('0.2.1-preview.2','0.2.1-preview.3')]:source=source.replace(old,new)
 if name=='build_presentation':source=source.replace('install_native_atlas.py','install_native_hd93.py')
 (ROOT/'tools'/(name+'93.py')).write_text(source,'utf8')
print('Local stage93 build/package runners prepared. No publishing operations.')
