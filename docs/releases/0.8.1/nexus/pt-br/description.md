# Gwent Beta Classic 0.8.1 — Português (Brasil)

> A versão 0.8.1 para Next-Gen 5.0+ foi testada no jogo. Classic 1.32 está sendo corrigida e testada separadamente; o arquivo atual é uma versão de teste.

## Importante

Faça backup dos seus saves antes de instalar e antes de cada atualização. O mod está em desenvolvimento ativo, então use um save separado nas primeiras partidas.

As traduções continuam em prévia: os textos das cartas vêm da localização oficial do beta e a interface foi traduzida com IA, podendo conter erros. As novas dicas adicionadas desde a 0.6.6 existem por enquanto só em inglês e russo; nos demais idiomas aparecem em inglês. Avise sobre tudo o que soar errado.

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

## Mudanças desde a 0.7.3a

- Cada pacote inclui as cinco dublagens e os 13 idiomas de texto. Não é mais preciso baixar um pacote diferente para cada voz.
- Dois botões lado a lado, Texto e Vozes, no menu do mod, com seleção automática ou manual independente.
- Detecção separada dos idiomas de texto e fala do jogo. Idiomas não disponíveis usam inglês.
- As preferências ficam no save. A escolha manual anterior do texto é mantida ao atualizar.
- Corrigidas as definições de barris e a recuperação do estoque no Novo Jogo +. Uma entrega que falhou não é mais marcada como concluída; barris vendidos não voltam toda vez que a loja abre.
- Revisados os três projéteis de Jotunn, Kambi/Hemdall, Ragh Nar Roog, Golden Froth, status, contadores e efeitos de armadura.
- Recursos da interface reorganizados dentro do orçamento de compilação de 63 MiB sem reduzir a resolução das texturas. Carregamento dos menus e estabilidade continuam na validação.

## Idiomas

Texto: inglês, russo, alemão, francês, italiano, polonês, espanhol (Espanha), espanhol (América Latina), português (Brasil), japonês, coreano, chinês simplificado e chinês tradicional. Troque a qualquer momento pelo botão de idioma do texto no canto superior esquerdo dos menus de baralhos e coleção, ou nas configurações de batalha; a escolha fica salva.

Cada pacote inclui vozes RU, EN, DE, IT e PT-BR. Texto e vozes são escolhidos separadamente por dois botões lado a lado no menu de baralhos/coleção do mod ou nas configurações da partida. Trocar as vozes não exige reinstalar arquivos. Automático segue separadamente os idiomas atuais de texto e fala do jogo; se um idioma não estiver disponível, usa inglês. Salve normalmente depois da escolha: as preferências pertencem a esse save e permanecem ao atualizar os arquivos do mod. A seleção manual anterior do texto é mantida. Algumas falas do troll dos barris em DE/IT continuam usando a substituição russa das gravações originais. Os nomes nativos dos itens seguem o idioma do jogo; algumas notificações externas continuam em RU/EN.

## Instalação

1. Feche o jogo e faça backup dos saves. Baixe o pacote para 1.32 ou Next-Gen (5.0+). Instale apenas uma versão de Beta Gwent.

2. Ao atualizar, primeiro mova a pasta antiga do mod Beta Gwent para fora de Mods. Não apague toda a pasta Mods nem misture arquivos de versões diferentes.

3. Copie Mods do arquivo para a pasta do jogo, ao lado de bin e content. Caminho final: Mods/modBetaGwentClassic132/content para 1.32 ou Mods/modBetaGwent0924/content para Next-Gen.

4. Carregue seu save. O menu normal de baralhos de Gwent abre o editor e os idiomas; converse com um NPC que joga para iniciar uma partida. Salve normalmente para manter suas preferências.

## Requisitos

The Witcher 3 para PC. Escolha a versão separada para Classic 1.32 ou Next-Gen (pacote identificado como 5.0+). REDkit, Wwise e instalador EXE não são necessários para jogar.

## Compatibilidade

Remova a pasta antiga modBetaGwentReduxCompat: a camada de compatibilidade separada não é mais incluída. A compatibilidade com Redux/Redo Expansion não foi confirmada separadamente. Outras reformulações do Gwent e mods que alterem seus menus, trocas de cartas ou recompensas podem causar conflitos. Depois de mudar os mods instalados, refaça a mesclagem dos scripts com Script Merger.

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
