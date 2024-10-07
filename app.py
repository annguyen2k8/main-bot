from flask import Flask, redirect, url_for, render_template, send_from_directory, session
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized, models
from flask_session import Session

from config import *
import os 

app = Flask(
    __name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates'
    )

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './session/'
Session(app)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

app.secret_key = SECRET_KEY
app.config['DISCORD_CLIENT_ID'] = CLIENT_ID
app.config['DISCORD_CLIENT_SECRET'] = CLIENT_SECRET
app.config['DISCORD_REDIRECT_URI'] = REDIRECT_URI
app.config['DISCORD_BOT_TOKEN'] = BOT_TOKEN

discord = DiscordOAuth2Session(app)

# Get statics

@app.route('/assets/<path:path>')
async def get_image(path: str) -> None:
    return send_from_directory('static/assets', path)

@app.route('/css/<path:path>')
async def get_font(path: str) -> None:
    return send_from_directory('static/css', path)

# Pages

@app.route('/')
async def index() -> None:
    user = discord.fetch_user() if discord.authorized else None
    return render_template(['index.html', 'layout.html'], user=user)

def get_guilds(user: models.User) -> list[models.Guild]:
    """
    Get guilds from user

    Args:
        user (models.User)

    Returns:
        list[models.Guild]
    """
    return [guild for guild in user.guilds if guild.is_owner]

@app.route('/servers')
@app.errorhandler(Unauthorized)
async def servers() -> None:
    user = discord.fetch_user()
    # guilds = get_guilds(user)
    print(user, user.guilds)
    return render_template(['servers.html', 'layout.html'], user=user)

# auth2 discord

@app.route("/login")
async def login():
    discord.revoke()
    return discord.create_session(['identify','guilds'])

@app.route("/oauth/callback/")
async def callback():
    try:
        discord.callback()
        return redirect(url_for("index"))
    except Exception as e:
        return f'Error during OAuth callback: {str(e)}', 500

@app.route('/logout')
async def logout():
    discord.revoke()
    session.clear()
    return redirect(url_for('index'))

# Error handler

@app.errorhandler(Unauthorized)
async def redirect_unauthorized(e):
    return redirect(url_for("login"))

@app.errorhandler(404)
def page_not_found(error):
    user = discord.fetch_user() if discord.authorized else None
    return render_template(['error404.html', 'layout.html'], user=user)

@app.errorhandler(500)
def page_error(error):
    user = discord.fetch_user() if discord.authorized else None
    return render_template(['error500.html', 'layout.html'], user=user)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port= 5000, debug=True)