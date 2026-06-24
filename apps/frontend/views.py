from django.shortcuts import render, get_object_or_404
from apps.schools.models import School
from apps.majors.models import Major, ScoreLine
from apps.subjects.models import SubjectCategory


def index(request):
    school_count = School.objects.count()
    major_count = Major.objects.count()
    subject_count = SubjectCategory.objects.count()
    score_line_count = ScoreLine.objects.count()
    hot_schools = School.objects.filter(is_985=True).select_related('province')[:6]
    return render(request, 'index.html', {
        'school_count': school_count,
        'major_count': major_count,
        'subject_count': subject_count,
        'score_line_count': score_line_count,
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
    return render(request, 'subject_list.html')


def subject_detail(request, pk):
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