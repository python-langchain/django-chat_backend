from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Django App Configuration for the Users application.

    This class configures the users app within the Django project.
    It defines the app's metadata and initialization settings.

    Attributes:
        default_auto_field: Specifies the type of auto-generated primary key fields
        name: The Python path to the app module
    """

    # Use BigAutoField for auto-generated primary keys (recommended for new projects)
    default_auto_field = "django.db.models.BigAutoField"

    # The app's module name/path
    name = "users"
