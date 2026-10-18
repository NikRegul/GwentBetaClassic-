# Gwent Beta Classic 0.8.1 — Español (Latinoamérica)

> La versión 0.8.1 para Next-Gen 5.0+ ya se probó dentro del juego. Classic 1.32 se está corrigiendo y probando por separado; su archivo actual es una versión de prueba.

## Importante

Haz un respaldo de tus partidas guardadas antes de instalar y antes de cada actualización. El mod está en desarrollo activo: usa una partida aparte para tus primeros juegos de Gwent.

Las traducciones siguen siendo una versión de prueba: los textos de las cartas vienen de la localización oficial de la beta y la interfaz se tradujo con IA, así que puede tener errores. Las nuevas indicaciones agregadas desde la 0.6.6 por ahora solo existen en inglés y ruso; en los demás idiomas aparecen en inglés. Avísanos de todo lo que suene raro.

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

## Cambios desde 0.7.3a

- Cada paquete incluye los cinco doblajes y los 13 idiomas de texto. Ya no hacen falta descargas separadas por idioma de voz.
- Dos botones contiguos, Texto y Voces, en el menú del mod, con selección automática o manual independiente.
- Detección separada del idioma del texto y de las voces del juego. Los idiomas no disponibles utilizan inglés.
- Las preferencias se guardan con la partida. La selección manual anterior del texto se mantiene al actualizar.
- Corregidas las definiciones de los barriles y la recuperación de existencias en Nueva partida +. Una entrega fallida ya no se marca como completada; los barriles vendidos no reaparecen cada vez que se abre la tienda.
- Revisados los tres proyectiles de Jotunn, Kambi/Hemdall, Ragh Nar Roog, Golden Froth, estados, temporizadores y efectos de armadura.
- Recursos de interfaz reorganizados dentro del presupuesto de compilación de 63 MiB sin reducir la resolución de las texturas. La carga de menús y la estabilidad siguen pendientes de validación.

## Idiomas

Texto: inglés, ruso, alemán, francés, italiano, polaco, español (España), español (Latinoamérica), portugués (Brasil), japonés, coreano, chino simplificado y chino tradicional. Cámbialo cuando quieras con el botón de idioma del texto, arriba a la izquierda en los menús de mazos y colección, o en la configuración de combate; la elección se guarda.

Cada paquete incluye voces RU, EN, DE, IT y PT-BR. El texto y las voces se eligen por separado con dos botones contiguos en el menú de mazos/colección del mod o en los ajustes de la partida. Cambiar las voces no requiere reinstalar archivos. Automático sigue por separado los idiomas actuales de texto y voz del juego; si falta un idioma, utiliza inglés. Guarda la partida normalmente después de elegir: las preferencias pertenecen a ese guardado y se mantienen al actualizar los archivos del mod. Se conserva la selección manual anterior del texto. Algunas frases del trol de los barriles en DE/IT mantienen el reemplazo ruso de las grabaciones originales. Los nombres nativos de objetos siguen el idioma del juego; algunas notificaciones externas siguen en RU/EN.

## Instalación

1. Cierra el juego y haz un respaldo de tus partidas. Descarga el paquete para 1.32 o Next-Gen (5.0+). Instala solo una versión de Beta Gwent.

2. Para actualizar, mueve primero la carpeta anterior del mod Beta Gwent fuera de Mods. No borres toda la carpeta Mods ni mezcles archivos de versiones distintas.

3. Copia Mods del archivo a la carpeta del juego, junto a bin y content. Ruta final: Mods/modBetaGwentClassic132/content para 1.32 o Mods/modBetaGwent0924/content para Next-Gen.

4. Carga tu partida. El menú normal de mazos de Gwent abre el editor y la selección de idiomas; habla con un NPC que juegue para iniciar una partida. Guarda normalmente para conservar tus preferencias.

## Requisitos

The Witcher 3 para PC. Elige la compilación separada de Classic 1.32 o Next-Gen (paquete marcado 5.0+). No necesitas REDkit, Wwise ni un instalador EXE para jugar.

## Compatibilidad

Elimina la carpeta anterior modBetaGwentReduxCompat: la capa de compatibilidad independiente ya no se incluye. La compatibilidad con Redux/Redo Expansion no se confirmó por separado. Otras modificaciones de Gwent y mods que cambien sus menús, el intercambio de cartas o las recompensas pueden causar conflictos. Después de cambiar los mods instalados, vuelve a combinar los scripts con Script Merger.

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
