from django.db import models
import random
import string
from datetime import date
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

def generate_transaction_id(length: int = 10) -> str:
    """Generate a pseudo transaction id for receipts."""
    allowed_chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(allowed_chars, k=length))


class User(models.Model):
    nm = models.CharField(max_length=100)
    email = models.EmailField(max_length=200)
    password = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profile_pics/', default='profile_pics/usericon.png')
    preferred_language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True, blank=True, related_name='users', help_text="User's preferred language for recommendations")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    last_login_at = models.DateTimeField(null=True, blank=True)
    login_count = models.PositiveIntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    block_reason = models.TextField(blank=True, null=True, help_text="Reason for blocking the user")

    class Meta:
        ordering = ['nm']

    def __str__(self):
        return self.nm

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class Subscription(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_name = models.CharField(max_length=100)
    sub_price = models.DecimalField(max_digits=10, decimal_places=2)
    sub_time_limit = models.CharField(max_length=20)

    def __str__(self):
        return self.sub_name


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('CARD', 'Credit / Debit Card'),
        ('UPI', 'UPI'),
        ('NETBANKING', 'Net Banking'),
    )

    pay_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        default=generate_transaction_id,
    )
    pay_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='CARD')
    card_last4 = models.CharField(max_length=4, blank=True)
    card_holder_nm = models.CharField(max_length=100, blank=True)
    expiry_date = models.CharField(max_length=7, blank=True)  # MM/YY
    sub_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField()
    payment_status = models.CharField(max_length=20, default='SUCCESS')
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = generate_transaction_id()
        if not self.sub_price:
            self.sub_price = self.subscription.sub_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.subscription.sub_name} ({self.transaction_id})"
    
class Categories(models.Model):
    cat_id = models.AutoField(primary_key=True)
    cat_name = models.CharField(max_length=50)

    def __str__(self):
        return self.cat_name


class Language(models.Model):
    """Model for managing movie languages."""
    language_id = models.AutoField(primary_key=True)
    language_name = models.CharField(max_length=50, unique=True, db_index=True)
    language_code = models.CharField(max_length=10, unique=True, help_text="ISO language code (e.g., 'hi', 'en', 'ta')")
    is_active = models.BooleanField(default=True, help_text="Show in language selection")
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which language appears")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'language_name']
        verbose_name = "Language"
        verbose_name_plural = "Languages"
        indexes = [
            models.Index(fields=['language_name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.language_name


class Star(models.Model):
    """Model for managing movie stars with photos and backgrounds."""
    star_id = models.AutoField(primary_key=True)
    star_name = models.CharField(max_length=100, unique=True, db_index=True)
    star_photo = models.ImageField(upload_to='stars/photos/', help_text="Star profile photo")
    star_background = models.ImageField(
        upload_to='stars/backgrounds/', 
        null=True, 
        blank=True,
        help_text="Background image for star profile"
    )
    star_bio = models.TextField(blank=True, null=True, help_text="Biography or description of the star")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['star_name']  # Alphabetical ordering by default
        verbose_name = "Star"
        verbose_name_plural = "Stars"
        indexes = [
            models.Index(fields=['star_name']),  # Index for faster alphabetical queries
        ]

    def __str__(self):
        return self.star_name

    @property
    def first_letter(self):
        """Get the first letter of the star's name for alphabetical filtering."""
        return self.star_name[0].upper() if self.star_name else ''
    
class Artist(models.Model):
    """Model for managing artists (actors, singers, directors, composers)."""
    CATEGORY_ACTOR = 'actor'
    CATEGORY_SINGER = 'singer'
    CATEGORY_DIRECTOR = 'director'
    CATEGORY_COMPOSER = 'composer'
    
    CATEGORY_CHOICES = (
        (CATEGORY_ACTOR, 'Actor'),
        (CATEGORY_SINGER, 'Singer'),
        (CATEGORY_DIRECTOR, 'Director'),
        (CATEGORY_COMPOSER, 'Composer'),
    )
    
    artist_id = models.AutoField(primary_key=True)
    artist_name = models.CharField(max_length=100, unique=True, db_index=True)
    artist_photo = models.ImageField(upload_to='artists/photos/', help_text="Artist profile photo")
    artist_background = models.ImageField(
        upload_to='artists/backgrounds/',
        null=True,
        blank=True,
        help_text="Background image for artist profile"
    )
    artist_bio = models.TextField(blank=True, null=True, help_text="Biography or description of the artist")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_ACTOR)
    popularity_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Popularity rating from 0.0 to 10.0"
    )
    is_featured = models.BooleanField(default=False, help_text="Show in popular artists section")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    movies = models.ManyToManyField('Movies', related_name='artists', blank=True, help_text="Movies associated with this artist")
    
    class Meta:
        ordering = ['-popularity_rating', 'artist_name']
        verbose_name = "Artist"
        verbose_name_plural = "Artists"
        indexes = [
            models.Index(fields=['artist_name']),
            models.Index(fields=['-popularity_rating']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.artist_name
    
    @property
    def follower_count(self):
        """Get the number of users following this artist."""
        return self.followers.count()
    
    def get_movies_by_role(self):
        """Get movies grouped by the artist's role."""
        movies_dict = {
            'acted': [],
            'directed': [],
            'composed': [],
        }
        all_movies = self.movies.all()
        for movie in all_movies:
            # Check if artist name appears in movie_star (acted)
            if self.artist_name.lower() in movie.movie_star.lower():
                movies_dict['acted'].append(movie)
            # Check if artist name appears in movie_director (directed)
            if self.artist_name.lower() in movie.movie_director.lower():
                movies_dict['directed'].append(movie)
            # For composed, we'd need a separate field or check
            # For now, we'll add all movies to acted if not found elsewhere
            if movie not in movies_dict['acted'] and movie not in movies_dict['directed']:
                movies_dict['acted'].append(movie)
        return movies_dict


class SingerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(category=Artist.CATEGORY_SINGER)

class Singer(Artist):
    """Proxy model for Singers to show separately in Django Admin."""
    objects = SingerManager()
    
    class Meta:
        proxy = True
        verbose_name = "Singer"
        verbose_name_plural = "Singers"
    
    def save(self, *args, **kwargs):
        self.category = self.CATEGORY_SINGER
        super().save(*args, **kwargs)

class UserArtistFollow(models.Model):
    """Track which artists users follow/like."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_artists')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'artist')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.nm} follows {self.artist.artist_name}"


class Movies(models.Model):
    movie_id = models.AutoField(primary_key=True)
    movie_name = models.CharField(max_length=100)
    movie_description = models.TextField()
    movie_director = models.CharField(max_length=100)
    movie_star = models.CharField(max_length=100)
    movie_rating = models.CharField(max_length=100)
    movie_duration = models.CharField(max_length=100)
    movie_release_date = models.CharField(max_length=100)
    movie_image = models.ImageField(upload_to='images/')
    movie_backdrop = models.ImageField(
        upload_to='images/backdrops/',
        null=True,
        blank=True,
        help_text="Optional cinematic background shown on detail page"
    )
    movie_video = models.FileField(upload_to='movies/', null=True, blank=True)
    # ForeignKey linking to Categories
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="movies")
    # ForeignKey linking to Language
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True, blank=True, related_name="movies", help_text="Primary language of the movie")

    def __str__(self):
        return self.movie_name


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=40, db_index=True)
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-login_time']

    def __str__(self):
        return f'{self.user.nm} logged in at {self.login_time}'

    @property
    def is_active(self):
        return self.logout_time is None


class MovieEvent(models.Model):
    EVENT_NEW_RELEASE = 'new_release'
    EVENT_SPECIAL_SCREENING = 'special_screening'
    EVENT_FREE_STREAM = 'free_stream'

    EVENT_TYPE_CHOICES = (
        (EVENT_NEW_RELEASE, 'New Release'),
        (EVENT_SPECIAL_SCREENING, 'Special Screening'),
        (EVENT_FREE_STREAM, 'Limited-Time Free Stream'),
    )

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=32, choices=EVENT_TYPE_CHOICES, default=EVENT_NEW_RELEASE)
    movie = models.ForeignKey(Movies, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['start_time', 'end_time']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_live(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time


class WatchHistory(models.Model):
    """Track how users interact with movies to power recommendations."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE, related_name='watch_logs')
    first_watched_at = models.DateTimeField(auto_now_add=True)
    last_watched_at = models.DateTimeField(default=timezone.now)
    times_watched = models.PositiveIntegerField(default=1)
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    completed = models.BooleanField(default=False)
    device_type = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-last_watched_at']
        indexes = [
            models.Index(fields=['user', 'movie']),
            models.Index(fields=['-last_watched_at']),
        ]
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.nm} - {self.movie.movie_name}"


class MovieFeedback(models.Model):
    """Store ratings and reviews users leave on movies."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_feedback')
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating between 1 (lowest) and 5 (highest).",
    )
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.movie.movie_name} review by {self.user.nm}"


class AppFeedback(models.Model):
    """Capture general feedback about the application."""

    CATEGORY_USABILITY = 'usability'
    CATEGORY_BUG = 'bug'
    CATEGORY_UI_UX = 'uiux'
    CATEGORY_OTHER = 'other'

    CATEGORY_CHOICES = (
        (CATEGORY_USABILITY, 'Usability'),
        (CATEGORY_BUG, 'Bug Report'),
        (CATEGORY_UI_UX, 'UI / UX'),
        (CATEGORY_OTHER, 'Other'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='app_feedback')
    email = models.EmailField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_USABILITY)
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Optional rating between 1 and 5 to describe overall satisfaction.",
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        name = self.user.nm if self.user else self.email or 'Anonymous'
        return f"{name} - {self.get_category_display()}"


class Genre(models.Model):
    """Model for web series genres."""
    genre_id = models.AutoField(primary_key=True)
    genre_name = models.CharField(max_length=50, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['genre_name']
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
    
    def __str__(self):
        return self.genre_name


class WebSeries(models.Model):
    """Model for web series with all required fields."""
    AGE_RATING_CHOICES = (
        ('U', 'U - Universal'),
        ('UA', 'UA - Parental Guidance'),
        ('A', 'A - Adults Only'),
        ('13+', '13+'),
        ('16+', '16+'),
        ('18+', '18+'),
    )
    
    webseries_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True, help_text="Short description for cards")
    poster = models.ImageField(upload_to='webseries/posters/')
    backdrop = models.ImageField(
        upload_to='webseries/backdrops/',
        null=True,
        blank=True,
        help_text="Hero background image for detail page"
    )
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True, related_name='webseries')
    genre = models.ManyToManyField(Genre, related_name='webseries', blank=True)
    age_rating = models.CharField(max_length=10, choices=AGE_RATING_CHOICES, default='U')
    year = models.PositiveIntegerField(help_text="Release year")
    cast = models.CharField(max_length=500, blank=True, help_text="Comma-separated cast names")
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Average rating from 0.0 to 10.0"
    )
    is_trending = models.BooleanField(default=False, help_text="Show in trending section")
    is_featured = models.BooleanField(default=False, help_text="Show in featured section")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Web Series"
        verbose_name_plural = "Web Series"
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['language']),
            models.Index(fields=['-rating']),
            models.Index(fields=['year']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def episode_count(self):
        """Get total number of episodes."""
        return self.episodes.count()
    
    @property
    def genres_display(self):
        """Get comma-separated genre names."""
        return ', '.join([g.genre_name for g in self.genre.all()])
    
    def get_cast_list(self):
        """Get cast as a list."""
        if self.cast:
            return [name.strip() for name in self.cast.split(',')]
        return []


class Episode(models.Model):
    """Model for web series episodes."""
    episode_id = models.AutoField(primary_key=True)
    webseries = models.ForeignKey(WebSeries, on_delete=models.CASCADE, related_name='episodes')
    episode_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True, help_text="Video URL or link")
    video_file = models.FileField(upload_to='webseries/episodes/', null=True, blank=True, help_text="Video file upload")
    thumbnail = models.ImageField(upload_to='webseries/episodes/thumbnails/', null=True, blank=True)
    duration = models.CharField(max_length=20, blank=True, help_text="Duration in minutes (e.g., '45 min')")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['episode_number']
        unique_together = ('webseries', 'episode_number')
        verbose_name = "Episode"
        verbose_name_plural = "Episodes"
        indexes = [
            models.Index(fields=['webseries', 'episode_number']),
        ]
    
    def __str__(self):
        return f"{self.webseries.title} - Episode {self.episode_number}: {self.title}"
    
    def get_video_source(self):
        """Get video source (file or URL)."""
        if self.video_file:
            return self.video_file.url
        return self.video_url


class WebSeriesWatchHistory(models.Model):
    """Track user watch history for web series episodes."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webseries_watch_history')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='watch_logs')
    first_watched_at = models.DateTimeField(auto_now_add=True)
    last_watched_at = models.DateTimeField(default=timezone.now)
    times_watched = models.PositiveIntegerField(default=1)
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-last_watched_at']
        unique_together = ('user', 'episode')
        indexes = [
            models.Index(fields=['user', 'episode']),
            models.Index(fields=['-last_watched_at']),
        ]
    
    def __str__(self):
        return f"{self.user.nm} - {self.episode}"


class WebSeriesWatchlist(models.Model):
    """User watchlist for web series."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webseries_watchlist')
    webseries = models.ForeignKey(WebSeries, on_delete=models.CASCADE, related_name='watchlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'webseries')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.nm} - {self.webseries.title}"


class WebSeriesLike(models.Model):
    """User likes/ratings for web series."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webseries_likes')
    webseries = models.ForeignKey(WebSeries, on_delete=models.CASCADE, related_name='likes')
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating between 1 and 5"
    )
    liked = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'webseries')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.nm} - {self.webseries.title} ({self.rating if self.rating else 'Liked'})"


class WebSeriesEvent(models.Model):
    """Editorial events/highlights for a web series."""
    STATUS_UPCOMING = 'upcoming'
    STATUS_LIVE = 'live'
    STATUS_ARCHIVED = 'archived'

    STATUS_CHOICES = (
        (STATUS_UPCOMING, 'Upcoming'),
        (STATUS_LIVE, 'Live'),
        (STATUS_ARCHIVED, 'Archived'),
    )

    webseries = models.ForeignKey(WebSeries, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UPCOMING)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    cta_label = models.CharField(max_length=80, blank=True, help_text="Optional call-to-action label")
    cta_url = models.URLField(blank=True, help_text="Link for the CTA button")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-start_time',)
        verbose_name = "Web Series Event"
        verbose_name_plural = "Web Series Events"
        indexes = [
            models.Index(fields=['webseries', 'status']),
            models.Index(fields=['-start_time']),
        ]

    def __str__(self):
        return f"{self.webseries.title} - {self.title}"

    @property
    def is_live(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time


class WebSeriesRecommendation(models.Model):
    """Admin-curated recommendation slots per web series."""
    source_webseries = models.ForeignKey(
        WebSeries,
        on_delete=models.CASCADE,
        related_name='curated_recommendations',
        help_text="Web series detail page where this recommendation should appear"
    )
    recommended_webseries = models.ForeignKey(
        WebSeries,
        on_delete=models.CASCADE,
        related_name='recommended_entries',
        help_text="Web series to promote in this slot"
    )
    title = models.CharField(max_length=150, blank=True, help_text="Optional override title")
    short_note = models.CharField(max_length=280, blank=True, help_text="Short note shown to viewers")
    priority = models.PositiveIntegerField(default=0, help_text="Lower value = higher priority")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('priority', '-updated_at')
        verbose_name = "Web Series Recommendation"
        verbose_name_plural = "Web Series Recommendations"
        unique_together = ('source_webseries', 'recommended_webseries')
        indexes = [
            models.Index(fields=['source_webseries', 'priority']),
        ]

    def __str__(self):
        return f"{self.source_webseries.title} recommends {self.recommended_webseries.title}"

class MovieSlider(models.Model):
    slider_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    slider_image = models.ImageField(upload_to='slider/', help_text="Image for the slider card")
    movie = models.ForeignKey(Movies, on_delete=models.SET_NULL, null=True, blank=True, related_name='slider_items')
    is_active = models.BooleanField(default=True, help_text="Show this slider")
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = "Movie Slider"
        verbose_name_plural = "Movie Sliders"

    def __str__(self):
        return self.title


class Song(models.Model):
    """Model for managing songs and audio tracks."""
    song_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='songs/covers/', help_text="Song cover image")
    audio_file = models.FileField(upload_to='songs/audio/', help_text="Upload audio file (mp3, wav)")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True, related_name='songs', help_text="Language of the song")
    singers = models.ManyToManyField(Artist, related_name='songs', limit_choices_to={'category': Artist.CATEGORY_SINGER}, help_text="Select singers")
    duration = models.CharField(max_length=20, blank=True, help_text="Duration (e.g., '3:45')")
    lyrics = models.TextField(blank=True, null=True, help_text="Optional lyrics for the song")
    release_date = models.DateField(default=date.today)
    is_featured = models.BooleanField(default=False)
    play_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-release_date']
        verbose_name = "Song"
        verbose_name_plural = "Songs"
        
    def __str__(self):
        return self.title


class UserSongLike(models.Model):
    """Model for saving/liking songs."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_songs')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'song')
        ordering = ['-created_at']


class Playlist(models.Model):
    """Model for user playlists."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='playlists/covers/', blank=True, null=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title


class PlaylistSong(models.Model):
    """Model for songs in a playlist."""
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='songs')
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'added_at']
        unique_together = ('playlist', 'song')