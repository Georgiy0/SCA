
from typing import Dict

from ..requests_sender_base import HttpRequestsSender

from .post_auth_sender import PostAuthRequestsSender

def get_requset_senders() -> Dict[str, HttpRequestsSender]:
    pa_sender = PostAuthRequestsSender()
    return {
        pa_sender.Name: pa_sender
    }