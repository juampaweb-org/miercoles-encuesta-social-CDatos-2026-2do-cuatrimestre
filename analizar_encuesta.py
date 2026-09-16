"""
Analiza la encuesta social del curso de C Datos y genera:

  - Gráficos de barras (con matplotlib) para las preguntas de opción múltiple.
  - Una página web (output/index.html) con esos gráficos y las respuestas
    de las preguntas de texto libre.

Para correrlo:
    python3 analizar_encuesta.py

El resultado queda en la carpeta output/ (se puede abrir output/index.html
directamente en el navegador, sin necesidad de servidor).
"""

import csv
import html
import random
import textwrap
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Rutas de archivos
# ---------------------------------------------------------------------------

CARPETA_BASE = Path(__file__).parent
ARCHIVO_CSV = CARPETA_BASE / "data" / "data-CD-miercoles.csv"
CARPETA_SALIDA = CARPETA_BASE / "output"
CARPETA_GRAFICOS = CARPETA_SALIDA / "graficos"

# ---------------------------------------------------------------------------
# Preguntas de opción (única o múltiple) que vamos a graficar.
# Cada una es: (columna en el csv, título del gráfico, archivo .png, tipo)
# tipo = "unica"    -> el alumno eligió una sola opción
# tipo = "multiple" -> el alumno pudo elegir varias, separadas por comas
# ---------------------------------------------------------------------------

PREGUNTAS_GRAFICO = [
    (
        "¿Cuál consideras que es tu nivel previo en programación?",
        "Nivel previo en programación",
        "nivel_previo.png",
        "unica",
    ),
    (
        "¿Has tenido contacto previo con algún lenguaje de programación? (Puedes marcar varios)",
        "Lenguajes de programación conocidos",
        "lenguajes.png",
        "multiple",
    ),
    (
        "¿Cuál crees que será tu mayor desafío a la hora de aprender a programar?",
        "Mayor desafío percibido",
        "desafio.png",
        "unica",
    ),
    (
        "¿Trabajas en el campo de la tecnología (IT)?",
        "¿Trabaja actualmente en el campo de IT?",
        "trabaja_it.png",
        "unica",
    ),
    (
        "Edad:",
        "Edad",
        "edad.png",
        "unica",
    ),
    (
        "Ocupación:",
        "Ocupación",
        "ocupacion.png",
        "multiple",
    ),
    (
        "Gustos e Intereses (pueden ser múltiples):",
        "Gustos e intereses",
        "gustos.png",
        "multiple",
    ),
    (
        "Provincia",
        "Provincia",
        "provincia.png",
        "unica",
    ),
]

# La provincia se escribió con mayúsculas/minúsculas y abreviaturas distintas
# (ej: "bs as", "Bs As", "Buenos aires"). Acá la normalizamos para que no
# queden separadas en el gráfico como si fueran cosas distintas.
NORMALIZACION_PROVINCIA = {
    "bs as": "Buenos Aires",
    "buenos aires": "Buenos Aires",
    "santa fe": "Santa Fe",
    "rio negro": "Río Negro",
    "río negro": "Río Negro",
    "caba": "CABA",
    "capital federal": "CABA",
    "ciudad autonoma de bs as": "CABA",
    "ciudad autónoma de bs as": "CABA",
}

# Preguntas de texto libre: se muestran como listado de respuestas, no se grafican.
PREGUNTAS_TEXTO_LIBRE = [
    (
        "¿Qué tipo de contenido te gustaría ver en futuras clases o actividades?"
        "Que temas te interesan para ver en la materia Programación 1. "
        "Que Programas te gustaría realizar ?",
        "Contenido que les gustaría ver en clase",
    ),
    (
        "¿Tienes alguna sugerencia para mejorar el ambiente en clase?",
        "Sugerencias para mejorar el ambiente en clase",
    ),
    (
        "¿Que te parece que se puede hacer para incentivar uso de las camaras en las clases?",
        "Ideas para incentivar el uso de cámaras",
    ),
    (
        "Algún libro / video / documento sobre IT que te gustó para recomendar ?",
        "Recomendaciones de IT (libros, videos, documentos)",
    ),
    (
        "Libros o películas en general para recomendar?",
        "Recomendaciones de libros o películas",
    ),
    (
        "Pregunta abierta, considera poner lo que quieras..",
        "Pregunta abierta",
    ),
]

# Resumen de las respuestas de cada pregunta de texto libre (todos escribieron
# cosas distintas, así que no se pueden graficar). Se procesó con IA a partir
# de las respuestas del CSV y se dejó escrito acá a mano: si se actualizan las
# respuestas en el CSV, hay que volver a pedir el resumen y actualizar estas
# variables manualmente, no se regenera solo.
RESUMENES_IA = {
    "Contenido que les gustaría ver en clase": (
        "Piden sobre todo contenido práctico y herramientas concretas: Python, Git/GitHub, "
        "VS Code y el manejo de la terminal. Aparecen varios pedidos de librerías "
        "(pandas, tkinter, expresiones regulares y, en el extremo más avanzado, TensorFlow "
        "o PyTorch), además de estructuras de datos, manejo de archivos, análisis de tablas "
        "con gráficos y desarrollo de páginas web. También hay quien quiere aprender a "
        "detectar errores pensando en un futuro puesto de analista, y quien dice que el "
        "contenido actual ya es el adecuado para arrancar."
    ),
    "Sugerencias para mejorar el ambiente en clase": (
        "Casi todas las respuestas son de conformidad: no tienen sugerencias porque el "
        "ambiente les parece bueno. Varios destacan que las clases son dinámicas y "
        "prácticas, y más de uno remarca que es la materia mejor adaptada al formato y la "
        "que más les gusta por la metodología de enseñanza."
    ),
    "Ideas para incentivar el uso de cámaras": (
        "Las propuestas apuntan a generar confianza y comodidad en el grupo, y a dedicar "
        "tiempo a resolver problemas entre todos; alguien sugiere directamente que ciertos "
        "días sea obligatoria. Del otro lado hay quien cuenta que se le complica prenderla "
        "por convivir con gente en una casa chica, y quien aclara que no le molesta ni "
        "que se use ni que no se use. Una persona cuenta que esta es la única clase "
        "en la que la prende y que no le molestaría que fuera así en todas."
    ),
    "Recomendaciones de IT (libros, videos, documentos)": (
        "La mitad contesta que no tiene ninguna recomendación a mano. Entre quienes sí "
        "responden, lo más citado es YouTube como fuente habitual (dos menciones), y "
        "aparecen además la documentación de MDN y W3Schools con Stack Overflow como "
        "comunidad, canales en inglés sobre IA (mencionan \"AI Search\") y el libro "
        "\"Fundamentos de ingeniería de datos\", de Joe Reis y Matt Housley."
    ),
    "Recomendaciones de libros o películas": (
        "Buena parte no tiene nada para recomendar en este momento. Entre quienes sí "
        "responden aparecen el anime Serial Experiments Lain, el gusto por la ciencia "
        "ficción (mencionan Proyecto Salvación como lo último visto) y, en libros, "
        "El mito de Sísifo de Albert Camus, recomendado con un 10/10."
    ),
    "Pregunta abierta": (
        "Los comentarios son en general positivos: destacan la buena predisposición del "
        "profesor y el buen ritmo al que avanza la cursada. El único pedido concreto es "
        "sumar más proyectos prácticos que permitan aplicar los conceptos aprendidos a "
        "problemas reales."
    ),
}


# ---------------------------------------------------------------------------
# Lectura de datos
# ---------------------------------------------------------------------------

def leer_respuestas():
    """Lee el CSV de la encuesta y devuelve una lista de diccionarios (uno por alumno)."""
    with open(ARCHIVO_CSV, encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        return list(lector)


# ---------------------------------------------------------------------------
# Conteo de respuestas
# ---------------------------------------------------------------------------

def contar_opcion_unica(respuestas, columna):
    """Cuenta cuántas veces aparece cada valor en una columna de opción única."""
    valores = []
    for fila in respuestas:
        valor = fila[columna].strip()
        if not valor:
            continue
        if columna == "Provincia":
            valor = NORMALIZACION_PROVINCIA.get(valor.lower(), valor)
        valores.append(valor)

    return Counter(valores)


def contar_opcion_multiple(respuestas, columna):
    """Cuenta cada opción por separado en columnas donde se eligió más de una,
    separadas por comas (ej: "Python, JavaScript, HTML / CSS (Desarrollo Web)")."""
    contador = Counter()
    for fila in respuestas:
        valor = fila[columna].strip()
        if not valor:
            continue
        opciones = valor.split(",")
        for opcion in opciones:
            opcion = opcion.strip()
            if opcion:
                contador[opcion] += 1
    return contador


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------

def generar_grafico_barras(contador, titulo, nombre_archivo):
    """Genera un gráfico de barras horizontales a partir de un Counter y lo guarda como PNG.
    Devuelve la ruta del archivo generado (relativa a output/), para usar en el HTML."""
    items = contador.most_common()
    etiquetas_completas = []
    cantidades = []
    for etiqueta, cantidad in items:
        etiquetas_completas.append(etiqueta)
        cantidades.append(cantidad)

    # Algunas respuestas son textos largos en vez de una opción corta
    # (ej: alguien que escribió su propia respuesta con sus palabras).
    # Se acortan con "…" para que no rompan el gráfico; el texto completo
    # queda igual disponible en la referencia (leyenda) de la derecha.
    etiquetas_cortas = []
    for etiqueta in etiquetas_completas:
        etiqueta_corta = textwrap.shorten(etiqueta, width=55, placeholder="…")
        etiquetas_cortas.append(etiqueta_corta)

    # Una color distinto por barra, para que se distingan mejor a simple vista.
    colores = plt.get_cmap("tab20").colors[: len(items)]

    alto = max(3, len(etiquetas_cortas) * 0.6)
    figura, ejes = plt.subplots(figsize=(9, alto))
    barras = ejes.barh(etiquetas_cortas, cantidades, color=colores)
    ejes.invert_yaxis()  # la opción más elegida queda arriba
    ejes.set_title(titulo)
    ejes.set_xlabel("Cantidad de alumnos")

    # Se envuelve en varias líneas para que una respuesta larga no estire
    # el ancho de la referencia (y de la imagen entera) sin límite.
    referencias = []
    for etiqueta, cantidad in zip(etiquetas_completas, cantidades):
        texto_referencia = f"{etiqueta} ({cantidad})"
        referencias.append(textwrap.fill(texto_referencia, width=45))
    ejes.legend(
        barras,
        referencias,
        title="Referencia",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize="small",
    )

    ruta_completa = CARPETA_GRAFICOS / nombre_archivo
    figura.savefig(ruta_completa, bbox_inches="tight")
    plt.close(figura)

    return ruta_completa.relative_to(CARPETA_SALIDA)


def generar_todos_los_graficos(respuestas):
    """Genera un gráfico por cada pregunta en PREGUNTAS_GRAFICO.
    Devuelve una lista de (titulo, ruta_imagen) para usar en el HTML."""
    CARPETA_GRAFICOS.mkdir(parents=True, exist_ok=True)

    graficos = []
    for columna, titulo, nombre_archivo, tipo in PREGUNTAS_GRAFICO:
        if tipo == "unica":
            contador = contar_opcion_unica(respuestas, columna)
        else:
            contador = contar_opcion_multiple(respuestas, columna)

        ruta_imagen = generar_grafico_barras(contador, titulo, nombre_archivo)
        graficos.append((titulo, ruta_imagen))

    return graficos


# ---------------------------------------------------------------------------
# Generación de la página web
# ---------------------------------------------------------------------------

def generar_html(respuestas, graficos):
    """Arma el archivo output/index.html con los gráficos y las respuestas de texto libre."""
    partes = [
        "<!DOCTYPE html>",
        '<html lang="es">',
        "<head>",
        '<meta charset="utf-8">',
        "<title>Encuesta social - C Datos (Miércoles)</title>",
        "<style>",
        "body { font-family: sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }",
        "h1 { text-align: center; }",
        "h2 { border-bottom: 2px solid #4C72B0; padding-bottom: 0.3rem; margin-top: 2.5rem; }",
        "img { max-width: 100%; display: block; margin: 1rem auto; }",
        "ul { line-height: 1.5; }",
        "li { margin-bottom: 0.6rem; }",
        ".resumen-ia { background: #eef3fa; border-left: 4px solid #4C72B0;"
        " padding: 0.6rem 1rem; font-style: italic; }",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>Encuesta social - C Datos (Miércoles)</h1>",
        f"<p style='text-align:center'>Total de respuestas: {len(respuestas)}</p>",
    ]

    partes.append("<h2>Gráficos</h2>")
    for titulo, ruta_imagen in graficos:
        titulo_seguro = html.escape(titulo)
        partes.append(f"<h3>{titulo_seguro}</h3>")
        partes.append(f'<img src="{ruta_imagen.as_posix()}" alt="{titulo_seguro}">')

    partes.append("<h2>Respuestas de texto libre</h2>")
    for columna, titulo in PREGUNTAS_TEXTO_LIBRE:
        respuestas_columna = []
        for fila in respuestas:
            respuesta = fila[columna].strip()
            if respuesta:
                respuestas_columna.append(respuesta)
        # Se mezclan para no mostrarlas siempre en el orden en que llegaron
        # las respuestas (ese orden no aporta nada y así queda más parejo).
        random.shuffle(respuestas_columna)

        partes.append(f"<h3>{html.escape(titulo)}</h3>")
        resumen = RESUMENES_IA.get(titulo)
        if resumen:
            partes.append(
                '<p class="resumen-ia"><strong>Resumen (procesado con IA):</strong> '
                f"{html.escape(resumen)}</p>"
            )
        if respuestas_columna:
            partes.append("<ul>")
            for respuesta in respuestas_columna:
                partes.append(f"<li>{html.escape(respuesta)}</li>")
            partes.append("</ul>")
        else:
            partes.append("<p><em>Sin respuestas.</em></p>")

    partes.append("</body>")
    partes.append("</html>")

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    ruta_html = CARPETA_SALIDA / "index.html"
    ruta_html.write_text("\n".join(partes), encoding="utf-8")
    return ruta_html


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def main():
    respuestas = leer_respuestas()
    graficos = generar_todos_los_graficos(respuestas)
    ruta_html = generar_html(respuestas, graficos)
    print(f"Listo. Abrí {ruta_html} en el navegador para ver el resultado.")


if __name__ == "__main__":
    main()
