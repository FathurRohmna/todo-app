from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Items, Category
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

existingCategory = Category.objects.all()

# Create your views here.
@login_required(login_url="login")
def index(request):
    data = Items.objects.filter(owner=request.user)
    paginator = Paginator(data, 6)
    page_number = request.GET.get("page")
    page_obj = Paginator.get_page(paginator, page_number)
    return render(
        request, 
        "items/index.html", 
        {"categories": existingCategory, "values": data, "page_obj": page_obj}
    )

@login_required(login_url="login")
def addItems(request):
    viewName = "addItems"
    data = request.POST

    if request.method == "POST":
        description = data.get("description")
        category = data.get("category")
        date = data.get("date")
        owner = request.user
        newTopic = None
        newTopic = Items.objects.create(
            owner=owner,
            date=date,
            category=category,
            description=description
        )
        newTopic.save()
        messages.success(request, "New Tasks added")
        return redirect("index")
    
    return render(
        request,
        "items/addItems.html",
        {"categories": existingCategory, "values": data, "viewName": viewName},
    )

@login_required
@require_POST
@csrf_exempt  # Only for demonstration - consider proper CSRF handling in production
def create_category(request):
    try:
        data = json.loads(request.body)
        category_name = data.get('name')
        
        if not category_name:
            return JsonResponse({'success': False, 'error': 'Category name is required'})
        
        if Category.objects.filter(name__iexact=category_name).exists():
            return JsonResponse({'success': True, 'message': 'Category already exists'})
        
        category = Category.objects.create(name=category_name)
        return JsonResponse({'success': True, 'id': category.id, 'name': category.name})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    

def statusItems(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pk = data.get("id")
        status = data.get("status")
        items = Items.objects.get(id=pk)
        items.status = status
        items.save()

        messages.success(request, "Status updated")
        return JsonResponse({"message": "Status updated"}, status=200)