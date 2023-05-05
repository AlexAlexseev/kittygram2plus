from rest_framework import viewsets

from .models import Achievement, Cat, User
from rest_framework.pagination import PageNumberPagination

from .permissions import OwnerOrReadOnly, ReadOnly
from rest_framework.throttling import AnonRateThrottle
from rest_framework import permissions
from rest_framework.throttling import ScopedRateThrottle

from .throttling import WorkingHoursRateThrottle
from rest_framework.pagination import LimitOffsetPagination
from .pagination import CatsPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import AchievementSerializer, CatSerializer, UserSerializer


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    permission_classes = (OwnerOrReadOnly,) 
    # throttle_classes = (AnonRateThrottle,)  # Подключили класс AnonRateThrottle 
    # # Для любых пользователей установим кастомный лимит 1 запрос в минуту
    # throttle_scope = 'low_request' 

    # Если кастомный тротлинг-класс вернёт True - запросы будут обработаны
    # Если он вернёт False - все запросы будут отклонены
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    # А далее применится лимит low_request
    # throttle_scope = 'low_request' 

    # pagination_class = PageNumberPagination 

        # Даже если на уровне проекта установлен PageNumberPagination
    # Для котиков будет работать LimitOffsetPagination
    # pagination_class = LimitOffsetPagination 

    # Вот он наш собственный класс пагинации с page_size=20
    # pagination_class = CatsPagination 

    # Указываем фильтрующий бэкенд DjangoFilterBackend
    # Из библиотеки django-filter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # Временно отключим пагинацию на уровне вьюсета, 
    # так будет удобнее настраивать фильтрацию
    pagination_class = None
    # Фильтровать будем по полям color и birth_year модели Cat
    filterset_fields = ('color', 'birth_year') 
    search_fields = ('name','achievements__name', 'owner__username') 
    ordering_fields = ('name', 'birth_year',) 
    #Если установлен атрибут ordering, то переданное ему 
    # значение будет использоваться в качестве поля для сортировки по умолчанию при выдаче. 
    ordering = ('birth_year',)

    def get_permissions(self):
    # Если в GET-запросе требуется получить информацию об объекте
        if self.action == 'retrieve':
            # Вернем обновленный перечень используемых пермишенов
            return (ReadOnly(),)
        # Для остальных ситуаций оставим текущий перечень пермишенов без изменений
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user) 


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer