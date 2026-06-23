from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import Favorite
from .serializers import (
    UserRegisterSerializer,
    UserSerializer,
    FavoriteSerializer,
)


class RegisterView(APIView):
    """用户注册
    POST /api/user/register/
    {"username": "xxx", "email": "xx@xx.com", "password": "xxx", "password2": "xxx"}
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)  # 注册后自动登录
            return Response({
                'message': '注册成功',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """用户登录
    POST /api/user/login/
    {"username": "xxx", "password": "xxx"}
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response(
                {'error': '用户名和密码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {'error': '用户名或密码错误'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        login(request, user)
        return Response({
            'message': '登录成功',
            'user': UserSerializer(user).data
        })


class LogoutView(APIView):
    """用户登出
    POST /api/user/logout/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': '已登出'})


class CurrentUserView(APIView):
    """获取当前登录用户信息
    GET /api/user/me/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class FavoriteViewSet(viewsets.ModelViewSet):
    """收藏接口
    - GET    /api/user/favorites/         查看我的收藏
    - POST   /api/user/favorites/         添加收藏
    - DELETE /api/user/favorites/<id>/    删除收藏
    """
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('school', 'major')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)