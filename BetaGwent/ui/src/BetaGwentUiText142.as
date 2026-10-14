package {
    // RU/EN preview hints. Other text languages use explicit English fallback
    // for these additions while retaining their existing translated dictionary.
    public class BetaGwentUiText142 {
        private static const EN:Object={
            "←→ рука · ": "Left/Right: hand · ",
            " сыграть · ": " play · ",
            " отменить · ": " cancel · ",
            "Яркость: ": "Brightness: ",
            "Темп меняет скорость. Яркость меняет только эффекты.\nВспышки, тряска и сцены настраиваются отдельно.\nНастройки эффектов действуют до закрытия меню игры.": "Tempo changes speed. Brightness changes effects only.\nFlashes, shake and scenes have separate settings.\nEffect settings last until this game menu closes.",
            "Одновременное усиление: ": "Simultaneous boosts: ",
            "Усиление после поглощения": "Boost after consuming",
            "Справочные надписи: вкл": "Board help: on",
            "Справочные надписи: выкл": "Board help: off",
            "A / × — пропустить вступление": "A / Cross: skip introduction",
            "Дождитесь окончания анимации или пропустите её": "Wait for the animation or skip it",
            "Ожидается обновление поля": "Waiting for the board to update",
            "Вы уже спасовали": "You have already passed",
            "Сейчас ход соперника": "It is the opponent's turn",
            "Эта карта не входит в допустимые цели способности": "This card is not a legal target for the ability",
            "Выберите отряд на поле": "Choose a unit on the board",
            "Нужен союзный отряд": "An allied unit is required",
            "Нужен вражеский отряд": "An enemy unit is required",
            "Этот тип карты не подходит": "This card type is not eligible",
            "Редкость карты не подходит для способности": "This card rarity is not eligible for the ability",
            "Защита или статус карты запрещает эту цель": "This card's protection or status prevents targeting",
            "Сила цели выше допустимой: ": "Target strength exceeds the limit: ",
            "Выбранная цель": "Selected target",
            " · сила ": " · strength ",
            " · броня ": " · armour ",
            "Нажмите, чтобы подтвердить цель": "Click to confirm the target",
            "МЕНЮ БОЯ": "MATCH MENU",
            "Действия": "Actions",
            "Эффекты": "Effects",
            "Звук и игра": "Audio and game",
            "Управление": "Controls",
            "Лидеры: динамические": "Leaders: animated",
            "Лидеры: статические": "Leaders: static",
            "Вступления: ": "Introductions: ",
            "Подписи цепочек: вкл": "Chain labels: on",
            "Подписи цепочек: выкл": "Chain labels: off",
            "Вернуться в бой": "Return to match",
            "LB/RB — вкладки. Настройки можно менять во время анимации.": "LB/RB: tabs. Settings remain available during animations.",
            "Портреты на поле, справа и во вступлении. Выбор сохраняется с игрой": "Board, side preview and introduction portraits. Saved with the game.",
            "Способность лидера уже использована": "Leader ability has already been used",
            "Лидер доступен в свой ход без незавершённого выбора": "Leader is available on your turn after pending choices are resolved",
            "Просмотр доступен после завершения текущего действия": "Inspection is available after the current action ends",
            "Сейчас нет проигрываемой анимации": "No animation is currently playing",
            "Откроется подтверждение выхода": "Opens the exit confirmation",
            "Звуковой банк ещё не загружен": "The sound bank has not loaded yet",
            "Голоса карт и лидеров": "Card and leader voices",
            "Сортировка доступна после окончания анимации": "Sorting is available after the animation ends",
            "Порядок добора не имеет обратной сортировки": "Draw order cannot be reversed",
            "В бою с NPC смена колоды недоступна": "Deck selection is unavailable during an NPC match",
            "Завершите текущее действие": "Finish the current action",
            "Удерживайте ПКМ · ускорить": "Hold RMB to speed up",
            "Ускорить · ПКМ в любом месте": "Speed up: RMB anywhere",
            "↑↓←→ пункт · ": "↑↓←→ item · ",
            " изменить / открыть · LB/RB вкладки · ": " change / open · LB/RB tabs · ",
            " / Start закрыть": " / Start close",
            " ускорить · ": " speed up · ",
            " пропустить · Start настройки": " skip · Start settings",
            "Крестовина / левый стик — выбор карты, цели или пункта\nA / × — подтвердить · B / ○ — назад\nX / □ — подробности карты · удерживать Y / △ — пас\nStart — меню боя · LB/RB — вкладки, ряды или страницы\nL3 / ↑ из руки — посмотреть поле · B / ○ — вернуться\nLT — свой сброс · RT — колода · оба курка — сброс соперника\nПравый стик — прокрутить описание · R3 — способность лидера": "D-pad / left stick: choose a card, target or menu item\nA / ×: confirm · B / ○: back\nX / □: card details · hold Y / △: pass\nStart: match menu · LB/RB: tabs, rows or pages\nL3 / Up from hand: inspect board · B / ○: return\nLT: your graveyard · RT: deck · both: opponent graveyard\nRight stick: scroll description · R3: leader ability"
        };
        public static function extend(value:int,data:Object):Object {
            if(value==1)return data;
            for(var key:String in EN){data[key]=EN[key];data[key.toUpperCase()]=String(EN[key]).toUpperCase();}
            return data;
        }
    }
}
