# Gwent Beta Classic 0.8.2 — Español (Latinoamérica)

> Versión 0.8.2 — paquetes separados para Classic 1.32 y Next-Gen 5.0+.

## Importante

Haz un respaldo de tus partidas guardadas antes de instalar y antes de cada actualización. El mod está en desarrollo activo: usa una partida aparte para tus primeros juegos de Gwent.

Los textos de las cartas vienen de la localización oficial de la beta. La interfaz se tradujo con ayuda de IA y puede contener errores. Los mensajes para compartir mazos están en los 13 idiomas; algunas ayudas anteriores todavía usan el inglés como alternativa. Tus sugerencias de traducción son bienvenidas.

## Acerca del mod

Gwent Beta Classic reemplaza el Gwent de The Witcher 3 con las cartas, las reglas y el tablero de Gwent Beta 0.9.24 independiente. Las partidas siguen siendo parte del mundo de The Witcher: juega contra NPC, completa misiones, compra barriles y arma tus propios mazos.

## Características

- 479 cartas coleccionables, incluidos 21 líderes, de las cinco facciones
- Tablero, interfaz, fuentes, marcos de cartas, clima y efectos de la beta; líderes animados
- Editor de mazos: cinco mazos iniciales editables y ocho espacios propios, filtros y búsqueda
- Rivales con 46 arquetipos de mazos de la beta y tres niveles de dificultad de la IA
- Barriles por 200 coronas con todos los posaderos, que se abren como en la beta
- Fragmentos: fabrica cartas por 30 / 80 / 200 / 800 según su rareza; las copias sobrantes se muelen automáticamente
- Tutorial, mulligan, consulta de cementerios y del mazo, vista detallada de las cartas
- Mouse, teclado y control

## Novedades de la 0.8.2

- Importa y exporta mazos como códigos BG1 desde el portapapeles, con una lista de cartas faltantes y una acción independiente para crearlas.
- Comandos de consola para recursos, búsqueda de cartas, colecciones de facción y existencias de barriles de los taberneros.
- Las cartas enviadas al cementerio vuelan al cementerio que les corresponde; las cartas especiales lo hacen después de resolverse. Se mantienen los efectos de destierro y disolución.
- Las definiciones integradas de objetos antiguos de Redux ayudan a evitar la pérdida del inventario o del cuerpo al cargar una partida después de cambiar de mod. No recuperan datos ya perdidos y guardados.
- Mejor espaciado de menús, estado del mazo y botones; con el control puedes pasar de las cartas visibles a Guardar y volver a las cartas.
- Los retratos de los líderes siguen animados después de su entrada en VS. La entrada de la reina de las arachas empieza junto con su voz. Classic 1.32 incluye las correcciones de escarcha y efectos de ataque.

## Compartir mazos

Exportar en el editor copia el código BG1 para compartirlo como texto. Puedes importar desde la lista de mazos o el editor. Pega el código completo; un código inválido no cambia nada. Si no funciona el acceso directo al portapapeles, usa Ctrl+C/Ctrl+V en el campo de texto. BG1 es el formato de este mod y no depende del idioma de la interfaz.

Las cartas faltantes, incluido el líder, aparecen con el costo total en fragmentos. Crearlas requiere una confirmación aparte y suficientes fragmentos. La importación arma un borrador: guarda el mazo después. Desde la lista se usa un espacio personalizado libre, sin sobrescribir los ocupados. El entrenamiento usa la colección ilimitada existente.

## Comandos de consola

bg_help() muestra la ayuda y bg_status() tu colección, barriles y fragmentos. bg_find('Imlerith') busca nombres e ID; bg_card(132102,1) entrega una carta, bg_faction('monsters') una facción. bg_leaders() / bg_allcards() completan líderes o colección hasta los límites normales. bg_kegs(10) y bg_scraps(1000) agregan recursos. Necesitas una partida cargada y estar fuera de menús y partidas de cartas; después guarda el juego normalmente. En la tienda abierta de un tabernero, bg_shopcheck() revisa los barriles y bg_shoprefill(5) lleva las existencias a cinco, sin agregar cinco en cada llamada. La consola del juego debe estar activada de antemano.

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

Texto: inglés, ruso, alemán, francés, italiano, polaco, español (España), español (Latinoamérica), portugués (Brasil), japonés, coreano, chino simplificado y chino tradicional. Cámbialo cuando quieras con el botón de idioma del texto, arriba a la izquierda en los menús de mazos y colección, o en la configuración de combate; la elección se guarda.

Cada paquete incluye voces RU, EN, DE, IT y PT-BR. El texto y las voces se eligen por separado con dos botones contiguos en el menú de mazos/colección del mod o en los ajustes de la partida. Cambiar las voces no requiere reinstalar archivos. Automático sigue por separado los idiomas actuales de texto y voz del juego; si falta un idioma, utiliza inglés. Guarda la partida normalmente después de elegir: las preferencias pertenecen a ese guardado y se mantienen al actualizar los archivos del mod. Se conserva la selección manual anterior del texto. Algunas frases del trol de los barriles en DE/IT mantienen el reemplazo ruso de las grabaciones originales. Los nombres nativos de objetos siguen el idioma del juego; algunas notificaciones externas siguen en RU/EN.

## Instalación

1. Cierra el juego y haz un respaldo de tus partidas. Descarga el paquete para 1.32 o Next-Gen (5.0+). Instala solo una versión de Beta Gwent.

2. Para actualizar, mueve primero la carpeta anterior del mod Beta Gwent fuera de Mods. No borres toda la carpeta Mods ni mezcles archivos de versiones distintas.

3. Copia Mods del archivo a la carpeta del juego, junto a bin y content. Para Classic 1.32, copia también la carpeta DLC incluida. Rutas: Mods/modBetaGwentClassic132/content y DLC/dlcBetaGwentClassic132Assets para 1.32; Mods/modBetaGwent0924/content para Next-Gen. Reemplaza únicamente las carpetas anteriores de este mod y conserva los demás mods y DLC.

4. Carga tu partida. El menú normal de mazos de Gwent abre el editor y la selección de idiomas; habla con un NPC que juegue para iniciar una partida. Guarda normalmente para conservar tus preferencias.

## Requisitos

The Witcher 3 para PC. Elige la compilación separada de Classic 1.32 o Next-Gen (paquete marcado 5.0+). No necesitas REDkit, Wwise ni un instalador EXE para jugar.

## Compatibilidad

Las definiciones de objetos antiguos de Redux están integradas para cargar partidas; elimina la carpeta obsoleta modBetaGwentReduxCompat. Si vienes de Redux, usa una copia de la partida anterior a la pérdida del inventario o del cuerpo: los datos perdidos no se recuperan. Las cartas Redux no se convierten en la colección Beta y no se garantiza compatibilidad con todas las funciones de Redux/Redo Expansion. Otras modificaciones de Gwent y cambios en menús, comercio o recompensas pueden causar conflictos. Después de cambiar los mods, vuelve a combinar los scripts en conflicto con Script Merger.

## Reportar errores

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

Gracias a CD Projekt por The Witcher y Gwent, a LegacyGwent DIY por los recursos de cartas y tablero, a la comunidad de Beta Gwent por conservar el material histórico y las ideas de arquetipos, y a todos los que prueban el mod y mandan reportes detallados.

Proyecto de fans no oficial. El código original del mod se distribuye bajo GPL-3.0-only; los recursos originales del juego pertenecen a sus dueños.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)
