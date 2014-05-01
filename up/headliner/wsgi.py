from up.headliner import Application
from up.headliner.utils import read_config_file
from up.headliner import http

config = read_config_file()
app = Application.instance(config)
http.load_routes(config.server["routes"])
print "starting app"
webapp = http.webapp
