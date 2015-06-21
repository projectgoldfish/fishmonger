import pyerl       as PyErl
import pybase.log  as PyLog
import pybase.find as PyFind

AppRequirements = {}

## Look at the applications entry of the app.
## If we have app.app in our intall directory then
## get it's apps as well.
## If we don't assume it's a native app.
def getRequiredApps(app, install_dir="."):
	PyLog.increaseIndent()

	global AppRequirements

	seen_apps = {}
	apps      = []

	PyLog.debug("Find", app)

	## If we already exist just return
	if app in AppRequirements:
		PyLog.debug("Already exist!")
		PyLog.decreaseIndent()
		return AppRequirements[app]

	app_file = None
	for search_dir in [install_dir] + ["/usr/lib/erlang", "/usr/lib64/erlang", "/usr/local/lib/erlang"]:
		PyLog.debug("Searching for .app file", app=app, search_dir=search_dir, log_level=5)
		app_file = PyFind.find("*/" + app + ".app", search_dir)
		PyLog.debug("Found .app file", app_file=app_file, log_level=5)
		if app_file:
			break

	if not app_file:
		PyLog.debug("Doesnt exist!")
		PyLog.decreaseIndent()
		return apps

	doc    = PyErl.parse_file(app_file)
	tuples = doc.getElementsByTagName("tuple")
	tuple  = None

	## Find Application tuple
	for ttuple in tuples:
		if ttuple[0].to_string() == "applications":
			tuple = ttuple
			break

	## If no apps are specified we can just start
	if tuple == None:
		PyLog.debug("No apps required")
		PyLog.decreaseIndent()
		return [app]
	
	all_dapps = []
	## For each required app
	for dapp in tuple[1]:
		## Get that apps required apps
		all_dapps += getRequiredApps(dapp.to_string(), install_dir)
			
	for t_app in all_dapps:
		if t_app in seen_apps:
			continue
		seen_apps[t_app] = 1
		apps.append(t_app)

	apps.append(app)
	AppRequirements[app] = apps

	PyLog.debug("APP USE", app=app, apps=apps)

	PyLog.debug("Complete")
	PyLog.decreaseIndent()
	return apps