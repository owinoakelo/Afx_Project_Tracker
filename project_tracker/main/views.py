from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from .models import Category, Project, Status
from users.models import User

# Create your views here.
def index(request):
    # Group projects by category for the dashboard
    categories = Category.objects.prefetch_related('project_set__project_status', 'project_set__owner').all().order_by('category_name')
    statuses = Status.objects.all()
    # Provide owners and phase choices for modal selects
    owners = User.objects.all().order_by('email')
    phase_field = Project._meta.get_field('project_phase')
    phases = getattr(phase_field, 'choices', [])
    return render(request, 'main/index.html', {
        'categories': categories,
        'statuses': statuses,
        'owners': owners,
        'phases': phases,
    })

def project_to_dict(project):
    return {
        'uid': str(project.uid),
        'project_name': project.project_name,
        'project_phase': project.project_phase,
        'project_status': project.project_status.status_name if project.project_status else None,
        'project_status_id': str(project.project_status.uid) if project.project_status else None,
        'stretch_target_date': project.stretch_target_date.isoformat() if project.stretch_target_date else None,
        'owner': project.owner.email if project.owner else None,
        'owner_id': str(project.owner.uid) if project.owner else None,
        'budget': str(project.budget) if project.budget is not None else None,
        'comment': project.comment if getattr(project, 'comment', None) else None,
    }

@require_http_methods(['GET'])
def project_detail(request, uid):
    project = get_object_or_404(Project, uid=uid)
    return JsonResponse({'project': project_to_dict(project)})

@require_http_methods(['POST'])
def project_update(request, uid):
    project = get_object_or_404(Project, uid=uid)
    # accept JSON or form-encoded
    data = request.POST if request.POST else None
    try:
        name = (data.get('project_name') if data else request.body and __import__('json').loads(request.body).get('project_name'))
    except Exception:
        return HttpResponseBadRequest('Invalid payload')

    if name:
        project.project_name = name
    phase = (data.get('project_phase') if data else __import__('json').loads(request.body).get('project_phase'))
    if phase:
        project.project_phase = phase
    date = (data.get('stretch_target_date') if data else __import__('json').loads(request.body).get('stretch_target_date'))
    if date:
        from django.utils.dateparse import parse_date
        d = parse_date(date)
        if d:
            project.stretch_target_date = d
    budget = (data.get('budget') if data else __import__('json').loads(request.body).get('budget'))
    if budget:
        try:
            project.budget = float(budget)
        except Exception:
            pass
    owner_id = (data.get('owner_id') if data else __import__('json').loads(request.body).get('owner_id'))
    if owner_id:
        try:
            owner = User.objects.get(uid=owner_id)
            project.owner = owner
        except User.DoesNotExist:
            pass
    # project-level comment
    comment = (data.get('comment') if data else __import__('json').loads(request.body).get('comment'))
    if comment is not None:
        project.comment = comment
    
    status_id = (data.get('project_status_id') if data else __import__('json').loads(request.body).get('project_status_id'))
    if status_id:
        try:
            status = Status.objects.get(uid=status_id)
            project.project_status = status
        except Status.DoesNotExist:
            pass

    project.save()
    return JsonResponse({'ok': True, 'project': project_to_dict(project)})