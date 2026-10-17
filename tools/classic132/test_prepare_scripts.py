"""Focused tests for method lowering and the Classic lifecycle adaptation."""
import re
import unittest

from prepare_scripts import adapt, extract_annotations, lower_wrapper, mask, member_span


class LoweringTests(unittest.TestCase):
    def test_nested_wrappers_preserve_order_and_original_return(self):
        original = 'class Test {\n public function Value(x : int) : int { return x + 1; }\n}'
        one = dict(target='Test', member='Value', text='function Value(x : int) : int { return wrappedMethod(x) * 2; }')
        two = dict(target='Test', member='Value', text='function Value(x : int) : int { return wrappedMethod(x) + 3; }')
        lowered = lower_wrapper(lower_wrapper(original, one, 1), two, 2)
        self.assertNotIn('wrappedMethod', mask(lowered))
        self.assertIn('return BetaGwentClassicOriginal_Value_2(x) + 3;', lowered)
        self.assertIn('return BetaGwentClassicOriginal_Value_1(x) * 2;', lowered)
        self.assertIn('private function BetaGwentClassicOriginal_Value_1(x : int) : int { return x + 1; }', lowered)
        # Execute the small arithmetic bodies to catch accidental chain reversal,
        # duplicate base calls and lost return values without a game compiler.
        calls = []
        def run(name, value):
            _, body, end, _ = member_span(lowered, 'Test', name)
            expression = re.search(r'\breturn\s+(.+?);', lowered[body:end])[1]
            calls.append(name)
            expression = re.sub(r'(BetaGwentClassicOriginal_\w+)\(x\)', lambda m: str(run(m[1], value)), expression)
            return eval(expression, {'__builtins__': {}}, {'x': value})
        self.assertEqual(run('Value', 4), 13)
        self.assertEqual(calls, ['Value', 'BetaGwentClassicOriginal_Value_2', 'BetaGwentClassicOriginal_Value_1'])

    def test_event_stays_event_and_helper_stays_callable(self):
        original = 'class Test {\n event OnSpawned(data : SData) { super.OnSpawned(data); }\n}'
        item = dict(target='Test', member='OnSpawned', text='function OnSpawned(data : SData) { wrappedMethod(data); Log(); }')
        lowered = lower_wrapper(original, item, 1)
        self.assertIn('event OnSpawned(data : SData)', lowered)
        self.assertIn('private function BetaGwentClassicOriginal_OnSpawned_1', lowered)
        self.assertIn('super.OnSpawned(data);', lowered)

    def test_event_passthrough_does_not_return_void(self):
        original = 'class Test {\n event OnBuyItem(item : int) { Buy(item); }\n}'
        item = dict(target='Test', member='OnBuyItem', text='function OnBuyItem(item : int) { if(item!=1)return wrappedMethod(item); return true; }')
        lowered = lower_wrapper(original, item, 1)
        self.assertIn('if(item!=1){ BetaGwentClassicOriginal_OnBuyItem_1(item); return false; }', lowered)
        self.assertIn('return true;', lowered)

    def test_wrapper_does_not_rewrite_literals(self):
        original = 'class Test {\n function Value() { }\n}'
        item = dict(target='Test', member='Value', text='function Value() { Log("wrappedMethod"); /* wrappedMethod */ wrappedMethod(); }')
        lowered = lower_wrapper(original, item, 1)
        self.assertIn('Log("wrappedMethod")', lowered)
        self.assertIn('/* wrappedMethod */', lowered)
        self.assertIn('BetaGwentClassicOriginal_Value_1();', lowered)

    def test_parameter_or_return_mismatch_fails(self):
        original = 'class Test {\n function Value(x : int) : int { return x; }\n}'
        for declaration in ('function Value(x : string) : int { return 1; }',
                            'function Value(x : int) : bool { return true; }'):
            with self.assertRaises(ValueError):
                lower_wrapper(original, dict(target='Test', member='Value', text=declaration), 1)

    def test_lexer_keeps_strings_comments_and_following_globals(self):
        source = '// @addMethod(Fake)\n@addMethod(Test)\nfunction Added() { Log("} @bad(Test)"); /* } */ }\nfunction Global() { }'
        remaining, items = extract_annotations(source, 'fixture.ws')
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['member'], 'Added')
        self.assertIn('Log("} @bad(Test)")', items[0]['text'])
        self.assertIn('function Global()', remaining)

    def test_unknown_annotation_fails(self):
        with self.assertRaises(ValueError):
            extract_annotations('@replaceMethod(Test)\nfunction Missing() {}', 'fixture.ws')

    def test_closing_callback_precedes_test_flag_reset_and_is_guarded(self):
        source = ('class CR4BetaGwentBoardMenu extends CR4Menu\n{\n'
                  'event OnClosingMenu() {\n'
                  'thePlayer.SetGwintMinigameState(EMS_End_PlayerLost | EMS_End_PlayerForfeited);\n'
                  '        setControllerInput.InvokeSelfFourArgs(FlashArgInt(value),FlashArgInt(0),FlashArgString(title),FlashArgBool(true));\n'
                  '        setControllerInput.InvokeSelfFourArgs(FlashArgInt(value),FlashArgInt(purpose),FlashArgString(title),FlashArgBool(true));return true;\n'
                  '            manager.testMatch=false;manager.SetForcedFaction(GwintFaction_Neutral);\n}\n}')
        source += '\n    public function FinishControllerText(value : int, purpose : int, title : string) {}'
        lowered = adapt('developmentBoardMenu.ws', source)
        self.assertLess(lowered.index('if(!classicEndNotified)'), lowered.index('manager.testMatch=false'))
        self.assertIn('classicEndNotified=true;', lowered)
        self.assertEqual(lowered.count('.BetaGwentClassicGameEnded()'), 1)

    def test_classic_keyboard_has_no_nextgen_native_dependency(self):
        lowered = adapt('deckNameInput.ws', '')
        self.assertNotIn('SVirtualKeyboardConfig', lowered)
        self.assertNotIn('OpenVirtualKeyboard', lowered)
        self.assertIn('menu.BeginClassicTextInput(value,inputPurpose,title)', lowered)


if __name__ == '__main__':
    unittest.main()
