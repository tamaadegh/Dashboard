import time
import os
from django.contrib import messages
import zipfile
from django.conf import settings
from django.shortcuts import render, redirect
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from django.template.loader import engines
from django.contrib.admin.views.decorators import staff_member_required

def home(request):
    return redirect(reverse('nxtbn_dashboard'))

def get_help(request):
    """Help/support page with contact info."""
    return render(request, 'help.html', {'phone_number': '+23320938747'})

def nxtbn_dashboard(request, *args, **kwargs):
    try:
        return render(request, 'dashboard.html')
    except TemplateDoesNotExist:
        return render(request, 'templatefailback.html')



def reload_templates():
    """Reloads the templates to reflect changes instantly"""
    for engine in engines.all():
        if hasattr(engine, 'engine'):
            engine.engine.template_loaders = engine.engine.get_template_loaders(engine.engine.loaders)

@staff_member_required
def upload_admin(request):
    if request.method == 'POST':
        print("POST received with file: ", request.FILES.get('dashboard-upload'))

    if request.method == 'POST' and request.FILES.get('dashboard-upload'):
        uploaded_file = request.FILES['dashboard-upload']
        if not uploaded_file.name.endswith('.zip'):
            messages.error(request, 'Only .zip files are allowed.')
            return redirect('nxtbn_dashboard')

        # Define paths
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Save the file temporarily
        with open(temp_file_path, 'wb') as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)

        try:
            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the extracted folder and rename it to 'admin-build'
            extracted_folder = os.path.join(temp_dir, zip_ref.namelist()[0].split('/')[0])
            admin_build_dir = os.path.join(settings.BASE_DIR, 'admin-build')
            if os.path.exists(admin_build_dir):
                os.rmdir(admin_build_dir)
            os.rename(extracted_folder, admin_build_dir)
            
            # Cleanup
            os.remove(temp_file_path)
            time.sleep(4)
            messages.success(request, 'File uploaded and extracted successfully.')
            # Clear template cache to reflect changes instantly
            reload_templates()

            return redirect('nxtbn_dashboard')
        except zipfile.BadZipFile:
            os.remove(temp_file_path)
            messages.error(request, 'Invalid zip file.')
            return redirect('nxtbn_dashboard')
        
    return redirect('nxtbn_dashboard')


