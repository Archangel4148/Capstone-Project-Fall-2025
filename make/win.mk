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
	foreach ($$f in (ls -filter *.ui -recurse src)) {$$f = $$f.fullname -replace ".{$$($$f.extension.length)}$$"; pyuic5.exe -o "$${f}_init.py" "$$f.ui"}

release: compile # compile and compress program
	mkdir -force releases >$$NULL
	tar.exe -c -f releases\\main.tar.gz bin
	mv releases\\main.tar.gz "releases\\main-$$(([datetimeoffset](date)).tounixtimeseconds()).tar.gz"

run: compile # compile and run program
	bin\\nudgy.py
