import os
import random
import tkinter as tk
from tkinter import messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class QuizFisicaApp:
    VIDAS_INICIALES = 3
    PUNTOS_POR_ACIERTO = 10
    CANTIDAD_PREGUNTAS = 5
    ARCHIVO_PREGUNTAS = os.path.join(BASE_DIR, "preguntas.txt")
    BARAJAR_OPCIONES = True

    def __init__(self, root):
        self.root = root
        self.root.title("Quiz de Física Básica")
        self.root.geometry("680x580")
        self.root.minsize(640, 540)
        self.root.protocol("WM_DELETE_WINDOW", self.al_cerrar)

        self.nombre_jugador = ""
        self.puntaje = 0
        self.vidas = self.VIDAS_INICIALES
        self.preguntas_seleccionadas = []
        self.indice_actual = 0
        self.scale_movido = False

        self.frame_actual = None
        self.mostrar_inicio()

    # = UTILIDADES =
    def limpiar_pantalla(self):
        self.root.unbind("1")
        self.root.unbind("2")
        self.root.unbind("3")
        self.root.unbind("4")
        self.root.unbind("<Return>")
        if self.frame_actual is not None:
            self.frame_actual.destroy()

    def al_cerrar(self):
        if messagebox.askokcancel("Salir", "¿Seguro que quieres salir?"):
            self.root.destroy()

    def cargar_preguntas(self):
        if not os.path.exists(self.ARCHIVO_PREGUNTAS):
            messagebox.showerror(
                "Error de Archivo",
                f"No se encontró el archivo:\n{self.ARCHIVO_PREGUNTAS}",
            )
            return None

        validas, errores = [], []
        try:
            with open(self.ARCHIVO_PREGUNTAS, "r", encoding="utf-8-sig") as archivo:
                for num, linea in enumerate(archivo, start=1):
                    linea = linea.strip()
                    if not linea:
                        continue

                    partes = [p.strip() for p in linea.split("|")]
                    if len(partes) != 6:
                        errores.append(
                            f"Línea {num}: tiene {len(partes)} campos (se esperan 6)."
                        )
                        continue

                    pregunta, *opciones, correcta = partes

                    if not pregunta or any(not op for op in opciones):
                        errores.append(f"Línea {num}: hay campos vacíos.")
                        continue
                    if len({op.casefold() for op in opciones}) != 4:
                        errores.append(f"Línea {num}: hay opciones repetidas.")
                        continue
                    if correcta not in opciones:
                        errores.append(
                            f"Línea {num}: la respuesta correcta no coincide con"
                            " ninguna opción."
                        )
                        continue

                    validas.append(
                        {
                            "pregunta": pregunta,
                            "opciones": opciones,
                            "correcta": correcta,
                        }
                    )
        except UnicodeDecodeError:
            messagebox.showerror(
                "Error de Codificación",
                "El archivo no está guardado en UTF-8.",
            )
            return None
        except OSError as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")
            return None

        if errores:
            detalle = "\n".join(errores[:8])
            if len(errores) > 8:
                detalle += f"\n... y {len(errores) - 8} más."
            messagebox.showwarning("Líneas ignoradas", detalle)

        if len(validas) < self.CANTIDAD_PREGUNTAS:
            messagebox.showerror(
                "Preguntas Insuficientes",
                f"Se necesitan al menos {self.CANTIDAD_PREGUNTAS} preguntas válidas.\n"
                f"Actualmente hay {len(validas)}.",
            )
            return None

        seleccion = random.sample(validas, self.CANTIDAD_PREGUNTAS)

        for p in seleccion:
            if self.BARAJAR_OPCIONES:
                random.shuffle(p["opciones"])
            p["indice_correcto"] = p["opciones"].index(p["correcta"]) + 1

        return seleccion

    # = INICIO =
    def mostrar_inicio(self):
        self.limpiar_pantalla()
        self.frame_actual = tk.Frame(self.root, padx=30, pady=40)
        self.frame_actual.pack(expand=True, fill="both")

        tk.Label(
            self.frame_actual,
            text="Quiz de Física Básica",
            font=("Arial", 20, "bold"),
        ).pack(pady=(10, 25))

        tk.Label(
            self.frame_actual,
            text="Ingresa tu nombre para comenzar:",
            font=("Arial", 12),
        ).pack(pady=5)

        self.entry_nombre = tk.Entry(
            self.frame_actual, font=("Arial", 12), width=30, justify="center"
        )
        self.entry_nombre.pack(pady=10)
        self.entry_nombre.focus()
        self.root.bind("<Return>", lambda e: self.iniciar_juego())

        tk.Button(
            self.frame_actual,
            text="Iniciar Juego",
            font=("Arial", 12, "bold"),
            bg="#2e7d32",
            fg="white",
            padx=20,
            pady=8,
            command=self.iniciar_juego,
        ).pack(pady=20)

    def iniciar_juego(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Atención", "Por favor, ingresa tu nombre.")
            self.entry_nombre.focus()
            return

        preguntas = self.cargar_preguntas()
        if preguntas is None:
            return

        self.nombre_jugador = nombre
        self.preguntas_seleccionadas = preguntas
        self.puntaje = 0
        self.vidas = self.VIDAS_INICIALES
        self.indice_actual = 0

        self.mostrar_juego()

    # ================= VISTA 2: JUEGO =================
    def _al_mover_scale(self, valor):
        self.scale_movido = True
        self.lbl_seleccion.config(text=f"Opción seleccionada: {int(float(valor))}")

    def _seleccionar_con_tecla(self, num):
        self.scale_respuesta.set(num)
        self.scale_movido = True
        self.lbl_seleccion.config(text=f"Opción seleccionada: {num}")

    def mostrar_juego(self):
        self.limpiar_pantalla()
        self.scale_movido = False

        self.frame_actual = tk.Frame(self.root, padx=25, pady=20)
        self.frame_actual.pack(expand=True, fill="both")

        self.frame_actual.columnconfigure(0, weight=1)
        self.frame_actual.columnconfigure(1, weight=1)

        pregunta_data = self.preguntas_seleccionadas[self.indice_actual]

        tk.Label(
            self.frame_actual,
            text=(
                f"Jugador: {self.nombre_jugador}  |  Pregunta"
                f" {self.indice_actual + 1}/{self.CANTIDAD_PREGUNTAS}"
            ),
            font=("Arial", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 15))

        tk.Label(
            self.frame_actual,
            text=f"Puntaje: {self.puntaje}   |   Vidas: {self.vidas}",
            font=("Arial", 11, "bold"),
            fg="#2b3f57",
        ).grid(row=0, column=1, sticky="e", pady=(0, 15))

        tk.Label(
            self.frame_actual,
            text=pregunta_data["pregunta"],
            font=("Times New Roman", 16, "bold"),
            fg="#0a0a0a",
            wraplength=600,
            justify="center",
        ).grid(row=1, column=0, columnspan=2, pady=(10, 18))

        frame_opciones = tk.Frame(self.frame_actual)
        frame_opciones.grid(
            row=2, column=0, columnspan=2, pady=(0, 12), sticky="w", padx=30
        )
        for i, opcion in enumerate(pregunta_data["opciones"], start=1):
            tk.Label(
                frame_opciones,
                text=f"{i}. {opcion}",
                font=("Arial", 12),
                anchor="w",
                wraplength=560,
                justify="left",
            ).pack(anchor="w", pady=3)

        tk.Label(
            self.frame_actual,
            text="Desliza o presiona 1–4 para elegir tu respuesta:",
            font=("Arial", 10, "italic"),
        ).grid(row=3, column=0, columnspan=2, pady=(8, 0))

        self.scale_respuesta = tk.Scale(
            self.frame_actual,
            from_=1,
            to=4,
            orient="horizontal",
            tickinterval=1,
            length=320,
            font=("Arial", 11, "bold"),
            command=self._al_mover_scale,
        )
        self.scale_respuesta.grid(row=4, column=0, columnspan=2, pady=(0, 4))
        # Resetear bandera tras inicialización automática del Scale
        self.scale_movido = False

        self.lbl_seleccion = tk.Label(
            self.frame_actual,
            text="Opción seleccionada: 1",
            font=("Arial", 10, "bold"),
            fg="#37474f",
        )
        self.lbl_seleccion.grid(row=5, column=0, columnspan=2, pady=(0, 12))

        tk.Button(
            self.frame_actual,
            text="Confirmar Respuesta",
            font=("Arial", 12, "bold"),
            bg="#1976d2",
            fg="white",
            padx=15,
            pady=6,
            command=self.verificar_respuesta,
        ).grid(row=6, column=0, columnspan=2, pady=8)

        for num in (1, 2, 3, 4):
            self.root.bind(str(num), lambda e, n=num: self._seleccionar_con_tecla(n))
        self.root.bind("<Return>", lambda e: self.verificar_respuesta())

    def verificar_respuesta(self):
        seleccion_usuario = self.scale_respuesta.get()
        if not self.scale_movido and seleccion_usuario == 1:
            continuar = messagebox.askyesno(
                "Confirmar opción 1",
                "No moviste el deslizador. ¿Seguro que quieres confirmar la opción 1?",
            )
            if not continuar:
                return

        pregunta_data = self.preguntas_seleccionadas[self.indice_actual]
        indice_correcto = pregunta_data["indice_correcto"]

        if seleccion_usuario == indice_correcto:
            self.puntaje += self.PUNTOS_POR_ACIERTO
            messagebox.showinfo(
                "¡Correcto!",
                f"¡Bien hecho! Ganaste {self.PUNTOS_POR_ACIERTO} puntos.",
            )
        else:
            self.vidas -= 1
            messagebox.showerror(
                "Incorrecto",
                "Respuesta incorrecta.\nLa respuesta correcta era la"
                f" {indice_correcto}: {pregunta_data['correcta']}",
            )

        self.indice_actual += 1

        if self.vidas <= 0 or self.indice_actual >= self.CANTIDAD_PREGUNTAS:
            self.mostrar_resultados()
        else:
            self.mostrar_juego()

    # = RESULTADOS =
    def mostrar_resultados(self):
        self.limpiar_pantalla()
        self.frame_actual = tk.Frame(self.root, padx=30, pady=40)
        self.frame_actual.pack(expand=True, fill="both")

        estado = "¡Juego Completado!" if self.vidas > 0 else "¡Te quedaste sin vidas!"

        tk.Label(
            self.frame_actual,
            text="Resultados Finales",
            font=("Arial", 20, "bold"),
        ).pack(pady=(10, 20))

        tk.Label(
            self.frame_actual,
            text=(
                f"Jugador: {self.nombre_jugador}\n\n"
                f"Puntaje Final: {self.puntaje} puntos\n"
                f"Vidas Restantes: {self.vidas}"
            ),
            font=("Arial", 14),
            justify="center",
        ).pack(pady=15)

        tk.Button(
            self.frame_actual,
            text="Volver a Jugar",
            font=("Arial", 12, "bold"),
            bg="#2e7d32",
            fg="white",
            padx=20,
            pady=8,
            command=self.mostrar_inicio,
        ).pack(pady=20)

        self.root.update_idletasks()
        messagebox.showinfo("Fin del Juego", f"{estado}\nPuntaje final: {self.puntaje}")


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizFisicaApp(root)
    root.mainloop()