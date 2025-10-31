IFS = .
SHELL = powershell.exe

help: # print this help and exit
	@select-string -casesensitive '^[a-z]' make\\win.mk | foreach {$$_.line -replace ':[^:#]*#\s+', "`t"}

clean: # remove generated files
	-rm -erroraction silentlycontinue -recurse bin, releases

compile: # compile program
	mkdir -force bin >$$NULL
	-robocopy.exe src bin /e /njh /njs /xf *.ui
	mv -force bin\\main.py bin\\nudgy.py

compile-ui: # compile ui
	for f in $$(find src -name '*.ui' | sed 's/\.[^\/]*$$//g'); do \
		pyuic5.exe -o "$${f}_init.py" "$$f.ui"; \
	done

# release: compile # compile and compress program
# 	-md releases
# 	tar.exe -c -f releases\\main.tar.gz bin
# 	mv releases/main.tar.gz "releases/main-$$(date +%s).tar.gz"

# run: compile # compile and run program
# 	bin\\nudgy.py
