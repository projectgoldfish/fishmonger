import pyerl       as PyErl
import pybase.find as PyFind

## Look at the applications entry of the app.
## If we have app.app in our intall directory then
## get it's apps as well.
## If we don't assume it's a native app.
def getRequiredApps(app, install_dir="."):
	apps     = []
	
	app_file = None
	for search_dir in [install_dir] + ["/usr/lib/erlang", "/usr/lib64/erlang", "/usr/local/lib/erlang"]:
		app_file = PyFind.find("*/" + app + ".app", search_dir)
		if app_file:
			break

	if not app_file:
		return apps

	(doc, ) = PyErl.parse_file(app_file),
	tuples  = doc.getElementsByTagName("tuple")
	tuple   = None
	for ttuple in tuples:
		if ttuple[0].to_string() == "applications":
			tuple = ttuple
			break
	if tuple == None:
		return [app]
	for dapp in tuple[1]:
		tapps = getRequiredApps(dapp.to_string(), install_dir)
		for tapp in tapps:
			if not tapp in apps:
				 apps.append(tapp)
	apps.append(app)
	return apps