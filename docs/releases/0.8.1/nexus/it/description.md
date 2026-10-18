# Gwent Beta Classic 0.8.1 — Italiano

> La versione 0.8.1 per Next-Gen 5.0+ è stata provata nel gioco. Classic 1.32 viene corretta e verificata separatamente; l’archivio attuale è una versione di prova.

## Importante

Esegui un backup dei salvataggi prima dell'installazione e prima di ogni aggiornamento. La mod è in sviluppo attivo: per le prime partite usa un salvataggio separato.

Le traduzioni restano un'anteprima: i testi delle carte provengono dalla localizzazione ufficiale della beta, l'interfaccia è stata tradotta con IA e può contenere errori. I nuovi suggerimenti aggiunti dalla 0.6.6 esistono per ora solo in inglese e russo; nelle altre lingue compaiono in inglese. Segnala tutto ciò che suona sbagliato.

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

## Novità dalla 0.7.3a

- Ogni pacchetto include tutti e cinque i doppiaggi e tutte le 13 lingue del testo. Non servono più download separati per le voci.
- Due pulsanti affiancati, Testo e Voci, nel menu della mod, con scelta automatica o manuale indipendente.
- Rilevamento separato delle lingue del testo e del parlato del gioco. Le lingue non supportate usano l’inglese.
- Preferenze salvate nella partita. La precedente scelta manuale del testo rimane dopo l’aggiornamento.
- Corretti definizioni dei barili e recupero delle scorte in Nuova partita +. Un’aggiunta fallita non risulta completata; le scorte vendute non si ripristinano a ogni apertura del negozio.
- Rivisti i tre proiettili di Jotunn, Kambi/Hemdall, Ragh Nar Roog, Golden Froth, stati, timer ed effetti dell’armatura.
- Risorse dell’interfaccia riorganizzate entro il budget di 63 MiB senza ridurre la risoluzione delle texture. Avvio dei menu e stabilità restano da verificare.

## Lingue

Testo: inglese, russo, tedesco, francese, italiano, polacco, spagnolo (Spagna), spagnolo (America Latina), portoghese (Brasile), giapponese, coreano, cinese semplificato e cinese tradizionale. Cambiala in qualsiasi momento con il pulsante della lingua del testo in alto a sinistra nei menu dei mazzi e della collezione, oppure nelle impostazioni di battaglia; la scelta viene salvata.

Ogni pacchetto contiene le voci RU, EN, DE, IT e PT-BR. Testo e voci si scelgono separatamente con due pulsanti affiancati nel menu dei mazzi/della collezione della mod o nelle impostazioni della partita. Non serve reinstallare per cambiare voci. Automatico segue separatamente le lingue attuali del testo e del parlato del gioco; se una lingua manca, usa l’inglese. Salva normalmente dopo la scelta: le preferenze appartengono al salvataggio e restano aggiornando i file della mod. La vecchia scelta manuale del testo viene mantenuta. Alcune battute del troll dei barili in DE/IT mantengono il russo sostitutivo delle registrazioni originali. I nomi nativi degli oggetti seguono la lingua del gioco; alcune notifiche esterne restano RU/EN.

## Installazione

1. Chiudi il gioco e fai un backup dei salvataggi. Scarica il pacchetto per 1.32 o Next-Gen (5.0+). Installa una sola versione di Beta Gwent.

2. Per aggiornare, sposta prima la vecchia cartella della mod Beta Gwent fuori da Mods. Non eliminare tutta Mods e non mescolare versioni diverse.

3. Copia Mods dall’archivio nella cartella del gioco, accanto a bin e content. Percorso finale: Mods/modBetaGwentClassic132/content per 1.32, Mods/modBetaGwent0924/content per Next-Gen.

4. Carica un salvataggio. Il normale menu dei mazzi di Gwent apre editor e scelta delle lingue; parla con un PNG che gioca per iniziare una partita. Salva normalmente per mantenere le preferenze.

## Requisiti

The Witcher 3 su PC. Scegli la build separata per Classic 1.32 o Next-Gen (pacchetto indicato come 5.0+). Per giocare non servono REDkit, Wwise o un programma d’installazione EXE.

## Compatibilità

Elimina la vecchia cartella modBetaGwentReduxCompat: il livello di compatibilità separato non è più incluso. La compatibilità con Redux/Redo Expansion non è stata confermata separatamente. Altre revisioni di Gwent e mod che cambiano menu, scambi di carte o ricompense possono causare conflitti. Dopo aver cambiato le mod installate, ripeti l'unione degli script con Script Merger.

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
