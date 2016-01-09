"""
Default

@author: Charles Zilm

Deafault fishmonger tool chain. Any tool chain that does not define an action will
use the behavior as it is defined here. Module should serve as a template/spec for all 
future modules.

Types as used by function documentation:

command()    - function(config()) -> boolean() | string() - When a string the value will be executed via shell. When a function it will be called with the config for the build stage.
config()     - BuildConfig()
boolean()    - True | False
dependency() - string() :: Name | (string() :: Name, string() :: Version)
"""

import pybase.find as PyFind

