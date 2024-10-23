from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import MedicineForm, UserCreateForm
from .models import Medicine
from django.core.paginator import Paginator
from django.http import JsonResponse

def signup_view(request):
    """Handle user signup."""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Signup successful! Please log in.')
            return redirect('login')
    else:
        form = UserCreateForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('add_medicine')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def add_medicine_view(request):
    """Handle adding new medicine."""
    user_medicines = Medicine.objects.filter(user=request.user)
    
    if user_medicines.count() >= 5:
        return render(request, 'add_medicine.html', {'limit_reached': True})

    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.user = request.user
            medicine.save()
            messages.success(request, 'Medicine added successfully.')
            return redirect('medicine_list')
    else:
        form = MedicineForm()

    return render(request, 'add_medicine.html', {'form': form, 'limit_reached': False})

@login_required
def medicine_list_view(request):
    """Display the list of medicines."""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Check for AJAX request
        query = request.GET.get('q', '')
        medicines = Medicine.objects.filter(name__icontains=query, user=request.user)
        data = list(medicines.values('name', 'stock', 'date', 'pk'))
        return JsonResponse({'medicines': data})

    medicines = Medicine.objects.filter(user=request.user)
    paginator = Paginator(medicines, 3)  # Items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'medicine_list.html', {'page_obj': page_obj})

@login_required
def edit_medicine_view(request, pk):
    """Handle editing existing medicine."""
    medicine = get_object_or_404(Medicine, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine details updated successfully.')
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=medicine)

    return render(request, 'edit_medicine.html', {'form': form})

@login_required
def delete_medicine_view(request, pk):
    """Handle deleting medicine."""
    medicine = get_object_or_404(Medicine, pk=pk, user=request.user)
    
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, 'Medicine deleted successfully.')
        return redirect('medicine_list')

    return render(request, 'delete_medicine.html', {'medicine': medicine})

@login_required(login_url='/login/')
def logout_view(request):
    """Handle user logout."""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Logged out successfully.')
        return redirect('login')

    return render(request, 'logout.html', {'user': request.user})
