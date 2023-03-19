import typer, subprocess

from site_sync import SiteSync
from cloud import server


app = typer.Typer()

@app.command('site:sync')
def sync_site(env: str, country: str = "all", config_file: str = "./config/sites.yml"):
    site_sync = SiteSync(config_file, env, country)
    site_sync.run()

@app.command('cloud:start')
def cloud_start(bind: str = typer.Argument("0.0.0.0:8000", envvar="CLOUD_BIND")):
    gunicorn_cmd = "gunicorn 'src.cloud:create_app()' -b {}".format(bind)
    subprocess.run(gunicorn_cmd, shell=True, check=True)

@app.command('cloud:stop')
def cloud_stop(service: str = typer.Argument("gunicorn", envvar="CLOUD_SERVICE")):
    if service == "gunicorn":
        subprocess.run("pkill gunicorn", shell=True, check=True)
    else:
        subprocess.run("systemctl stop {}".format(service), shell=True, check=True)

if __name__ == '__main__':
    app()
