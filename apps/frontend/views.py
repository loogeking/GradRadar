from django.shortcuts import render, get_object_or_404
from apps.schools.models import School
from apps.majors.models import Major


def index(request):
    """首页"""
    school_count = School.objects.count()
    major_count = Major.objects.count()
    hot_schools = School.objects.filter(is_985=True)[:6]
    return render(request, 'index.html', {
        'school_count': school_count,
        'major_count': major_count,
        'hot_schools': hot_schools,
    })


def school_list(request):
    """院校列表页"""
    return render(request, 'school_list.html')


def school_detail(request, pk):
    """院校详情页"""
    school = get_object_or_404(School, pk=pk)
    return render(request, 'school_detail.html', {'school_id': school.id})


def major_detail(request, pk):
    """专业详情页"""
    major = get_object_or_404(Major, pk=pk)
    return render(request, 'major_detail.html', {'major_id': major.id})


def search(request):
    """搜索结果页"""
    keyword = request.GET.get('q', '')
    return render(request, 'search_results.html', {'keyword': keyword})


def compare(request):
    """对比页"""
    return render(request, 'compare.html')


def login_page(request):
    """登录页"""
    return render(request, 'login.html')


def register_page(request):
    """注册页"""
    return render(request, 'register.html')


def favorites(request):
    """我的收藏页"""
    return render(request, 'favorites.html')