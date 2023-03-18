import pathlib, sys, yaml, mergedeep, subprocess, gzip, shutil

from yaml.loader import SafeLoader
from selenium_loader import Browser


class SiteSync:
	def __init__(self, config_file: str, envs: str, countries: str) -> None:
		self._config = self._load_config(config_file)
		self._envs = self._load_envs(envs)
		self._countries = self._load_countries(countries)

	def _load_config(self, config_file: str):
		config_file = pathlib.Path(config_file)
		if not config_file.exists():
			print("The config file doesn't exist")
			sys.exit(1)
		else:
			with open(config_file.absolute(), "r") as stream:
				return yaml.load(stream, Loader=SafeLoader)

	def _load_automation_config(self, automation_config_file: str):
		automation_config_file = pathlib.Path(automation_config_file)
		if not automation_config_file.exists():
			print("The automation config file doesn't exist")
			sys.exit(1)
		else:
			with open(automation_config_file.absolute(), "r") as stream:
				return yaml.load(stream, Loader=SafeLoader)

	def _load_envs(self, envs: str):
		return set([
			key_env for key_env in self._config["environments"].keys()
			if key_env in envs.split(",")
		])

	def _load_countries(self, countries: str):
		return set([
			key_country
			for env in self._config["environments"].values()
			for key_country in env["countries"].keys()
			if key_country in countries.split(",") or countries == "all"
		])

	def _run_commands(self, commands: list[str], cwd: str = "./"):
		while len(commands) > 0:
			process = subprocess.Popen(
				["{} > /dev/null 2>&1".format(commands.pop(0))],
				shell=True,
				cwd=cwd,
				stdout=subprocess.DEVNULL
			)
			process.wait()

	def _load_backup(self, env, country):
		automation_config = country["automation_config"] if "automation_config" in country else self._config["general"]["automation_config"]
		config = mergedeep.merge(
			self._load_automation_config(automation_config),
			{
				"general": {
					"variables": {
						"base_url": country["url"],
						"username": country["variables"]["username"],
						"password": country["variables"]["password"],
						"downloaded_files": []
					}
				}
			}
		)

		browser = Browser(config)
		browser.run()
		backup_path = browser.config.get("general.variables.downloaded_files")

		if len(backup_path):
			backup_path = pathlib.Path(backup_path[0])
			if backup_path.exists():
				with gzip.open(backup_path.absolute(), "rb") as f_in:
					output_name = backup_path.parent.joinpath("uncompress.tmp")
					with open(output_name, "wb") as f_out:
						shutil.copyfileobj(f_in, f_out)

				commands = [
					"{} sql:drop -y ".format(self._config["general"]["drush_command"]),
					"{} sql:cli < {}".format(self._config["general"]["drush_command"], output_name),
					"{} cr".format(self._config["general"]["drush_command"]),
					"rm {} -f".format(backup_path.absolute()),
					"rm {} -f".format(output_name),
				]

				self._run_commands(commands, country["local"])
			else:
				print("Error downloading backup for {} in {}".format(country["name"], env["name"]))
				sys.exit(1)

	def run(self):
		for env in self._envs:
			env = self._config["environments"][env]
			for country in self._countries:
				if country not in env["countries"].keys():
					continue
				country = env["countries"][country]

				print("{} in {} will sync with {}".format(country["name"], env["name"], country["url"]))
				self._load_backup(env, country)
