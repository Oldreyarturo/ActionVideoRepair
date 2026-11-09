# ActionVideoRepair

Aplicación de escritorio para **analizar y reparar archivos MP4 dañados**, por ejemplo videos de cámaras de acción que se cortaron por batería agotada, memoria llena o una tarjeta retirada a mitad de la grabación.

Desarrollada en **Python + Tkinter**, integra **FFprobe**, **FFmpeg** y **Untrunc** para detectar errores, reconstruir el archivo y verificar que el resultado se pueda reproducir.

<!-- Agrega aquí una captura de la app: arrastra la imagen al editor de GitHub y se insertará el enlace -->

## Características

- **Análisis** del archivo con FFprobe para detectar si el contenedor MP4 está dañado o incompleto.
- **Reparación** del video con FFmpeg y, en casos graves, con Untrunc usando un video sano de referencia grabado con la misma cámara.
- **Verificación de integridad** del archivo recuperado.
- **Interfaz gráfica** sencilla, sin necesidad de usar la línea de comandos.
- **Instalador para Windows** generado con PyInstaller e Inno Setup.

## Tecnologías

| Herramienta | Uso |
|---|---|
| Python 3 / Tkinter | Lógica de la aplicación e interfaz gráfica |
| FFprobe | Análisis de la estructura y los flujos del video |
| FFmpeg | Reconstrucción y conversión del archivo |
| Untrunc | Recuperación de MP4 truncados a partir de un video de referencia |
| PyInstaller | Empaquetado en ejecutable (`ActionVideoRepair.spec`) |
| Inno Setup | Creación del instalador (`ActionVideoRepair.iss`) |

## Instalación

### Opción 1: instalador (Windows)

Descarga el instalador desde la sección [Releases](../../releases) y sigue los pasos.

### Opción 2: desde el código

1. Instala [Python 3](https://www.python.org/downloads/) (incluye Tkinter).
2. Descarga [FFmpeg](https://ffmpeg.org/download.html) (incluye FFprobe) y [Untrunc](https://github.com/anthwlock/untrunc).
3. Coloca los ejecutables en la carpeta `tools/` dentro del proyecto.
4. Ejecuta:

```bash
python ActionVideoRepair.py
```

## Uso

1. Abre la aplicación y selecciona el video dañado.
2. Ejecuta el análisis para ver qué errores tiene el archivo.
3. Si se requiere Untrunc, selecciona un video sano grabado con la misma cámara y la misma configuración.
4. Inicia la reparación y espera a que se verifique el archivo recuperado.

> El archivo original nunca se modifica: la aplicación genera una copia reparada.

## Compilar el instalador

```bash
pyinstaller ActionVideoRepair.spec
```

Después abre `ActionVideoRepair.iss` con Inno Setup y compílalo para generar el instalador.

## Licencia

El código de este proyecto se distribuye bajo la licencia [MIT](LICENSE).

FFmpeg y Untrunc son proyectos independientes con sus propias licencias (LGPL/GPL) y **no se incluyen en este repositorio**.

## Autor

**Arturo Michel Rodríguez** · [GitHub](https://github.com/Oldreyarturo) · [LinkedIn](https://www.linkedin.com/in/arturo-michel-rodriguez-854717445/)
