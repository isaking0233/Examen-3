from rest_framework import serializers

class LoadDataSerializer(serializers.Serializer):
    id_estudiante = serializers.IntegerField()
    id_asignatura = serializers.IntegerField()
    id_profesor   = serializers.IntegerField()
    id_tiempo     = serializers.IntegerField()
    id_modalidad  = serializers.IntegerField()
    calificacion  = serializers.DecimalField(max_digits=5, decimal_places=2)
    creditos      = serializers.IntegerField()
