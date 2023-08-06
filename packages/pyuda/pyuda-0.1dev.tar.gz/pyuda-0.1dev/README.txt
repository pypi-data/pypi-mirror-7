Pyuda takes care of the annoying details of working with Python

# Gets a URL opener using an optional cookie file.  Returns a URL opener object and a cookie jar object.
  - def get_url_opener(cookie_file=None)

# GETs a URL using a URL opener
  - def get_url(opener, url)

# POSTs to a URL using a URL opener.  The fields are specified as a dictionary.
  - def post_url(opener, url, fields=None)

# Checks to see if a specific dependency exists, print instructions on how to get to the dependencies installed
  - def check_dependencies(dependencies)

# Takes an ordered list of parameter descriptions, makes sure the parameter count is correct, and either returns the parameters as a list or exits by printing the missing parameter's description
  - def get_command_line_arguments(parameters)
