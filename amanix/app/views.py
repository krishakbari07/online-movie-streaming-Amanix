import logging
import re
import os
import json
from django.conf import settings
from django.contrib.staticfiles import finders
from collections import Counter
from datetime import date

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.db.models import Avg, Count, F, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
from django.utils import timezone
from .models import (
    User,
    Subscription,
    Payment,
    Categories,
    Movies,
    Star,
    UserSession,
    WatchHistory,
    MovieFeedback,
    AppFeedback,
    Artist,
    UserArtistFollow,
    Language,
    WebSeries,
    Episode,
    Genre,
    WebSeriesWatchHistory,
    WebSeriesWatchlist,
    WebSeriesLike,
    MovieEvent,
    WebSeriesEvent,
    WebSeriesRecommendation,
    MovieSlider,
    Song,
    UserSongLike,
    Playlist,
    PlaylistSong,
)
from dateutil.relativedelta import relativedelta  # Correctly handles month and year additions
from xhtml2pdf import pisa
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    AI_RECOMMENDATIONS_AVAILABLE = True
except ImportError:
    AI_RECOMMENDATIONS_AVAILABLE = False
# Create your views here.

nm=""
email = ""
password = ""

logger = logging.getLogger(__name__)


def _get_client_ip(request):
    """Resolve the best-effort client IP for login tracking."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
        if ip:
            return ip
    return request.META.get('REMOTE_ADDR') or '0.0.0.0'


def _record_login_session(request, user):
    """Persist a login session row and keep only the latest five records."""
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    if not session_key:
        # As a fallback, regenerate a key to avoid blank values
        request.session.cycle_key()
        session_key = request.session.session_key or f'manual-{timezone.now().timestamp()}'

    ip_address = _get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]

    UserSession.objects.create(
        user=user,
        ip_address=ip_address,
        session_key=session_key,
        user_agent=user_agent,
    )

    now = timezone.now()
    User.objects.filter(pk=user.pk).update(
        last_login_at=now,
        login_count=F('login_count') + 1
    )
    user.last_login_at = now
    user.login_count = (user.login_count or 0) + 1

    stale_ids = list(
        UserSession.objects.filter(user=user).order_by('-login_time').values_list('id', flat=True)[5:]
    )
    if stale_ids:
        UserSession.objects.filter(id__in=stale_ids).delete()


def _mark_session_logout(user_id, session_key):
    """Update logout timestamp for a session when the user signs out."""
    if not (user_id and session_key):
        return
    UserSession.objects.filter(
        user_id=user_id,
        session_key=session_key,
        logout_time__isnull=True,
    ).update(logout_time=timezone.now())


def _calculate_end_date(duration_string: str, start_date: date) -> date:
    """Parse subscription duration text (e.g., '6 Months') and return end date."""
    if not duration_string:
        return start_date

    match = re.match(r"(\d+)\s*(day|month|year)s?", duration_string.strip().lower())
    if not match:
        return start_date

    value = int(match.group(1))
    unit = match.group(2)

    if unit == "day":
        return start_date + relativedelta(days=value)
    if unit == "month":
        return start_date + relativedelta(months=value)
    if unit == "year":
        return start_date + relativedelta(years=value)
    return start_date


def index(request):
    """Landing page that personalizes content for the logged-in user."""
    is_login = request.session.get('is_login', False)
    user_name = request.session.get('user_name', '')
    user_mail = request.session.get('user_email')
    user_id = request.session.get('user_id')

    user = None
    latest_payment = None
    sub_plan = None
    has_paid = False
    profile_image = '/media/profile_pics/usericon.png'
    end_date = None

    categories = Categories.objects.prefetch_related('movies').all()

    if user_id:
        try:
            user = User.objects.get(id=user_id)
            latest_payment = (
                Payment.objects.filter(user_id=user_id)
                .order_by('-end_date')
                .first()
            )
            if latest_payment and latest_payment.subscription:
                sub_plan = latest_payment.subscription.sub_name
                end_date = latest_payment.end_date
                # Check if currently active
                if latest_payment.end_date >= timezone.now().date():
                    has_paid = True

            if user.profile_image:
                profile_image = user.profile_image.url
        except User.DoesNotExist:
            user = None

    recent_sessions = []
    recommendations = []
    popular_artists = Artist.objects.filter(is_featured=True).order_by('-popularity_rating')[:12]
    languages = Language.objects.filter(is_active=True).order_by('display_order', 'language_name')
    recommended_language_movies = []
    preferred_language = None

    trending_webseries = WebSeries.objects.filter(
        is_trending=True
    ).select_related(
        'language'
    ).prefetch_related(
        'genre'
    ).order_by('-updated_at', '-rating')[:12]
    featured_webseries = WebSeries.objects.filter(
        is_featured=True
    ).select_related(
        'language'
    ).prefetch_related(
        'genre'
    ).order_by('-updated_at', '-rating')[:8]
    latest_webseries = WebSeries.objects.select_related(
        'language'
    ).prefetch_related(
        'genre'
    ).order_by('-created_at')[:12]
    
    # Get active movie events
    now = timezone.now()
    movie_events = MovieEvent.objects.filter(
        end_time__gte=now
    ).select_related('movie').order_by('start_time')[:10]
    
    # Get active webseries events
    webseries_events = WebSeriesEvent.objects.filter(
        is_active=True,
        end_time__gte=now
    ).select_related('webseries').order_by('start_time')[:10]
    
    # Get active sliders
    movie_sliders = MovieSlider.objects.filter(is_active=True).select_related('movie').order_by('display_order', '-created_at')
    
    # Get recent songs
    recent_songs = Song.objects.prefetch_related('singers').order_by('-created_at')[:10]
    
    if user:
        recent_sessions = list(user.sessions.all()[:5])
        recommendations = _get_recommendations(user)
        # Get language-based recommendations
        preferred_language = _get_user_preferred_language(user)
        if preferred_language:
            recommended_language_movies = _get_language_recommendations(user, preferred_language)[:12]


    return render(
        request,
        "index.html",
        {
            "is_login": is_login,
            "user_name": user_name,
            "user_email": user_mail,
            'sub_plan': sub_plan,
            "has_paid": has_paid,
            "categories": categories,
            "end_date": end_date,
            "profile_image": profile_image,
            "recent_sessions": recent_sessions,
            "recommendations": recommendations,
            "popular_artists": popular_artists,
            "languages": languages,
            "recommended_language_movies": recommended_language_movies,
            "preferred_language": preferred_language,
            "trending_webseries": trending_webseries,
            "featured_webseries": featured_webseries,
            "latest_webseries": latest_webseries,
            "movie_events": movie_events,
            "webseries_events": webseries_events,
            "latest_payment": latest_payment,
            "movie_sliders": movie_sliders,
            "recent_songs": recent_songs,
        }
    )


def movies_list(request, language_id=None):
    from django.db.models import Prefetch
    is_login = request.session.get('is_login', False)
    user_name = request.session.get('user_name', '')
    user_email = request.session.get('user_email')
    user_id = request.session.get('user_id')

    user = None
    latest_payment = None
    sub_plan = None
    has_paid = False
    profile_image = '/media/profile_pics/usericon.png'
    end_date = None

    languages = Language.objects.filter(is_active=True).order_by('display_order', 'language_name')
    selected_language = None

    if language_id:
        selected_language = get_object_or_404(Language, language_id=language_id)
        movies = Movies.objects.filter(language=selected_language).select_related('category', 'language')
    else:
        movies = Movies.objects.select_related('category', 'language').all()

    if user_id:
        try:
            user = User.objects.get(id=user_id)
            latest_payment = (
                Payment.objects.filter(user_id=user_id)
                .order_by('-end_date')
                .first()
            )
            if latest_payment and latest_payment.subscription:
                sub_plan = latest_payment.subscription.sub_name
                end_date = latest_payment.end_date
                if latest_payment.end_date >= timezone.now().date():
                    has_paid = True

            if user.profile_image:
                profile_image = user.profile_image.url
        except User.DoesNotExist:
            user = None

    return render(request, "movies_list.html", {
        "is_login": is_login,
        "user_name": user_name,
        "user_email": user_email,
        "movies": movies,
        "languages": languages,
        "selected_language": selected_language,
        "profile_image": profile_image,
        "sub_plan": sub_plan,
        "end_date": end_date,
        "has_paid": has_paid,
    })


def login(request):
    if request.method == 'POST':
        username = request.POST.get('unm')
        password = request.POST.get('pass')

        try:
            # Check if the user exists
            user = User.objects.filter(email=username).first()

            if user is None:
                messages.error(request, "Invalid Email.")
            elif user.is_blocked:
                messages.error(request, "Your account has been blocked. Please contact support.")
            # Compare the hashed password
            elif not check_password(password, user.password):
                messages.error(request, "Incorrect password.")
            else:
                # Create a session
                request.session['user_id'] = user.id
                request.session['user_name'] = user.nm # Store the user's first name in the session
                request.session['user_email'] = user.email
                request.session['is_login'] = True
                _record_login_session(request, user)
                # Redirect to the index page after successful login
                return redirect('index')
        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist.")


    return render(request, "login.html")

def register(request):
    if request.method == "POST":
        nm = request.POST.get('nm')
        email = request.POST.get('mail')
        password = request.POST.get('pass')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered. Please log in.")
            return redirect('login')

        hashed_password = make_password(password)
        user = User.objects.create(
        nm=nm,
        email=email,
        password=hashed_password
        )
        ok = user.save()
        messages.success(request,'Registration Successfull')

        return redirect('login')
    return render(request, "register.html")

def logout(request):
    session_key = request.session.session_key
    user_id = request.session.get('user_id')
    _mark_session_logout(user_id, session_key)
    request.session.flush()  # Clears all session data
    from django.contrib import messages
    messages.success(request, 'You have been successfully logged out.')
    return redirect('index')

def subscription(requset):
    subs = Subscription.objects.all()
    return render(requset, "subscription.html",{"subs": subs})

def payment(request, sub_id):
    user_mail = request.session.get('user_email')
    user_id = request.session.get('user_id')  # Get logged-in user ID

    if not user_mail or not user_id:
        return redirect('login')  # Redirect to login if user is not logged in

    subscription = get_object_or_404(Subscription, sub_id=sub_id)
    start_date = date.today()
    end_date = _calculate_end_date(subscription.sub_time_limit, start_date)

    return render(request, 'payment.html', {
        'subscription': subscription,
        'start_date': start_date,
        'end_date': end_date,
        "user_email":user_mail
    })

def _get_user_preferred_language(user):
    """Detect user's preferred language based on watch history, ratings, and profile."""
    if not user:
        return None
    
    # 1. Check user's profile preference
    if user.preferred_language:
        return user.preferred_language
    
    # 2. Detect from watch history (most watched language)
    watched_languages = Language.objects.filter(
        movies__watch_logs__user=user
    ).annotate(
        watch_count=Count('movies__watch_logs')
    ).order_by('-watch_count').first()
    
    if watched_languages:
        return watched_languages
    
    # 3. Detect from highly rated movies
    highly_rated_movies = MovieFeedback.objects.filter(
        user=user, rating__gte=4
    ).select_related('movie__language').values_list('movie__language_id', flat=True)
    
    if highly_rated_movies:
        language_ids = [lid for lid in highly_rated_movies if lid]
        if language_ids:
            most_common_lang_id = Counter(language_ids).most_common(1)[0][0]
            try:
                return Language.objects.get(pk=most_common_lang_id)
            except Language.DoesNotExist:
                pass
    
    return None


def _get_ai_movie_recommendations(user, limit=10):
    """Generate AI-powered movie recommendations using TF-IDF and cosine similarity."""
    if not user or not AI_RECOMMENDATIONS_AVAILABLE:
        return []
        
    # Get user's watched or highly rated movies to use as a seed
    watched_ids = set(WatchHistory.objects.filter(user=user).values_list('movie_id', flat=True))
    liked_ids = set(MovieFeedback.objects.filter(user=user, rating__gte=4).values_list('movie_id', flat=True))
    
    seed_ids = liked_ids if liked_ids else watched_ids
    if not seed_ids:
        return []
        
    all_movies = list(Movies.objects.select_related('category', 'language').all())
    if not all_movies:
        return []
        
    movie_texts = []
    movie_id_to_index = {}
    
    for idx, movie in enumerate(all_movies):
        cat_name = movie.category.cat_name if movie.category else ""
        lang_name = movie.language.language_name if movie.language else ""
        # Combine relevant textual features
        text = f"{movie.movie_name} {movie.movie_description} {movie.movie_director} {movie.movie_star} {cat_name} {lang_name}"
        movie_texts.append(text)
        movie_id_to_index[movie.movie_id] = idx
        
    # Create TF-IDF matrix
    tfidf = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = tfidf.fit_transform(movie_texts)
    except ValueError:
        # If all texts are empty or stop words
        return []
        
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Calculate aggregated similarity scores for all seed movies
    scores = np.zeros(len(all_movies))
    for movie_id in seed_ids:
        if movie_id in movie_id_to_index:
            idx = movie_id_to_index[movie_id]
            scores += cosine_sim[idx]
            
    # Sort by highest score
    movie_indices = np.argsort(scores)[::-1]
    
    recommendations = []
    seen_ids = watched_ids | set(MovieFeedback.objects.filter(user=user).values_list('movie_id', flat=True))
    
    for idx in movie_indices:
        movie = all_movies[idx]
        # Only recommend movies not already seen/rated
        if movie.movie_id not in seen_ids:
            recommendations.append(movie)
            if len(recommendations) >= limit:
                break
                
    return recommendations


def _get_recommendations(user):
    """Generate movie recommendations based on user's watch history, ratings, and preferences."""
    if not user:
        # Return trending movies if no user
        return Movies.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-review_count', '-avg_rating')[:10]
    
    watched_movie_ids = set(WatchHistory.objects.filter(user=user).values_list('movie_id', flat=True))
    rated_movie_ids = set(MovieFeedback.objects.filter(user=user).values_list('movie_id', flat=True))
    
    # Get user's preferred language
    preferred_language = _get_user_preferred_language(user)
    
    # Get user's preferred categories from watch history
    preferred_categories = Categories.objects.filter(
        movies__watch_logs__user=user
    ).annotate(
        watch_count=Count('movies__watch_logs')
    ).order_by('-watch_count')[:3]
    
    # Get highly rated movies by user (4+ stars)
    highly_rated = MovieFeedback.objects.filter(
        user=user, rating__gte=4
    ).values_list('movie_id', flat=True)
    
    recommendations = []
    seen_ids = watched_movie_ids | rated_movie_ids
    
    # 0. Try AI-based recommendations first
    ai_recs = _get_ai_movie_recommendations(user, limit=5)
    if ai_recs:
        recommendations.extend(ai_recs)
        for rec in ai_recs:
            seen_ids.add(rec.movie_id)
    
    # 1. Based on preferred language (highest priority)
    if preferred_language:
        lang_recs = Movies.objects.filter(
            language=preferred_language
        ).exclude(movie_id__in=seen_ids).annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-review_count', '-avg_rating')[:5]
        recommendations.extend(lang_recs)
    
    # 2. Based on preferred genres
    if preferred_categories.exists():
        genre_recs = Movies.objects.filter(
            category__in=preferred_categories
        ).exclude(movie_id__in=seen_ids).distinct()[:5]
        recommendations.extend(genre_recs)
    
    # 3. Based on highly rated movies (similar directors/stars)
    if highly_rated.exists():
        highly_rated_movies = Movies.objects.filter(movie_id__in=highly_rated)
        directors = highly_rated_movies.values_list('movie_director', flat=True).distinct()
        stars = highly_rated_movies.values_list('movie_star', flat=True).distinct()
        
        similar_recs = Movies.objects.filter(
            Q(movie_director__in=directors) | Q(movie_star__in=stars)
        ).exclude(movie_id__in=seen_ids).distinct()[:5]
        recommendations.extend(similar_recs)
    
    # 4. Popular trending movies (by review count and average rating)
    trending = Movies.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).filter(
        review_count__gte=3
    ).exclude(
        movie_id__in=seen_ids
    ).order_by('-review_count', '-avg_rating')[:5]
    recommendations.extend(trending)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_recs = []
    for rec in recommendations:
        if rec.movie_id not in seen:
            seen.add(rec.movie_id)
            unique_recs.append(rec)
    
    # Fill remaining slots with any popular movies
    if len(unique_recs) < 10:
        remaining = Movies.objects.exclude(
            movie_id__in=[r.movie_id for r in unique_recs] + list(seen_ids)
        ).annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')[:10 - len(unique_recs)]
        unique_recs.extend(remaining)
    
    return unique_recs[:10]


def _get_language_recommendations(user, language):
    """Get recommended movies in a specific language for a user."""
    if not user or not language:
        # Return popular movies in that language
        return Movies.objects.filter(
            language=language
        ).annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-review_count', '-avg_rating')[:20]
    
    watched_movie_ids = set(WatchHistory.objects.filter(user=user).values_list('movie_id', flat=True))
    rated_movie_ids = set(MovieFeedback.objects.filter(user=user).values_list('movie_id', flat=True))
    seen_ids = watched_movie_ids | rated_movie_ids
    
    # Get user's preferred categories
    preferred_categories = Categories.objects.filter(
        movies__watch_logs__user=user,
        movies__language=language
    ).annotate(
        watch_count=Count('movies__watch_logs')
    ).order_by('-watch_count')[:3]
    
    recommendations = []
    
    # 1. Movies in preferred categories within this language
    if preferred_categories.exists():
        genre_recs = Movies.objects.filter(
            language=language,
            category__in=preferred_categories
        ).exclude(movie_id__in=seen_ids).annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-review_count', '-avg_rating')[:10]
        recommendations.extend(genre_recs)
    
    # 2. Popular movies in this language
    popular = Movies.objects.filter(
        language=language
    ).exclude(
        movie_id__in=seen_ids
    ).annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-review_count', '-avg_rating')[:15]
    recommendations.extend(popular)
    
    # Remove duplicates
    seen = set()
    unique_recs = []
    for rec in recommendations:
        if rec.movie_id not in seen:
            seen.add(rec.movie_id)
            unique_recs.append(rec)
    
    return unique_recs[:20]


def movie(request, movie_id):
    movie = get_object_or_404(Movies, movie_id=movie_id)
    user_id = request.session.get('user_id')
    user = None
    user_feedback = None
    is_login = request.session.get('is_login', False)
    
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            # Track watch history
            watch_history, created = WatchHistory.objects.get_or_create(
                user=user,
                movie=movie,
                defaults={'last_watched_at': timezone.now()}
            )
            if not created:
                watch_history.times_watched = F('times_watched') + 1
                watch_history.last_watched_at = timezone.now()
                watch_history.save()
            
            # Get user's feedback if exists
            user_feedback = MovieFeedback.objects.filter(user=user, movie=movie).first()
        except User.DoesNotExist:
            pass
    
    # Get all reviews for this movie
    reviews = MovieFeedback.objects.filter(movie=movie).select_related('user').order_by('-created_at')[:10]
    avg_rating = MovieFeedback.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Check subscription
    latest_payment = Payment.objects.filter(user_id=user_id).order_by('-end_date').first()
    has_paid = False
    if latest_payment and latest_payment.end_date >= timezone.now().date():
        has_paid = True

    context = {
        'movie': movie,
        'is_login': is_login,
        'user_feedback': user_feedback,
        'reviews': reviews,
        'has_paid': has_paid,
        'avg_rating': round(avg_rating, 1) if avg_rating else None,
        'review_count': reviews.count(),
    }
    
    return render(request, 'movie.html', context)

def process_payment(request):
    """Process payment form submission and save data in Payment model."""
    if request.method == "POST":
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')  # Ensure the user is logged in

        sub_id = request.POST.get('sub_id')
        subscription = get_object_or_404(Subscription, sub_id=sub_id)
        user = get_object_or_404(User, id=user_id)

        raw_card_number = request.POST.get('card-number', '')
        card_number = re.sub(r'\D', '', raw_card_number or '')
        card_holder = request.POST.get('card-holder-name', '')
        expiry_month = request.POST.get('exp-month', '')
        expiry_year = request.POST.get('exp-year', '')
        expiry_month = expiry_month.zfill(2)
        expiry_year = expiry_year.zfill(2)

        if len(card_number) < 4 or not card_number.isdigit():
            messages.error(request, "Please enter a valid card number.")
            return redirect('payment', sub_id=sub_id)

        if not (expiry_month.isdigit() and expiry_year.isdigit()):
            messages.error(request, "Please enter a valid expiry date.")
            return redirect('payment', sub_id=sub_id)

        expiry_date = f"{expiry_month}/{expiry_year}"

        start_date = date.today()
        end_date = _calculate_end_date(subscription.sub_time_limit, start_date)

        try:
            with transaction.atomic():
                payment = Payment.objects.create(
                    user=user,
                    subscription=subscription,
                    pay_method='CARD',
                    card_last4=card_number[-4:],
                    card_holder_nm=card_holder,
                    expiry_date=expiry_date,
                    sub_price=subscription.sub_price,
                    start_date=start_date,
                    end_date=end_date,
                )
        except Exception as exc:
            logger.exception("Payment processing failed for user %s subscription %s", user.email, subscription.sub_name)
            messages.error(request, "We couldn't process your payment. Please try again.")
            return redirect('payment', sub_id=sub_id)

        # Store subscription info in session
        request.session['sub_plan'] = subscription.sub_name
        request.session['last_payment_id'] = payment.pay_id
        request.session.modified = True

        messages.success(request, "Payment processed successfully.")
        return redirect('payment_succesfull', payment_id=payment.pay_id)  # Redirect to success page

    return redirect('subscription')  # Redirect to subscription page if no POST request

def payment_succesfull(request, payment_id):
    payment = get_object_or_404(Payment, pay_id=payment_id)
    user_id = request.session.get('user_id')

    if user_id and payment.user_id != user_id:
        messages.error(request, "You are not allowed to view this receipt.")
        return redirect('index')

    request.session['last_payment_id'] = payment.pay_id
    request.session.modified = True

    return render(request, "payment_succesfull.html", {
        'payment': payment,
    })


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    sUrl = settings.STATIC_URL        # /static/
    mUrl = settings.MEDIA_URL         # /media/
    mRoot = settings.MEDIA_ROOT       # .../media/

    # Handle Media Files (e.g., profile pics, uploaded content)
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    
    # Handle Static Files (e.g., logos, css)
    elif uri.startswith(sUrl):
        relative_path = uri.replace(sUrl, "")
        # Use finders to locate the file in app directories or static root
        path = finders.find(relative_path)
        if not path:
             # Fallback if finders can't find it (unlikely in dev, but possible)
             sRoot = settings.STATIC_ROOT # Might be None in dev
             if sRoot:
                path = os.path.join(sRoot, relative_path)
    
    # Handle absolute paths or other cases
    else:
        return uri

    # Verify formatting of path for Windows
    if path and not os.path.isfile(path):
         # Sometimes finders return a list/tuple
         if isinstance(path, (list, tuple)):
             path = path[0]

    # Final check
    if path and not os.path.isfile(path):
        # logging.warning(f"Static file not found for PDF: {uri} -> {path}")
        return uri  # Return original if resolved path is invalid
        
    return path

def download_receipt(request, payment_id):
    payment = get_object_or_404(Payment, pay_id=payment_id)
    user_id = request.session.get('user_id')
    last_payment_id = request.session.get('last_payment_id')

    if user_id:
        if payment.user_id != user_id:
            messages.error(request, "You are not allowed to download this receipt.")
            return redirect('index')
    elif last_payment_id != payment_id:
        return redirect('login')

    template_path = 'receipt.html'
    context = {'payment': payment}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.transaction_id}.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback
    )
    
    if pisa_status.err:
        return HttpResponse("We had some errors while generating the receipt.")
    return response

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms(request):
    return render(request, 'terms.html')

def profile_pic(request):
    user_id = request.session.get('user_id')  # Get logged-in user ID
    user = User.objects.get(id=user_id)

    if request.method == "POST" and request.FILES.get('profilePic'):
        user.profile_image = request.FILES['profilePic']
        user.save()
        return redirect('index')  # Redirect to index page after upload

    return render(request, 'profile_pic.html')

def learn_more_subcription(request):
    return render(request, 'learn_more_subcription.html')

def search_movies(request):
    """Search and filter movies by star, director, movie name, and alphabet."""
    is_login = request.session.get('is_login', False)
    user_name = request.session.get('user_name', '')
    user_mail = request.session.get('user_email')
    user_id = request.session.get('user_id')
    
    # Get filter parameters
    query = request.GET.get('q', '').strip()
    filter_type = request.GET.get('filter', 'all')  # all, star, director, movie
    alphabet = request.GET.get('alphabet', '')  # A-Z or all
    
    # Check if searching for a star and if exact star match exists, redirect to star page
    if query and filter_type == 'star':
        try:
            star = Star.objects.filter(star_name__iexact=query).first()
            if star:
                return redirect('star_detail', star_id=star.star_id)
        except:
            pass
    
    # Get user subscription info
    latest_payment = None
    has_paid = False
    if user_id:
        latest_payment = Payment.objects.filter(user_id=user_id).order_by('-end_date').first()
        if latest_payment and latest_payment.end_date >= timezone.now().date():
            has_paid = True
    sub_plan = latest_payment.subscription.sub_name if latest_payment and latest_payment.subscription else None
    
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = None
    
    profile_image = user.profile_image.url if user and user.profile_image else '/media/profile_pics/usericon.png'
    end_date = latest_payment.end_date if latest_payment else None
    
    # Start with all movies
    movies = Movies.objects.all()
    
    # Apply alphabetical filter first (if no query)
    if alphabet and alphabet != 'all' and alphabet.isalpha() and not query:
        movies = movies.filter(movie_name__istartswith=alphabet.upper())
    
    # Apply search filter
    if query:
        if filter_type == 'star':
            movies = movies.filter(movie_star__icontains=query)
        elif filter_type == 'director':
            movies = movies.filter(movie_director__icontains=query)
        elif filter_type == 'movie':
            movies = movies.filter(movie_name__icontains=query)
        else:  # all - search in all fields
            movies = movies.filter(
                Q(movie_name__icontains=query) |
                Q(movie_director__icontains=query) |
                Q(movie_star__icontains=query)
            )
        
        # Apply alphabet filter on top of query results
        if alphabet and alphabet != 'all' and alphabet.isalpha():
            movies = movies.filter(movie_name__istartswith=alphabet.upper())
    
    # Order by movie name
    movies = movies.order_by('movie_name')
    
    # Get unique stars and directors for suggestions
    all_stars = Movies.objects.values_list('movie_star', flat=True).distinct()
    all_directors = Movies.objects.values_list('movie_director', flat=True).distinct()
    all_movie_names = Movies.objects.values_list('movie_name', flat=True).distinct()
    
    # Get Star objects for linking - create a dictionary mapping star names to star_ids
    star_objects = {}
    # Get all Star objects to match against movie star names
    all_star_objects = Star.objects.all()
    for star_obj in all_star_objects:
        # Case-insensitive matching - store both original and lowercase versions
        star_objects[star_obj.star_name.lower()] = star_obj.star_id
        star_objects[star_obj.star_name] = star_obj.star_id
    
    context = {
        'movies': movies,
        'query': query,
        'filter_type': filter_type,
        'alphabet': alphabet,
        'is_login': is_login,
        'user_name': user_name,
        'user_email': user_mail,
        'sub_plan': sub_plan,
        'has_paid': has_paid,
        'end_date': end_date,
        'profile_image': profile_image,
        'all_stars': all_stars,
        'all_directors': all_directors,
        'all_movie_names': all_movie_names,
        'star_objects': star_objects,  # For linking star names to star pages
    }
    
    return render(request, 'search_results.html', context)

def star_detail(request, star_id):
    """Display star profile page with all movies starring that star."""
    is_login = request.session.get('is_login', False)
    user_name = request.session.get('user_name', '')
    user_mail = request.session.get('user_email')
    user_id = request.session.get('user_id')
    
    # Get star object
    star = get_object_or_404(Star, star_id=star_id)
    
    # Get all movies by this star (match by star_name in movie_star field)
    movies = Movies.objects.filter(movie_star__icontains=star.star_name).select_related('category', 'language').order_by('movie_name')
    
    # Get user subscription info
    latest_payment = None
    if user_id:
        latest_payment = Payment.objects.filter(user_id=user_id).order_by('-end_date').first()
    sub_plan = latest_payment.subscription.sub_name if latest_payment and latest_payment.subscription else None
    has_paid = latest_payment is not None
    
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = None
    
    profile_image = user.profile_image.url if user and user.profile_image else '/media/profile_pics/usericon.png'
    end_date = latest_payment.end_date if latest_payment else None
    
    context = {
        'star': star,
        'movies': movies,
        'is_login': is_login,
        'user_name': user_name,
        'user_email': user_mail,
        'sub_plan': sub_plan,
        'has_paid': has_paid,
        'end_date': end_date,
        'profile_image': profile_image,
    }
    
    return render(request, 'star_detail.html', context)

def autocomplete_suggestions(request):
    """API endpoint for autocomplete suggestions."""
    query = request.GET.get('q', '').strip().lower()
    filter_type = request.GET.get('type', 'all')  # all, star, director, movie
    
    suggestions = []
    
    if not query:
        return JsonResponse({'suggestions': []})
    
    if filter_type == 'star':
        # Search in Star model for autocomplete
        stars = Star.objects.filter(star_name__icontains=query)[:10]
        suggestions = [{'value': star.star_name, 'type': 'Star', 'id': star.star_id, 'url': f'/star/{star.star_id}/'} for star in stars]
        # Also include stars from Movies model that aren't in Star model
        movie_stars = Movies.objects.filter(movie_star__icontains=query).values_list('movie_star', flat=True).distinct()[:5]
        existing_star_names = {star.star_name for star in stars}
        for movie_star in movie_stars:
            if movie_star not in existing_star_names:
                suggestions.append({'value': movie_star, 'type': 'Star', 'id': None, 'url': f'/search/?q={movie_star}&filter=star'})
    elif filter_type == 'director':
        directors = Movies.objects.filter(movie_director__icontains=query).values_list('movie_director', flat=True).distinct()[:10]
        suggestions = [{'value': director, 'type': 'Director'} for director in directors]
    elif filter_type == 'movie':
        movies = Movies.objects.filter(movie_name__icontains=query).values_list('movie_name', flat=True).distinct()[:10]
        suggestions = [{'value': movie, 'type': 'Movie'} for movie in movies]
    else:  # all
        # Search Star model first
        stars = Star.objects.filter(star_name__icontains=query)[:5]
        star_suggestions = [{'value': star.star_name, 'type': 'Star', 'id': star.star_id, 'url': f'/star/{star.star_id}/'} for star in stars]
        
        # Get movie stars and directors
        movie_stars = Movies.objects.filter(movie_star__icontains=query).values_list('movie_star', flat=True).distinct()[:3]
        directors = Movies.objects.filter(movie_director__icontains=query).values_list('movie_director', flat=True).distinct()[:3]
        movies = Movies.objects.filter(movie_name__icontains=query).values_list('movie_name', flat=True).distinct()[:4]
        
        existing_star_names = {star.star_name for star in stars}
        additional_stars = [{'value': movie_star, 'type': 'Star', 'id': None, 'url': f'/search/?q={movie_star}&filter=star'} 
                           for movie_star in movie_stars if movie_star not in existing_star_names]
        
        suggestions = (
            star_suggestions +
            additional_stars +
            [{'value': director, 'type': 'Director'} for director in directors] +
            [{'value': movie, 'type': 'Movie'} for movie in movies]
        )[:15]  # Limit total suggestions
    
    return JsonResponse({'suggestions': suggestions})


def submit_movie_feedback(request, movie_id):
    """Submit rating and review for a movie."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
    
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'error': 'Please login to submit feedback'}, status=401)
    
    try:
        user = User.objects.get(id=user_id)
        movie = get_object_or_404(Movies, movie_id=movie_id)
        
        rating = int(request.POST.get('rating', 0))
        review = request.POST.get('review', '').strip()
        
        if not (1 <= rating <= 5):
            return JsonResponse({'success': False, 'error': 'Rating must be between 1 and 5'}, status=400)
        
        feedback, created = MovieFeedback.objects.update_or_create(
            user=user,
            movie=movie,
            defaults={
                'rating': rating,
                'review': review,
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Feedback submitted successfully',
            'created': created
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def submit_app_feedback(request):
    """Submit general app feedback."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
    
    user_id = request.session.get('user_id')
    user = None
    email = request.POST.get('email', '').strip()
    
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            email = user.email
        except User.DoesNotExist:
            pass
    
    if not email:
        return JsonResponse({'success': False, 'error': 'Email is required'}, status=400)
    
    category = request.POST.get('category', AppFeedback.CATEGORY_OTHER)
    rating = request.POST.get('rating')
    message = request.POST.get('message', '').strip()
    
    if not message:
        return JsonResponse({'success': False, 'error': 'Message is required'}, status=400)
    
    try:
        feedback = AppFeedback.objects.create(
            user=user,
            email=email,
            category=category,
            rating=int(rating) if rating and rating.isdigit() else None,
            message=message,
        )
        
        messages.success(request, 'Thank you for your feedback!')
        return JsonResponse({
            'success': True,
            'message': 'Feedback submitted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def app_feedback_page(request):
    """Display app feedback form page."""
    is_login = request.session.get('is_login', False)
    user_name = request.session.get('user_name', '')
    user_mail = request.session.get('user_email')
    
    return render(request, 'app_feedback.html', {
        'is_login': is_login,
        'user_name': user_name,
        'user_email': user_mail,
    })


def artist_list(request):
    """Display list of all artists."""
    is_login = request.session.get('is_login', False)
    user_name = request.session.get('user_name', '')
    user_mail = request.session.get('user_email')
    user_id = request.session.get('user_id')
    
    category_filter = request.GET.get('category', '')
    artists = Artist.objects.all()
    
    if category_filter:
        artists = artists.filter(category=category_filter)
    
    artists = artists.order_by('-popularity_rating', 'artist_name')
    
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass
    
    profile_image = user.profile_image.url if user and user.profile_image else '/media/profile_pics/usericon.png'
    
    context = {
        'artists': artists,
        'is_login': is_login,
        'user_name': user_name,
        'user_email': user_mail,
        'profile_image': profile_image,
        'category_filter': category_filter,
    }
    
    return render(request, 'artist_list.html', context)


def artist_detail(request, artist_id):
    """Display artist profile page with movies."""
    is_login = request.session.get('is_login', False)
    user_name = request.session.get('user_name', '')
    user_mail = request.session.get('user_email')
    user_id = request.session.get('user_id')
    
    artist = get_object_or_404(Artist, artist_id=artist_id)
    
    # Get movies by role
    movies_by_role = artist.get_movies_by_role()
    
    # Get songs by artist
    artist_songs = artist.songs.all()
    
    # Check if user follows this artist
    is_following = False
    if user_id:
        is_following = UserArtistFollow.objects.filter(user_id=user_id, artist=artist).exists()
    
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass
    
    profile_image = user.profile_image.url if user and user.profile_image else '/media/profile_pics/usericon.png'
    
    # Get user subscription info
    latest_payment = None
    if user_id:
        latest_payment = Payment.objects.filter(user_id=user_id).order_by('-end_date').first()
    sub_plan = latest_payment.subscription.sub_name if latest_payment and latest_payment.subscription else None
    has_paid = latest_payment is not None
    end_date = latest_payment.end_date if latest_payment else None
    
    context = {
        'artist': artist,
        'movies_acted': movies_by_role['acted'],
        'movies_directed': movies_by_role['directed'],
        'movies_composed': movies_by_role['composed'],
        'artist_songs': artist_songs,
        'is_following': is_following,
        'is_login': is_login,
        'user_name': user_name,
        'user_email': user_mail,
        'profile_image': profile_image,
        'sub_plan': sub_plan,
        'has_paid': has_paid,
        'end_date': end_date,
    }
    
    return render(request, 'artist_detail.html', context)


def toggle_follow_artist(request, artist_id):
    """Toggle follow/unfollow an artist."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
    
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'error': 'Please login to follow artists'}, status=401)
    
    try:
        user = User.objects.get(id=user_id)
        artist = get_object_or_404(Artist, artist_id=artist_id)
        
        follow, created = UserArtistFollow.objects.get_or_create(user=user, artist=artist)
        
        if not created:
            follow.delete()
            is_following = False
        else:
            is_following = True
        
        return JsonResponse({
            'success': True,
            'is_following': is_following,
            'follower_count': artist.follower_count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def language_movies(request, language_id):
    """Display movies filtered by language."""
    is_login = request.session.get('is_login', False)
    user_name = request.session.get('user_name', '')
    user_mail = request.session.get('user_email')
    user_id = request.session.get('user_id')
    
    language = get_object_or_404(Language, language_id=language_id, is_active=True)
    
    # Get movies in this language
    movies = Movies.objects.filter(language=language).annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-review_count', '-avg_rating', 'movie_name')
    
    # Get user subscription info
    latest_payment = None
    if user_id:
        latest_payment = Payment.objects.filter(user_id=user_id).order_by('-end_date').first()
    sub_plan = latest_payment.subscription.sub_name if latest_payment and latest_payment.subscription else None
    has_paid = latest_payment is not None
    
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass
    
    profile_image = user.profile_image.url if user and user.profile_image else '/media/profile_pics/usericon.png'
    end_date = latest_payment.end_date if latest_payment else None
    
    # Get all languages for navigation
    languages = Language.objects.filter(is_active=True).order_by('display_order', 'language_name')
    
    context = {
        'language': language,
        'movies': movies,
        'languages': languages,
        'is_login': is_login,
        'user_name': user_name,
        'user_email': user_mail,
        'profile_image': profile_image,
        'sub_plan': sub_plan,
        'has_paid': has_paid,
        'end_date': end_date,
    }
    
    return render(request, 'language_movies.html', context)


# ==================== WEB SERIES VIEWS ====================

def webseries_language_list(request, language_id=None):
    """Display web series filtered by language."""
    is_login = request.session.get('is_login', False)
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name', '')
    user_mail = request.session.get('user_email', '')
    
    # Get all active languages
    languages = Language.objects.filter(is_active=True).order_by('display_order', 'language_name')
    
    # Get user info
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass
    
    profile_image = user.profile_image.url if user and user.profile_image else '/media/profile_pics/usericon.png'
    
    # Get subscription info
    latest_payment = None
    if user_id:
        latest_payment = Payment.objects.filter(user_id=user_id).order_by('-end_date').first()
    sub_plan = latest_payment.subscription.sub_name if latest_payment and latest_payment.subscription else None
    has_paid = latest_payment is not None
    end_date = latest_payment.end_date if latest_payment else None
    
    # Get web series by language
    selected_language = None
    webseries_list = WebSeries.objects.all()
    
    if language_id:
        selected_language = get_object_or_404(Language, language_id=language_id, is_active=True)
        webseries_list = webseries_list.filter(language=selected_language)
    
    webseries_list = webseries_list.select_related('language').prefetch_related('genre').order_by('-created_at')
    
    context = {
        'languages': languages,
        'selected_language': selected_language,
        'webseries_list': webseries_list,
        'is_login': is_login,
        'user_name': user_name,
        'user_email': user_mail,
        'profile_image': profile_image,
        'sub_plan': sub_plan,
        'has_paid': has_paid,
        'end_date': end_date,
    }
    
    return render(request, 'webseries/webseries_language_list.html', context)


def webseries_detail(request, webseries_id):
    """Display web series detail page with episodes."""
    is_login = request.session.get('is_login', False)
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name', '')
    user_mail = request.session.get('user_email', '')
    
    webseries = get_object_or_404(WebSeries.objects.select_related('language').prefetch_related('genre', 'episodes'), webseries_id=webseries_id)
    episodes = list(webseries.episodes.all().order_by('episode_number'))
    first_episode = episodes[0] if episodes else None
    first_episode_source = first_episode.get_video_source() if first_episode else None
    
    # Get user info
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass
    
    profile_image = user.profile_image.url if user and user.profile_image else '/media/profile_pics/usericon.png'
    
    # Get subscription info
    latest_payment = None
    if user_id:
        latest_payment = Payment.objects.filter(user_id=user_id).order_by('-end_date').first()
    has_paid = False
    if latest_payment and latest_payment.end_date >= timezone.now().date():
        has_paid = True
    sub_plan = latest_payment.subscription.sub_name if latest_payment and latest_payment.subscription else None
    end_date = latest_payment.end_date if latest_payment else None
    
    # Check if in watchlist
    in_watchlist = False
    if user_id:
        in_watchlist = WebSeriesWatchlist.objects.filter(user_id=user_id, webseries=webseries).exists()
    
    # Get user like/rating
    user_like = None
    if user_id:
        try:
            user_like = WebSeriesLike.objects.get(user_id=user_id, webseries=webseries)
        except WebSeriesLike.DoesNotExist:
            pass
    
    # Get watch history for episodes
    episode_watch_status = {}
    if user_id:
        watch_history = WebSeriesWatchHistory.objects.filter(
            user_id=user_id,
            episode__in=episodes
        ).select_related('episode')
        for history in watch_history:
            episode_watch_status[history.episode.episode_id] = {
                'completed': history.completed,
                'progress': history.progress_percent,
            }
    
    now = timezone.now()
    events = webseries.events.filter(
        is_active=True,
        end_time__gte=now
    ).order_by('start_time')
    admin_recommendations = WebSeriesRecommendation.objects.filter(
        source_webseries=webseries,
        is_active=True
    ).select_related('recommended_webseries').order_by('priority', '-updated_at')

    context = {
        'webseries': webseries,
        'episodes': episodes,
        'first_episode': first_episode,
        'first_episode_source': first_episode_source,
        'in_watchlist': in_watchlist,
        'user_like': user_like,
        'episode_watch_status': episode_watch_status,
        'is_login': is_login,
        'user_name': user_name,
        'user_email': user_mail,
        'profile_image': profile_image,
        'sub_plan': sub_plan,
        'has_paid': has_paid,
        'end_date': end_date,
        'events': events,
        'admin_recommendations': admin_recommendations,
    }
    
    return render(request, 'webseries/webseries_detail.html', context)


def _get_ai_webseries_recommendations(user, limit=10):
    """Generate AI-powered web series recommendations using TF-IDF and cosine similarity."""
    if not user or not AI_RECOMMENDATIONS_AVAILABLE:
        return []
        
    watched_episodes = WebSeriesWatchHistory.objects.filter(user=user).select_related('episode__webseries')
    watched_ws_ids = set([wh.episode.webseries.webseries_id for wh in watched_episodes])
    
    liked_ws = WebSeriesLike.objects.filter(user=user, liked=True).select_related('webseries')
    liked_ws_ids = set([like.webseries.webseries_id for like in liked_ws])
    
    seed_ws_ids = liked_ws_ids if liked_ws_ids else watched_ws_ids
    if not seed_ws_ids:
        return []
        
    all_ws = list(WebSeries.objects.select_related('language').prefetch_related('genre').all())
    if not all_ws:
        return []
        
    ws_texts = []
    ws_id_to_index = {}
    
    for idx, ws in enumerate(all_ws):
        genres = " ".join([g.genre_name for g in ws.genre.all()])
        lang_name = ws.language.language_name if ws.language else ""
        text = f"{ws.title} {ws.description} {ws.cast} {genres} {lang_name}"
        ws_texts.append(text)
        ws_id_to_index[ws.webseries_id] = idx
        
    tfidf = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = tfidf.fit_transform(ws_texts)
    except ValueError:
        return []
        
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    scores = np.zeros(len(all_ws))
    for ws_id in seed_ws_ids:
        if ws_id in ws_id_to_index:
            idx = ws_id_to_index[ws_id]
            scores += cosine_sim[idx]
            
    ws_indices = np.argsort(scores)[::-1]
    
    recommendations = []
    for idx in ws_indices:
        ws = all_ws[idx]
        if ws.webseries_id not in watched_ws_ids:
            recommendations.append(ws)
            if len(recommendations) >= limit:
                break
                
    return recommendations


def webseries_recommendations(request):
    """Generate personalized web series recommendations."""
    is_login = request.session.get('is_login', False)
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name', '')
    user_mail = request.session.get('user_email', '')
    
    # Get user info
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass
    
    profile_image = user.profile_image.url if user and user.profile_image else '/media/profile_pics/usericon.png'
    
    # Get subscription info
    latest_payment = None
    if user_id:
        latest_payment = Payment.objects.filter(user_id=user_id).order_by('-end_date').first()
    sub_plan = latest_payment.subscription.sub_name if latest_payment and latest_payment.subscription else None
    has_paid = latest_payment is not None
    end_date = latest_payment.end_date if latest_payment else None
    
    # Get all languages
    languages = Language.objects.filter(is_active=True).order_by('display_order', 'language_name')
    
    recommended_webseries = []
    
    if user_id:
        # Get user's watch history
        watched_episodes = WebSeriesWatchHistory.objects.filter(user_id=user_id).select_related('episode__webseries')
        watched_webseries_ids = set([wh.episode.webseries.webseries_id for wh in watched_episodes])
        
        # Get liked web series
        liked_webseries = WebSeriesLike.objects.filter(user_id=user_id, liked=True).select_related('webseries')
        liked_webseries_ids = set([like.webseries.webseries_id for like in liked_webseries])
        
        # Get user's preferred language
        preferred_language = user.preferred_language if user else None
        
        # Get most watched language from watch history
        language_counts = Counter()
        for wh in watched_episodes:
            if wh.episode.webseries.language:
                language_counts[wh.episode.webseries.language.language_id] += 1
        
        most_watched_language_id = None
        if language_counts:
            most_watched_language_id = language_counts.most_common(1)[0][0]
        
        # Recommendation logic
        # 0. AI-based recommendations
        ai_recs = _get_ai_webseries_recommendations(user, limit=5)
        if ai_recs:
            recommended_webseries.extend(ai_recs)
            for rec in ai_recs:
                watched_webseries_ids.add(rec.webseries_id)

        # 1. Based on preferred language
        if preferred_language:
            lang_series = WebSeries.objects.filter(
                language=preferred_language
            ).exclude(webseries_id__in=watched_webseries_ids).order_by('-rating', '-created_at')[:10]
            recommended_webseries.extend(lang_series)
        
        # 2. Based on most watched language
        preferred_lang_id = preferred_language.language_id if preferred_language else None
        if most_watched_language_id and most_watched_language_id != preferred_lang_id:
            try:
                lang = Language.objects.get(language_id=most_watched_language_id)
                lang_series = WebSeries.objects.filter(
                    language=lang
                ).exclude(webseries_id__in=watched_webseries_ids).order_by('-rating', '-created_at')[:10]
                recommended_webseries.extend(lang_series)
            except Language.DoesNotExist:
                pass
        
        # 3. Based on liked web series genres
        if liked_webseries:
            liked_genres = set()
            for like in liked_webseries:
                liked_genres.update(like.webseries.genre.all())
            
            if liked_genres:
                genre_series = WebSeries.objects.filter(
                    genre__in=liked_genres
                ).exclude(webseries_id__in=watched_webseries_ids).distinct().order_by('-rating', '-created_at')[:10]
                recommended_webseries.extend(genre_series)
        
        # 4. Trending in user's preferred language
        if preferred_language:
            trending = WebSeries.objects.filter(
                language=preferred_language,
                is_trending=True
            ).exclude(webseries_id__in=watched_webseries_ids).order_by('-rating', '-created_at')[:5]
            recommended_webseries.extend(trending)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommended = []
        for ws in recommended_webseries:
            if ws.webseries_id not in seen:
                seen.add(ws.webseries_id)
                unique_recommended.append(ws)
        recommended_webseries = unique_recommended[:20]  # Limit to 20
    
    # If no recommendations, show trending
    if not recommended_webseries:
        recommended_webseries = WebSeries.objects.filter(is_trending=True).order_by('-rating', '-created_at')[:20]
    
    context = {
        'recommended_webseries': recommended_webseries,
        'languages': languages,
        'is_login': is_login,
        'user_name': user_name,
        'user_email': user_mail,
        'profile_image': profile_image,
        'sub_plan': sub_plan,
        'has_paid': has_paid,
        'end_date': end_date,
    }
    
    return render(request, 'webseries/webseries_recommendations.html', context)


def toggle_watchlist(request, webseries_id):
    """Add or remove web series from watchlist."""
    if not request.session.get('is_login'):
        return JsonResponse({'success': False, 'message': 'Please login first'})
    
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'User not found'})
    
    webseries = get_object_or_404(WebSeries, webseries_id=webseries_id)
    
    if request.method == 'POST':
        watchlist_item, created = WebSeriesWatchlist.objects.get_or_create(
            user_id=user_id,
            webseries=webseries
        )
        
        if not created:
            watchlist_item.delete()
            return JsonResponse({'success': True, 'in_watchlist': False, 'message': 'Removed from watchlist'})
        
        return JsonResponse({'success': True, 'in_watchlist': True, 'message': 'Added to watchlist'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# ==================== SONGS VIEWS ====================

def songs_list(request, language_id=None):
    """Display list of all songs with an audio player, filtered by language if provided."""
    is_login = request.session.get('is_login', False)
    user_name = request.session.get('user_name', '')
    user_email = request.session.get('user_email')
    user_id = request.session.get('user_id')
    
    songs = Song.objects.prefetch_related('singers', 'language').order_by('-release_date', '-is_featured')
    
    liked_song_ids = []
    if user_id:
        liked_song_ids = list(UserSongLike.objects.filter(user_id=user_id).values_list('song_id', flat=True))
    
    selected_language = None
    if language_id:
        selected_language = get_object_or_404(Language, language_id=language_id)
        songs = songs.filter(language=selected_language)
        
    languages = Language.objects.filter(is_active=True).order_by('display_order', 'language_name')
    
    # Get user info and subscription
    user = None
    profile_image = '/media/profile_pics/usericon.png'
    sub_plan = None
    has_paid = False
    end_date = None
    
    user_playlists = []
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            if user.profile_image:
                profile_image = user.profile_image.url
                
            latest_payment = Payment.objects.filter(user_id=user_id).order_by('-end_date').first()
            if latest_payment and latest_payment.subscription:
                sub_plan = latest_payment.subscription.sub_name
                end_date = latest_payment.end_date
                if latest_payment.end_date >= timezone.now().date():
                    has_paid = True
            
            user_playlists = Playlist.objects.filter(user=user).prefetch_related('songs__song')
        except User.DoesNotExist:
            pass
            
    context = {
        'songs': songs,
        'liked_song_ids': liked_song_ids,
        'languages': languages,
        'selected_language': selected_language,
        'is_login': is_login,
        'user_name': user_name,
        'user_email': user_email,
        'profile_image': profile_image,
        'sub_plan': sub_plan,
        'has_paid': has_paid,
        'end_date': end_date,
        'user_playlists': user_playlists,
    }
    
    return render(request, 'songs_list.html', context)

def like_song(request, song_id):
    """Like or unlike a song."""
    if not request.session.get('is_login'):
        return JsonResponse({'success': False, 'message': 'Please login first'})
    
    user_id = request.session.get('user_id')
    song = get_object_or_404(Song, song_id=song_id)
    
    if request.method == 'POST':
        like, created = UserSongLike.objects.get_or_create(user_id=user_id, song=song)
        if not created:
            like.delete()
            return JsonResponse({'success': True, 'liked': False, 'message': 'Removed from liked songs'})
        return JsonResponse({'success': True, 'liked': True, 'message': 'Added to liked songs'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def search_songs(request):
    """Search songs via AJAX."""
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
        
    songs = Song.objects.filter(
        Q(title__icontains=query) | 
        Q(singers__artist_name__icontains=query) |
        Q(language__language_name__icontains=query)
    ).distinct()[:10]
    
    results = []
    for song in songs:
        results.append({
            'id': song.song_id,
            'title': song.title,
            'cover': song.cover_image.url if song.cover_image else '/static/images/logo/amanix_song_logo.png',
            'artist': ', '.join([s.artist_name for s in song.singers.all()]) or 'Unknown Artist',
            'audio': song.audio_file.url if song.audio_file else '',
        })
        
    return JsonResponse({'results': results})



def like_webseries(request, webseries_id):
    """Like or rate a web series."""
    if not request.session.get('is_login'):
        return JsonResponse({'success': False, 'message': 'Please login first'})
    
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'User not found'})
    
    webseries = get_object_or_404(WebSeries, webseries_id=webseries_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        liked = request.POST.get('liked', 'true').lower() == 'true'
        
        # Safely convert rating to int
        rating_value = None
        if rating:
            try:
                rating_value = int(rating)
                if rating_value < 1 or rating_value > 5:
                    rating_value = None
            except (ValueError, TypeError):
                rating_value = None
        
        like_obj, created = WebSeriesLike.objects.get_or_create(
            user_id=user_id,
            webseries=webseries,
            defaults={'liked': liked, 'rating': rating_value}
        )
        
        if not created:
            like_obj.liked = liked
            if rating_value:
                like_obj.rating = rating_value
            like_obj.save()
        
        # Update average rating for web series
        avg_rating = WebSeriesLike.objects.filter(
            webseries=webseries,
            rating__isnull=False
        ).aggregate(Avg('rating'))['rating__avg']
        
        if avg_rating:
            webseries.rating = round(float(avg_rating) * 2, 1)  # Convert 1-5 to 0-10 scale
            webseries.save()
        
        return JsonResponse({
            'success': True,
            'liked': like_obj.liked,
            'rating': like_obj.rating,
            'message': 'Rating updated' if not created else 'Liked successfully'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def watch_episode(request, episode_id):
    """Render the episode player on GET and capture watch progress on POST."""
    is_login = request.session.get('is_login', False)
    if request.method == 'GET' and not is_login:
        return redirect('login')
    if not is_login:
        return JsonResponse({'success': False, 'message': 'Please login first'})
    
    user_id = request.session.get('user_id')
    if not user_id:
        if request.method == 'GET':
            return redirect('login')
        return JsonResponse({'success': False, 'message': 'User not found'})
    
    episode = get_object_or_404(
        Episode.objects.select_related('webseries__language'),
        episode_id=episode_id
    )
    webseries = episode.webseries
    
    latest_payment = Payment.objects.filter(user_id=user_id).order_by('-end_date').first()
    has_paid = False
    if latest_payment and latest_payment.end_date >= timezone.now().date():
        has_paid = True
    
    if request.method == 'GET':
        if not has_paid:
            messages.warning(request, 'Please subscribe to watch episodes.')
            return redirect('subscription')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = None
        
        profile_image = user.profile_image.url if user and user.profile_image else '/media/profile_pics/usericon.png'
        sub_plan = latest_payment.subscription.sub_name if latest_payment and latest_payment.subscription else None
        end_date = latest_payment.end_date if latest_payment else None
        episodes = list(webseries.episodes.all().order_by('episode_number'))
        video_source = episode.get_video_source()
        is_file_source = bool(episode.video_file)
        
        context = {
            'webseries': webseries,
            'episode': episode,
            'episodes': episodes,
            'video_source': video_source,
            'is_file_source': is_file_source,
            'is_login': is_login,
            'profile_image': profile_image,
            'sub_plan': sub_plan,
            'has_paid': has_paid,
            'end_date': end_date,
        }
        return render(request, 'webseries/watch_episode.html', context)
    
    if not has_paid:
        return JsonResponse({'success': False, 'message': 'Please subscribe to continue'})
    
    if request.method == 'POST':
        try:
            progress = float(request.POST.get('progress', 0))
            progress = max(0, min(progress, 100))
        except (ValueError, TypeError):
            progress = 0
        completed = request.POST.get('completed', 'false').lower() == 'true'
        
        watch_history, created = WebSeriesWatchHistory.objects.get_or_create(
            user_id=user_id,
            episode=episode,
            defaults={
                'progress_percent': progress,
                'completed': completed,
                'times_watched': 1
            }
        )
        
        if not created:
            watch_history.progress_percent = progress
            watch_history.completed = completed
            watch_history.times_watched += 1
            watch_history.last_watched_at = timezone.now()
            watch_history.save()
        
        return JsonResponse({
            'success': True,
            'progress': watch_history.progress_percent,
            'completed': watch_history.completed,
            'message': 'Watch history updated'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})
@csrf_exempt
def create_playlist(request):
    if not request.session.get('is_login'):
        return JsonResponse({'success': False, 'message': 'Not logged in'})
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            user_id = request.session.get('user_id')
            user = User.objects.get(id=user_id)
            playlist = Playlist.objects.create(user=user, title=title)
            return JsonResponse({'success': True, 'id': playlist.id, 'title': playlist.title})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False})

@csrf_exempt
def add_to_playlist(request):
    if not request.session.get('is_login'):
        return JsonResponse({'success': False, 'message': 'Not logged in'})
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            playlist_id = data.get('playlist_id')
            song_id = data.get('song_id')
            playlist = Playlist.objects.get(id=playlist_id)
            song = Song.objects.get(song_id=song_id)
            
            if PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
                return JsonResponse({'success': False, 'message': 'Already in playlist'})
                
            PlaylistSong.objects.create(playlist=playlist, song=song)
            return JsonResponse({'success': True, 'message': f'Added to {playlist.title}'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False})
