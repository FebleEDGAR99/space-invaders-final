# Space Invaders — proyecto final

Juego de escritorio en Python y Pygame Community Edition. Incluye el código,
las imágenes necesarias, efectos de sonido y un lanzador para Windows.

## Cómo ejecutarlo en Windows

1. Instala Python 3.10 o superior (incluye Python 3.14).
2. Extrae TODO el ZIP. No ejecutes el juego desde dentro del archivo comprimido.
3. Abre la carpeta `spaceinvaders_final` y haz doble clic en `JUGAR_WINDOWS.bat`.
   El lanzador crea un entorno `.venv`, instala la dependencia la primera vez
   (requiere Internet) y abre el juego.

También puedes abrir una terminal en esa carpeta y ejecutar:

```powershell
py -m pip install --only-binary=:all: -r requirements.txt
py main.py
```

En macOS/Linux, utiliza un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Se instala **pygame-ce**, pero el código utiliza `import pygame`. No es necesario
instalar el paquete `pygame` por separado. Las rutas de imágenes y sonidos se
calculan desde `main.py`, por lo que no dependen de la carpeta de la terminal.

## Controles

| Tecla | Acción |
| --- | --- |
| Enter | Comenzar o volver a jugar |
| Flechas izquierda/derecha o A/D | Mover la nave |
| Espacio (mantener) | Disparar |
| P | Pausar o continuar |
| M | Silenciar o activar efectos |
| R | Reiniciar después de ganar o perder |
| Esc | Salir |

## Reglas

- Completa cinco oleadas para ganar. La velocidad y los disparos enemigos
  aumentan con cada nivel.
- Tienes tres vidas. Tras un impacto hay 1,5 segundos de protección; la nave
  parpadea mientras está protegida.
- Si las naves enemigas llegan a la altura del jugador, pierdes la partida.
- Cada enemigo vale entre 10 y 40 puntos según su fila.
- La munición es ilimitada, con un intervalo de 0,24 segundos entre disparos.
  `BALAS` muestra los proyectiles del jugador que están actualmente en pantalla.
- El juego se pausa automáticamente si la ventana pierde el foco.
- Los efectos de audio son opcionales: se puede jugar sin dispositivo de sonido.

## Estructura y avance

- `main.py`: clases `Game`, `Player`, `Enemy` y `Bullet`; eventos, movimiento,
  colisiones, HUD, niveles, pausa, victoria y derrota.
- `img/`: siete imágenes utilizadas por el juego.
- `sounds/`: tres efectos WAV incluidos.
- `requirements.txt`: dependencia fijada para reproducir la instalación.
- `JUGAR_WINDOWS.bat`: instalación y ejecución en Windows.
- `tests/test_game.py`: pruebas de lógica con vídeo y audio simulados.

Para ejecutar las pruebas desde la carpeta del proyecto:

```powershell
py -m unittest discover -s tests -v
```

## Procedencia y licencia

Esta es una versión completada y adaptada con ayuda de ChatGPT del proyecto
https://github.com/FebleEDGAR99/spaceinvaders, un fork de
https://github.com/mendiolaleonel2002-debug/spaceinvaders.

Las imágenes proceden del primer repositorio. Se conserva su archivo `LICENSE`
original (MIT). Los efectos WAV se sintetizaron para esta entrega. El código
añadido se distribuye también bajo licencia MIT.

Este repositorio contiene la versión final del proyecto y conserva los créditos
y la licencia del repositorio original.
