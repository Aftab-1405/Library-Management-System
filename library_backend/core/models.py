from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """
    Custom user model to support library-specific user management
    """
    email = models.EmailField(unique=True)
    is_librarian = models.BooleanField(default=False)
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='library_users',
        related_query_name='library_user'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='library_users',
        related_query_name='library_user'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Book(models.Model):
    """
    Represents individual book copies in the library
    """
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=50, unique=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.title} by {self.author}"

class BookRequest(models.Model):
    """
    Tracks book borrowing requests and their status
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
        ('RETURNED', 'Returned')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_requests')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    borrow_start_date = models.DateField()
    borrow_end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    def save(self, *args, **kwargs):
        """
        Custom save method to validate request
        """
        # Only perform conflict check for new or modified requests
        if not self.pk:
            conflicting_requests = BookRequest.objects.filter(
                book=self.book,
                status__in=['PENDING', 'APPROVED'],
                borrow_start_date__lte=self.borrow_end_date,
                borrow_end_date__gte=self.borrow_start_date
            )
            
            if conflicting_requests.exists():
                raise ValueError("Book is not available during the requested period")
        
        super().save(*args, **kwargs)