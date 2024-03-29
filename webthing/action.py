"""High-level Action base class implementation."""

import webthing
from typing import Dict
from abc import ABC, abstractmethod
import asyncio
from asyncio import Task


class Action(ABC):
    """
    An Action represents an individual action on a Thing.
    """

    def __init__(self, id_: str, thing: webthing.thing.Thing, name: str, input_: Dict):
        """
        Initialize the object.

        id_ -- ID of this action.
        thing -- the Thing this action belongs to
        name -- name of the action
        input -- any action inputs
        """
        self.id = id_
        self.thing = thing
        self.name = name
        self.input = input_
        self.href_prefix = ""
        self.href = "/actions/{}/{}".format(self.name, self.id)
        self.status = "created"
        self.time_requested = webthing.utils.timestamp()
        self.time_completed: str = ""

    def as_action_description(self) -> Dict:
        """
        Get the action description.

        Returns a disctionary describing the action.
        """
        description = {
            self.name: {
                "href": self.href_prefix + self.href,
                "timeRequested": self.time_requested,
                "status": self.status,
            },
        }

        if self.input is not None:
            description[self.name]["input"] = self.input

        if self.time_completed is not None:
            description[self.name]["timeCompleted"] = self.time_completed

        return description

    def set_href_prefix(self, prefix) -> None:
        """
        Set the prefix of any hrefs associated with this action.

        prefix -- the prefix
        """
        self.href_prefix = prefix

    def get_id(self) -> str:
        """Get this action's ID."""
        return self.id

    def get_name(self) -> str:
        """Get this action's name."""
        return self.name

    def get_href(self) -> str:
        """Get this action's href."""
        return self.href_prefix + self.href

    def get_status(self) -> str:
        """Get this action's status."""
        return self.status

    def get_thing(self) -> webthing.thing.Thing:
        """Get the thing associated with this action."""
        return self.thing

    def get_time_requested(self) -> str:
        """Get the time the action was requested."""
        return self.time_requested

    def get_time_completed(self) -> str | None:
        """Get the time the action was completed."""
        return self.time_completed

    def get_input(self) -> Dict:
        """Get the inputs for this action."""
        return self.input

    def start(self) -> Task:
        """
        Start performing the action.
        """

        async def action_task():
            self.status = "pending"
            self.thing.action_notify(self)
            await self.perform_action()
            self.finish()

        task = asyncio.create_task(action_task())

        return task

    def cancel(self) -> None:
        """
        Override this with the code necessary to cancel the action.
        """
        pass

    def finish(self) -> None:
        """
        Finish performing the action.
        """
        self.status = "completed"
        self.time_completed = webthing.utils.timestamp()
        self.thing.action_notify(self)

    @abstractmethod
    async def perform_action(self) -> None:
        """
        Override this with the code necessary to perform the action
        """
        await self._perform_action()
