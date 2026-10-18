# Gwent Beta Classic 0.8.2 — Português (Brasil)

> Versão 0.8.2 — pacotes separados para Classic 1.32 e Next-Gen 5.0+.

## Importante

Faça backup dos seus saves antes de instalar e antes de cada atualização. O mod está em desenvolvimento ativo, então use um save separado nas primeiras partidas.

Os textos das cartas vêm da localização oficial da beta. A interface foi traduzida com auxílio de IA e pode conter erros. As mensagens de troca de decks estão nos 13 idiomas; algumas dicas antigas ainda usam o inglês como alternativa. Sugestões de tradução são bem-vindas.

## Sobre o mod

Gwent Beta Classic substitui o Gwent de The Witcher 3 pelas cartas, regras e tabuleiro do Gwent Beta 0.9.24 independente. As partidas continuam fazendo parte do mundo de The Witcher: jogue contra NPCs, conclua missões, compre barris e monte seus próprios baralhos.

## Recursos

- 479 cartas colecionáveis, incluindo 21 líderes, das cinco facções
- Tabuleiro, interface, fontes, molduras de cartas, clima e efeitos do beta; líderes animados
- Editor de baralhos: cinco baralhos iniciais editáveis e oito espaços próprios, filtros e busca
- Oponentes com 46 arquétipos de baralho do beta e três níveis de dificuldade da IA
- Barris por 200 coroas com todos os taverneiros, abertos como no beta
- Fragmentos: crie cartas por 30 / 80 / 200 / 800 conforme a raridade; cópias excedentes são moídas automaticamente
- Tutorial, mulligan, visualização dos cemitérios e do baralho, detalhes completos das cartas
- Mouse, teclado e controle

## Novidades da 0.8.2

- Importação e exportação de decks por códigos BG1 na área de transferência, com lista de cartas ausentes e ação separada para criá-las.
- Comandos de console para recursos, busca de cartas, coleções de facção e estoque de barris dos estalajadeiros.
- Cartas enviadas ao cemitério voam para o cemitério correto; cartas especiais fazem o mesmo após a resolução. Os efeitos de banimento e dissolução foram mantidos.
- Definições integradas de itens antigos do Redux ajudam a evitar a perda de inventário ou do corpo ao carregar um save após a troca de mod. Não recuperam dados já perdidos e salvos.
- Espaçamento de menus, estado do deck e botões reorganizados; o controle permite passar das cartas visíveis para Salvar e voltar às cartas.
- Os retratos dos líderes continuam animados após a entrada na tela VS. A entrada da rainha das aracnas começa junto com sua fala. Classic 1.32 inclui correções da geada e dos efeitos de ataque.

## Compartilhamento de decks

Exportar no editor copia o código BG1 para compartilhar como texto. Importar está disponível na lista de decks e no editor. Cole o código completo; um código inválido não altera nada. Se o acesso direto à área de transferência não funcionar, use Ctrl+C/Ctrl+V no campo de texto. BG1 é o formato deste mod e independe do idioma da interface.

As cartas ausentes, incluindo o líder, aparecem com o custo total em fragmentos. Criá-las exige confirmação separada e fragmentos suficientes. A importação monta um rascunho: salve o deck depois. Pela lista, um espaço personalizado livre é usado sem sobrescrever os ocupados. O treino usa a coleção ilimitada existente.

## Comandos de console

bg_help() mostra a ajuda e bg_status() a coleção, os barris e os fragmentos. bg_find('Imlerith') busca nomes e IDs; bg_card(132102,1) concede uma carta, bg_faction('monsters') uma facção. bg_leaders() / bg_allcards() completam líderes ou coleção até os limites normais. bg_kegs(10) e bg_scraps(1000) adicionam recursos. É preciso ter um save carregado e estar fora dos menus e partidas; depois salve o jogo normalmente. Na loja aberta de um estalajadeiro, bg_shopcheck() verifica os barris e bg_shoprefill(5) completa o estoque até cinco, sem adicionar cinco a cada chamada. O console do jogo deve estar ativado previamente.

```text
bg_help()
bg_status()
bg_find('Imlerith')
bg_card(132102,1)
bg_faction('monsters')
bg_leaders()
bg_allcards()
bg_kegs(10)
bg_scraps(1000)
bg_shopcheck()
bg_shoprefill(5)
```

## Idiomas

Texto: inglês, russo, alemão, francês, italiano, polonês, espanhol (Espanha), espanhol (América Latina), português (Brasil), japonês, coreano, chinês simplificado e chinês tradicional. Troque a qualquer momento pelo botão de idioma do texto no canto superior esquerdo dos menus de baralhos e coleção, ou nas configurações de batalha; a escolha fica salva.

Cada pacote inclui vozes RU, EN, DE, IT e PT-BR. Texto e vozes são escolhidos separadamente por dois botões lado a lado no menu de baralhos/coleção do mod ou nas configurações da partida. Trocar as vozes não exige reinstalar arquivos. Automático segue separadamente os idiomas atuais de texto e fala do jogo; se um idioma não estiver disponível, usa inglês. Salve normalmente depois da escolha: as preferências pertencem a esse save e permanecem ao atualizar os arquivos do mod. A seleção manual anterior do texto é mantida. Algumas falas do troll dos barris em DE/IT continuam usando a substituição russa das gravações originais. Os nomes nativos dos itens seguem o idioma do jogo; algumas notificações externas continuam em RU/EN.

## Instalação

1. Feche o jogo e faça backup dos saves. Baixe o pacote para 1.32 ou Next-Gen (5.0+). Instale apenas uma versão de Beta Gwent.

2. Ao atualizar, primeiro mova a pasta antiga do mod Beta Gwent para fora de Mods. Não apague toda a pasta Mods nem misture arquivos de versões diferentes.

3. Copie Mods do arquivo para a pasta do jogo, ao lado de bin e content. Para Classic 1.32, copie também a pasta DLC incluída. Caminhos: Mods/modBetaGwentClassic132/content e DLC/dlcBetaGwentClassic132Assets para 1.32; Mods/modBetaGwent0924/content para Next-Gen. Substitua apenas as pastas anteriores deste mod, mantendo os outros mods e DLC.

4. Carregue seu save. O menu normal de baralhos de Gwent abre o editor e os idiomas; converse com um NPC que joga para iniciar uma partida. Salve normalmente para manter suas preferências.

## Requisitos

The Witcher 3 para PC. Escolha a versão separada para Classic 1.32 ou Next-Gen (pacote identificado como 5.0+). REDkit, Wwise e instalador EXE não são necessários para jogar.

## Compatibilidade

As definições dos itens antigos do Redux estão integradas para carregar saves; remova a pasta obsoleta modBetaGwentReduxCompat. Ao migrar do Redux, use uma cópia do save anterior à perda do inventário ou do corpo: dados perdidos não são recuperados. As cartas Redux não são convertidas para a coleção Beta, e não há garantia de compatibilidade com todas as funções do Redux/Redo Expansion. Outras reformulações de Gwent e alterações em menus, comércio ou recompensas podem causar conflitos. Após mudar os mods, refaça as mesclagens dos scripts conflitantes no Script Merger.

## Relatar bugs

Encontrou um problema? Informe as versões do mod e do jogo, os idiomas escolhidos para texto e vozes (inclusive Automático), se é Novo Jogo +, outros mods, cartas/líderes e os passos para reproduzir. Uma captura e um save anterior ao problema ajudam. Para traduções, indique idioma, tela e uma sugestão de texto melhor.

### Como ativar o log

1. Adicione -debugscripts depois das aspas finais no destino de um atalho para witcher3.exe. Steam: Propriedades → Geral → Opções de inicialização. No GOG, use um atalho direto para witcher3.exe.

2. Inicie o jogo, reproduza o problema e feche-o. Copie scriptslog.txt imediatamente: a próxima inicialização substitui o arquivo. Se houver apenas um cabeçalho, avise; pode ser necessária uma configuração adicional.

3. Se o Windows criou um dump da falha, anexe também o último .dmp correspondente.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Agradecimentos

Obrigado à CD Projekt por The Witcher e Gwent, ao LegacyGwent DIY pelos recursos de cartas e tabuleiro, à comunidade do Beta Gwent por preservar o material histórico e as ideias de arquétipos, e a todos que testam o mod e enviam relatórios detalhados.

Projeto de fã não oficial. O código original do mod é distribuído sob GPL-3.0-only; os recursos originais do jogo pertencem aos seus donos.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)
