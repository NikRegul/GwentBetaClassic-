package {
    [SWF(width="1920", height="1080", frameRate="60", backgroundColor="#080909")]
    // Stage 109: keg-opening menu (guiconfig BetaGwentKeg -> betagwent\betagwent_kegop.menu).
    // Same board code; build_board.py embeds only card, interface, HUD and keg pages.
    public class BetaGwentKegMenu extends BetaGwentBoard {
        override protected function registrationName():String { return "BetaGwentKeg"; }
    }
}
