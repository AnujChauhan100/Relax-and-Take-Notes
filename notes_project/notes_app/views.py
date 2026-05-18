from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Note
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import uuid

def get_session_notes(request):
    session_notes = request.session.get('anonymous_notes', [])

    return [
        type('Note', (), {
            'id': note['id'],
            'title': note.get('title', 'Untitled'),
            'content': note.get('content', ''),
            'created_at': note.get('created_at', ''),
            'is_anonymous': True
        })
        for note in session_notes
    ]

def index(request):
    """Show notes from both authenticated user and session"""
    if request.user.is_authenticated:
        # User is logged in - show database notes
        notes = Note.objects.filter(user=request.user).order_by('-created_at')
    else:
        # Anonymous user - show session notes
        notes = get_session_notes(request)
    
    return render(request, 'notes_app/index.html', {'notes': notes})

def add_note(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled')
        content = request.POST.get('content', '').strip()
        
        if request.user.is_authenticated:
            # Save to database
            Note.objects.create(user=request.user, title=title, content=content)
        else:
            # Save to session
            session_notes = request.session.get('anonymous_notes', [])
            from datetime import datetime
            session_notes.append({
                'id': str(uuid.uuid4()),
                'title': title,
                'content': content,
                'created_at': datetime.now().isoformat()
            })
            request.session['anonymous_notes'] = session_notes
        
        return redirect('index')
    
    return render(request, 'notes_app/add_note.html')

def note_detail(request, note_id):
    if request.user.is_authenticated:
        # Get from database
        note = get_object_or_404(Note, id=note_id, user=request.user)
        return render(request, 'notes_app/note_detail.html', {'note': note})
    else:
        # Get from session
        session_notes = request.session.get('anonymous_notes', [])

        note_data = next(
            (note for note in session_notes if note['id'] == str(note_id)),
            None
        )

        if note_data:
            note = type('Note', (), {
                'id': note_data['id'],
                'title': note_data.get('title', 'Untitled'),
                'content': note_data.get('content', ''),
                'created_at': note_data.get('created_at', ''),
                'is_anonymous': True
            })

            return render(request, 'notes_app/note_detail.html', {'note': note})

        return redirect('index')

@require_POST
def delete_note(request, note_id):
    if request.user.is_authenticated:
        # Delete from database
        note = get_object_or_404(Note, id=note_id, user=request.user)
        note.delete()
    else:
        # Delete from session
        session_notes = request.session.get('anonymous_notes', [])
        updated_notes = [
            note for note in session_notes
            if note['id'] != str(note_id)
        ]
        request.session['anonymous_notes'] = updated_notes
    
    return redirect('index')

def signup(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Merge anonymous notes with user account
            session_notes = request.session.get('anonymous_notes', [])
            for note_data in session_notes:
                Note.objects.create(
                    user=user,
                    title=note_data.get('title', 'Untitled'),
                    content=note_data.get('content', '')
                )
            # Clear session notes after merge
            request.session['anonymous_notes'] = []
            messages.success(request, 'Account created! Your temporary notes have been saved.')
            next_url = request.POST.get('next')
            return redirect(next_url if next_url else 'index')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})