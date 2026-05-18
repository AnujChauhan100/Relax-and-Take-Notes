from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Note

@login_required # <--- THE SECURITY GUARD
def index(request):
    # Only get notes belonging to the logged-in user
    notes = Note.objects.filter(user=request.user).order_by('created_at') 
    return render(request, 'notes_app/index.html', {'notes': notes})

@login_required
def add_note(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content', '').strip()
        Note.objects.create(user=request.user, title=title, content=content)
        return redirect('index')
    return render(request, 'notes_app/add_note.html')

@login_required
def note_detail(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    return render(request, 'notes_app/note_detail.html', {'note': note})

@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.delete()
    return redirect('index')