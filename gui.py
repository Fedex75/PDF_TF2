'''GUI'''
import os
import threading
import datetime
import math
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import utils
import data

# Definitions
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300

PRIMARY_TEXT_COLOR = '#dfe6e9'
SECONDARY_TEXT_COLOR = '#636e72'

class Manager:
    '''Window state manager'''
    files_are_hovering = False
    files_have_dropped = False
    number_of_files_dropped = 0
    number_of_files_processed = 0
    number_of_files_with_error = 0
    error = ''
    finished_processing = False
    timestamp_processing_start = 0

    def update_canvas(self):
        '''Render graphics on the canvas'''
        canvas.delete('all')
        canvas.create_rectangle(-1, -1, WINDOW_WIDTH, WINDOW_HEIGHT, fill='#2d3436')

        if self.error != '' and (not self.files_are_hovering):
            draw_error()
        elif (not self.files_are_hovering) and (self.files_have_dropped or self.finished_processing):
            draw_processing_files()
        else:
            draw_drop_zone()

    def set_start_processing(self, number_of_files):
        '''Set state to Processing'''
        self.files_are_hovering = False
        self.files_have_dropped = True
        self.number_of_files_dropped = number_of_files
        self.number_of_files_processed = 0
        self.number_of_files_with_error = 0
        self.error = ''
        self.finished_processing = False
        self.timestamp_processing_start = datetime.datetime.now()
        self.update_canvas()

    def set_finished_processing(self):
        '''Set state to Finished Processing'''
        self.files_have_dropped = False
        self.error = ''
        self.finished_processing = True
        self.timestamp_processing_start = 0
        self.update_canvas()

    def set_error(self, error):
        '''Set state to Error'''
        self.files_have_dropped = True
        self.error = error
        self.finished_processing = False
        self.timestamp_processing_start = 0
        self.number_of_files_with_error = 0
        self.update_canvas()

    def increment_processed_file_counter(self, error=False):
        '''Increment the processed file counter'''
        if error:
            self.number_of_files_with_error += 1
        else:
            self.number_of_files_processed += 1
        self.update_canvas()

def drop(event):
    '''Handle drop event'''
    if manager.files_have_dropped:
        return
    manager.files_are_hovering = False
    path_names = event.data.split()
    if len(path_names) == 1:
        if os.path.isdir(path_names[0]):
            file_names = utils.get_unique_pdf_files(path_names[0])
            manager.number_of_files_dropped = len(file_names)
            if manager.number_of_files_dropped > 0:
                basename = os.path.basename(os.path.normpath(path_names[0]))
                out_file = None
                header = None
                process_function = None
                if basename == 'faena':
                    out_file = 'datos_f.csv'
                    header = 'FECHA,FRIGORIFICO,PROCESO,ID,PRODUCTO,CL,UNIDADES,KG'
                    process_function = data.process_pdf_F
                elif basename == 'carneo':
                    out_file = 'datos_c.csv'
                    header = 'FECHA,FRIGORIFICO,PROCESO,ID,PRODUCTO,CL,UNIDADES,KG'
                    process_function = data.process_pdf_C
                elif basename == 'despostada':
                    out_file = 'datos_d.csv'
                    header = 'CONSIGNATARIO,FECHA_INICIO,FECHA_FIN,PROCESO,ID,PRODUCTO,DESTINO,CONSERVACION,MARCA,CL,PIEZAS,UNIDADES,KILOS,ID PDF'
                    process_function = data.process_pdf_D
                else:
                    manager.set_error('Carpeta desconocida')
                    return

                manager.set_start_processing(len(file_names))

                worker = threading.Thread(target=utils.csv_output, args=(path_names[0], file_names, out_file, header, process_function, manager.increment_processed_file_counter, manager.set_finished_processing))
                worker.start()
            else:
                manager.set_error('La carpeta está vacía. Nada para hacer.')

def drop_enter(_):
    '''Handle drop enter event'''
    manager.files_are_hovering = True
    manager.update_canvas()

def drop_leave(_):
    '''Handle drop leave event'''
    manager.files_are_hovering = False
    manager.update_canvas()

def draw_drop_zone():
    '''Draw rectangle and plus icon'''
    drop_zone_padding = 20
    x1, y1, x2, y2 = drop_zone_padding, drop_zone_padding, WINDOW_WIDTH - drop_zone_padding, WINDOW_HEIGHT - drop_zone_padding
    radius = 20

    points = [x1+radius, y1,
                x1+radius, y1,
                x2-radius, y1,
                x2-radius, y1,
                x2, y1,
                x2, y1+radius,
                x2, y1+radius,
                x2, y2-radius,
                x2, y2-radius,
                x2, y2,
                x2-radius, y2,
                x2-radius, y2,
                x1+radius, y2,
                x1+radius, y2,
                x1, y2,
                x1, y2-radius,
                x1, y2-radius,
                x1, y1+radius,
                x1, y1+radius,
                x1, y1]

    canvas.create_polygon(points, outline='white' if manager.files_are_hovering else 'gray', width=1, fill='', smooth=True)

    plus_size = 30
    canvas.create_line(WINDOW_WIDTH / 2 - plus_size / 2, WINDOW_HEIGHT / 2, WINDOW_WIDTH / 2 + plus_size / 2, WINDOW_HEIGHT / 2, fill=PRIMARY_TEXT_COLOR if manager.files_are_hovering else SECONDARY_TEXT_COLOR, width=4)
    canvas.create_line(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - plus_size / 2, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + plus_size / 2, fill=PRIMARY_TEXT_COLOR if manager.files_are_hovering else SECONDARY_TEXT_COLOR, width=4)
    if not manager.files_are_hovering:
        canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + plus_size, text="Arrastrá la carpeta acá", fill=SECONDARY_TEXT_COLOR)

def draw_processing_files():
    '''Draw folder icon and progress'''
    canvas.create_image(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 20, image=folder_img)
    if manager.number_of_files_dropped > 0:
        error_text_offset = 60
        if manager.finished_processing:
            canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 40, text='Completado ✔', fill='#2ecc71')
        else:
            canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 40, text=f'Procesando {manager.number_of_files_dropped} archivos', fill='gray')
            remaining_string = f'{manager.number_of_files_processed} de {manager.number_of_files_dropped}. '
            if manager.number_of_files_processed == 0:
                remaining_string += 'Calculando tiempo restante...'
            else:
                remaining_seconds = int(math.ceil((manager.number_of_files_dropped - manager.number_of_files_processed) * (datetime.datetime.now() - manager.timestamp_processing_start).total_seconds() / manager.number_of_files_processed))
                remaining_string += f'{remaining_seconds} segundo{'' if remaining_seconds == 1 else 's'} restantes...'
            canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 60, text=remaining_string, fill='gray')
            error_text_offset = 80
        if manager.number_of_files_with_error > 0:
            canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + error_text_offset, text=f'{manager.number_of_files_with_error} errores', fill='#e74c3c')

def draw_error():
    '''Draw error message'''
    canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, text=manager.error, fill='#e74c3c')

manager = Manager()

root = TkinterDnD.Tk()
root.title("PDF_TF")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.iconphoto(True, tk.PhotoImage(file='assets/AppIcon.png'))

canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, highlightthickness=0)
canvas.pack()

canvas.drop_target_register(DND_FILES)
canvas.dnd_bind('<<Drop>>', drop)
canvas.dnd_bind('<<DropEnter>>', drop_enter)
canvas.dnd_bind('<<DropLeave>>', drop_leave)

folder_img = tk.PhotoImage(file="assets/folder.png")

manager.update_canvas()

root.mainloop()
