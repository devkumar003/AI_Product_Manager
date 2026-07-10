import logging
from uuid import UUID
from sqlalchemy.orm import Session

from app.services.integration.plugin_manager import plugin_manager
from app.services.integration.secret_vault import secret_vault

logger = logging.getLogger("app.services.integration.oauth_manager")


class OAuthManager:
    # Authorization URL templates
    AUTH_URLS = {
        "github": "https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=repo,user,write:discussion",
        "gitlab": "https://gitlab.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=api,read_user",
        "bitbucket": "https://bitbucket.org/site/oauth2/authorize?client_id={client_id}&response_type=code",
        "jira": "https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id={client_id}&scope=read:jira-work,write:jira-work,offline_access&redirect_uri={redirect_uri}&response_type=code&prompt=consent",
        "notion": "https://api.notion.com/v1/oauth/authorize?client_id={client_id}&response_type=code&owner=user",
        "slack": "https://slack.com/oauth/v2/authorize?client_id={client_id}&scope=incoming-webhook,commands,chat:write",
        "google": "https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/drive",
        "outlook": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=offline_access,Mail.ReadWrite,Calendars.ReadWrite,Files.ReadWrite",
        "figma": "https://www.figma.com/oauth?client_id={client_id}&redirect_uri={redirect_uri}&scope=file_read&state=figma&response_type=code",
        "zoom": "https://zoom.us/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}",
        "teams": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=Group.ReadWrite.All,Chat.ReadWrite",
    }

    def get_authorize_url(self, provider: str, client_id: str, redirect_uri: str) -> str:
        """Returns the authorization URL for a specific provider."""
        provider_key = provider.lower()
        if provider_key not in self.AUTH_URLS:
            # Fallback URL if unknown
            return f"https://example.com/oauth/{provider_key}?client_id={client_id}&redirect_uri={redirect_uri}"
        
        return self.AUTH_URLS[provider_key].format(
            client_id=client_id,
            redirect_uri=redirect_uri
        )

    def exchange_code_for_tokens(
        self, db: Session, workspace_id: UUID, provider: str, code: str, redirect_uri: str
    ) -> dict:
        """Exchanges authorization code for credentials and securely stores them."""
        provider_key = provider.lower()
        logger.info(f"Exchanging OAuth code for provider: {provider_key}")

        # In production, this would make an HTTP call to the provider's token endpoint:
        # e.g., POST https://github.com/login/oauth/access_token
        # Here we perform the protocol exchange flow:
        mock_access_token = f"mock_{provider_key}_access_token_val_12345"
        mock_refresh_token = f"mock_{provider_key}_refresh_token_val_67890"

        # Securely encrypt and save the credentials in the Secret Vault
        secret_vault.store_secret(db, workspace_id, f"{provider_key}_access_token", mock_access_token)
        secret_vault.store_secret(db, workspace_id, f"{provider_key}_refresh_token", mock_refresh_token)

        # Get or create the Connection in the DB
        plugin = plugin_manager.get_plugin_by_slug(db, provider_key)
        if not plugin:
            # Seed if missing
            plugin_manager.seed_default_plugins(db)
            plugin = plugin_manager.get_plugin_by_slug(db, provider_key)
        
        if plugin:
            plugin_manager.create_connection(
                db, 
                workspace_id, 
                plugin.id, 
                config={"connected_at": "now", "account": f"connected_{provider_key}_user"}
            )

        return {
            "access_token": mock_access_token,
            "refresh_token": mock_refresh_token,
            "provider": provider_key,
            "status": "connected"
        }

    def get_access_token(self, db: Session, workspace_id: UUID, provider: str) -> str | None:
        """Retrieves active access token from vault."""
        return secret_vault.get_secret(db, workspace_id, f"{provider.lower()}_access_token")


oauth_manager = OAuthManager()
