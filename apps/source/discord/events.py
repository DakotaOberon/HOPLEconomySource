from economy.util import AppEventManager


class ClientEvent():
    def __init__(self, client, **kwargs):
        self.client = client

        for key in kwargs:
            setattr(self, key, kwargs[key])

def register_events(event_manager: AppEventManager):
    # Models
    event_manager.register_event('on_client_created')
    event_manager.register_event('on_client_deleted')
    event_manager.register_event('on_client_updated')
    # Custom Client
    event_manager.register_event('on_client_sync')
    event_manager.register_event('on_client_sync_global')
    # Gateway
    event_manager.register_event('on_client_ready')
    # Guild
    event_manager.register_event('on_guild_join')
    event_manager.register_event('on_guild_remove')
    event_manager.register_event('on_guild_update')
    event_manager.register_event('on_guild_channel_create')
    event_manager.register_event('on_guild_channel_delete')
    event_manager.register_event('on_guild_channel_update')
    event_manager.register_event('on_thread_create')
    event_manager.register_event('on_thread_join')
    event_manager.register_event('on_thread_update')
    event_manager.register_event('on_thread_delete')
    # Interaction
    event_manager.register_event('on_interaction')
    # Member
    event_manager.register_event('on_member_join')
    event_manager.register_event('on_member_remove')
    event_manager.register_event('on_member_update')
    event_manager.register_event('on_user_update')
    event_manager.register_event('on_thread_member_join')
    event_manager.register_event('on_thread_member_remove')
    # Invite
    event_manager.register_event('on_invite_create')
    event_manager.register_event('on_invite_delete')
    # Voice State
    event_manager.register_event('on_voice_state_update')
    # Presence
    event_manager.register_event('on_presence_update')
    # Message
    event_manager.register_event('on_message')
    # Reaction
    event_manager.register_event('on_reaction_add')
    event_manager.register_event('on_reaction_remove')


def register_functions(event_manager: AppEventManager):
    pass
