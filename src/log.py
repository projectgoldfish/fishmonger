## Python3.4
import os
import os.path
import sys
import inspect

Indent   = ""
LogLevel = 3

def formatMsg(log_msg="", *args, **kwargs):
	seperator = ": "
	msg_args  = ""
	for arg in args:
		if msg_args == "":
			msg_args = str(arg)
		else:
			msg_args += ", " + str(arg)

	for kwarg in kwargs:
		if msg_args == "":
			msg_args  = kwarg
		else:
			msg_args += ", " + kwarg
		msg_args += "="
		msg_args += str(kwargs[kwarg])
		
	if msg_args == "":
		seperator = ""
	return str(log_msg) + seperator + msg_args

def output(header, log_msg="", *args, **kwargs):
	global Indent, LogLevel
	
	log_level = -1 if "log_level" not in kwargs else kwargs["log_level"]
	if "log_level" in kwargs:
		del kwargs["log_level"]

	disable_line_no = False if "disable_line_no" not in kwargs else kwargs["disable_line_no"]
	if "disable_line_no" in kwargs:
		del kwargs["disable_line_no"]

	if LogLevel < log_level:
		return

	fun = ""
	if not disable_line_no:
		frame = inspect.currentframe()
		frame = inspect.getouterframes(frame, 3)

		fun = "%20s@%-6s" % (frame[2][1][-20:], frame[2][2])
		fun.strip()
		fun = fun.ljust(20, " ")

	header = ("{" + str(os.getpid()).rjust(6, "0") + "}") + ("[" + header[:6] + "]").rjust(8, " ")

	formatted_msg = formatMsg(log_msg, *args, **kwargs)

	msg_buffer   = ""
	for x in formatted_msg.split("\n"):
		msg_buffer += header + fun + Indent + "> " + x + "\n"

	sys.stdout.write(msg_buffer)
	sys.stdout.flush()

def log(log_msg="", *args, **kwargs):
	kwargs["log_level"]       = -1
	kwargs["disable_line_no"] = True
	output("LOG", log_msg, *args, **kwargs)
	
def debug(log_msg="", *args, **kwargs):
	output("DEBUG", log_msg, *args, **kwargs)

def warning(log_msg="", *args, **kwargs):
	kwargs["disable_line_no"] = True
	output("WARNING", log_msg, *args, **kwargs)

def error(log_msg="", *args, **kwargs):
	kwargs["log_level"]       = -1
	kwargs["disable_line_no"] = True
	output("ERROR", log_msg, *args, **kwargs)

def increaseIndent():
	global Indent
	Indent = "==" + Indent

def decreaseIndent():
	global Indent
	if Indent == "":
		Indent = ""
	else:
		Indent = Indent[2:]

def setLogLevel(level):
	global LogLevel
	LogLevel = level