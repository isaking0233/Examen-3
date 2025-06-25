from django.urls import path
from .views import (
    LoadDataView, AvgPerCareerView,
    ReprobationRateView, GradeDistView,
    UpdateDimensionView
)

urlpatterns = [
    path('load-data/', LoadDataView.as_view()),
    path('analytics/average-per-career/', AvgPerCareerView.as_view()),
    path('analytics/reprobation-rate/', ReprobationRateView.as_view()),
    path('analytics/grade-distribution/', GradeDistView.as_view()),
    path('dimension/<str:dim_name>/<int:pk>/', UpdateDimensionView.as_view()),
]
