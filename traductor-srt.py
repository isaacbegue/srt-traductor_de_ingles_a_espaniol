import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import pysrt
from deep_translator import GoogleTranslator
import threading

def select_srt_files():
    file_paths = filedialog.askopenfilenames(
        title="Seleccionar Archivos de Subtítulos",
        filetypes=[("Archivos de subtítulos", "*.srt")]
    )
    if file_paths:
        entry_srt_paths.delete(0, tk.END)
        entry_srt_paths.insert(0, ";".join(file_paths))

def translate_srt_files_thread():
    # Deshabilitar el botón de traducir
    button_translate.config(state=tk.DISABLED)
    # Actualizar el mensaje de estado
    status_label.config(text="Procesando...")
    # Iniciar la barra de progreso
    progress_bar['value'] = 0
    progress_bar.pack(pady=10)  # Mostrar la barra de progreso

    def task():
        input_paths = entry_srt_paths.get().split(";")
        
        print(f"DEBUG: input_paths={input_paths}")
        
        if not input_paths:
            messagebox.showwarning("Error de Entrada", "Por favor, selecciona al menos un archivo SRT.")
            button_translate.config(state=tk.NORMAL)
            status_label.config(text="")
            progress_bar.pack_forget()  # Ocultar la barra de progreso
            return

        # Abrir un diálogo para seleccionar la carpeta de salida
        output_dir = filedialog.askdirectory(title="Seleccionar Directorio de Salida")

        print(f"DEBUG: output_dir={output_dir}")

        if not output_dir:
            button_translate.config(state=tk.NORMAL)
            status_label.config(text="")
            progress_bar.pack_forget()  # Ocultar la barra de progreso
            return  # El usuario canceló la selección del directorio

        try:
            translator = GoogleTranslator(source='auto', target='es')

            total_files = len(input_paths)
            for idx, input_path in enumerate(input_paths):
                subs = pysrt.open(input_path)
                translated_subs = pysrt.SubRipFile()

                print(f"DEBUG: Traduciendo {input_path}")

                for sub in subs:
                    # Traducir el texto
                    try:
                        translated_text = translator.translate(sub.text)
                    except Exception as e:
                        print(f"DEBUG: Error al traducir el texto: {sub.text}\nError: {e}")
                        translated_text = sub.text  # Mantener original si falla la traducción
                        # Mostrar la caja de logs si ocurre un error
                        text_log.pack(pady=5)
                        # Registrar el error en la caja de mensajes
                        text_log.insert(tk.END, f"Error al traducir: {sub.text}\nError: {e}\n")
                        text_log.see(tk.END)

                    # Crear un nuevo subtítulo
                    new_sub = pysrt.SubRipItem(index=sub.index, start=sub.start, end=sub.end, text=translated_text)
                    translated_subs.append(new_sub)

                # Guardar los subtítulos traducidos
                base_name = os.path.basename(input_path)
                file_name, _ = os.path.splitext(base_name)
                output_file = os.path.join(output_dir, f"{file_name}_es.srt")

                translated_subs.save(output_file, encoding='utf-8')
                print(f"DEBUG: Guardado {output_file}")

                # Actualizar la barra de progreso
                progress = int(((idx + 1) / total_files) * 100)
                progress_bar['value'] = progress
                root.update_idletasks()

            messagebox.showinfo("Éxito", f"Subtítulos traducidos exitosamente y guardados en {output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")
            print(f"DEBUG: Detalles de la excepción: {e}")
            # Mostrar la caja de logs si ocurre un error
            text_log.pack(pady=5)
            text_log.insert(tk.END, f"Error inesperado: {e}\n")
            text_log.see(tk.END)
        finally:
            button_translate.config(state=tk.NORMAL)
            status_label.config(text="")
            progress_bar['value'] = 0
            progress_bar.pack_forget()  # Ocultar la barra de progreso

    threading.Thread(target=task).start()

# Crear la ventana principal
root = tk.Tk()
root.title("Traductor de Subtítulos")
root.geometry("600x400")

# Rutas de archivos SRT
label_srt_paths = tk.Label(root, text="Traducir archivos .srt")
label_srt_paths.pack(pady=10)
entry_srt_paths = tk.Entry(root, width=60)
entry_srt_paths.pack(pady=5)
button_browse_srts = tk.Button(root, text="Cargar archivo", command=select_srt_files)
button_browse_srts.pack(pady=5)

# Botón para traducir
button_translate = tk.Button(root, text="Traducir Subtítulos", command=translate_srt_files_thread)
button_translate.pack(pady=20)

# Barra de progreso (no se muestra inicialmente)
progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')

# Etiqueta de estado
status_label = tk.Label(root, text="")
status_label.pack()

# Caja de texto para logs (no se muestra inicialmente)
text_log = tk.Text(root, height=5, width=70)

# Iniciar la aplicación
root.mainloop()
