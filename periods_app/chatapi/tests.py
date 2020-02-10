from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
import pytest

from periods_app.routing import application


TEST_CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}


@database_sync_to_async
def create_user(*,email="abc@gmail.com", username="abc", password="12345678", date_of_birth="2000-10-01", phone_no="9876543210"):
    # Create user.
    user = get_user_model().objects.create_user(
        username=username,
        password=password,
        email=email,
        date_of_birth=date_of_birth,
        phone_no=phone_no
    )
    return user


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestWebsockets:

    async def test_authorized_user_can_connect(self, settings):
        # Use in-memory channel layers for testing.
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

        # Force authentication to get session ID.
        client = Client()
        user = await create_user()
        client.force_login(user=user)

        print("authenticated")
        # Pass session ID in headers to authenticate.
        communicator = WebsocketCommunicator(
            application=application,
            path='/ws/chat/room/',
            headers=[(
                b'cookie',
                f'sessionid={client.cookies["sessionid"].value}'.encode('ascii')
            )]
        )
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()