ZIPNAME = lambda

PYTHON_FILES  = lambda_function.py
PYTHON_FILES += oauth_secret.py
PYTHON_FILES += wrt_agenda_command.py
PYTHON_FILES += wrt_bay_command.py
PYTHON_FILES += wrt_dynamodb_handler.py
PYTHON_FILES += wrt_lists.py
PYTHON_FILES += wrt_respond.py
PYTHON_FILES += wrt_todo_command.py
PYTHON_FILES += wrt_slack_handler.py
PYTHON_FILES += wrt_usernames.py

.PHONY: all
all:
	-rm $(ZIPNAME).zip
	zip $(ZIPNAME) $(PYTHON_FILES)
