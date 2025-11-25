from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from config import settings

# OAuth configuration
config = Config('.env')

oauth = OAuth()

# Google OAuth
oauth.register(
    name='google',
    client_id=getattr(settings, 'GOOGLE_CLIENT_ID', ''),
    client_secret=getattr(settings, 'GOOGLE_CLIENT_SECRET', ''),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# GitHub OAuth
oauth.register(
    name='github',
    client_id=getattr(settings, 'GITHUB_CLIENT_ID', ''),
    client_secret=getattr(settings, 'GITHUB_CLIENT_SECRET', ''),
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'}
)

async def get_google_user_info(token: dict) -> dict:
    """Get user info from Google"""
    return token.get('userinfo', {})

async def get_github_user_info(client, token: dict) -> dict:
    """Get user info from GitHub"""
    resp = await client.get('user', token=token)
    profile = resp.json()
    
    # Get email separately if not in profile
    if not profile.get('email'):
        email_resp = await client.get('user/emails', token=token)
        emails = email_resp.json()
        for email in emails:
            if email.get('primary') and email.get('verified'):
                profile['email'] = email['email']
                break
    
    return profile
