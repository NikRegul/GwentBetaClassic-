# Gwent Beta Classic 0.8.2 — Español (España)

> Versión 0.8.2 — paquetes separados para Classic 1.32 y Next-Gen 5.0+.

## Importante

Haz una copia de seguridad de tus partidas guardadas antes de instalar y antes de cada actualización. El mod está en desarrollo activo: usa una partida aparte para tus primeras partidas de Gwent.

Los textos de las cartas proceden de la localización oficial de la beta. La interfaz se ha traducido con ayuda de IA y puede contener errores. Los mensajes de intercambio de mazos están en los 13 idiomas; algunas ayudas antiguas siguen usando el inglés como alternativa. Se agradecen las sugerencias de traducción.

## Sobre el mod

Gwent Beta Classic sustituye el Gwent de The Witcher 3 por las cartas, las reglas y el tablero de Gwent Beta 0.9.24 independiente. Las partidas siguen formando parte del mundo de The Witcher: juega contra PNJ, completa misiones, compra barriles y crea tus propios mazos.

## Características

- 479 cartas coleccionables, incluidos 21 líderes, de las cinco facciones
- Tablero, interfaz, fuentes, marcos de cartas, clima y efectos de la beta; líderes animados
- Editor de mazos: cinco mazos iniciales editables y ocho huecos propios, filtros y búsqueda
- Rivales con 46 arquetipos de mazos de la beta y tres niveles de dificultad de la IA
- Barriles por 200 coronas en todos los posaderos, que se abren como en la beta
- Fragmentos: fabrica cartas por 30 / 80 / 200 / 800 según su rareza; las copias sobrantes se muelen automáticamente
- Tutorial, mulligan, consulta de cementerios y del mazo, vista detallada de las cartas
- Ratón, teclado y mando

## Novedades de la 0.8.2

- Importación y exportación de mazos mediante códigos BG1 en el portapapeles, con lista de cartas que faltan y una acción separada para crearlas.
- Comandos de consola para recursos, búsqueda de cartas, colecciones de facción y existencias de barriles de los taberneros.
- Las cartas enviadas al cementerio vuelan hacia el cementerio correspondiente; las cartas especiales hacen lo mismo tras resolverse. Se conservan los efectos de destierro y disolución.
- Las definiciones integradas de objetos antiguos de Redux ayudan a evitar la pérdida de inventario o del cuerpo al cargar una partida tras cambiar de mod. No recuperan datos ya perdidos y guardados.
- Espaciado de menús, estado del mazo y botones revisados; el mando permite pasar de las cartas visibles a Guardar y volver a las cartas.
- Los retratos de los líderes siguen animados tras su entrada en VS. La entrada de la reina de las arachas comienza con su voz. Classic 1.32 incluye las correcciones de escarcha y efectos de ataque.

## Compartir mazos

Exportar en el editor copia el código BG1 para compartirlo como texto. Importar está disponible en la lista de mazos y en el editor. Pega el código completo; uno incorrecto no cambia nada. Si no hay acceso directo al portapapeles, utiliza Ctrl+C/Ctrl+V en el campo de texto. BG1 es el formato de este mod y no depende del idioma de la interfaz.

Se muestran las cartas que faltan, incluido el líder, con el coste total en fragmentos. Crearlas requiere una confirmación aparte y suficientes fragmentos. La importación prepara un borrador: guarda después el mazo. Desde la lista se usa un espacio personalizado libre, sin sobrescribir los ocupados. El entrenamiento utiliza la colección ilimitada existente.

## Comandos de consola

bg_help() muestra la ayuda y bg_status() la colección, barriles y fragmentos. bg_find('Imlerith') busca nombres e ID; bg_card(132102,1) da una carta, bg_faction('monsters') una facción. bg_leaders() / bg_allcards() completan líderes o colección hasta los límites normales. bg_kegs(10) y bg_scraps(1000) añaden recursos. Se necesita una partida cargada, fuera de menús y partidas de cartas; guarda el juego después. En la tienda abierta de un tabernero, bg_shopcheck() comprueba los barriles y bg_shoprefill(5) repone las existencias hasta cinco, en vez de añadir cinco cada vez. La consola del juego debe estar activada previamente.

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

Texto: inglés, ruso, alemán, francés, italiano, polaco, español (España), español (Latinoamérica), portugués (Brasil), japonés, coreano, chino simplificado y chino tradicional. Cámbialo cuando quieras con el botón de idioma del texto, arriba a la izquierda en los menús de mazos y colección, o en los ajustes de combate; la elección se guarda.

Cada paquete incluye voces RU, EN, DE, IT y PT-BR. El texto y las voces se eligen por separado con dos botones contiguos en el menú de mazos/colección del mod o en los ajustes de la partida. Cambiar las voces no requiere reinstalar archivos. Automático sigue por separado los idiomas actuales de texto y voz del juego; si falta un idioma, utiliza inglés. Guarda la partida normalmente después de elegir: las preferencias pertenecen a ese guardado y se mantienen al actualizar los archivos del mod. Se conserva la selección manual anterior del texto. Algunas frases del trol de los barriles en DE/IT mantienen el reemplazo ruso de las grabaciones originales. Los nombres nativos de objetos siguen el idioma del juego; algunas notificaciones externas siguen en RU/EN.

## Instalación

1. Cierra el juego y haz una copia de seguridad de las partidas. Descarga el paquete para 1.32 o Next-Gen (5.0+). Instala una sola versión de Beta Gwent.

2. Al actualizar, mueve primero la carpeta anterior del mod Beta Gwent fuera de Mods. No elimines toda la carpeta Mods ni mezcles versiones.

3. Copia Mods del archivo a la carpeta del juego, junto a bin y content. Para Classic 1.32, copia también la carpeta DLC incluida. Rutas: Mods/modBetaGwentClassic132/content y DLC/dlcBetaGwentClassic132Assets para 1.32; Mods/modBetaGwent0924/content para Next-Gen. Sustituye solo las carpetas anteriores de este mod, conservando los demás mods y DLC.

4. Carga una partida. El menú habitual de mazos de Gwynt abre el editor y los idiomas; habla con un PNJ que juegue para comenzar una partida. Guarda normalmente para conservar tus preferencias.

## Requisitos

The Witcher 3 para PC. Elige la compilación separada de Classic 1.32 o Next-Gen (paquete marcado 5.0+). No necesitas REDkit, Wwise ni un instalador EXE para jugar.

## Compatibilidad

Las definiciones de objetos antiguos de Redux están integradas para cargar partidas; elimina la carpeta obsoleta modBetaGwentReduxCompat. Al cambiar desde Redux, usa una copia de la partida anterior a la pérdida del inventario o cuerpo: no se recuperan datos perdidos. Las cartas Redux no se convierten en la colección Beta y no se garantiza compatibilidad con todas las funciones de Redux/Redo Expansion. Otras revisiones de Gwent y cambios en menús, comercio o recompensas pueden entrar en conflicto. Tras cambiar los mods, vuelve a fusionar los scripts afectados con Script Merger.

## Informar de errores

¿Has encontrado un problema? Indica las versiones del mod y del juego, los idiomas elegidos para texto y voces (incluido Automático), si usas Nueva partida +, otros mods, cartas/líderes y los pasos para reproducirlo. Ayudan una captura y un guardado anterior al problema. Para traducciones, indica idioma y pantalla y sugiere una redacción mejor.

### Cómo activar el registro

1. Añade -debugscripts después de las comillas de cierre del destino de un acceso directo a witcher3.exe. Steam: Propiedades → General → Parámetros de lanzamiento. En GOG puedes usar un acceso directo al propio witcher3.exe.

2. Inicia el juego, reproduce el problema y ciérralo. Copia scriptslog.txt inmediatamente: el siguiente inicio lo sobrescribe. Si solo contiene una cabecera, indícalo; puede hacer falta una configuración adicional.

3. Si Windows ha creado un volcado del fallo, adjunta también el último archivo .dmp correspondiente.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Agradecimientos

Gracias a CD Projekt por The Witcher y Gwent, a LegacyGwent DIY por los recursos de cartas y tablero, a la comunidad de Beta Gwent por conservar el material histórico y las ideas de arquetipos, y a todos los que prueban el mod y envían informes detallados.

Proyecto de fans no oficial. El código original del mod se distribuye bajo GPL-3.0-only; los recursos originales del juego pertenecen a sus propietarios.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)
