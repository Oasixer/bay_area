ZIPNAME = lambda

.PHONY: all
all:
	-rm $(ZIPNAME).zip
	zip $(ZIPNAME) *.py
