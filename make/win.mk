help: # print this help and exit
	@powershell.exe -command "select-string '^[a-z]' make\\win.mk | foreach {$$_.line -replace ':[^:#]*#\s+', """`t"""}"

clean: # remove generated files
	-rd /q /s bin releases

compile: # compile program
	-md bin
	robocopy.exe src bin /e /njh /njs /xf *.ui
	mv /y bin\\main.py bin\\nudgy.py

compile-ui: # compile ui
	for f in $$(find src -name '*.ui' | sed 's/\.[^\/]*$$//g'); do \
		pyuic5.exe -o "$${f}_init.py" "$$f.ui"; \
	done

release: compile # compile and compress program
	-md releases
	tar.exe -c -f releases\\main.tar.gz bin
	mv releases/main.tar.gz "releases/main-$$(date +%s).tar.gz"

run: compile # compile and run program
	bin\\nudgy.py
