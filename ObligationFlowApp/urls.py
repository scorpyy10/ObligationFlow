from django.urls import path, re_path
from django.conf import settings
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    path("documents_list/", document_table_list, name="document_list"),
    path("task_dashboard/", task_dashboard, name="task_dashboard"),
    path('document_obligation_list/<int:id>/',document_obligation_table_list,name="document_obligation_list"),
    path("document_form_submit_from_list_view/",create_document_from_list_view,name="document_form_submit"),
    path("display_extracted_result/<int:id>/",display_extracted_result,name="display_extracted_result"),
    path("obligation_task/<int:doc_id>/<int:obligation_id>/",obligation_task,name="obligation_task"),
    path("", index, name="index"),
    path("create_risk_tracking/", create_risk_tracking, name="create_risk_tracking"),
    # path("create_risk_tracking/", create_risk_and_milestone, name="create_risk_tracking"),
    path("create_milestone/", create_milestone, name="create_milestone"),
    # path("", export_data_to_excel, name="index"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)