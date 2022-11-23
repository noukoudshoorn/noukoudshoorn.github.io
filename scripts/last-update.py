import datetime

with open("../index.html", "r") as file: # index because this goes after the other script
	data = file.read()

data = data.replace("{{date_last}}", datetime.datetime.now().strftime("%Y-%m-%d, %H:%M (CET)"))
data = data.replace("{{year}}", datetime.datetime.now().strftime("%Y"))

with open("../index.html", "w") as file:
	file.write(data)