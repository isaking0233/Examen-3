-- Dimensiones
CREATE TABLE IF NOT EXISTS DimTiempo (
  id_tiempo   SERIAL     PRIMARY KEY,
  fecha       DATE       NOT NULL,
  semestre    VARCHAR(6) NOT NULL,
  año         INTEGER    NOT NULL,
  trimestre   SMALLINT   NOT NULL
);

CREATE TABLE IF NOT EXISTS DimEstudiante (
  id_estudiante   SERIAL PRIMARY KEY,
  nombre          TEXT   NOT NULL,
  genero          CHAR(1),
  fecha_nacimiento DATE,
  programa        TEXT   NOT NULL,
  año_ingreso     SMALLINT NOT NULL
);

CREATE TABLE IF NOT EXISTS DimAsignatura (
  id_asignatura   SERIAL PRIMARY KEY,
  nombre_asignatura TEXT NOT NULL,
  nivel           VARCHAR(20),
  creditos        SMALLINT NOT NULL,
  departamento    TEXT   NOT NULL
);

CREATE TABLE IF NOT EXISTS DimProfesor (
  id_profesor     SERIAL PRIMARY KEY,
  nombre_profesor TEXT   NOT NULL,
  departamento    TEXT   NOT NULL,
  grado_academico TEXT
);

CREATE TABLE IF NOT EXISTS DimModalidad (
  id_modalidad   SERIAL PRIMARY KEY,
  tipo_modalidad TEXT   NOT NULL
);

-- Hechos
CREATE TABLE IF NOT EXISTS FactCalificaciones (
  id_fact         SERIAL     PRIMARY KEY,
  id_estudiante   INTEGER    NOT NULL REFERENCES DimEstudiante(id_estudiante),
  id_asignatura   INTEGER    NOT NULL REFERENCES DimAsignatura(id_asignatura),
  id_profesor     INTEGER    NOT NULL REFERENCES DimProfesor(id_profesor),
  id_tiempo       INTEGER    NOT NULL REFERENCES DimTiempo(id_tiempo),
  id_modalidad    INTEGER    NOT NULL REFERENCES DimModalidad(id_modalidad),
  calificacion    NUMERIC(5,2) NOT NULL,
  creditos        SMALLINT      NOT NULL
);

-- Índices OLAP
CREATE INDEX IF NOT EXISTS idx_fact_tiempo      ON FactCalificaciones(id_tiempo);
CREATE INDEX IF NOT EXISTS idx_fact_estudiante  ON FactCalificaciones(id_estudiante);
CREATE INDEX IF NOT EXISTS idx_fact_asignatura  ON FactCalificaciones(id_asignatura);
CREATE INDEX IF NOT EXISTS idx_fact_profesor    ON FactCalificaciones(id_profesor);
CREATE INDEX IF NOT EXISTS idx_fact_modalidad   ON FactCalificaciones(id_modalidad);
