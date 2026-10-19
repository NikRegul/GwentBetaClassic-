# Gwent Beta Classic 0.9.0 — Italiano

> Versione 0.9.0 — pacchetti separati per Classic 1.32 e Next-Gen 5.0+.

## Importante

Esegui un backup dei salvataggi prima dell'installazione e prima di ogni aggiornamento. La mod è in sviluppo attivo: per le prime partite usa un salvataggio separato.

I testi delle carte provengono dalla localizzazione ufficiale della beta. L’interfaccia è stata tradotta con l’aiuto dell’IA e può contenere imprecisioni. I messaggi di scambio dei mazzi sono disponibili in tutte le 13 lingue; alcuni suggerimenti precedenti usano ancora l’inglese come alternativa. I suggerimenti di traduzione sono benvenuti.

**Steam Deck:** la mod funziona su Steam Deck (testata dall’autore).

## Novità della 0.9.0

- Esporta mostra un codice BG1.
- Comandi della console per risorse, ricerca delle carte, collezioni di fazione e scorte di barili degli osti.
- Le carte destinate al cimitero volano verso il cimitero corretto; lo stesso vale per le carte speciali dopo la risoluzione. Restano gli effetti di esilio e dissoluzione.
- Definizioni integrate dei vecchi oggetti Redux aiutano a evitare la perdita di inventario e corpo caricando salvataggi dopo il passaggio. Non recuperano dati già persi e salvati.
- Spaziature dei menu, stato del mazzo e pulsanti rivisti; con il controller si passa dalle carte visibili a Salva e si torna alle carte.
- I ritratti dei leader continuano ad animarsi dopo l’ingresso nella schermata VS. L’ingresso della regina delle aracne comincia insieme alla sua battuta. Classic 1.32 include le correzioni del gelo e degli effetti d’attacco.
- Vista completa della carta in stile beta: carta grande con lo stendardo di fazione originale della beta 0.9.24 (fazioni, carte neutrali e comandanti), forza base, citazione leggibile, parole chiave evidenziate e scorrimento ←/→.
- Incolla un codice mazzo dagli appunti di Windows nella schermata di importazione (pulsante Incolla o Ctrl+V; richiede Optional-CopyButton).
- Tutorial ampliato a 10 pagine: mulligan e pescate, file e vicini, stati delle carte.
- Carte corrette come nella beta: Myrgtabrakke infligge 2 danni tre volte, l'abilità di Harald lo Storpio colpisce dieci volte.
- Migliorata la gestione dei backup della collezione e dei mazzi. Questo può aiutare in alcuni casi di perdita dei progressi; il ripristino dipende dai dati disponibili nel backup.


## IA e interfaccia

Migliorate le valutazioni di Igni, Yrden, del meteo di Birna e delle abilità di armatura del cavaliere, dell’élite e dello scudiero redaniani. Dopo un passo, il recupero considera azioni e cambi di turno reali; l’ultimo passo non concede effetti aggiuntivi. Nel primo round una carta di svantaggio può andare bene, due richiedono una valutazione e tre vengono evitate negli inseguimenti facoltativi. Evitare la sconfitta nell’incontro ha precedenza. Rivisti pulsanti tradotti e spaziature.

Isengrim: Fuorilegge confronta ora carta speciale e creazione, anche dopo Decreto reale. L’IA evita Esca senza un bersaglio alleato Bronzo o Argento valido e valuta la scelta casuale fra tre carte senza conoscere i risultati futuri.

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

## Condividere i mazzi

Esporta mostra un codice BG1 indipendente dalla lingua. Copia lo inserisce direttamente negli appunti di Windows; incollalo ovunque con Ctrl+V. Serve la cartella facoltativa Optional-CopyButton: copia la sua cartella bin nella directory del gioco (dinput8.dll e plugins/GwentBetaClipboard.asi accanto a witcher3.exe). La mod funziona anche senza. Se un’altra mod ha già il proprio dinput8.dll, tienilo e carica GwentBetaClipboard.asi con il suo loader ASI. Senza questi file i pulsanti Importa ed Esporta sono nascosti. Importa accetta il codice BG1 completo nel campo di testo.

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

## Classic 1.32: dimensioni e DLC

Classic occupa circa 623 MB, Next-Gen 448 MB, con le stesse carte e regole. Il vecchio formato e il limite di circa 32 MiB per risorsa caricata in modo asincrono richiedono pagine grafiche separate. In Classic vanno installate entrambe le cartelle Mods e DLC. DLC/dlcBetaGwentClassic132Assets contiene grafica essenziale e la sua registrazione, senza nuova storia. Circa 105 MB del download provengono da questa cartella; il resto della differenza dipende dalla preparazione per il vecchio motore.

## Requisiti

The Witcher 3 su PC. Scegli la build separata per Classic 1.32 o Next-Gen (pacchetto indicato come 5.0+). Per giocare non servono REDkit, Wwise o un programma d’installazione EXE.

## Compatibilità

Le definizioni dei vecchi oggetti Redux sono integrate per caricare i salvataggi; elimina la vecchia cartella modBetaGwentReduxCompat. Per passare da Redux usa una copia del salvataggio precedente alla perdita dell’inventario o del corpo: i dati persi non vengono recuperati. Le carte Redux non vengono convertite nella collezione Beta e non è garantita la compatibilità con ogni funzione di Redux/Redo Expansion. Altre revisioni del Gwent e modifiche a menu, scambi o ricompense possono creare conflitti. Dopo aver cambiato i mod, unisci nuovamente gli script in conflitto con Script Merger.

## Redux

Dei 400 nomi di vecchi oggetti verificati, 197 mantengono le definizioni native e 203 ricevono definizioni inerti, nelle partite normali e NG+. Sono nascosti, senza peso o valore. L’inventario già perso non viene recuperato. Disinstallando, gli oggetti Redux rimasti richiedono di nuovo il fornitore originale delle definizioni.

## Pulizia integrata prima della disinstallazione

Non serve un mod di pulizia separato. Fai una copia del salvataggio, termina la partita ed esci da combattimenti e menu. bg_clean_preview() mostra soltanto istruzioni. Con il mod principale ancora installato, conferma:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

Vengono eliminati collezione, mazzi, risorse, impostazioni, ricompense note, copie di riserva e oggetti betagwent_* nell’inventario del giocatore. Un indicatore salvato impedisce il ripristino anche dopo un nuovo caricamento. Salva in un NUOVO slot, esci, rimuovi il mod e il suo DLC Classic, aggiorna Script Merger, carica lo slot nuovo e salva ancora. Missioni, obiettivi e corone spese rimangono. Mercanti non caricati, deposito e contenitori del mondo non vengono esaminati. Per vecchi fatti di ricompensa orfani: save_fact_index.py e bg_clean_keys('…') dopo la conferma. Non è garantita la cancellazione fisica di ogni traccia storica. Se alcuni oggetti Beta non possono essere rimossi, appare INCOMPLETE invece del successo: gettali o vendili e ripeti il comando. Disinstallando, elimina anche i file di Optional-CopyButton se li hai installati: bin\…\plugins\GwentBetaClipboard.asi e il dinput8.dll di questa mod (non di altre).

**Dopo la disinstallazione:** copia la cartella Mods dalla cartella After-Uninstall dell’archivio nella cartella del gioco (Mods/modBetaGwentKeepItems). Conserva definizioni nascoste degli oggetti della mod, così mercanti, deposito e contenitori che contengono ancora carte o barili della beta non perdono l’intero inventario. Non installarla insieme alla mod.

## Verso la 1.0

Fino alla 1.0 l’attenzione sarà su traduzioni, correzioni di errori e ulteriori miglioramenti a IA e interfaccia. I test automatici non sostituiscono le prove nel gioco o un vero ciclo di salvataggio/caricamento dopo la pulizia.

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
