"""Simple authentication provider for the admin interface."""

from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
from starlette_admin.exceptions import FormValidationError, LoginFailed

from ... import config


class UsernameAndPasswordProvider(AuthProvider):
    """Simple authentication provider.

    Inspired by the demo provider shown at:

    https://jowilf.github.io/starlette-admin/tutorial/authentication/

    """

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        if len(username) < 3:
            """Form data validation"""
            raise FormValidationError(
                {"username": "Ensure username has at least 3 characters"}
            )

        settings: config.ArpavPpcvSettings = request.app.state.settings
        if (
            username == settings.admin_user.username
            and password == settings.admin_user.password
        ):
            """Save `username` in session"""
            request.session.update({"username": username})
            return response

        raise LoginFailed("Invalid username or password")

    async def is_authenticated(self, request) -> bool:
        settings: config.ArpavPpcvSettings = request.app.state.settings
        if request.session.get("username", None) == settings.admin_user.username:
            """
            Save current `user` object in the request state. Can be used later
            to restrict access to connected user.
            """
            request.state.user = settings.admin_user
            return True

        return False

    def get_admin_config(self, request: Request) -> AdminConfig:
        user: config.AdminUserSettings = request.state.user  # Retrieve current user
        # Update app title according to current_user
        custom_app_title = "Hello, " + user.name + "!"
        # Update logo url according to current_user
        custom_logo_url = None
        if (logo := user.company_logo_url) is not None:
            custom_logo_url = request.url_for("static", path=logo)
        return AdminConfig(
            app_title=custom_app_title,
            logo_url=custom_logo_url,
        )

    def get_admin_user(self, request: Request) -> AdminUser:
        user: config.AdminUserSettings = request.state.user  # Retrieve current user
        photo_url = None
        if (avatar := user.avatar) is not None:
            photo_url = request.url_for("static", path=avatar)
        return AdminUser(username=user.name, photo_url=photo_url)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
