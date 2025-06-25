from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoadDataSerializer

class LoadDataView(APIView):
    """
    POST /api/load-data/
    Recibe una lista de registros para FactCalificaciones y los inserta.
    """
    def post(self, request):
        serializer = LoadDataSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        records = serializer.validated_data

        with connection.cursor() as cur:
            args_str = ",".join(["(%s,%s,%s,%s,%s,%s,%s)"] * len(records))
            flattened = []
            for r in records:
                flattened += [
                    r['id_estudiante'],
                    r['id_asignatura'],
                    r['id_profesor'],
                    r['id_tiempo'],
                    r['id_modalidad'],
                    r['calificacion'],
                    r['creditos']
                ]
            sql = f"""
                INSERT INTO FactCalificaciones
                  (id_estudiante,id_asignatura,id_profesor,id_tiempo,id_modalidad,calificacion,creditos)
                VALUES {args_str};
            """
            cur.execute(sql, flattened)
        return Response({'inserted': len(records)}, status=status.HTTP_201_CREATED)


class AvgPerCareerView(APIView):
    """
    GET /api/analytics/average-per-career/
    Devuelve el promedio general por programa (carrera) en la dimensión estudiante.
    """
    def get(self, request):
        with connection.cursor() as cur:
            cur.execute("""
                SELECT e.programa,
                       ROUND(AVG(f.calificacion)::numeric,2) AS promedio
                  FROM FactCalificaciones f
                  JOIN DimEstudiante e ON f.id_estudiante = e.id_estudiante
                 GROUP BY e.programa
                 ORDER BY e.programa;
            """)
            rows = cur.fetchall()
        return Response([{'programa': prog, 'promedio': float(avg)} for prog,avg in rows])


class ReprobationRateView(APIView):
    """
    GET /api/analytics/reprobation-rate/
    Tasa de reprobación (> %50 de calif < 60) por departamento y semestre.
    """
    def get(self, request):
        with connection.cursor() as cur:
            cur.execute("""
              SELECT a.departamento,
                     t.semestre,
                     ROUND(
                       SUM(CASE WHEN f.calificacion < 60 THEN 1 ELSE 0 END)::numeric
                       / COUNT(*) * 100,2
                     ) AS tasa_reprobacion
                FROM FactCalificaciones f
                JOIN DimAsignatura a ON f.id_asignatura = a.id_asignatura
                JOIN DimTiempo t     ON f.id_tiempo     = t.id_tiempo
               GROUP BY a.departamento, t.semestre
               ORDER BY a.departamento, t.semestre;
            """)
            rows = cur.fetchall()
        return Response([
            {'departamento': dept, 'semestre': sem, 'tasa_reprobacion': float(rate)}
            for dept,sem,rate in rows
        ])


class GradeDistView(APIView):
    """
    GET /api/analytics/grade-distribution/
    Distribución de calificaciones A–F por modalidad.
    """
    def get(self, request):
        with connection.cursor() as cur:
            cur.execute("""
              SELECT m.tipo_modalidad,
                     SUM(CASE WHEN f.calificacion>=90 THEN 1 ELSE 0 END) AS A,
                     SUM(CASE WHEN f.calificacion>=80 AND f.calificacion<90 THEN 1 ELSE 0 END) AS B,
                     SUM(CASE WHEN f.calificacion>=70 AND f.calificacion<80 THEN 1 ELSE 0 END) AS C,
                     SUM(CASE WHEN f.calificacion>=60 AND f.calificacion<70 THEN 1 ELSE 0 END) AS D,
                     SUM(CASE WHEN f.calificacion<60 THEN 1 ELSE 0 END) AS F
                FROM FactCalificaciones f
                JOIN DimModalidad m ON f.id_modalidad = m.id_modalidad
               GROUP BY m.tipo_modalidad;
            """)
            rows = cur.fetchall()
        return Response([
            {'modalidad': mod, 'A': a,'B': b,'C': c,'D': d,'F': f}
            for mod,a,b,c,d,f in rows
        ])
        

class UpdateDimensionView(APIView):
    """
    PUT /api/dimension/<dim_name>/<int:pk>/
    Permite actualizar atributos de una dimensión (Estudiante, Profesor, etc.).
    """
    ALLOWED = {'estudiante':'DimEstudiante', 
               'profesor':'DimProfesor',
               'asignatura':'DimAsignatura',
               'modalidad':'DimModalidad'}
    def put(self, request, dim_name, pk):
        table = self.ALLOWED.get(dim_name)
        if not table:
            return Response({'error':'Dimensión no soportada'}, status=404)
        # Esperamos un JSON con pares columna:valor
        updates = request.data
        cols = ",".join([f"{col} = %s" for col in updates])
        vals = list(updates.values()) + [pk]
        sql = f"UPDATE {table} SET {cols} WHERE id_{dim_name} = %s;"
        with connection.cursor() as cur:
            cur.execute(sql, vals)
        return Response({'updated': pk})
