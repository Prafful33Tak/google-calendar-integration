# import the necessary modules :

from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse
from django.conf import settings
import requests
from google.oauth2.credentials import Credentials



# Create a view for the /rest/v1/calendar/init/ endpoint:

class GoogleCalendarInitView(View):
    def get(self, request, *args, **kwargs):
        # Generate the OAuth2 URL to redirect the user to
        auth_url, state = get_authorization_url(request)
        request.session['oauth_state'] = state
        return redirect(auth_url)

# This view will redirect the user to the OAuth2 URL to grant access to their calendar.



# Create a view for the /rest/v1/calendar/redirect/ endpoint:

class GoogleCalendarRedirectView(View):
    def get(self, request, *args, **kwargs):
        # Handle the redirect request and get the access_token
        access_token = handle_redirect(request)

        # Use the access_token to get the user's calendar events
        events = get_calendar_events(access_token)

        # Return the calendar events as a JSON response
        return JsonResponse(events, safe=False)

# This view will handle the redirect request sent by Google, use the code provided to get the access_token, 
# and then use the access_token to get the user's calendar events.



# Define helper functions to handle the details of generating the OAuth2 URL, 
# handling the redirect request, and getting the calendar events:

def get_authorization_url(request):
    client_id = settings.GOOGLE_CLIENT_ID
    redirect_uri = request.build_absolute_uri(reverse('calendar_redirect'))
    scope = ['https://www.googleapis.com/auth/calendar.events']
    auth_url, state = google.auth.default().create_authorization_url(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope
    )
    return auth_url, state


def handle_redirect(request):
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    redirect_uri = request.build_absolute_uri(reverse('calendar_redirect'))
    code = request.GET.get('code')
    state = request.session.get('oauth_state')
    token_response = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        },
    )
    token = token_response.json
