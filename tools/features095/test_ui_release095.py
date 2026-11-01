"""Release-gate failure tests with tiny local fixtures; no release build/game starts."""
from pathlib import Path
import copy,hashlib,io,json,tempfile,unittest,zipfile
from unittest.mock import patch
import ui_release095 as ui
class Contracts(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=ui.ROOT/'tmp',prefix='ui-release095-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.sources=self.root/'ui';self.saved={'uiSources':{},'audioSourceSha256':hashlib.sha256(b'audio').hexdigest()}
        script=self.root/'scripts/game/betagwent/duelAudio.ws';script.parent.mkdir(parents=True);script.write_bytes(b'audio')
        script.with_name('developmentBoardMenu.ws').write_bytes(b'menu')
        for platform,canonical in [('classic','tools/features091/BetaGwentBoard_classic093.as'),('nextgen','BetaGwent/ui/src/BetaGwentBoard.as')]:
            board=self.sources/platform/'ui/src/BetaGwentBoard.as';board.parent.mkdir(parents=True);board.write_bytes(platform.encode())
            self.saved['uiSources'][canonical]=ui.sha(board)
            for prefix,count in ui.UI_REPORTS.items():
                self.write(prefix+'-'+platform+'.json',{'checks':count,'failures':[],'actualActionScript':True,'sourceSha256':ui.sha(board),'nativeGameTested':False})
        self.write('window-audio-check.json',{'checks':97,'failures':[],'actualWitcherScript':True,'sourceSha256':self.saved['audioSourceSha256'],'audibleGameVerified':False})
        self.write('outcome-faction-check.json',{'checks':62,'failures':[],'actualActionScript':True,'actualWitcherScript':True,'nativeGameTested':False,'menuSourceSha256':ui.sha(script.with_name('developmentBoardMenu.ws')),'records':[{'source':n,'sha256':h} for n,h in self.saved['uiSources'].items()]})
        self.write(ui.CONTRACT,self.saved)
    def write(self,n,d):(self.root/n).write_text(json.dumps(d),'utf8')
    def gate(self):
        with patch.object(ui,'inputs',return_value=self.saved):return ui.reports(self.root,self.sources)
    def test_real_gate_accepts_matching_proofs(self):self.assertEqual(len(self.gate()),17)
    def test_wrong_reward_faction_source_rejected(self):
        d=ui.read(self.root/'outcome-faction-check.json');d['menuSourceSha256']='0'*64;self.write('outcome-faction-check.json',d)
        with self.assertRaises(AssertionError):self.gate()
    def test_old_pad_count_rejected(self):
        p='pad-legend-classic.json';d=ui.read(self.root/p);d['checks']=22;self.write(p,d)
        with self.assertRaises(AssertionError):self.gate()
    def test_wrong_board_rejected(self):
        p='windows-nextgen.json';d=ui.read(self.root/p);d['sourceSha256']='0'*64;self.write(p,d)
        with self.assertRaises(AssertionError):self.gate()
    def test_failed_report_rejected(self):
        p='battle-cleanup-classic.json';d=ui.read(self.root/p);d['failures']=['service text returned'];self.write(p,d)
        with self.assertRaises(AssertionError):self.gate()
    def test_missing_report_rejected(self):
        (self.root/'preview-keywords-nextgen.json').unlink()
        with self.assertRaises(FileNotFoundError):self.gate()
    def test_changed_prepared_audio_rejected(self):
        (self.root/'scripts/game/betagwent/duelAudio.ws').write_bytes(b'old sound map')
        with self.assertRaises(AssertionError):self.gate()
    def test_changed_inputs_rejected(self):
        newer=copy.deepcopy(self.saved);newer['audioSourceSha256']='1'*64
        with patch.object(ui,'inputs',return_value=newer):
            with self.assertRaises(AssertionError):ui.validate_frozen(self.root)
    def test_packaged_cache_is_verified_for_both_platforms(self):
        for platform,mod in [('classic','modBetaGwentClassic132'),('nextgen','modBetaGwent0924')]:
            data=io.BytesIO()
            with zipfile.ZipFile(data,'w')as z:z.writestr('Mods/'+mod+'/content/soundspc.cache',b'correct cache')
            expected={'audio':{platform:{'cacheSha256':hashlib.sha256(b'correct cache').hexdigest()}}}
            data.seek(0)
            with zipfile.ZipFile(data)as z:
                ui.verify_archive_audio(z,platform,mod,expected)
                expected['audio'][platform]['cacheSha256']='0'*64
                with self.assertRaises(AssertionError):ui.verify_archive_audio(z,platform,mod,expected)
    def test_freeze_does_not_overwrite_completed_inputs(self):
        newer={'changed':True}
        with patch.object(ui,'inputs',return_value=newer):
            with self.assertRaises(AssertionError):ui.freeze(self.root)
        self.assertEqual(ui.read(self.root/ui.CONTRACT),self.saved)
if __name__=='__main__':unittest.main()
