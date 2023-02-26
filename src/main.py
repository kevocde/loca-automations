import typer

from yaml.loader import SafeLoader
from site_sync import SiteSync



app = typer.Typer()

@app.command('site:sync')
def sync_site(env: str, country: str = "all", config_file: str = "./config/sites.yml"):
  site_sync = SiteSync(config_file, env, country)
  site_sync.run()


if __name__ == '__main__':
  app()
