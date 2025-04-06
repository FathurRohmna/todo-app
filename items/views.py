from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Items, Category
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .tasks import send_task_notification_email  
import logging

logger = logging.getLogger('task_notifications')

existingCategory = Category.objects.all()

# Create your views here.
@login_required(login_url="login")
def index(request):
    data = Items.objects.filter(owner=request.user)
    
    # Handle status filtering
    selected_statuses = request.GET.getlist('status')  # Get multiple status values
    if selected_statuses:
        data = data.filter(status__in=selected_statuses)
    
    paginator = Paginator(data, 6)
    page_number = request.GET.get("page")
    page_obj = Paginator.get_page(paginator, page_number)
    
    return render(
        request, 
        "items/index.html", 
        {
            "categories": existingCategory, 
            "values": data, 
            "page_obj": page_obj,
            "selected_statuses": selected_statuses,  # Pass selected statuses to template
            "status_choices": Items.STATUS_CHOICES,
        }
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
        
        try:
            # Create the new task
            new_task = Items.objects.create(
                owner=owner,
                date=date,
                category=category,
                description=description
            )
            new_task.save()
            
            # Log the task creation
            logger.info(f"New task created: ID={new_task.id}, Description={description}, Owner={owner.username}")
            
            # Queue the email notification task
            send_task_notification_email(
                new_task.id,
                description,
                category,
                date,
                "fr081938@gmail.com"
            )
            
            messages.success(request, "New task added and notification email queued")
            return redirect("index")
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            messages.error(request, f"Error creating task: {str(e)}")
    
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
    

@csrf_exempt
@require_POST
@login_required
def statusItems(request):
    try:
        data = json.loads(request.body)
        pk = data.get("id")
        status = data.get("status")
        if status not in ["TODO", "INPROGRESS", "DONE"]:
            return JsonResponse({"message": "Invalid status"}, status=400)

        item = Items.objects.get(id=pk, owner=request.user)
        item.status = status
        item.save()
        return JsonResponse({"message": "Status updated"}, status=200)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)
    

@login_required(login_url="login")
def updateItems(request):
    viewname = "updateItems"
    existingCategory = Category.objects.all()
    if request.method == "GET":
        op = request.GET
        pk = op.get("update")
        items = Items.objects.get(id=pk)
        return render(
            request,
            "items/addItems.html",
            {"categories": existingCategory, "values": items, "viewName": viewname},
        )
    else:
        if request.method == "POST":
            data = request.POST
            pk = data.get("update")
            items = Items.objects.get(id=pk)

            description = data.get("description")
            category = data.get("category")
            date = data.get("date")
            if category:
                items.description = description
                items.category = category
                items.date = date
                messages.success(request, "Task updated")
                items.save()
                return redirect("index")
            else:
                messages.warning(request, "Category is required")
                return render(
                    request,
                    "items/addItems.html",
                    {
                        "categories": existingCategory,
                        "values": items,
                        "viewName": viewname,
                    },
                )

        return redirect("index")


@login_required(login_url="login")
def deleteItems(request):

    print("Entered delete")
    if request.method == "POST":
        op = request.POST
        pk = op.get("delete")
        items = Items.objects.get(id=pk)
        items.delete()
        messages.info(request, "Task deleted")
        return redirect("index")