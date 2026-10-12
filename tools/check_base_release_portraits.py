"""Exercise the actual packaging functions without starting REDkit or a build."""
import ast
from pathlib import Path
import shutil
import tempfile

root=Path(__file__).resolve().parents[1]
source=root/'tools/build_language_release.py'
tree=ast.parse(source.read_text('utf8'))
names={'copy_release_tree','check_no_premium_portraits'}
functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names]
assert len(functions)==len(names)
scope={'shutil':shutil}
exec(compile(ast.Module(body=functions,type_ignores=[]),str(source),'exec'),scope)
temporary_root=(root/'BetaGwent/build').resolve()
temporary_root.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='base-release-portraits-',dir=temporary_root) as temporary:
    base=Path(temporary)
    assert base.resolve().is_relative_to(temporary_root)
    original=base/'source'
    premium=original/'gameplay/gui_new/swf/betagwentpremium'
    premium.mkdir(parents=True)
    (premium/'portrait.redswf').write_bytes(b'optional animation')
    ordinary=original/'gameplay/gui_new/swf/static.redswf'
    ordinary.write_bytes(b'base resource')
    target=base/'release'
    scope['copy_release_tree'](original,target)
    assert (target/ordinary.relative_to(original)).read_bytes()==b'base resource'
    assert not (target/premium.relative_to(original)).exists()
    scope['check_no_premium_portraits'](target)
    # An old frozen/partial stage must fail, even if the folder has different casing.
    stale=target/'gameplay/gui_new/swf/BetaGwentPremium'
    stale.mkdir()
    (stale/'portrait.redswf').write_bytes(b'cached animation')
    try:
        scope['check_no_premium_portraits'](target)
    except RuntimeError as error:
        assert 'clean staging directory' in str(error)
    else:
        raise AssertionError('Stale premium staging was accepted')
print('PASS: base resource retained; premium excluded; clean stage accepted; stale premium stage rejected')
