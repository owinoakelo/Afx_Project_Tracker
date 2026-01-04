import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Category, Project, Status
from users.models import User
from decimal import Decimal
from django.utils.dateparse import parse_date

# Create your views here.
@login_required(login_url="users/login")
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
        'measure_initiative_weight': str(project.measure_initiative_weight) if getattr(project, 'measure_initiative_weight', None) is not None else None,
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
    measure = (data.get('measure_initiative_weight') if data else __import__('json').loads(request.body).get('measure_initiative_weight'))
    if measure:
        try:
            project.measure_initiative_weight = Decimal(str(measure))
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

def category_to_dict(category):
    return {
        'uid': str(category.uid),
        'category_name': category.category_name,
        'objective_weight': str(category.objective_weight),
        'scorecard_year': category.scorecard_year,
    }

@require_http_methods(['GET'])
def category_detail(request, uid):
    category = get_object_or_404(Category, uid=uid)
    return JsonResponse({'category': category_to_dict(category)})

@require_http_methods(['POST'])
def category_update(request, uid):
    category = get_object_or_404(Category, uid=uid)
    data = request.POST if request.POST else None
    try:
        name = (data.get('category_name') if data else request.body and __import__('json').loads(request.body).get('category_name'))
    except Exception:
        return HttpResponseBadRequest('Invalid payload')

    if name:
        category.category_name = name
    weight = (data.get('objective_weight') if data else __import__('json').loads(request.body).get('objective_weight'))
    if weight:
        try:
            category.objective_weight = Decimal(str(weight))
        except Exception:
            pass
    year = (data.get('scorecard_year') if data else __import__('json').loads(request.body).get('scorecard_year'))
    if year:
        try:
            category.scorecard_year = int(year)
        except Exception:
            pass

    category.save()
    return JsonResponse({'ok': True, 'category': category_to_dict(category)})

@require_http_methods(['POST'])
def category_create(request):
    data = request.POST if request.POST else None
    try:
        name = (data.get('category_name') if data else request.body and __import__('json').loads(request.body).get('category_name'))
    except Exception:
        return HttpResponseBadRequest('Invalid payload')
    
    if not name:
        return HttpResponseBadRequest('Category name is required')
    
    weight = (data.get('objective_weight') if data else __import__('json').loads(request.body).get('objective_weight'))
    year = (data.get('scorecard_year') if data else __import__('json').loads(request.body).get('scorecard_year'))
    
    try:
        w = Decimal(str(weight)) if weight else Decimal('1.0')
        y = int(year) if year else 2026
        category = Category.objects.create(
            category_name=name,
            objective_weight=w,
            scorecard_year=y,
        )
        return JsonResponse({'ok': True, 'category': category_to_dict(category)})
    except Exception as e:
        return HttpResponseBadRequest(f'Error creating category: {str(e)}')

@require_http_methods(['POST'])
def project_create(request, cat_uid):
    
    try:
        my_data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON payload')

    name = (my_data.get('project_name') or '').strip()
    if not name:
        return HttpResponseBadRequest('Project name is required')

    phase = my_data.get('project_phase') or 'Requirement'
    date_str = my_data.get('stretch_target_date')

    target_date = parse_date(date_str) if date_str else None
    if not target_date:
        return HttpResponseBadRequest('Valid stretch_target_date is required (YYYY-MM-DD)')

    
    try:
        category = Category.objects.get(uid=cat_uid)
    except Category.DoesNotExist:
        return HttpResponseBadRequest('Category not found')

    status_id = my_data.get('project_status_id')
    owner_id = my_data.get('owner_id')

    if not status_id:
        return HttpResponseBadRequest('project_status_id is required')
    if not owner_id:
        return HttpResponseBadRequest('owner_id is required')

    try:
        status = Status.objects.get(pk=status_id)
    except Status.DoesNotExist:
        return HttpResponseBadRequest('Status not found')

    try:
        owner = User.objects.get(pk=owner_id)
    except User.DoesNotExist:
        return HttpResponseBadRequest('Owner not found')

    budget_raw = my_data.get('budget')
    weight_raw = my_data.get('measure_initiative_weight')

    try:
        budget = Decimal(str(budget_raw)) if budget_raw not in (None, '',) else Decimal('0.0')
    except Exception:
        return HttpResponseBadRequest('Invalid budget')

    try:
        weight = Decimal(str(weight_raw)) if weight_raw not in (None, '',) else Decimal('0.0')
    except Exception:
        return HttpResponseBadRequest('Invalid measure_initiative_weight')

   
    try:
        project = Project.objects.create(
            project_name=name,
            category=category,                 
            project_phase=phase,
            project_status=status,             
            owner=owner,                       
            stretch_target_date=target_date,   
            budget=budget,
            measure_initiative_weight=weight,
        )
    except Exception as e:
        return HttpResponseBadRequest(f'Error creating project: {str(e)}')

    return JsonResponse({'ok': True, 'project': project_to_dict(project)})