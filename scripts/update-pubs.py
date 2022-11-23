import re

with open("../files/publications.bib", "r") as file:
	data = file.read()

curr = ""
mode = "eating"
entries = []
for char in data:
	if mode == "eating":
		if char in {"}", "\n"} and curr[-1] == "}":
			curr += "\n}"
			entries.append(curr)
			curr = ""
			mode = "waiting"
		else:
			curr += char
	else:
		if char == "@":
			curr = "@"
			mode = "eating"

def month_gt(m1, m2):
	row = ["january", "february", "march", "april", "may", "june", "july", "september", "october", "november", "december"]
	return row.index(m1.lower()) < row.index(m2.lower())

class Entry:
	def __init__(self, entry):


		self.the_type = None
		self.file_name = None
		self.author_surnames = None
		self.authors = None
		self.school = None
		self.note = None
		self.conference = None
		self.publisher = None
		self.month = None
		self.year = None
		self.title = None
		self.booktitle = None

		entry = entry.replace("\n", " ")
		self.the_type = re.match(r"@([^\{]*)\{", entry).group(1)
		self.file_name = re.match(r"@[^\{]*\{([^,]*),", entry).group(1)
		authors = re.match(r".*author[^\{]*\{([^\}]*)\}", entry).group(1)
		authors = authors.split(" and ")
		authors_good = []
		self.author_surnames = [author.split(", ")[0] for author in authors]
		for author in authors:
			authors_good.append(" ".join(author.split(", ")[::-1]))
		
		if len(authors_good) > 1:
			self.authors = ", ".join(authors_good[:-1])
			self.authors += " and " + authors_good[-1]
		else:
			self.authors = authors_good[0]

		self.month = re.match(r".*month[^\{]*\{([^\}]*)\}", entry).group(1)
		self.year = re.match(r".*year[^\{]*\{([^\}]*)\}", entry).group(1)

		booktitle = re.match(r".*booktitle[^\{]*\{([^\}]*)\}", entry)
		if booktitle is not None:
			self.booktitle = booktitle.group(1)
			conference = re.match(r"[^\(]*(\(.*\))$", self.booktitle)
			if conference is not None:
				self.conference = conference.group(1)
				self.booktitle = self.booktitle.replace(" " + self.conference, "")

		publisher = re.match(r".*publisher[^\{]*\{([^\}]*)\}", entry)
		if publisher is not None:
			self.publisher = publisher.group(1)

		note = re.match(r".*note[^\{]*\{([^\}]*)\}", entry)
		if note is not None:
			self.note = note.group(1)

		school = re.match(r".*school[^\{]*\{([^\}]*)\}", entry)
		if school is not None:
			self.school = school.group(1)

		title = re.match(r".*[^k]title[^\{]*\{(.*)", entry).group(1)

		title_good = ""
		mode = "looking"
		for char in title:
			if char == "{":
				if mode == "looking":
					mode = "checked"
			elif char == "}":
				if mode == "looking":
					break
				else:
					mode = "looking"
			else:
				title_good += char

		self.title = title_good

	def __gt__(self, other):
		if self.year > other.year:
			return True
		elif self.year < other.year:
			return False
		elif month_gt(self.month, other.month):
			return True
		elif month_gt(other.month, self.month):			
			return False
		elif self.author_surnames > other.author_surnames:
			return True
		elif self.author_surnames < other.author_surnames:
			return False
		else:
			return self.title > other.title

entries = list(map(Entry, entries))

years = {}
for entry in entries:
	if entry.year in years:
		years[entry.year].add(entry)
	else:
		years[entry.year] = {entry}

result = "<!-- Automatically generated from my personal .bib file -->\n<h2 id=\"publications\">Publications</h2>\n"

for year, year_entries in years.items():
	result += f"<h3>{year}</h3>\n\t<ul>\n"
	for entry in sorted(year_entries):
		result += "\t\t<li> "

		if entry.the_type == "inproceedings":
			result += entry.authors + ". <strong>" + entry.title + "</strong>. "
			result += "In <em>" + entry.booktitle + "</em> " + entry.conference
			if entry.publisher is not None:
				result += ", " + entry.publisher
			result += f", {entry.month} {entry.year}. " + ("" if entry.note is None else f"{entry.note}. ")
			result += "[<a target=\"_blank\" href=\"./files/" + entry.file_name + ".pdf\">pdf</a>]"

		elif entry.the_type == "mastersthesis":
			result += entry.authors + ". <strong>" + entry.title + "</strong>. "
			result += "Master's Thesis, " + entry.school
			result += f", {entry.month} {entry.year}. " + ("" if entry.note is None else f"{entry.note}. ")
			result += "[<a target=\"_blank\" href=\"./files/" + entry.file_name + ".pdf\">pdf</a>]"

		else:
			raise NotImplementedError

		result += "\n"


	result += "\t</ul>\n"

result += "<!-- END PUBLICATIONS -->"

with open("index_template.html", "r") as file:
	data = file.read()

data = data.replace("{{publications}}", result)

with open("../index.html", "w") as file:
	file.write(data)