from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Message, MessageThread

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class AdminSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile information"""
    bio = forms.CharField(
        max_length=500, 
        required=False, 
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about yourself...'})
    )
    phone = forms.CharField(
        max_length=20, 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': '+1 (555) 123-4567'})
    )
    location = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'City, Country'})
    )
    website = forms.URLField(
        required=False, 
        widget=forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'})
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class SecuritySettingsForm(forms.Form):
    """Form for security settings"""
    show_email_publicly = forms.BooleanField(
        required=False,
        label="Show email address in public profile",
        help_text="Allow other users to see your email address"
    )
    show_real_name = forms.BooleanField(
        required=False,
        label="Show real name in public profile",
        help_text="Display your first and last name instead of username"
    )
    allow_messages = forms.BooleanField(
        required=False,
        label="Allow messages from other users",
        help_text="Let other users send you private messages"
    )
    email_notifications = forms.BooleanField(
        required=False,
        label="Email notifications",
        help_text="Receive email notifications for new answers and messages"
    )

class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with better styling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your current password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })

class ThemePreferenceForm(forms.Form):
    """Form for theme preferences"""
    THEME_CHOICES = [
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
        ('auto', 'Auto (System Default)'),
    ]
    
    theme = forms.ChoiceField(
        choices=THEME_CHOICES,
        widget=forms.RadioSelect,
        initial='light',
        label="Choose your preferred theme"
    )
    
    compact_mode = forms.BooleanField(
        required=False,
        label="Compact mode",
        help_text="Use smaller spacing and condensed layouts"
    )
    
    animations = forms.BooleanField(
        required=False,
        label="Enable animations",
        help_text="Show smooth transitions and animations",
        initial=True
    )

class NotificationSettingsForm(forms.Form):
    """Form for notification preferences"""
    email_new_answer = forms.BooleanField(
        required=False,
        label="New answer notifications",
        help_text="Get notified when someone answers your question"
    )
    email_new_message = forms.BooleanField(
        required=False,
        label="New message notifications", 
        help_text="Get notified when you receive a new message"
    )
    email_weekly_digest = forms.BooleanField(
        required=False,
        label="Weekly digest",
        help_text="Receive a weekly summary of platform activity"
    )
    browser_notifications = forms.BooleanField(
        required=False,
        label="Browser notifications",
        help_text="Show browser notifications for important updates"
    )

class MessageForm(forms.ModelForm):
    """Form for sending messages to admins"""
    class Meta:
        model = Message
        fields = ['subject', 'message_type', 'content', 'priority']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message_type': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

class MessageReplyForm(forms.ModelForm):
    """Form for replying to messages"""
    class Meta:
        model = MessageThread
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Type your reply...'})
        }
