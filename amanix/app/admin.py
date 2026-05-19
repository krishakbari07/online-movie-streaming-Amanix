from datetime import timedelta
from django.contrib import admin
from django.utils import timezone
from django.db.models import Sum
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    User,
    Subscription,
    Categories,
    Movies,
    Payment,
    Star,
    UserSession,
    MovieEvent,
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
    WebSeriesEvent,
    WebSeriesRecommendation,
    MovieSlider,
    Song,
    UserSongLike,
    Playlist,
    PlaylistSong,
    Singer,
)
# Register your models here.


class JoinDateFilter(SimpleListFilter):
    title = 'Join date'
    parameter_name = 'join_date'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('7d', 'Last 7 days'),
            ('30d', 'Last 30 days'),
            ('older', 'Older than 30 days'),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        now = timezone.now()
        if self.value() == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(created_at__gte=start)
        if self.value() == '7d':
            return queryset.filter(created_at__gte=now - timedelta(days=7))
        if self.value() == '30d':
            return queryset.filter(created_at__gte=now - timedelta(days=30))
        if self.value() == 'older':
            return queryset.filter(created_at__lt=now - timedelta(days=30))
        return queryset


class NameStartsWithFilter(SimpleListFilter):
    title = 'Name (A-Z)'
    parameter_name = 'name_letter'

    def lookups(self, request, model_admin):
        return [(chr(code), chr(code)) for code in range(ord('A'), ord('Z') + 1)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(nm__istartswith=self.value())
        return queryset


class LoginRecencyFilter(SimpleListFilter):
    title = 'Last login'
    parameter_name = 'login_recency'

    def lookups(self, request, model_admin):
        return (
            ('24h', 'Within 24h'),
            ('7d', 'Within 7 days'),
            ('30d', 'Within 30 days'),
            ('never', 'Never logged in'),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        now = timezone.now()
        if self.value() == '24h':
            return queryset.filter(last_login_at__gte=now - timedelta(hours=24))
        if self.value() == '7d':
            return queryset.filter(last_login_at__gte=now - timedelta(days=7))
        if self.value() == '30d':
            return queryset.filter(last_login_at__gte=now - timedelta(days=30))
        if self.value() == 'never':
            return queryset.filter(last_login_at__isnull=True)
        return queryset


class LoginFrequencyFilter(SimpleListFilter):
    title = 'Login count'
    parameter_name = 'login_freq'

    def lookups(self, request, model_admin):
        return (
            ('none', 'No logins'),
            ('1-5', '1-5 logins'),
            ('6-20', '6-20 logins'),
            ('20+', 'More than 20'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'none':
            return queryset.filter(login_count=0)
        if self.value() == '1-5':
            return queryset.filter(login_count__gte=1, login_count__lte=5)
        if self.value() == '6-20':
            return queryset.filter(login_count__gte=6, login_count__lte=20)
        if self.value() == '20+':
            return queryset.filter(login_count__gt=20)
        return queryset


class UserSessionInline(admin.TabularInline):
    model = UserSession
    extra = 0
    can_delete = False
    ordering = ('-login_time',)
    readonly_fields = ('login_time', 'logout_time', 'ip_address', 'session_key', 'user_agent')
    fields = ('login_time', 'logout_time', 'ip_address', 'user_agent')


class UserAdmin(admin.ModelAdmin):
    list_display = ('nm', 'email', 'preferred_language', 'is_blocked', 'created_at', 'last_login_at', 'login_count')
    search_fields = ('nm', 'email')
    list_filter = (NameStartsWithFilter, JoinDateFilter, LoginRecencyFilter, LoginFrequencyFilter, 'preferred_language', 'is_blocked')
    readonly_fields = ('created_at', 'updated_at', 'last_login_at', 'login_count')
    ordering = ('nm',)
    inlines = [UserSessionInline]
    fieldsets = (
        ('Profile', {'fields': ('nm', 'email', 'password', 'profile_image', 'preferred_language')}),
        ('Status', {'fields': ('is_blocked', 'block_reason')}),
        ('Activity', {'fields': ('created_at', 'updated_at', 'last_login_at', 'login_count')}),
    )
    date_hierarchy = 'created_at'
    actions = ['block_users', 'delete_users_with_notification']

    def block_users(self, request, queryset):
        if 'apply' in request.POST:
            reason = request.POST.get('reason')
            for user in queryset:
                user.is_blocked = True
                user.block_reason = reason
                user.save()
                # Send email
                try:
                    send_mail(
                        'Account Blocked - Amanix',
                        f'Dear {user.nm},\n\nYour account has been blocked for the following reason:\n{reason}\n\nContact support if you think this is a mistake.',
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    pass 
            self.message_user(request, f"Blocked {queryset.count()} users.")
            return None
        
        return render(request, 'admin/action_reason.html', context={
            'queryset': queryset,
            'action_name': 'block',
            'action_value': 'block_users',
            'title': 'Block Users',
        })
    block_users.short_description = "Block selected users"

    def delete_users_with_notification(self, request, queryset):
        if 'apply' in request.POST:
            reason = request.POST.get('reason')
            count = queryset.count()
            for user in queryset:
                # Send email before deleting
                try:
                    send_mail(
                        'Account Deleted - Amanix',
                        f'Dear {user.nm},\n\nYour account has been deleted for the following reason:\n{reason}\n\nWe are sorry to see you go.',
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    pass
                user.delete()
            self.message_user(request, f"Deleted {count} users.")
            return None

        return render(request, 'admin/action_reason.html', context={
            'queryset': queryset,
            'action_name': 'delete',
            'action_value': 'delete_users_with_notification',
            'title': 'Delete Users',
        })
    delete_users_with_notification.short_description = "Delete selected users with notification"


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('sub_name', 'sub_price','sub_time_limit')
    search_fields = ('sub_name',)


class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('cat_id','cat_name',)
    search_fields = ('cat_name',)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('language_name', 'language_code', 'is_active', 'display_order', 'movie_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('language_name', 'language_code')
    ordering = ('display_order', 'language_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Language Information', {
            'fields': ('language_name', 'language_code', 'is_active', 'display_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def movie_count(self, obj):
        """Display number of movies in this language."""
        return obj.movies.count()
    movie_count.short_description = 'Movies'

@admin.register(Movies)
class MoviesAdmin(admin.ModelAdmin):
    list_display = ('movie_image_thumb', 'movie_name', 'category', 'language', 'movie_rating', 'has_backdrop')
    list_filter = ('category', 'language', 'movie_rating')
    search_fields = ('movie_name', 'category__cat_name', 'language__language_name')
    readonly_fields = ('movie_image_preview', 'movie_backdrop_preview')
    fieldsets = (
        ('Details', {
            'fields': ('movie_name', 'movie_description', 'movie_director', 'movie_star', 'movie_rating', 'movie_duration', 'movie_release_date')
        }),
        ('Classification', {
            'fields': ('category', 'language')
        }),
        ('Media', {
            'fields': ('movie_image', 'movie_image_preview', 'movie_backdrop', 'movie_backdrop_preview', 'movie_video'),
            'description': 'Upload both poster and cinematic background to power the hero section.'
        }),
    )
    
    # Ensure only existing categories and languages can be selected
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = Categories.objects.all()
        elif db_field.name == "language":
            kwargs["queryset"] = Language.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def movie_image_thumb(self, obj):
        if obj.movie_image:
            return format_html(
                '<img src="{}" style="width:50px;height:70px;object-fit:cover;border-radius:6px;" />',
                obj.movie_image.url
            )
        return "—"
    movie_image_thumb.short_description = 'Poster'
    
    def has_backdrop(self, obj):
        return bool(obj.movie_backdrop)
    has_backdrop.boolean = True
    has_backdrop.short_description = 'Backdrop'
    
    def movie_image_preview(self, obj):
        if obj.movie_image:
            return format_html(
                '<img src="{}" style="max-width:200px;border-radius:10px;" />',
                obj.movie_image.url
            )
        return "No poster uploaded"
    movie_image_preview.short_description = 'Poster Preview'
    
    def movie_backdrop_preview(self, obj):
        if obj.movie_backdrop:
            return format_html(
                '<img src="{}" style="max-width:300px;border-radius:10px;" />',
                obj.movie_backdrop.url
            )
        return "No backdrop uploaded"
    movie_backdrop_preview.short_description = 'Backdrop Preview'

class PaymentDateFilter(SimpleListFilter):
    """Filter payments by date range."""
    title = 'Payment Date'
    parameter_name = 'payment_date'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('year', 'This Year'),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        now = timezone.now()
        if self.value() == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(created_at__gte=start)
        if self.value() == 'week':
            return queryset.filter(created_at__gte=now - timedelta(days=7))
        if self.value() == 'month':
            return queryset.filter(created_at__gte=now - timedelta(days=30))
        if self.value() == 'year':
            return queryset.filter(created_at__gte=now - timedelta(days=365))
        return queryset


class PaymentStatusFilter(SimpleListFilter):
    """Filter payments by status."""
    title = 'Payment Status'
    parameter_name = 'payment_status'

    def lookups(self, request, model_admin):
        return (
            ('SUCCESS', 'Success'),
            ('PENDING', 'Pending'),
            ('FAILED', 'Failed'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(payment_status=self.value())
        return queryset


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription', 'pay_method', 'sub_price', 'transaction_id', 'payment_status', 'created_at')
    list_filter = (
        'pay_method',
        PaymentStatusFilter,
        PaymentDateFilter,
        'subscription',
        'created_at',
    )
    search_fields = (
        'transaction_id',
        'user__nm',
        'user__email',
        'subscription__sub_name',
    )
    readonly_fields = ('transaction_id', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'subscription', 'transaction_id', 'sub_price', 'pay_method', 'payment_status')
        }),
        ('Card Details', {
            'fields': ('card_last4', 'card_holder_nm', 'expiry_date'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'created_at')
        }),
    )

    def changelist_view(self, request, extra_context=None):
        """Modify the changelist view to include total income in the admin panel."""
        extra_context = extra_context or {}

        # Calculate total income
        total = Payment.objects.aggregate(Sum('sub_price'))['sub_price__sum']
        total_income = f"${total:.2f}" if total else "$0.00"

        # Add total income to the context
        extra_context['total_income'] = mark_safe(f'<h2 style="margin: 10px 0; color:#fff">Total Income: <strong>{total_income}</strong></h2>')

        return super().changelist_view(request, extra_context=extra_context)
    


class AlphabetFilter(SimpleListFilter):
    """Custom filter for alphabetical filtering by first letter."""
    title = 'First Letter'
    parameter_name = 'first_letter'

    def lookups(self, request, model_admin):
        """Return a list of tuples for filter options (A-Z)."""
        letters = []
        stars = Star.objects.all().order_by('star_name')
        used_letters = set()
        for star in stars:
            first_letter = star.first_letter
            if first_letter and first_letter not in used_letters:
                letters.append((first_letter, first_letter))
                used_letters.add(first_letter)
        return sorted(letters)

    def queryset(self, request, queryset):
        """Filter queryset by selected first letter."""
        if self.value():
            return queryset.filter(star_name__istartswith=self.value())
        return queryset


@admin.register(Star)
class StarAdmin(admin.ModelAdmin):
    """Admin panel for managing Stars with photos and alphabetical filtering."""
    list_display = ('star_photo_preview', 'star_name', 'first_letter_column', 'created_at', 'star_background_preview')
    list_display_links = ('star_name',)
    list_filter = (AlphabetFilter, 'created_at')
    search_fields = ('star_name', 'star_bio')
    ordering = ('star_name',)  # Alphabetical ordering
    readonly_fields = ('star_photo_preview', 'star_background_preview', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Star Information', {
            'fields': ('star_name', 'star_photo', 'star_photo_preview', 'star_background', 'star_background_preview', 'star_bio')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def star_photo_preview(self, obj):
        """Display star photo thumbnail in admin list."""
        if obj.star_photo:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 50%;" />',
                obj.star_photo.url
            )
        return "No Photo"
    star_photo_preview.short_description = 'Photo'


    def star_background_preview(self, obj):
        """Display star background thumbnail in admin list and detail view."""
        if obj.star_background:
            return format_html(
                '<img src="{}" style="width: 100px; height: 60px; object-fit: cover; border-radius: 5px;" />',
                obj.star_background.url
            )
        return "No Background"
    star_background_preview.short_description = 'Background'

    def first_letter_column(self, obj):
        """Display first letter for easy identification."""
        letter = obj.first_letter
        return format_html(
            '<span style="font-weight: bold; font-size: 18px; color: #e50914;">{}</span>',
            letter
        )
    first_letter_column.short_description = 'Letter'
    first_letter_column.admin_order_field = 'star_name'

    def get_queryset(self, request):
        """Optimize queryset with select_related if needed."""
        qs = super().get_queryset(request)
        return qs.select_related()


# Register the User model with the UserAdmin class
admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Payment, PaymentAdmin)


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time', 'ip_address', 'session_key', 'user_agent')
    list_filter = ('user', 'login_time', 'logout_time')
    search_fields = ('user__nm', 'user__email', 'ip_address', 'session_key', 'user_agent')
    ordering = ('-login_time',)


@admin.register(MovieEvent)
class MovieEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'movie', 'start_time', 'end_time', 'is_featured')
    list_filter = ('event_type', 'is_featured', 'start_time')
    search_fields = ('title', 'description', 'movie__movie_name')
    ordering = ('-start_time',)
    autocomplete_fields = ('movie',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'event_type', 'movie', 'description', 'is_featured')
        }),
        ('Schedule', {
            'fields': ('start_time', 'end_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'first_watched_at', 'last_watched_at', 'times_watched', 'completed', 'progress_percent')
    list_filter = ('completed', 'first_watched_at', 'last_watched_at')
    search_fields = ('user__nm', 'user__email', 'movie__movie_name')
    readonly_fields = ('first_watched_at', 'last_watched_at')
    ordering = ('-last_watched_at',)
    autocomplete_fields = ('user', 'movie')


@admin.register(MovieFeedback)
class MovieFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'rating', 'created_at', 'updated_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__nm', 'user__email', 'movie__movie_name', 'review')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    autocomplete_fields = ('user', 'movie')
    fieldsets = (
        ('Feedback', {
            'fields': ('user', 'movie', 'rating', 'review')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AppFeedback)
class AppFeedbackAdmin(admin.ModelAdmin):
    list_display = ('email', 'category', 'rating', 'created_at')
    list_filter = ('category', 'rating', 'created_at')
    search_fields = ('email', 'user__nm', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    fieldsets = (
        ('Feedback', {
            'fields': ('user', 'email', 'category', 'rating', 'message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    """Admin panel for managing Artists."""
    list_display = ('artist_photo_preview', 'artist_name', 'category', 'popularity_rating', 'follower_count_display', 'is_featured', 'created_at')
    list_display_links = ('artist_name',)
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('artist_name', 'artist_bio')
    ordering = ('-popularity_rating', 'artist_name')
    readonly_fields = ('artist_photo_preview', 'artist_background_preview', 'created_at', 'updated_at', 'follower_count_display')
    filter_horizontal = ('movies',)
    
    fieldsets = (
        ('Artist Information', {
            'fields': ('artist_name', 'category', 'artist_photo', 'artist_photo_preview', 'artist_background', 'artist_background_preview', 'artist_bio', 'popularity_rating', 'is_featured')
        }),
        ('Movies', {
            'fields': ('movies',)
        }),
        ('Statistics', {
            'fields': ('follower_count_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def artist_photo_preview(self, obj):
        """Display artist photo thumbnail in admin list."""
        if obj.artist_photo:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 50%;" />',
                obj.artist_photo.url
            )
        return "No Photo"
    artist_photo_preview.short_description = 'Photo'

    def artist_background_preview(self, obj):
        """Display artist background thumbnail."""
        if obj.artist_background:
            return format_html(
                '<img src="{}" style="width: 100px; height: 60px; object-fit: cover; border-radius: 5px;" />',
                obj.artist_background.url
            )
        return "No Background"
    artist_background_preview.short_description = 'Background'

    def follower_count_display(self, obj):
        """Display follower count."""
        return obj.follower_count
    follower_count_display.short_description = 'Followers'

@admin.register(Singer)
class SingerAdmin(ArtistAdmin):
    """Admin panel specifically for managing Singers."""
    
    def get_queryset(self, request):
        return super().get_queryset(request)
        
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['category'] = 'singer'
        return initial


@admin.register(UserArtistFollow)
class UserArtistFollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'artist', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__nm', 'user__email', 'artist__artist_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


# ==================== WEB SERIES ADMIN ====================

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('genre_name', 'created_at')
    search_fields = ('genre_name',)
    ordering = ('genre_name',)
    readonly_fields = ('created_at',)


class EpisodeInline(admin.TabularInline):
    """Inline admin for episodes within web series."""
    model = Episode
    extra = 1
    fields = ('episode_number', 'title', 'description', 'video_url', 'video_file', 'thumbnail', 'duration')
    ordering = ('episode_number',)


class WebSeriesEventInline(admin.StackedInline):
    model = WebSeriesEvent
    extra = 0
    fields = (
        'title',
        'description',
        'status',
        ('start_time', 'end_time'),
        ('cta_label', 'cta_url'),
        'is_active',
    )
    ordering = ('-start_time',)
    show_change_link = True


class WebSeriesRecommendationInline(admin.TabularInline):
    model = WebSeriesRecommendation
    extra = 0
    fk_name = 'source_webseries'
    autocomplete_fields = ('recommended_webseries',)
    fields = ('recommended_webseries', 'title', 'short_note', 'priority', 'is_active')
    ordering = ('priority',)


class LanguageFilter(admin.SimpleListFilter):
    """Filter web series by language."""
    title = 'Language'
    parameter_name = 'language'

    def lookups(self, request, model_admin):
        languages = Language.objects.filter(is_active=True).order_by('language_name')
        return [(lang.language_id, lang.language_name) for lang in languages]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(language_id=self.value())
        return queryset


class GenreFilter(admin.SimpleListFilter):
    """Filter web series by genre."""
    title = 'Genre'
    parameter_name = 'genre'

    def lookups(self, request, model_admin):
        genres = Genre.objects.all().order_by('genre_name')
        return [(genre.genre_id, genre.genre_name) for genre in genres]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(genre__genre_id=self.value()).distinct()
        return queryset


class YearFilter(admin.SimpleListFilter):
    """Filter web series by year."""
    title = 'Year'
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        years = WebSeries.objects.values_list('year', flat=True).distinct().order_by('-year')
        return [(year, str(year)) for year in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(year=self.value())
        return queryset


@admin.register(WebSeries)
class WebSeriesAdmin(admin.ModelAdmin):
    """Admin panel for managing Web Series."""
    list_display = ('poster_preview', 'title', 'language', 'year', 'age_rating', 'rating', 'episode_count_display', 'has_backdrop', 'is_trending', 'is_featured', 'created_at')
    list_display_links = ('title',)
    list_filter = (LanguageFilter, GenreFilter, YearFilter, 'age_rating', 'is_trending', 'is_featured', 'created_at')
    search_fields = ('title', 'description', 'cast', 'language__language_name')
    ordering = ('-created_at',)
    readonly_fields = ('poster_preview', 'backdrop_preview', 'episode_count_display', 'created_at', 'updated_at')
    filter_horizontal = ('genre',)
    inlines = [EpisodeInline, WebSeriesEventInline, WebSeriesRecommendationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'short_description', 'poster', 'poster_preview', 'backdrop', 'backdrop_preview')
        }),
        ('Details', {
            'fields': ('language', 'genre', 'age_rating', 'year', 'cast', 'rating')
        }),
        ('Features', {
            'fields': ('is_trending', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('episode_count_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def poster_preview(self, obj):
        """Display poster thumbnail in admin list."""
        if obj.poster:
            return format_html(
                '<img src="{}" style="width: 80px; height: 120px; object-fit: cover; border-radius: 5px;" />',
                obj.poster.url
            )
        return "No Poster"
    poster_preview.short_description = 'Poster'

    def episode_count_display(self, obj):
        """Display episode count."""
        return obj.episode_count
    episode_count_display.short_description = 'Episodes'
    
    def has_backdrop(self, obj):
        return bool(obj.backdrop)
    has_backdrop.boolean = True
    has_backdrop.short_description = 'Backdrop'
    
    def backdrop_preview(self, obj):
        if obj.backdrop:
            return format_html(
                '<img src="{}" style="width: 220px; height: 120px; object-fit: cover; border-radius: 10px;" />',
                obj.backdrop.url
            )
        return "No backdrop uploaded"
    backdrop_preview.short_description = 'Backdrop Preview'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter language choices to active languages only."""
        if db_field.name == "language":
            kwargs["queryset"] = Language.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    """Admin panel for managing Episodes."""
    list_display = ('thumbnail_preview', 'webseries', 'episode_number', 'title', 'duration', 'created_at')
    list_display_links = ('title',)
    list_filter = ('webseries', 'created_at')
    search_fields = ('title', 'description', 'webseries__title')
    ordering = ('webseries', 'episode_number')
    readonly_fields = ('thumbnail_preview', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Episode Information', {
            'fields': ('webseries', 'episode_number', 'title', 'description', 'duration')
        }),
        ('Media', {
            'fields': ('thumbnail', 'thumbnail_preview', 'video_url', 'video_file')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def thumbnail_preview(self, obj):
        """Display thumbnail in admin list."""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 5px;" />',
                obj.thumbnail.url
            )
        elif obj.webseries and obj.webseries.poster:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 5px; opacity: 0.5;" />',
                obj.webseries.poster.url
            )
        return "No Thumbnail"
    thumbnail_preview.short_description = 'Thumbnail'


@admin.register(WebSeriesWatchHistory)
class WebSeriesWatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'episode', 'first_watched_at', 'last_watched_at', 'times_watched', 'completed', 'progress_percent')
    list_filter = ('completed', 'first_watched_at', 'last_watched_at')
    search_fields = ('user__nm', 'user__email', 'episode__title', 'episode__webseries__title')
    readonly_fields = ('first_watched_at', 'last_watched_at')
    ordering = ('-last_watched_at',)
    autocomplete_fields = ('user', 'episode')


@admin.register(WebSeriesWatchlist)
class WebSeriesWatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'webseries', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__nm', 'user__email', 'webseries__title')
    ordering = ('-added_at',)
    readonly_fields = ('added_at',)
    autocomplete_fields = ('user', 'webseries')


@admin.register(WebSeriesLike)
class WebSeriesLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'webseries', 'liked', 'rating', 'created_at', 'updated_at')
    list_filter = ('liked', 'rating', 'created_at')
    search_fields = ('user__nm', 'user__email', 'webseries__title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    autocomplete_fields = ('user', 'webseries')
    fieldsets = (
        ('Like/Rating', {
            'fields': ('user', 'webseries', 'liked', 'rating')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WebSeriesEvent)
class WebSeriesEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'webseries', 'status', 'start_time', 'end_time', 'is_active')
    list_filter = ('status', 'is_active', 'start_time')
    search_fields = ('title', 'webseries__title')
    ordering = ('-start_time',)
    autocomplete_fields = ('webseries',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WebSeriesRecommendation)
class WebSeriesRecommendationAdmin(admin.ModelAdmin):
    list_display = ('source_webseries', 'recommended_webseries', 'priority', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('source_webseries__title', 'recommended_webseries__title', 'title', 'short_note')
    ordering = ('priority', 'source_webseries__title')
    autocomplete_fields = ('source_webseries', 'recommended_webseries')

@admin.register(MovieSlider)
class MovieSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'movie', 'is_active', 'display_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'movie__movie_name')
    ordering = ('display_order', '-created_at')
    autocomplete_fields = ('movie',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Banner Details', {
            'fields': ('title', 'description', 'slider_image', 'movie', 'is_active', 'display_order')
        }),
    )

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('cover_preview', 'title', 'language', 'duration', 'release_date', 'play_count', 'is_featured')
    list_filter = ('language', 'is_featured', 'release_date')
    search_fields = ('title', 'singers__artist_name')
    filter_horizontal = ('singers',)
    readonly_fields = ('play_count', 'created_at', 'cover_preview')
    ordering = ('-release_date',)
    
    def cover_preview(self, obj):
        if obj.cover_image:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.cover_image.url)
        return "No Cover"
    cover_preview.short_description = 'Cover'

@admin.register(UserSongLike)
class UserSongLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'song__title')

class PlaylistSongInline(admin.TabularInline):
    model = PlaylistSong
    extra = 1

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('title', 'user__username')
    inlines = [PlaylistSongInline]