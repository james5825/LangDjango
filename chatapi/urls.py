from django.urls import path

from chatapi.views import views

urlpatterns = [
    path('messages/<str:user_id>/<int:thread_id>/', views.messages),
    path('message/<str:user_id>/<int:thread_id>/<int:sequential_order>', views.message),
    path('chat/', views.chat)
]

# views = NinjaAPI(csrf=True)
# views.add_router('auth/', auth_api)
# views.add_router('', chat_api)
#
# urlpatterns = [
#     path("views/", views.urls, name="views"),
#     path("", redirect_to_docs, name="index"),
# ]
