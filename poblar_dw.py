import os
import random
from datetime import date
from faker import Faker
import psycopg2

# Leer credenciales desde env vars
DB_CONFIG = {
    'dbname':   os.getenv('POSTGRES_DB', 'mi_dw'),
    'user':     os.getenv('POSTGRES_USER', 'dw_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'secreto123'),
    'host':     os.getenv('POSTGRES_HOST', 'db'),   # <— aquí el cambio
    'port':     os.getenv('POSTGRES_PORT', '5432'),
}

fake = Faker('es_MX')
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# 1. Poblar DimTiempo: últimos 8 semestres (16 trimestres)
def populate_dim_tiempo():
    semestres = []
    today = date.today()
    year = today.year
    # Asumimos 2 semestres por año: 'YYYY-1' (ene–jun) y 'YYYY-2' (jul–dic)
    for y in range(year - 4, year + 1):
        for s in (1, 2):
            fecha_ref = date(y, 1 if s==1 else 7, 1)
            trimestre = (s - 1) * 2 + 1
            semestres.append((fecha_ref, f"{y}-{s}", y, trimestre))
    cur.executemany("""
        INSERT INTO DimTiempo (fecha, semestre, año, trimestre)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, semestres)

# 2. Poblar DimModalidad (fijo)
def populate_dim_modalidad():
    modalidades = [('Presencial',), ('En línea',)]
    cur.executemany("""
        INSERT INTO DimModalidad (tipo_modalidad)
        VALUES (%s)
        ON CONFLICT DO NOTHING;
    """, modalidades)

# 3. Poblar DimEstudiante
def populate_dim_estudiante(n=500):
    estudiantes = []
    for _ in range(n):
        nombre = fake.name()
        genero = random.choice(['M','F','O'])
        fnac = fake.date_of_birth(minimum_age=18, maximum_age=35)
        programa = random.choice([
            'Ingeniería Civil', 'Economía', 'Medicina', 'Derecho',
            'Arquitectura', 'Ingeniería Informática'
        ])
        ingreso = random.randint(fnac.year + 18, date.today().year)
        estudiantes.append((nombre, genero, fnac, programa, ingreso))
    cur.executemany("""
        INSERT INTO DimEstudiante (nombre, genero, fecha_nacimiento, programa, año_ingreso)
        VALUES (%s, %s, %s, %s, %s);
    """, estudiantes)

# 4. Poblar DimAsignatura
def populate_dim_asignatura(lista_asigs=None):
    if lista_asigs is None:
        lista_asigs = [
            ('Cálculo I', 'Básico', 8, 'Matemáticas'),
            ('Física I', 'Básico', 7, 'Física'),
            ('Programación I', 'Básico', 6, 'Informática'),
            ('Economía I', 'Básico', 6, 'Economía'),
            ('Metodología de la Investigación', 'Intermedio', 5, 'Ciencias Sociales'),
            # … añade más asignaturas según necesites …
        ]
    cur.executemany("""
        INSERT INTO DimAsignatura (nombre_asignatura, nivel, creditos, departamento)
        VALUES (%s, %s, %s, %s);
    """, lista_asigs)

# 5. Poblar DimProfesor
def populate_dim_profesor(n=50):
    profes = []
    departamentos = ['Matemáticas','Física','Informática','Economía','Derecho','Arquitectura']
    grados = ['Lic.','MSc','PhD']
    for _ in range(n):
        profes.append((
            fake.name(),
            random.choice(departamentos),
            random.choice(grados)
        ))
    cur.executemany("""
        INSERT INTO DimProfesor (nombre_profesor, departamento, grado_academico)
        VALUES (%s, %s, %s);
    """, profes)

# 6. Poblar FactCalificaciones
def populate_fact_calificaciones(n=5000):
    # Obtener listas de IDs existentes
    cur.execute("SELECT id_tiempo FROM DimTiempo;")
    tiempos = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id_estudiante FROM DimEstudiante;")
    estudiantes = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id_asignatura FROM DimAsignatura;")
    asignaturas = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id_profesor FROM DimProfesor;")
    profesores = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id_modalidad FROM DimModalidad;")
    modalidades = [r[0] for r in cur.fetchall()]

    hechos = []
    for _ in range(n):
        id_t = random.choice(tiempos)
        id_e = random.choice(estudiantes)
        id_a = random.choice(asignaturas)
        id_p = random.choice(profesores)
        id_m = random.choice(modalidades)
        # Generar calificación con curva normal centrada en 75, desviación 15
        calif = max(0, min(100, random.gauss(75, 15)))
        # Obtener créditos de la asignatura
        cur.execute("SELECT creditos FROM DimAsignatura WHERE id_asignatura=%s;", (id_a,))
        creditos = cur.fetchone()[0]
        hechos.append((id_e, id_a, id_p, id_t, id_m, round(calif,2), creditos))

    cur.executemany("""
        INSERT INTO FactCalificaciones
        (id_estudiante, id_asignatura, id_profesor, id_tiempo, id_modalidad, calificacion, creditos)
        VALUES (%s,%s,%s,%s,%s,%s,%s);
    """, hechos)

# Ejecutar todo
if __name__ == "__main__":
    populate_dim_tiempo()
    populate_dim_modalidad()
    populate_dim_estudiante(n=500)
    populate_dim_asignatura()
    populate_dim_profesor(n=50)
    conn.commit()  # guardar dimensiones antes de los hechos
    populate_fact_calificaciones(n=5000)
    conn.commit()
    cur.close()
    conn.close()
    print("Carga de datos sintéticos completada.")
