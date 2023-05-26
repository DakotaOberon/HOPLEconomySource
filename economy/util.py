from django.apps import apps
from django.urls import path, include

class EventManager:
    def __init__(self):
        self.installed_apps = get_installed_apps_by_domain()
        for domain in self.installed_apps:
            setattr(self, domain, DomainEventManager(domain))

class DomainEventManager:
    def __init__(self, domain):
        self.installed_apps = get_installed_apps_by_domain()[domain]
        for app_label in self.installed_apps:
            app_config = apps.get_app_config(app_label)
            app_event_manager = getattr(app_config, 'event_manager', AppEventManager())
            setattr(self, app_label, app_event_manager)

class AppEventManager():
    def __init__(self):
        self.event_handlers = {}

    def register_event(self, event_name):
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []

    def event(self, event_name=None):
        def decorator(handler_function):
            nonlocal event_name
            event_name = handler_function.__name__ if event_name is None else event_name
            self.register_event(event_name)
            self.event_handlers[event_name].append(handler_function)
            return handler_function
        return decorator

    def unsubscribe(self, event_name, handler_function):
        if event_name in self.event_handlers:
            handlers = self.event_handlers[event_name]
            if handler_function in handlers:
                handlers.remove(handler_function)

    def trigger(self, event_name, *args, **kwargs):
        if event_name in self.event_handlers:
            handlers = self.event_handlers[event_name]
            for handler in handlers:
                handler(*args, **kwargs)

def get_installed_apps_by_domain() -> dict:
    app_configs = apps.get_app_configs()
    app_domains = {}
    for app_config in app_configs:
        if not (app_config.name.startswith('apps')):
            continue
        domain = app_config.name.split('.')[1]
        app_label = app_config.name.split('.')[2]
        if domain not in app_domains:
            app_domains[domain] = []
        app_domains[domain].append(app_label)
    
    return app_domains

def register_installed_app_events(event_manager):
    installed_apps = get_installed_apps_by_domain()
    for domain in installed_apps:
        for app_label in installed_apps[domain]:
            app_config = apps.get_app_config(app_label)
            if hasattr(app_config, 'add_events'):
                app_config.add_events(event_manager)

def get_installed_app_urls():
    installed_apps = get_installed_apps_by_domain()
    urls = []
    for domain in installed_apps:
        for app_label in installed_apps[domain]:
            app_config = apps.get_app_config(app_label)
            if hasattr(app_config, 'urlpatterns'):
                urls.append(path(f'apps/{domain}/{app_label}/', include(app_config.urlpatterns), name=f'{domain}-{app_label}'))
    return urls
