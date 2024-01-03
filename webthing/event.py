'''High-level Event base class implementation.'''

import webthing
from typing import Any, Dict

class Event:
    '''
    An Event represents an individual event from a thing.
    '''

    def __init__(self, thing: webthing.thing.Thing, name: str, data: Any | None = None):
        '''
        Initialize the object.
        
        '''
        self.thing = thing
        self.name = name
        self.data = data
        self.time = webthing.utils.timestamp()

    def as_event_description(self) -> Dict:
        """
        Get the event description.

        Returns a dictionary describing the event.
        """
        description = {
            self.name: {
                'timestamp': self.time,
            },
        }

        if self.data is not None:
            description[self.name]['data'] = self.data

        return description

    def get_thing(self) -> webthing.thing.Thing:
        """Get the thing associated with this event."""
        return self.thing

    def get_name(self) -> str:
        """Get the event's name."""
        return self.name

    def get_data(self) -> Any | None:
        """Get the event's data."""
        return self.data

    def get_time(self) -> str:
        """Get the event's timestamp."""
        return self.time