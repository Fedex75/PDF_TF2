'''Data functions'''
import re
from utils import text_between, read_pdf, filter_empty_lines

def get_data_C(lines, id_pdf):
    '''Extract data from PDF type C'''
    result = []
    frigorifico = (text_between(lines[0], "", "   "))
    fecha = text_between(lines[3], "el:","al").strip()

    count = 0
    entrada_table_start_height = 0
    entrada_table_end_height = 0

    salida_table_start_height = 0
    salida_table_end_height = 0

    for i, line in enumerate(lines):
        if line[0] == '-':
            count += 1
            if count == 2:
                entrada_table_start_height = i + 1
            if count == 3:
                entrada_table_end_height = i
            if count == 4:
                salida_table_start_height = i + 1
            if count == 5:
                salida_table_end_height = i

    cl_left = lines[5].index("CL")

    for i in range(entrada_table_start_height, entrada_table_end_height):
        linea = lines[i]
        if i == entrada_table_start_height:
            linea = linea.replace("ENTRADA", "       ")
        izq = linea[:cl_left].strip().split()
        data_id = izq[0]
        producto = " ".join(izq[1:])
        der = linea[cl_left:].strip().split()
        cl = der[0]
        unidades = der[1]
        kg = der[2].replace(",","")

        result.append(f"{fecha},{frigorifico},ENTRADA,{data_id},{producto},{cl},{unidades},{kg},{id_pdf}")

    for i in range(salida_table_start_height, salida_table_end_height):
        linea = lines[i]
        if i == salida_table_start_height:
            linea = linea.replace("SALIDA", "      ")
        izq = linea[:cl_left].strip().split()
        data_id = izq[0]
        producto = " ".join(izq[1:])
        der = linea[cl_left:].strip().split()
        cl = der[0]
        unidades = der[1]
        kg = der[2].replace(",","")

        result.append(f"{fecha},{frigorifico},SALIDA,{data_id},{producto},{cl},{unidades},{kg},{id_pdf}")

    return result

def process_pdf_C(path, id_pdf):
    '''Process PDF using C method'''
    reader = read_pdf(path)
    lines = []
    for page in reader.pages:
        lines.extend(page.extract_text().split('\n'))

    lines = filter_empty_lines(lines)

    indeces = []
    for i, line in enumerate(lines):
        if line[0] == '(':
            indeces.append(i-2)
    indeces.append(len(lines))

    result = []
    for i in range(len(indeces) - 1):
        result.extend(get_data_C(lines[indeces[i]:indeces[i + 1]], id_pdf))

    return result

def get_data_D(lines, id_pdf):
    '''Extract data from PDF type D'''
    result = []

    consignatario = ' '.join(lines[0].split()[0:-5])

    for line in lines:
        if "desde el:" in line:
            fechas = text_between(line, "desde el:", "D:").strip().split("al")
            fecha_inicio = fechas[0].strip()
            fecha_fin = fechas[1].strip()
            break

    for line in lines:
        if "Destino" in line:
            print(line)
            index_destino = line.index("Destino")
            index_conse = line.index("Conse")
            index_marca = line.index("Marca")
            index_tropa = line.index("Tropa-Lt") - 1
            index_piezas = line.index("Piezas") - 1
            index_uni = line.index("Uni.") - 1
            index_cl = line.index("Cl") - 1
            index_kilos = line.index("Kilos") - 1

    inicio_tabla_entrada = 0
    i = 0
    while i < len(lines):
        if lines[i] != "Entrada Despostada":
            i += 1
        else:
            inicio_tabla_entrada = i
            break

    fin_tabla_entrada = 0
    i = 0
    while i < len(lines):
        if lines[i][0] != "=":
            i += 1
        else:
            fin_tabla_entrada = i
            break

    for i in range(inicio_tabla_entrada + 1, fin_tabla_entrada - 4):
        if lines[i].split()[0].strip().isnumeric():
            cod_prod = lines[i].split()[0].strip()
            producto = " ".join(lines[i][:index_destino].strip().split()[1:])
            destino = lines[i][index_destino:index_conse].strip()
            cl = lines[i][index_cl:index_tropa].strip()
            tropa = lines[i][index_tropa:index_piezas].strip()
            uni = lines[i][index_piezas:index_uni+4].strip()
            kilos = lines[i][index_uni+4:index_kilos+5].strip().replace(",","")

            result.append(f"{consignatario},{fecha_inicio},{fecha_fin},ENTRADA,{cod_prod},{producto},{destino},,,{cl},,{tropa},{uni},{kilos},{id_pdf}")

    i = fin_tabla_entrada + 1
    fin_tabla_salida = 0
    while i < len(lines):
        if lines[i].strip()[0] != "-":
            i += 1
        else:
            fin_tabla_salida = i
            break

    for i in range(fin_tabla_entrada + 2, fin_tabla_salida):
        if lines[i].split()[0].strip().isnumeric():
            print(lines[i])
            cod_prod = lines[i].split()[0].strip()
            producto = " ".join(lines[i][:index_destino].strip().split()[1:])
            destino = lines[i][index_destino:index_conse].strip()
            conse = lines[i][index_conse:index_marca].strip()
            marca = lines[i][index_marca:index_cl].strip()

            piezas = lines[i][index_tropa+8:index_piezas+6].strip().replace(",","")
            uni = lines[i][index_piezas+7:index_uni+5].strip().replace(",","")
            kilos = lines[i][index_uni+5:index_kilos+6].strip().replace(",","")

            result.append(f"{consignatario},{fecha_inicio},{fecha_fin},SALIDA,{cod_prod},{producto},{destino},{conse},{marca},,{piezas},,{uni},{kilos},{id_pdf}")

    return result

def process_pdf_D(path, id_pdf):
    '''Extract data from PDF type D'''
    reader = read_pdf(path)
    lines = []
    for page in reader.pages:
        lines.extend(page.extract_text().split('\n'))

    lines = filter_empty_lines(lines)

    indices = []
    for i, line in enumerate(lines):
        if line[0] == '(':
            indices.append(i-2)
    indices.append(len(lines))

    result = []
    for i in range(len(indices) - 1):
        result.extend(get_data_D(lines[indices[i]:indices[i + 1]], id_pdf))

    return result

def get_data_F(lines, id_pdf):
    '''Extract data from PDF type F'''
    # Obtener info encabezado

    indices = [m.start() for m in re.finditer('/', lines[0])]
    if len(indices) > 0:
        consignatario = lines[0][indices[0] + 1 : indices[1]].strip()
        razon_social = lines[0][indices[1] + 1 :].strip()
    else:
        consignatario = lines[0].strip()
        razon_social = consignatario

    #localidad = lines[1][18:index_cuit].strip()
    localidad = text_between(lines[1], "Procedencia:", "CUIT:").split("-")[1].strip()
    cuit = text_between(lines[1], "CUIT:", "RENSPA:")
    renspa = text_between(lines[1], "RENSPA:", "- DTE:")
    dte = text_between(lines[1], "DTE:", "")
    tropa_nro = text_between(lines[3], "TROPA NRO..:", "-").replace(",", ".")
    nro_guia = text_between(lines[4], "NRO.DE GUIA:", "CABEZAS FAENADAS:")
    fecha_faena = text_between(lines[3], "FECHA DE FAENA:", "")
    romaneo = text_between(lines[4], "ROMANEO INT.#.:", "").replace(",", ".")

    print("Procesando tabla: " + consignatario + " " + razon_social + " " + fecha_faena)

    # Hallar inicio de la tabla de kilos

    count = 0
    table_start_height = 0
    for i, line in enumerate(lines):
        if line[0] == '=':
            count += 1
            if count == 2:
                table_start_height = i + 1

    # Hallar posicion de los separadores verticales

    count = 0
    kilo_table_left = 0
    kilo_table_right = 0
    total_names_right = 0
    for i in range(len(lines[table_start_height])):
        if lines[table_start_height][i] == '|':
            count += 1
            if count == 2:
                kilo_table_left = i + 1
            if count == 3:
                kilo_table_right = i
            if count == 4:
                total_names_right = i

    kgvtot = 0
    for line in lines[table_start_height:]:
        if line[kilo_table_right + 1:total_names_right].strip() == "KGVTOT":
            kgvtot = int(line[total_names_right + 1:-1])

    # Hallar ultima fila

    last_table_line = len(lines) - 2
    while lines[last_table_line][1] == " ":
        last_table_line -= 1
    last_table_line += 1

    # Crear tabla de IDs

    result = []
    for i in range(table_start_height, last_table_line, 2):
        ids = (lines[i][kilo_table_left:kilo_table_right]).split()
        kilos = (lines[i+1][kilo_table_left:kilo_table_right]).split()
        info = (lines[i+1][1:kilo_table_left-1]).split()

        for j in range(len(ids)):
            result.append(f"{info[0]},{info[1]},{info[2]},{ids[j]},{kilos[j]},{kgvtot},{consignatario},{razon_social},{localidad},{cuit},{renspa},{dte},{tropa_nro},{nro_guia},{fecha_faena},{romaneo},{id_pdf}")

    return result

def process_pdf_F(path, id_pdf):
    '''Process PDF using F method'''
    reader = read_pdf(path)
    lines = []
    for page in reader.pages:
        lines.extend(page.extract_text().split('\n'))

    lines = filter_empty_lines(lines)

    indeces = []
    for i, line in enumerate(lines):
        if line[0] == '(':
            indeces.append(i)
    indeces.append(len(lines))

    result = []
    for i in range(len(indeces) - 1):
        result.extend(get_data_F(lines[indeces[i]:indeces[i + 1]], id_pdf))

    return result
