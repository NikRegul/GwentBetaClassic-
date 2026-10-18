# Gwent Beta Classic 0.8.2 — Italiano

> Versione 0.8.2 — pacchetti separati per Classic 1.32 e Next-Gen 5.0+.

## Importante

Esegui un backup dei salvataggi prima dell'installazione e prima di ogni aggiornamento. La mod è in sviluppo attivo: per le prime partite usa un salvataggio separato.

I testi delle carte provengono dalla localizzazione ufficiale della beta. L’interfaccia è stata tradotta con l’aiuto dell’IA e può contenere imprecisioni. I messaggi di scambio dei mazzi sono disponibili in tutte le 13 lingue; alcuni suggerimenti precedenti usano ancora l’inglese come alternativa. I suggerimenti di traduzione sono benvenuti.

## La mod

Gwent Beta Classic sostituisce il Gwent di The Witcher 3 con le carte, le regole e il tabellone di Gwent Beta 0.9.24 standalone. Le partite restano parte del mondo di The Witcher: sfida i PNG, completa missioni, compra barili e costruisci i tuoi mazzi.

## Caratteristiche

- 479 carte collezionabili, tra cui 21 comandanti, per tutte e cinque le fazioni
- Tabellone, interfaccia, caratteri, cornici delle carte, clima ed effetti della beta; comandanti animati
- Editor dei mazzi: cinque mazzi iniziali modificabili e otto slot personali, filtri e ricerca
- Avversari con 46 archetipi di mazzi della beta e tre livelli di difficoltà dell'IA
- Barili da 200 corone da tutti i locandieri, aperti come nella beta
- Frammenti: crea carte per 30 / 80 / 200 / 800 in base alla rarità; le copie in eccesso vengono macinate automaticamente
- Tutorial, mulligan, visualizzazione dei cimiteri e del mazzo, scheda dettagliata delle carte
- Mouse, tastiera e controller

## Novità della 0.8.2

- Importazione ed esportazione dei mazzi tramite codici BG1 negli appunti, con elenco delle carte mancanti e creazione su richiesta.
- Comandi della console per risorse, ricerca delle carte, collezioni di fazione e scorte di barili degli osti.
- Le carte destinate al cimitero volano verso il cimitero corretto; lo stesso vale per le carte speciali dopo la risoluzione. Restano gli effetti di esilio e dissoluzione.
- Definizioni integrate dei vecchi oggetti Redux aiutano a evitare la perdita di inventario e corpo caricando salvataggi dopo il passaggio. Non recuperano dati già persi e salvati.
- Spaziature dei menu, stato del mazzo e pulsanti rivisti; con il controller si passa dalle carte visibili a Salva e si torna alle carte.
- I ritratti dei leader continuano ad animarsi dopo l’ingresso nella schermata VS. L’ingresso della regina delle aracne comincia insieme alla sua battuta. Classic 1.32 include le correzioni del gelo e degli effetti d’attacco.

## Condividere i mazzi

Nell’editor, Esporta copia il codice BG1 da condividere come testo. Importa è disponibile nell’elenco dei mazzi e nell’editor. Incolla il codice completo: se non è valido, non cambia nulla. Se l’accesso diretto agli appunti non funziona, usa Ctrl+C/Ctrl+V nel campo di testo. BG1 è il formato di questa mod e non dipende dalla lingua dell’interfaccia.

Le carte mancanti, leader incluso, sono elencate con il costo totale in frammenti. Per crearle servono una conferma separata e abbastanza frammenti. L’importazione prepara una bozza: salva poi il mazzo. Dall’elenco viene usato uno spazio personalizzato libero, senza sovrascrivere quelli occupati. In allenamento si usa la collezione illimitata esistente.

## Comandi della console

bg_help() mostra la guida e bg_status() collezione, barili e frammenti. bg_find('Imlerith') cerca nomi e ID; bg_card(132102,1) assegna una carta, bg_faction('monsters') una fazione. bg_leaders() / bg_allcards() completano leader o collezione entro i normali limiti di copie. bg_kegs(10) e bg_scraps(1000) aggiungono risorse. Le assegnazioni richiedono un salvataggio caricato, fuori dai menu e dalle partite; poi salva normalmente. Nel negozio aperto di un oste, bg_shopcheck() controlla i barili e bg_shoprefill(5) porta le scorte a cinque, senza aggiungerne cinque a ogni chiamata. La console del gioco deve essere già abilitata.

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

## Lingue

Testo: inglese, russo, tedesco, francese, italiano, polacco, spagnolo (Spagna), spagnolo (America Latina), portoghese (Brasile), giapponese, coreano, cinese semplificato e cinese tradizionale. Cambiala in qualsiasi momento con il pulsante della lingua del testo in alto a sinistra nei menu dei mazzi e della collezione, oppure nelle impostazioni di battaglia; la scelta viene salvata.

Ogni pacchetto contiene le voci RU, EN, DE, IT e PT-BR. Testo e voci si scelgono separatamente con due pulsanti affiancati nel menu dei mazzi/della collezione della mod o nelle impostazioni della partita. Non serve reinstallare per cambiare voci. Automatico segue separatamente le lingue attuali del testo e del parlato del gioco; se una lingua manca, usa l’inglese. Salva normalmente dopo la scelta: le preferenze appartengono al salvataggio e restano aggiornando i file della mod. La vecchia scelta manuale del testo viene mantenuta. Alcune battute del troll dei barili in DE/IT mantengono il russo sostitutivo delle registrazioni originali. I nomi nativi degli oggetti seguono la lingua del gioco; alcune notifiche esterne restano RU/EN.

## Installazione

1. Chiudi il gioco e fai un backup dei salvataggi. Scarica il pacchetto per 1.32 o Next-Gen (5.0+). Installa una sola versione di Beta Gwent.

2. Per aggiornare, sposta prima la vecchia cartella della mod Beta Gwent fuori da Mods. Non eliminare tutta Mods e non mescolare versioni diverse.

3. Copia Mods dall’archivio nella cartella del gioco, accanto a bin e content. Per Classic 1.32 copia anche la cartella DLC inclusa. Percorsi: Mods/modBetaGwentClassic132/content e DLC/dlcBetaGwentClassic132Assets per 1.32; Mods/modBetaGwent0924/content per Next-Gen. Sostituisci solo le vecchie cartelle di questa mod, conservando gli altri mod e DLC.

4. Carica un salvataggio. Il normale menu dei mazzi di Gwent apre editor e scelta delle lingue; parla con un PNG che gioca per iniziare una partita. Salva normalmente per mantenere le preferenze.

## Requisiti

The Witcher 3 su PC. Scegli la build separata per Classic 1.32 o Next-Gen (pacchetto indicato come 5.0+). Per giocare non servono REDkit, Wwise o un programma d’installazione EXE.

## Compatibilità

Le definizioni dei vecchi oggetti Redux sono integrate per caricare i salvataggi; elimina la vecchia cartella modBetaGwentReduxCompat. Per passare da Redux usa una copia del salvataggio precedente alla perdita dell’inventario o del corpo: i dati persi non vengono recuperati. Le carte Redux non vengono convertite nella collezione Beta e non è garantita la compatibilità con ogni funzione di Redux/Redo Expansion. Altre revisioni del Gwent e modifiche a menu, scambi o ricompense possono creare conflitti. Dopo aver cambiato i mod, unisci nuovamente gli script in conflitto con Script Merger.

## Segnalazione bug

Hai trovato un problema? Indica versioni di mod e gioco, lingue scelte per testo e voci (anche Automatico), uso di Nuova partita +, altre mod, carte/leader e passaggi per riprodurlo. Sono utili uno screenshot e un salvataggio precedente al problema. Per le traduzioni indica lingua e schermata e proponi una formulazione migliore.

### Come attivare il log

1. Aggiungi -debugscripts dopo le virgolette finali nella destinazione di un collegamento a witcher3.exe. Steam: Proprietà → Generali → Opzioni di avvio. Con GOG puoi usare un collegamento diretto a witcher3.exe.

2. Avvia il gioco, riproduci il problema e chiudilo. Copia subito scriptslog.txt: l’avvio successivo lo sovrascrive. Se contiene solo l’intestazione, segnalalo; potrebbe servire una configurazione aggiuntiva.

3. Se Windows ha creato un dump dell’arresto, allega anche l’ultimo .dmp pertinente.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Ringraziamenti

Grazie a CD Projekt per The Witcher e Gwent, a LegacyGwent DIY per le risorse di carte e tabellone, alla community di Beta Gwent per aver conservato il materiale storico e le idee per gli archetipi, e a tutti coloro che testano la mod e inviano segnalazioni dettagliate.

Progetto amatoriale non ufficiale. Il codice originale della mod è distribuito con licenza GPL-3.0-only; i contenuti originali del gioco appartengono ai rispettivi proprietari.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)
