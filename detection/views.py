import os
import pickle
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Q, Count
from .models import User, NewsArticle, Feedback

# Model loading logic
MODEL = None
VECTORIZER = None

def get_ml_model():
    global MODEL, VECTORIZER
    if MODEL is None or VECTORIZER is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'ml_models', 'model.pkl')
        vectorizer_path = os.path.join(current_dir, 'ml_models', 'vectorizer.pkl')
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            with open(model_path, 'rb') as f:
                MODEL = pickle.load(f)
            with open(vectorizer_path, 'rb') as f:
                VECTORIZER = pickle.load(f)
        else:
            raise FileNotFoundError("Model or Vectorizer files missing. Please run the training script first.")
    return MODEL, VECTORIZER

def predict_news(title, content):
    try:
        model, vectorizer = get_ml_model()
        combined_text = f"{title} {content}"
        transformed_text = vectorizer.transform([combined_text])
        prediction = model.predict(transformed_text)[0]  # 'REAL' or 'FAKE'
        return prediction
    except Exception as e:
        print(f"Prediction error: {e}")
        return 'PENDING'

# Role-based decorators
def role_required(allowed_roles):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied("You do not have permission to access this page.")
        return _wrapped_view
    return decorator

# Landing Page
def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    return render(request, 'index.html')

# Authentication Views
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            # Create user as standard "user" role
            user = User.objects.create_user(username=username, email=email, password=password, role='user')
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard_redirect')

    return render(request, 'register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard_redirect')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

@login_required
def dashboard_redirect(request):
    if request.user.role == 'admin' or request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.role == 'editor':
        return redirect('editor_dashboard')
    else:
        return redirect('user_dashboard')


# ==========================================
# ADMIN MODULE
# ==========================================

@role_required(['admin'])
def admin_dashboard(request):
    editors_count = User.objects.filter(role='editor').count()
    users_count = User.objects.filter(role='user').count()
    total_articles = NewsArticle.objects.count()
    fake_articles = NewsArticle.objects.filter(classification='FAKE').count()
    real_articles = NewsArticle.objects.filter(classification='REAL').count()
    feedback_count = Feedback.objects.count()

    context = {
        'editors_count': editors_count,
        'users_count': users_count,
        'total_articles': total_articles,
        'fake_articles': fake_articles,
        'real_articles': real_articles,
        'feedback_count': feedback_count,
    }
    return render(request, 'admin/dashboard.html', context)

@role_required(['admin'])
def manage_editors(request):
    editors = User.objects.filter(role='editor')
    return render(request, 'admin/editors.html', {'editors': editors})

@role_required(['admin'])
def add_editor(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            editor = User.objects.create_user(username=username, email=email, password=password, role='editor')
            messages.success(request, f'News Editor "{editor.username}" added successfully!')
            return redirect('manage_editors')

    return render(request, 'admin/editor_form.html', {'action': 'Add'})

@role_required(['admin'])
def edit_editor(request, pk):
    editor = get_object_or_404(User, pk=pk, role='editor')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        new_password = request.POST.get('password')

        if User.objects.filter(username=username).exclude(pk=pk).exists():
            messages.error(request, 'Username already exists.')
        else:
            editor.username = username
            editor.email = email
            if new_password:
                editor.set_password(new_password)
            editor.save()
            messages.success(request, f'Editor "{editor.username}" updated successfully.')
            return redirect('manage_editors')

    return render(request, 'admin/editor_form.html', {'editor': editor, 'action': 'Edit'})

@role_required(['admin'])
def delete_editor(request, pk):
    editor = get_object_or_404(User, pk=pk, role='editor')
    editor_username = editor.username
    editor.delete()
    messages.success(request, f'News Editor "{editor_username}" has been deleted.')
    return redirect('manage_editors')

@role_required(['admin'])
def monitor_articles(request):
    articles = NewsArticle.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        new_status = request.POST.get('status')
        article = get_object_or_404(NewsArticle, id=article_id)
        if new_status in ['verified', 'rejected', 'pending']:
            article.status = new_status
            article.save()
            messages.success(request, f'Article "{article.title}" status updated to {new_status}.')
        return redirect('monitor_articles')
        
    return render(request, 'admin/monitor_articles.html', {'articles': articles})

@role_required(['admin'])
def view_reports(request):
    # Calculate detailed fake news ratio, category metrics
    fake_count = NewsArticle.objects.filter(classification='FAKE').count()
    real_count = NewsArticle.objects.filter(classification='REAL').count()
    pending_count = NewsArticle.objects.filter(classification='PENDING').count()
    
    verified_count = NewsArticle.objects.filter(status='verified').count()
    rejected_count = NewsArticle.objects.filter(status='rejected').count()
    draft_count = NewsArticle.objects.filter(status='draft').count()
    pending_verif_count = NewsArticle.objects.filter(status='pending').count()

    # Get article counts grouped by editors
    editor_stats = User.objects.filter(role='editor').annotate(
        article_count=Count('articles')
    ).order_by('-article_count')

    context = {
        'fake_count': fake_count,
        'real_count': real_count,
        'pending_count': pending_count,
        'verified_count': verified_count,
        'rejected_count': rejected_count,
        'draft_count': draft_count,
        'pending_verif_count': pending_verif_count,
        'editor_stats': editor_stats
    }
    return render(request, 'admin/reports.html', context)

@role_required(['admin'])
def view_feedback(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'admin/feedback.html', {'feedbacks': feedbacks})


# ==========================================
# NEWS EDITOR MODULE
# ==========================================

@role_required(['editor'])
def editor_dashboard(request):
    articles = NewsArticle.objects.filter(author=request.user).order_by('-created_at')
    draft_count = articles.filter(status='draft').count()
    pending_count = articles.filter(status='pending').count()
    verified_count = articles.filter(status='verified').count()
    rejected_count = articles.filter(status='rejected').count()

    context = {
        'articles': articles,
        'draft_count': draft_count,
        'pending_count': pending_count,
        'verified_count': verified_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'editor/dashboard.html', context)

@role_required(['editor'])
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        status = request.POST.get('status', 'draft') # Can be draft or pending (submitted for verification)
        image = request.FILES.get('image')
        
        article = NewsArticle.objects.create(
            title=title,
            content=content,
            author=request.user,
            status=status,
            image=image
        )

        if status == 'pending':
            # Run prediction immediately
            prediction = predict_news(title, content)
            article.classification = prediction
            article.save()
            messages.success(request, f'Article "{article.title}" saved and submitted for verification (Predicted: {prediction})!')
        else:
            messages.success(request, f'Article "{article.title}" saved as draft.')
        
        return redirect('editor_dashboard')

    return render(request, 'editor/article_form.html', {'action': 'Add'})

@role_required(['editor'])
def edit_article(request, pk):
    article = get_object_or_404(NewsArticle, pk=pk, author=request.user)
    
    if article.status == 'verified':
        messages.error(request, "Cannot edit already verified articles.")
        return redirect('editor_dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        status = request.POST.get('status', 'draft')

        article.title = title
        article.content = content
        article.status = status
        
        if 'image' in request.FILES:
            article.image = request.FILES['image']

        if status == 'pending':
            prediction = predict_news(title, content)
            article.classification = prediction
            messages.success(request, f'Article updated and submitted for verification (Predicted: {prediction})!')
        else:
            messages.success(request, 'Article updated successfully.')
        
        article.save()
        return redirect('editor_dashboard')

    return render(request, 'editor/article_form.html', {'article': article, 'action': 'Edit'})

@role_required(['editor'])
def delete_article(request, pk):
    article = get_object_or_404(NewsArticle, pk=pk, author=request.user)
    if article.status == 'verified':
        messages.error(request, "Cannot delete verified articles.")
    else:
        article_title = article.title
        article.delete()
        messages.success(request, f'Article "{article_title}" deleted.')
    return redirect('editor_dashboard')

@role_required(['editor'])
def submit_article(request, pk):
    article = get_object_or_404(NewsArticle, pk=pk, author=request.user)
    if article.status in ['draft', 'rejected']:
        prediction = predict_news(article.title, article.content)
        article.status = 'pending'
        article.classification = prediction
        article.save()
        messages.success(request, f'Article "{article.title}" has been submitted for verification. ML Prediction: {prediction}')
    else:
        messages.error(request, "Article is already pending or verified.")
    return redirect('editor_dashboard')


# ==========================================
# REGULAR USER MODULE
# ==========================================

@role_required(['user'])
def user_dashboard(request):
    query = request.GET.get('q', '')
    
    # Users can only view verified news
    articles = NewsArticle.objects.filter(status='verified')
    
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        
    articles = articles.order_by('-created_at')
    
    return render(request, 'user/dashboard.html', {
        'articles': articles,
        'query': query
    })

@role_required(['user'])
def article_detail(request, pk):
    article = get_object_or_404(NewsArticle, pk=pk, status='verified')
    return render(request, 'user/article_detail.html', {'article': article})

@role_required(['user'])
def add_feedback(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        Feedback.objects.create(
            user=request.user,
            subject=subject,
            message=message
        )
        messages.success(request, 'Thank you! Your feedback has been submitted to the Admin.')
        return redirect('user_dashboard')
        
    return render(request, 'user/add_feedback.html')
