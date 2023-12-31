from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError

from wilderwatch_api.models import WilderUser

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    '''Handles the authentication of a gamer

    Method arguments:
      request -- The full HTTP request object
    '''
    username = request.data['username']
    password = request.data['password']

    # Use the built-in authenticate method to verify
    # authenticate returns the user object or None if no user is found
    authenticated_user = authenticate(username=username, password=password)

    # If authentication was successful, respond with their token
    if authenticated_user is not None:
        token = Token.objects.get(user=authenticated_user)
        wilder_user = WilderUser.objects.get(user=authenticated_user)
        data = {
            'valid': True,
            'token': token.key,
            'isStaff': authenticated_user.is_staff,
            'isResearcher': wilder_user.is_researcher
        }
        return Response(data)
    else:
        # Bad login details were provided. So we can't log the user in.
        data = { 'valid': False }
        return Response(data)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    '''Handles the creation of a wilder_user for authentication

    Method arguments:
      request -- The full HTTP request object
    '''
    try:
        # Create a new user by invoking the `create_user` helper method
        # on Django's built-in User model
        new_user = User.objects.create_user(
            username=request.data['username'],
            password=request.data['password'],
            email=request.data['email'],
            first_name=request.data['first_name'],
            last_name=request.data['last_name']
        )

        # Now save the extra info in the wilderwatch_api_wilderuser table
        wilder_user = WilderUser.objects.create(
            bio="",
            user=new_user
        )

        # Use the REST Framework's token generator on the new user account
        token = Token.objects.create(user=wilder_user.user)
        # Return the token to the client
        data = {
            'valid': True,
            'token': token.key,
            'isStaff': new_user.is_staff,
            'isResearcher': wilder_user.is_researcher
        }
    except IntegrityError:
        data = { 'message': "Username already taken" }
    except KeyError as ex:
            return Response({'message': f"{ex.args[0]} is required"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(data)