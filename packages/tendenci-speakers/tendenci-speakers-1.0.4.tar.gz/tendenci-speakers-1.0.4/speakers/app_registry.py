from tendenci.core.registry import site
from tendenci.core.registry.base import AppRegistry

from speakers.models import Speaker


class SpeakerRegistry(AppRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create speaker biographies easily with photo,' \
                  ' position, tagline and more ..'
                  
    event_logs = {
        'speaker':{
            'base':('1070000','99EE66'),
            'add':('1070100','119933'),
            'edit':('1070200','EEDD55'),
            'delete':('1070300','AA2222'),
            'search':('1070400','CC55EE'),
            'view':('1070500','55AACC'),
        }
    }

site.register(Speaker, SpeakerRegistry)
