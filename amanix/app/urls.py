from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('subscription/', views.subscription, name='subscription'),
    path('movies/', views.movies_list, name='movies_list'),
    path('movies/language/<int:language_id>/', views.movies_list, name='movies_by_language'),
    path('payment/<int:sub_id>/', views.payment, name='payment'),
    path('movie/<int:movie_id>/', views.movie, name='movie'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('payment_succesfull/<int:payment_id>/', views.payment_succesfull, name='payment_succesfull'),
    path('receipt/<int:payment_id>/', views.download_receipt, name='download_receipt'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),
    path('profile_pic/', views.profile_pic, name='profile_pic'),
    path('learn_more_subcription/', views.learn_more_subcription, name='learn_more_subcription'),
    path('search/', views.search_movies, name='search_movies'),
    path('autocomplete/', views.autocomplete_suggestions, name='autocomplete_suggestions'),
    path('star/<int:star_id>/', views.star_detail, name='star_detail'),
    path('movie/<int:movie_id>/feedback/', views.submit_movie_feedback, name='submit_movie_feedback'),
    path('app-feedback/', views.app_feedback_page, name='app_feedback_page'),
    path('app-feedback/submit/', views.submit_app_feedback, name='submit_app_feedback'),
    path('artists/', views.artist_list, name='artist_list'),
    path('artist/<int:artist_id>/', views.artist_detail, name='artist_detail'),
    path('artist/<int:artist_id>/follow/', views.toggle_follow_artist, name='toggle_follow_artist'),
    path('language/<int:language_id>/', views.language_movies, name='language_movies'),
    path('webseries/', views.webseries_language_list, name='webseries_list'),
    path('webseries/language/<int:language_id>/', views.webseries_language_list, name='webseries_by_language'),
    path('webseries/<int:webseries_id>/', views.webseries_detail, name='webseries_detail'),
    path('webseries/recommendations/', views.webseries_recommendations, name='webseries_recommendations'),
    path('webseries/<int:webseries_id>/watchlist/', views.toggle_watchlist, name='toggle_webseries_watchlist'),
    path('webseries/<int:webseries_id>/like/', views.like_webseries, name='like_webseries'),
    path('episode/<int:episode_id>/watch/', views.watch_episode, name='watch_episode'),
    path('songs/', views.songs_list, name='songs_list'),
    path('songs/language/<int:language_id>/', views.songs_list, name='songs_by_language'),
    path('songs/<int:song_id>/like/', views.like_song, name='like_song'),
    path('songs/search/', views.search_songs, name='search_songs'),
    path('api/playlist/create/', views.create_playlist, name='create_playlist'),
    path('api/playlist/add_song/', views.add_to_playlist, name='add_to_playlist'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
