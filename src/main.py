import typer

from site_sync import SiteSync
from cloud_webhook import Webhook


app = typer.Typer()

@app.command('site:sync')
def sync_site(env: str, country: str = "all", config_file: str = "./config/sites.yml"):
    site_sync = SiteSync(config_file, env, country)
    site_sync.run()

@app.command('cloud:start')
def cloud_webhook():
    Webhook.run() # To run with gunicorn, use: gunicorn "src.cloud_webhook:create_app()"

if __name__ == '__main__':
    app()
