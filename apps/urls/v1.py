from django.urls import path, include

app_name = 'v1'

urlpatterns = [
    path('products/', include('apps.products.urls.v1', namespace='products')),
    path('users/', include('apps.users.urls.v1', namespace='users')),
    path('history/', include('apps.history.urls.v1', namespace='history')),
    path('carts/', include('apps.carts.urls.v1', namespace='carts')),
    path('recipes/', include('apps.recipes.urls.v1', namespace='recipes')),
    path('questionnaires/', include('apps.questionnaires.urls.v1', namespace='questionnaires')),
    path('admins/', include('apps.admins.urls.v1', namespace='admins')),
]
