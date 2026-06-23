from django.shortcuts import render, get_object_or_404
from apps.schools.models import School
from apps.majors.models import Major
from apps.subjects.models import SubjectCategory


def index(request):
    school_count = School.objects.count()
    major_count = Major.objects.count()
    hot_schools = School.objects.filter(is_985=True)[:6]
    return render(request, 'index.html', {
        'school_count': school_count,
        'major_count': major_count,
        'hot_schools': hot_schools,
    })


def school_list(request):
    return render(request, 'school_list.html')


def school_detail(request, pk):
    school = get_object_or_404(School, pk=pk)
    return render(request, 'school_detail.html', {'school_id': school.id})


def major_detail(request, pk):
    major = get_object_or_404(Major, pk=pk)
    return render(request, 'major_detail.html', {'major_id': major.id})


def subject_list(request):
    """专业（学科）列表页"""
    return render(request, 'subject_list.html')


def subject_detail(request, pk):
    """专业（学科）详情页"""
    subject = get_object_or_404(SubjectCategory, pk=pk)
    return render(request, 'subject_detail.html', {'subject_id': subject.id})


def search(request):
    keyword = request.GET.get('q', '')
    return render(request, 'search_results.html', {'keyword': keyword})


def compare(request):
    return render(request, 'compare.html')


def login_page(request):
    return render(request, 'login.html')


def register_page(request):
    return render(request, 'register.html')


def favorites(request):
    return render(request, 'favorites.html')