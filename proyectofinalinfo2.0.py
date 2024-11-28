import mysql.connector
from mysql.connector import Error
import os
import json
import datetime  # Para manejar las fechas



#Crea una base de datos en MySQL.

def connect_mysql(SERVER, USER, PASSWD, DB=None):
    """
    Conecta al servidor MySQL y retorna la conexión.
    """
    try:
        conn = mysql.connector.connect(
            host=SERVER,
            user=USER,
            password=PASSWD,
            database=DB,
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None
   

# Función de autenticación
def authenticate():
    """
    Función de autenticación basada en un archivo JSON.
    """
    try:
        with open("login.json", "r") as file:
            credentials = json.load(file)
        if "credentials" in credentials:
            username = credentials["credentials"].get("username")
            password = credentials["credentials"].get("password_hash")
            if username == "admin_hospital" and password == "test1234*":
                print("Autenticación exitosa.")
                return True
        print("Credenciales incorrectas.")
        return False
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error al procesar el archivo de credenciales: {e}")
        return False


# Función genérica para obtener datos de una tabla
def obtener_info_mysql(SERVER,USER,PASSWD,DB,tabla):
    conn = connect_mysql(SERVER,USER,PASSWD,DB)
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {tabla}"
        cursor.execute(query)
        resultados = cursor.fetchall()
        return resultados
    except mysql.connector.Error as err:
        print(f"Error al obtener datos de la tabla {tabla}: {err}")
        return []
    finally:
        if conn:
            conn.close()

# Función genérica para agregar datos a una tabla
def agregar_info_mysql(SERVER,USER, PASSWD,DB,tabla,datos):
    conn = connect_mysql(SERVER,USER,PASSWD,DB)
    if not conn:
        return
    try:
        cursor = conn.cursor()
        columnas = ", ".join(datos.keys())
        valores = ", ".join(["%s"] * len(datos))
        query = f"INSERT INTO {tabla} ({columnas}) VALUES ({valores})"
        cursor.execute(query, list(datos.values()))
        conn.commit()
        print("Información añadida correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al insertar datos en la tabla {tabla}: {err}")
    finally:
        conn.close()

# Función genérica para editar datos en una tabla
def editar_info_mysql(SERVER, USER, PASSWD, DB,tabla, id_registro, datos):
    conn = connect_mysql(SERVER, USER, PASSWD, DB)
    if not conn:
        return
    try:
        cursor = conn.cursor()
        set_clause = ", ".join([f"{k} = %s" for k in datos.keys()])
        query = f"UPDATE {tabla} SET {set_clause} WHERE id = %s"
        cursor.execute(query, list(datos.values()) + [id_registro])
        conn.commit()
        print("Información actualizada correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al actualizar datos en la tabla {tabla}: {err}")
    finally:
        if conn:
            conn.close()

# Función genérica para eliminar datos de una tabla
def eliminar_info_mysql(SERVER, USER, PASSWD, DB,tabla, id_registro):
    conn = connect_mysql(SERVER, USER, PASSWD, DB)
    
    try:
        cursor = conn.cursor()
        query = f"DELETE FROM {tabla} WHERE id = %s"
        cursor.execute(query, (id_registro,))
        conn.commit()
        print("Información eliminada correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al eliminar datos de la tabla {tabla}: {err}")
    finally:
        if conn:
            conn.close()


# Función para exportar datos a un archivo JSON
def exportar_a_json(data, nombre_tabla, contador_query):
    if not os.path.exists("Queries"):
        os.makedirs("Queries")

    # Convertir fechas a texto para serializar correctamente
    def convertir_fechas(obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()  # Formato ISO (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
        elif isinstance(obj, datetime.timedelta):
            # Convertimos el timedelta a segundos para poder serializarlo
            return str(obj.total_seconds())  # O usar obj.days si prefieres días
        raise TypeError(f"Tipo de dato {type(obj)} no serializable por JSON.")

    with open(f"Queries/{nombre_tabla}_{contador_query}.json", "w") as file:
        json.dump(data, file, indent=4, default=convertir_fechas)

# Creación de tablas
def crear_tablas(SERVER, USER, PASSWD,DB):
    conn = connect_mysql(SERVER, USER, PASSWD,DB)
    if not conn:
        return
    try:
        cursor = conn.cursor()
        MEDICOS = '''
        CREATE TABLE IF NOT EXISTS `medicos` (
            `ID` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `Nombre` CHAR(100),
            `Apellido` CHAR(100),
            `Especialidad` CHAR(100),
            `Telefono` CHAR(50),
            `Correo` CHAR(100),
            PRIMARY KEY (`ID`)
        ) ENGINE=INNODB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
        '''
        cursor.execute(MEDICOS)

        PACIENTES = '''
        CREATE TABLE IF NOT EXISTS `pacientes` (
            `ID` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `Nombre` CHAR(100),
            `Apellido` CHAR(100),
            `Nacimiento` DATE,
            `Genero` CHAR(1),
            `Direccion` CHAR(250),
            `Telefono` CHAR(100),
            PRIMARY KEY (`ID`)
        ) ENGINE=INNODB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
        '''
        cursor.execute(PACIENTES)

        H_MED = '''
        CREATE TABLE IF NOT EXISTS `Historia_medica` (
            `ID` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `ID_paciente` INT(10) UNSIGNED NOT NULL,
            `Fecha_visita` DATE,
            `Diagnostico` CHAR(250),
            `Tratamiento` CHAR(250),
            `Notas` TEXT,
            PRIMARY KEY (`ID`)
        ) ENGINE=INNODB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
        '''
        cursor.execute(H_MED)

        CITAS = '''
        CREATE TABLE IF NOT EXISTS `citas` (
            `ID` INT(10) NOT NULL AUTO_INCREMENT,
            `ID_paciente` INT(10),
            `ID_medico` INT(10),
            `Fecha_cita` DATE,
            `Hora_cita` TIME,
            `Razon_cita` TEXT DEFAULT NULL,
            PRIMARY KEY (`ID`)
        ) ENGINE=INNODB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
        '''
        cursor.execute(CITAS)

        conn.commit()
        print("Tablas creadas correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al crear tablas: {err}")
    finally:
        if conn:
            conn.close()




# Menú principal del programa
def main():
    SERVER = "localhost"
    USER = "root"
    PASSWD = "bio123"
    DB = 'general_hospital'

    # Crear base de datos
    conn = connect_mysql(SERVER, USER, PASSWD)
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB}")
            print(f"Base de datos '{DB}' creada o ya existente.")
            conn.close()
        except Exception as e:
            print(f"Error al crear la base de datos: {e}")

    # Crear tablas    
    crear_tablas(SERVER, USER, PASSWD,DB)

    # Autenticación
    if not authenticate():
        return
    
    # Menú principal del programa
    contador_query = 1
    while True:
        print("\n1. Consultar tabla\n2. Ingresar datos\n3. Editar información\n4. Eliminar información\n5. Salir")
        opcion = input("Ingrese opción: ")

        if opcion == "1":
            tabla = input("Ingrese el nombre de la tabla (medicos, pacientes, historia_medica, citas): ")
            data_mysql = obtener_info_mysql(SERVER,USER,PASSWD,DB,tabla)
            if data_mysql:
                exportar_a_json(data_mysql, tabla, contador_query)
                print(f"Consulta exportada en Queries/{tabla}_{contador_query}.json")
                contador_query += 1
            else:
                print(f"No se encontraron datos en la tabla {tabla}.")

        elif opcion == "2":
            tabla = input("Ingrese el nombre de la tabla (medicos, pacientes, historia_medica, citas): ")
            datos = {}
            if tabla == "medicos":
                datos = {
                    "Nombre": input("Nombre: "),
                    "Apellido": input("Apellido: "),
                    "Especialidad": input("Especialidad: "),
                    "Telefono": input("Teléfono: "),
                    "Correo": input("Correo: ")
            }
            elif tabla == "pacientes":
                datos = {
                    "Nombre": input("Nombre: "),
                    "Apellido": input("Apellido: "),
                    "Nacimiento": input("Fecha de nacimiento (YYYY-MM-DD): "),
                    "Genero": input("Género (M/F): "),
                    "Direccion": input("Dirección: "),
                    "Telefono": input("Teléfono: ")
                }
            elif tabla == "historia_medica":
                datos = {
                        "ID_paciente": input("ID Paciente: "),
                        "Fecha_visita": input("Fecha de visita (YYYY-MM-DD): "),
                        "Diagnostico": input("Diagnóstico: "),
                        "Tratamiento": input("Tratamiento: "),
                        "Notas": input("Notas: ")
                    }
            elif tabla == "citas":
                datos = {
                    "ID_paciente": input("ID Paciente: "),
                    "ID_medico": input("ID Médico: "),
                    "Fecha_cita": input("Fecha de cita (YYYY-MM-DD): "),
                    "Hora_cita": input("Hora de cita (HH:MM:SS): "),
                    "Razon_cita": input("Razón de la cita: ")
                }
            agregar_info_mysql(SERVER, USER, PASSWD,DB,tabla,datos)
            
            print("Datos ingresados:")
            for key, value in datos.items():
                print(f"{key}: {value}")


        elif opcion == "3":
            tabla = input("Ingrese el nombre de la tabla (medicos, pacientes, historia_medica, citas): ")
            id_registro = int(input("Ingrese el ID del registro a editar: "))
            datos = {}
            if tabla == "medicos":
                datos = {
                    "Nombre": input("Nombre: "),
                    "Apellido": input("Apellido: "),
                    "Especialidad": input("Especialidad: "),
                    "Telefono": input("Teléfono: "),
                    "Correo": input("Correo: ")
                }
            elif tabla == "pacientes":
                datos = {
                    "Nombre": input("Nombre: "),
                    "Apellido": input("Apellido: "),
                    "Nacimiento": input("Fecha de nacimiento (YYYY-MM-DD): "),
                    "Genero": input("Género (M/F): "),
                    "Direccion": input("Dirección: "),
                    "Telefono": input("Teléfono: ")
                }
            elif tabla == "historia_medica":
                datos = {
                    "ID_paciente": input("ID Paciente: "),
                    "Fecha_visita": input("Fecha de visita (YYYY-MM-DD): "),
                    "Diagnostico": input("Diagnóstico: "),
                    "Tratamiento": input("Tratamiento: "),
                    "Notas": input("Notas: ")
                }
            elif tabla == "citas":
                datos = {
                    "ID_paciente": input("ID Paciente: "),
                    "ID_medico": input("ID Médico: "),
                    "Fecha_cita": input("Fecha de cita (YYYY-MM-DD): "),
                    "Hora_cita": input("Hora de cita (HH:MM:SS): "),
                    "Razon_cita": input("Razón de la cita: ")
                }
            editar_info_mysql(SERVER,USER,PASSWD,DB,tabla, id_registro, datos)
            print("Datos Editados:")
            for key, value in datos.items():
                print(f"{key}: {value}")

        elif opcion == "4":
            tabla = input("Ingrese el nombre de la tabla (medicos, pacientes, historia_medica, citas): ")
            id_registro = int(input("Ingrese el ID del registro a eliminar: "))
            eliminar_info_mysql(SERVER,USER,PASSWD,DB,tabla, id_registro)

        elif opcion == "5":
            print("Saliendo del programa...")
            break

        else:
            print("Opción no válida. Intente de nuevo.")


if __name__ == "__main__":
    main()            