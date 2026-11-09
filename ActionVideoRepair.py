import os
import sys
import subprocess
import tkinter as tk
import shutil

from tkinter import filedialog, messagebox, scrolledtext
from datetime import datetime


# ============================================================
# CONFIGURACIÓN
# ============================================================

# ------------------------------------------------------------
# DIRECTORIO DE LA APLICACIÓN
# ------------------------------------------------------------

if getattr(sys, "frozen", False):
    # Cuando se ejecuta como EXE
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Cuando se ejecuta como archivo .py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------
# HERRAMIENTAS
# ------------------------------------------------------------

TOOLS_DIR = os.path.join(
    BASE_DIR,
    "tools"
)


FFMPEG = os.path.join(
    TOOLS_DIR,
    "ffmpeg.exe"
)


FFPROBE = os.path.join(
    TOOLS_DIR,
    "ffprobe.exe"
)


UNTRUNC = os.path.join(
    TOOLS_DIR,
    "untrunc.exe"
)


# ------------------------------------------------------------
# CARPETA DE DATOS DEL USUARIO
# ------------------------------------------------------------

# No guardamos archivos modificables dentro de Program Files.
# Windows permite escribir normalmente dentro de Documents.

USER_DATA_DIR = os.path.join(
    os.path.expanduser("~"),
    "Documents",
    "Action Video Repair"
)


VIDEO_DIR = os.path.join(
    USER_DATA_DIR,
    "videos",
    "corruptos"
)


REPAIRED_DIR = os.path.join(
    USER_DATA_DIR,
    "videos",
    "reparados"
)


LOG_DIR = os.path.join(
    USER_DATA_DIR,
    "logs"
)


# ============================================================
# CREAR CARPETAS
# ============================================================

os.makedirs(
    VIDEO_DIR,
    exist_ok=True
)

os.makedirs(
    REPAIRED_DIR,
    exist_ok=True
)

os.makedirs(
    LOG_DIR,
    exist_ok=True
)


# ============================================================
# LOG
# ============================================================

def log(text):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    line = f"[{timestamp}] {text}"

    console.insert(
        tk.END,
        line + "\n"
    )

    console.see(
        tk.END
    )

    logfile = os.path.join(
        LOG_DIR,
        "repair_log.txt"
    )

    try:

        with open(
            logfile,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                line + "\n"
            )

    except Exception:
        pass


# ============================================================
# EJECUTAR COMANDO
# ============================================================

def run_command(command):

    try:

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        return (
            result.returncode,
            result.stdout
        )

    except Exception as error:

        return (
            -1,
            str(error)
        )


# ============================================================
# COMPROBAR HERRAMIENTAS
# ============================================================

def check_tools():

    missing = []

    if not os.path.isfile(FFMPEG):

        missing.append(
            "ffmpeg.exe"
        )

    if not os.path.isfile(FFPROBE):

        missing.append(
            "ffprobe.exe"
        )

    if not os.path.isfile(UNTRUNC):

        missing.append(
            "untrunc.exe"
        )

    if missing:

        messagebox.showerror(
            "Herramientas faltantes",
            "Faltan las siguientes herramientas:\n\n"
            + "\n".join(missing)
            + "\n\n"
            + "Revisa la carpeta:\n"
            + TOOLS_DIR
        )

        return False

    return True


# ============================================================
# PROBAR HERRAMIENTAS
# ============================================================

def test_tools():

    log(
        "Comprobando herramientas..."
    )

    tools = [
        ("FFmpeg", FFMPEG),
        ("FFprobe", FFPROBE),
        ("Untrunc", UNTRUNC)
    ]

    for name, path in tools:

        if not os.path.isfile(path):

            log(
                f"ERROR: {name} no encontrado."
            )

            return False

        log(
            f"OK: {name}"
        )


    # --------------------------------------------------------
    # PROBAR FFMPEG
    # --------------------------------------------------------

    code, output = run_command(
        [
            FFMPEG,
            "-version"
        ]
    )

    if code != 0:

        log(
            "ERROR: FFmpeg no pudo ejecutarse."
        )

        return False

    log(
        "OK: FFmpeg funciona."
    )


    # --------------------------------------------------------
    # PROBAR FFPROBE
    # --------------------------------------------------------

    code, output = run_command(
        [
            FFPROBE,
            "-version"
        ]
    )

    if code != 0:

        log(
            "ERROR: FFprobe no pudo ejecutarse."
        )

        return False

    log(
        "OK: FFprobe funciona."
    )


    # --------------------------------------------------------
    # PROBAR UNTRUNC
    # --------------------------------------------------------

    code, output = run_command(
        [
            UNTRUNC
        ]
    )

    # Algunas versiones devuelven código distinto
    # aunque puedan ejecutarse correctamente.

    if code == -1073741515:

        log(
            "ERROR: Untrunc tiene una DLL faltante."
        )

        log(
            "Revisa las DLL de Untrunc."
        )

        return False

    log(
        "OK: Untrunc puede ejecutarse."
    )

    return True


# ============================================================
# ANALIZAR VIDEO CON FFPROBE
# ============================================================

def analyze_video(video):

    command = [
        FFPROBE,

        "-v",
        "error",

        "-show_entries",
        "format=duration,size",

        "-show_entries",
        "stream=codec_name,codec_type,width,height,r_frame_rate,duration",

        "-of",
        "default=noprint_wrappers=1",

        video
    ]

    code, output = run_command(
        command
    )

    return code, output


# ============================================================
# COMPROBAR SI EL VIDEO FUNCIONA
# ============================================================

def is_video_valid(video):

    code, output = analyze_video(
        video
    )

    if code != 0:
        return False

    if not output.strip():
        return False

    return True


# ============================================================
# OBTENER INFORMACIÓN DEL VIDEO
# ============================================================

def get_video_info(video):

    code, output = analyze_video(
        video
    )

    if code != 0:
        return None

    info = {}

    for line in output.splitlines():

        if "=" not in line:
            continue

        key, value = line.split(
            "=",
            1
        )

        info.setdefault(
            key,
            []
        )

        info[key].append(
            value
        )

    return info


# ============================================================
# BUSCAR ARCHIVO GENERADO POR UNTRUNC
# ============================================================

def find_untrunc_output(
    directory,
    original
):

    candidates = []

    for filename in os.listdir(
        directory
    ):

        lower = filename.lower()

        if not lower.endswith(
            ".mp4"
        ):
            continue

        if "_fixed" not in lower:
            continue

        full_path = os.path.join(
            directory,
            filename
        )

        if os.path.abspath(
            full_path
        ) == os.path.abspath(
            original
        ):
            continue

        candidates.append(
            full_path
        )


    if not candidates:
        return None


    # El archivo más reciente normalmente es
    # el resultado recién generado.

    candidates.sort(
        key=lambda x: os.path.getmtime(x),
        reverse=True
    )

    return candidates[0]


# ============================================================
# REPARAR CON UNTRUNC
# ============================================================

def repair_with_untrunc(
    reference,
    corrupted
):

    directory = os.path.dirname(
        corrupted
    )

    log(
        "Ejecutando Untrunc..."
    )

    log(
        f"Referencia: {os.path.basename(reference)}"
    )

    log(
        f"Corrupto: {os.path.basename(corrupted)}"
    )


    command = [
        UNTRUNC,
        reference,
        corrupted
    ]

    code, output = run_command(
        command
    )


    if output.strip():

        log(
            output
        )


    if code == -1073741515:

        log(
            "ERROR: Untrunc no pudo iniciarse."
        )

        log(
            "Revisa las DLL de Untrunc."
        )

        return None


    # Buscar resultado generado por Untrunc

    result = find_untrunc_output(
        directory,
        corrupted
    )


    if result is None:

        log(
            "No se encontró archivo reparado."
        )

        return None


    size = os.path.getsize(
        result
    )


    if size == 0:

        log(
            "Untrunc generó un archivo vacío."
        )

        return None


    log(
        f"Archivo generado: "
        f"{os.path.basename(result)}"
    )

    log(
        f"Tamaño: "
        f"{size / 1024 / 1024:.2f} MB"
    )

    return result


# ============================================================
# VERIFICAR ARCHIVO REPARADO
# ============================================================

def verify_repaired(
    video
):

    log(
        "Verificando reparación..."
    )


    code, output = analyze_video(
        video
    )


    if code != 0:

        log(
            "ERROR: FFprobe no pudo leer "
            "el archivo reparado."
        )

        return False, None


    info = get_video_info(
        video
    )


    if info is None:

        return False, None


    types = info.get(
        "codec_type",
        []
    )


    log(
        "Información recuperada:"
    )


    for key in [
        "codec_name",
        "codec_type",
        "width",
        "height",
        "r_frame_rate",
        "duration",
        "size"
    ]:

        if key in info:

            log(
                f"{key}: "
                + ", ".join(
                    info[key]
                )
            )


    has_video = (
        "video" in types
    )


    has_audio = (
        "audio" in types
    )


    if has_video:

        log(
            "✓ Stream de video encontrado."
        )

    else:

        log(
            "✗ No se encontró stream de video."
        )


    if has_audio:

        log(
            "✓ Stream de audio encontrado."
        )

    else:

        log(
            "⚠ No se encontró audio."
        )


    if has_video:

        log(
            "✓ ARCHIVO RECUPERADO"
        )

        return True, info


    log(
        "✗ La reparación no produjo "
        "un video válido."
    )

    return False, info


# ============================================================
# MOVER RESULTADO
# ============================================================

def move_to_repaired(
    repaired_file,
    original
):

    original_name = os.path.splitext(
        os.path.basename(original)
    )[0]


    destination = os.path.join(
        REPAIRED_DIR,
        original_name + "_REPARADO.mp4"
    )


    # Evitar sobrescribir archivos existentes

    counter = 1

    base_destination = destination


    while os.path.exists(
        destination
    ):

        destination = os.path.join(
            REPAIRED_DIR,
            f"{original_name}_REPARADO_{counter}.mp4"
        )

        counter += 1


    shutil.move(
        repaired_file,
        destination
    )


    return destination


# ============================================================
# REPARAR UN VIDEO
# ============================================================

def process_video(
    reference,
    video,
    index,
    total
):

    log("")

    log(
        "=" * 70
    )

    log(
        f"VIDEO {index}/{total}"
    )

    log(
        os.path.basename(video)
    )

    log(
        "=" * 70
    )


    size = os.path.getsize(
        video
    )


    log(
        f"Tamaño original: "
        f"{size / 1024 / 1024:.2f} MB"
    )


    # --------------------------------------------------------
    # ANALIZAR
    # --------------------------------------------------------

    valid = is_video_valid(
        video
    )


    if valid:

        log(
            "✓ El video ya puede ser leído."
        )

        log(
            "No se modifica."
        )

        return "VALIDO"


    log(
        "⚠ El video parece estar corrupto."
    )


    # --------------------------------------------------------
    # REPARAR
    # --------------------------------------------------------

    repaired = repair_with_untrunc(
        reference,
        video
    )


    if repaired is None:

        log(
            "✗ REPARACIÓN FALLIDA"
        )

        return "FALLIDO"


    # --------------------------------------------------------
    # VERIFICAR
    # --------------------------------------------------------

    valid, info = verify_repaired(
        repaired
    )


    if not valid:

        log(
            "✗ El resultado no pudo "
            "verificarse correctamente."
        )

        return "FALLIDO"


    # --------------------------------------------------------
    # MOVER
    # --------------------------------------------------------

    destination = move_to_repaired(
        repaired,
        video
    )


    log(
        "Resultado guardado en:"
    )

    log(
        destination
    )


    return "RECUPERADO"


# ============================================================
# SELECCIONAR REFERENCIA
# ============================================================

def select_reference():

    path = filedialog.askopenfilename(
        title="Selecciona un video SANO de Action!",
        filetypes=[
            (
                "Videos MP4",
                "*.mp4"
            ),
            (
                "Todos los archivos",
                "*.*"
            )
        ]
    )


    if path:

        reference_entry.delete(
            0,
            tk.END
        )

        reference_entry.insert(
            0,
            path
        )


# ============================================================
# SELECCIONAR CARPETA
# ============================================================

def select_folder():

    folder = filedialog.askdirectory(
        title="Selecciona la carpeta de videos"
    )


    if folder:

        folder_entry.delete(
            0,
            tk.END
        )

        folder_entry.insert(
            0,
            folder
        )


# ============================================================
# INICIAR REPARACIÓN
# ============================================================

def start_repair():

    if not check_tools():
        return


    if not test_tools():

        messagebox.showerror(
            "Error",
            "Una o más herramientas "
            "no funcionan correctamente.\n\n"
            "Revisa la consola."
        )

        return


    reference = (
        reference_entry
        .get()
        .strip()
    )


    folder = (
        folder_entry
        .get()
        .strip()
    )


    if not os.path.isfile(
        reference
    ):

        messagebox.showwarning(
            "Referencia",
            "Selecciona un video sano."
        )

        return


    if not os.path.isdir(
        folder
    ):

        messagebox.showwarning(
            "Carpeta",
            "Selecciona una carpeta válida."
        )

        return


    # --------------------------------------------------------
    # VIDEOS
    # --------------------------------------------------------

    videos = []


    for filename in os.listdir(
        folder
    ):

        if not filename.lower().endswith(
            ".mp4"
        ):
            continue


        path = os.path.join(
            folder,
            filename
        )


        if os.path.abspath(
            path
        ) == os.path.abspath(
            reference
        ):
            continue


        videos.append(
            path
        )


    if not videos:

        messagebox.showinfo(
            "Videos",
            "No se encontraron videos MP4."
        )

        return


    # --------------------------------------------------------
    # CONFIRMACIÓN
    # --------------------------------------------------------

    answer = messagebox.askyesno(
        "Iniciar recuperación",
        f"Se encontraron {len(videos)} videos.\n\n"
        "Los originales NO serán modificados.\n\n"
        "¿Quieres comenzar?"
    )


    if not answer:
        return


    repair_button.config(
        state="disabled"
    )


    success = 0
    failed = 0
    valid = 0


    try:

        log("")

        log(
            "#" * 70
        )

        log(
            "ACTION! VIDEO REPAIR"
        )

        log(
            f"Videos encontrados: "
            f"{len(videos)}"
        )

        log(
            "#" * 70
        )


        for index, video in enumerate(
            videos,
            1
        ):

            result = process_video(
                reference,
                video,
                index,
                len(videos)
            )


            if result == "RECUPERADO":

                success += 1


            elif result == "FALLIDO":

                failed += 1


            elif result == "VALIDO":

                valid += 1


        # ----------------------------------------------------
        # RESUMEN
        # ----------------------------------------------------

        log("")

        log(
            "#" * 70
        )

        log(
            "PROCESO TERMINADO"
        )

        log(
            f"Recuperados: {success}"
        )

        log(
            f"Ya válidos:  {valid}"
        )

        log(
            f"Fallidos:    {failed}"
        )

        log(
            "#" * 70
        )


        messagebox.showinfo(
            "Proceso terminado",
            "Recuperación terminada.\n\n"
            f"Recuperados: {success}\n"
            f"Ya válidos: {valid}\n"
            f"Fallidos: {failed}\n\n"
            "Los videos recuperados están en:\n"
            f"{REPAIRED_DIR}"
        )


    finally:

        repair_button.config(
            state="normal"
        )


# ============================================================
# INTERFAZ
# ============================================================

root = tk.Tk()


root.title(
    "Action! Video Repair"
)


root.geometry(
    "950x700"
)


root.minsize(
    800,
    600
)


# ============================================================
# TÍTULO
# ============================================================

title = tk.Label(
    root,
    text="ACTION! VIDEO REPAIR",
    font=(
        "Segoe UI",
        22,
        "bold"
    )
)


title.pack(
    pady=(15, 2)
)


subtitle = tk.Label(
    root,
    text=(
        "Recuperación automática de "
        "videos MP4 corruptos de Action!"
    ),
    font=(
        "Segoe UI",
        10
    )
)


subtitle.pack(
    pady=(0, 15)
)


# ============================================================
# REFERENCIA
# ============================================================

reference_frame = tk.Frame(
    root
)


reference_frame.pack(
    fill="x",
    padx=20,
    pady=5
)


tk.Label(
    reference_frame,
    text="Video sano de referencia:",
    width=27,
    anchor="w"
).pack(
    side="left"
)


reference_entry = tk.Entry(
    reference_frame
)


reference_entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=5
)


tk.Button(
    reference_frame,
    text="Seleccionar",
    command=select_reference
).pack(
    side="right"
)


# ============================================================
# CARPETA
# ============================================================

folder_frame = tk.Frame(
    root
)


folder_frame.pack(
    fill="x",
    padx=20,
    pady=5
)


tk.Label(
    folder_frame,
    text="Carpeta de videos corruptos:",
    width=27,
    anchor="w"
).pack(
    side="left"
)


folder_entry = tk.Entry(
    folder_frame
)


folder_entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=5
)


# Usar la carpeta predeterminada

folder_entry.insert(
    0,
    VIDEO_DIR
)


tk.Button(
    folder_frame,
    text="Seleccionar",
    command=select_folder
).pack(
    side="right"
)


# ============================================================
# BOTÓN
# ============================================================

repair_button = tk.Button(
    root,
    text="REPARAR VIDEOS",
    command=start_repair,
    font=(
        "Segoe UI",
        13,
        "bold"
    ),
    height=2
)


repair_button.pack(
    pady=15
)


# ============================================================
# CONSOLA
# ============================================================

console = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    font=(
        "Consolas",
        9
    )
)


console.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=(5, 15)
)


# ============================================================
# INICIO
# ============================================================

log(
    "Action! Video Repair iniciado."
)

log(
    f"Directorio: {BASE_DIR}"
)

log(
    f"Herramientas: {TOOLS_DIR}"
)

log(
    f"Videos corruptos: {VIDEO_DIR}"
)

log(
    f"Videos reparados: {REPAIRED_DIR}"
)

log(
    f"Logs: {LOG_DIR}"
)

log(
    "Originales: NO serán modificados."
)


# ============================================================
# INICIAR
# ============================================================

root.mainloop()