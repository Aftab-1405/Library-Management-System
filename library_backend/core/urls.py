from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.user_registration, name='user_registration'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),

    # Book Management URLs
    path('books/add/', views.add_book, name='add_book'),
    path('books/', views.list_books, name='list_books'),
    path('books/request/', views.submit_book_request, name='submit_book_request'),
    path('books/history/', views.user_borrow_history, name='user_borrow_history'),
    
    # Librarian URLs
    path('librarian/book-requests/', views.librarian_book_requests, name='librarian_book_requests'),
    path('librarian/approve-request/', views.approve_book_request, name='approve_book_request'),

    # Bonus feature to downloead borrow history in the form of CSV
    path('books/history/download/', views.download_borrow_history_csv, name='download_borrow_history_csv'),
]