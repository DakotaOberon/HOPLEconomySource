from economy.util import AppEventManager

def register_events(event_manager: AppEventManager):
    event_manager.register_event('on_citizen_created')
    event_manager.register_event('on_citizen_deleted')
    event_manager.register_event('on_citizen_updated')

def register_functions(event_manager: AppEventManager):
    pass
