from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from core.models import Book, BookRequest, User
import csv
from django.http import HttpResponse

@csrf_exempt
def user_registration(request):
    """
    API endpoint for user registration using email, password and librarian flag.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            is_librarian = data.get('is_librarian', False)

            # Validate input
            if not email or not password:
                return JsonResponse({
                    'error': 'Email and password are required'
                }, status=400)

            # Check if user already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'error': 'User with this email already exists'
                }, status=400)

            # Create new user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                is_librarian=is_librarian
            )

            return JsonResponse({
                'message': 'User registered successfully',
                'user_id': user.id
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON'
            }, status=400)

    return JsonResponse({
        'error': 'Method not allowed'
    }, status=405)

@csrf_exempt
def user_login(request):
    """
    API endpoint for user login for specific user by using email and password set during the registration.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            # Validate input
            if not email or not password:
                return JsonResponse({
                    'error': 'Email and password are required'
                }, status=400)

            # Authenticate user
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return JsonResponse({
                    'message': 'Login successful',
                    'user_id': user.id,
                    'is_librarian': user.is_librarian
                })
            else:
                return JsonResponse({
                    'error': 'Invalid credentials'
                }, status=401)

        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON'
            }, status=400)

    return JsonResponse({
        'error': 'Method not allowed'
    }, status=405)

def user_logout(request):
    """
    API endpoint for user logout
    """
    logout(request)
    return JsonResponse({
        'message': 'Logout successful'
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def add_book(request):
    """
    API endpoint for adding a new book (Librarian only)
    """
    if not request.user.is_librarian:
        return JsonResponse({
            'error': 'Unauthorized. Only librarians can add books.'
        }, status=403)

    try:
        data = json.loads(request.body)
        title = data.get('title')
        author = data.get('author')
        isbn = data.get('isbn')
        total_copies = data.get('total_copies', 1)

        # Validate input
        if not all([title, author, isbn]):
            return JsonResponse({
                'error': 'Title, author, and ISBN are required'
            }, status=400)

        # Check if book with same ISBN already exists
        if Book.objects.filter(isbn=isbn).exists():
            return JsonResponse({
                'error': 'Book with this ISBN already exists'
            }, status=400)

        # Create new book
        book = Book.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            total_copies=total_copies,
            available_copies=total_copies
        )

        return JsonResponse({
            'message': 'Book added successfully',
            'book_id': book.id
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON'
        }, status=400)

@login_required
@require_http_methods(["GET"])
def list_books(request):
    """
    API endpoint for listing all books
    """
    books = Book.objects.all()
    book_list = [{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'isbn': book.isbn,
        'total_copies': book.total_copies,
        'available_copies': book.available_copies
    } for book in books]

    return JsonResponse({
        'books': book_list
    })

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def submit_book_request(request):
    """
    API endpoint for submitting a book borrow request
    """
    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')
        borrow_start_date = data.get('borrow_start_date')
        borrow_end_date = data.get('borrow_end_date')

        # Validate input
        if not all([book_id, borrow_start_date, borrow_end_date]):
            return JsonResponse({
                'error': 'Book ID, start date, and end date are required'
            }, status=400)

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return JsonResponse({
                'error': 'Book not found'
            }, status=404)

        # Check book availability
        if book.available_copies <= 0:
            return JsonResponse({
                'error': 'No copies of this book are currently available'
            }, status=400)

        # Create book request
        try:
            book_request = BookRequest.objects.create(
                user=request.user,
                book=book,
                borrow_start_date=borrow_start_date,
                borrow_end_date=borrow_end_date
            )

            return JsonResponse({
                'message': 'Book request submitted successfully',
                'request_id': book_request.id
            }, status=201)

        except ValueError as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON'
        }, status=400)

@login_required
@require_http_methods(["GET"])
def user_borrow_history(request):
    """
    API endpoint for viewing user's book borrow history
    """
    book_requests = BookRequest.objects.filter(user=request.user)
    history = [{
        'request_id': req.id,
        'book_title': req.book.title,
        'book_author': req.book.author,
        'borrow_start_date': req.borrow_start_date,
        'borrow_end_date': req.borrow_end_date,
        'status': req.status
    } for req in book_requests]

    return JsonResponse({
        'borrow_history': history
    })

@login_required
@require_http_methods(["GET"])
def librarian_book_requests(request):
    """
    API endpoint for librarians to view all book borrow requests
    """
    if not request.user.is_librarian:
        return JsonResponse({
            'error': 'Unauthorized. Only librarians can view book requests.'
        }, status=403)

    book_requests = BookRequest.objects.all()
    requests_list = [{
        'request_id': req.id,
        'user_email': req.user.email,
        'book_title': req.book.title,
        'borrow_start_date': req.borrow_start_date,
        'borrow_end_date': req.borrow_end_date,
        'status': req.status
    } for req in book_requests]

    return JsonResponse({
        'book_requests': requests_list
    })

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def approve_book_request(request):
    """
    API endpoint for librarians to approve or deny book requests
    """
    if not request.user.is_librarian:
        return JsonResponse({
            'error': 'Unauthorized. Only librarians can approve book requests.'
        }, status=403)

    try:
        data = json.loads(request.body)
        request_id = data.get('request_id')
        status = data.get('status')  # 'APPROVED' or 'DENIED'

        if not all([request_id, status]):
            return JsonResponse({
                'error': 'Request ID and status are required'
            }, status=400)

        try:
            book_request = BookRequest.objects.get(id=request_id)
        except BookRequest.DoesNotExist:
            return JsonResponse({
                'error': 'Book request not found'
            }, status=404)

        # Check for conflicting requests before approving
        if status == 'APPROVED':
            conflicting_requests = BookRequest.objects.filter(
                book=book_request.book,
                status__in=['PENDING', 'APPROVED'],
                borrow_start_date__lte=book_request.borrow_end_date,
                borrow_end_date__gte=book_request.borrow_start_date
            ).exclude(id=book_request.id)

            if conflicting_requests.exists():
                return JsonResponse({
                    'error': 'Book is not available during the requested period'
                }, status=400)

        # Update book request status
        book_request.status = status
        book_request.save()

        # Update book availability if approved
        if status == 'APPROVED':
            book_request.book.available_copies -= 1
            book_request.book.save()

        return JsonResponse({
            'message': f'Book request {status.lower()}',
            'request_id': book_request.id
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON'
        }, status=400)

# Bonus feature 01 is implemented only as per the given requirements.
@login_required
def download_borrow_history_csv(request):
    """
    API endpoint for downloading user's borrow history as a CSV file.
    """
    # Fetch the user's borrow history
    book_requests = BookRequest.objects.filter(user=request.user)
    
    # Create the HTTP response object with CSV headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="borrow_history.csv"'

    # Create a CSV writer
    writer = csv.writer(response)
    # Write the header row
    writer.writerow(['Request ID', 'Book Title', 'Book Author', 'Borrow Start Date', 'Borrow End Date', 'Status'])

    # Write the data rows
    for req in book_requests:
        writer.writerow([
            req.id,
            req.book.title,
            req.book.author,
            req.borrow_start_date,
            req.borrow_end_date,
            req.status
        ])

    return response
