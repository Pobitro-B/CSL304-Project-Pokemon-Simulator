from enum import Enum, auto

class ActionType(Enum):
    MOVE = auto()
    SWITCH = auto()
    ITEM = auto()
    RUN = auto()

class Action:
    def __init__(self, action_type: ActionType, actor, target=None, move=None, switch_to=None, item=None):
        """
        Represents a single action taken by a Pokémon or trainer.
        :param action_type: The type of action (MOVE, SWITCH, ITEM, RUN)
        :param actor: The Pokémon performing the action
        :param target: The Pokémon targeted by the action
        :param move: The Move object if action_type == MOVE
        :param switch_to: The Pokémon to switch into if action_type == SWITCH
        :param item: The item used if action_type == ITEM
        """
        self.action_type = action_type
        self.actor = actor
        self.target = target
        self.move = move
        self.switch_to = switch_to
        self.item = item

    def __repr__(self):
        return f"<Action {self.action_type.name} by {self.actor.species.name}>"
