from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Checks that all app dependencies are installed"
    app_configs = apps.get_app_configs()
    installed_apps = [app.name for app in app_configs]

    def check_if_dependencies_are_installed(self, app):
        return [dependency for dependency in app.dependencies if dependency not in self.installed_apps]

    def handle(self, *args, **options):
        apps_missing_dependencies = []
        for app in self.app_configs:
            if not hasattr(app, 'dependencies'):
                continue
            missing = self.check_if_dependencies_are_installed(app)
            if len(missing) > 0:
                apps_missing_dependencies.append({'name': app.name, 'missing': missing})

        if (len(apps_missing_dependencies) > 0):
            self.stderr.write(self.style.ERROR('The following apps are missing dependencies:'))
            for app in apps_missing_dependencies:
                self.stderr.write(self.style.WARNING(f'{app["name"]} is missing -> {" | ".join(app["missing"])}'))
            return

        self.stdout.write(self.style.SUCCESS('All app dependencies are installed'))

if __name__ == "__main__":
    Command().handle()
