help: # print this help and exit
	@grep -E '^[a-zA-Z]' make/unix.mk | sed -E 's/:.*#\s*/\t/g' | grep -Ev '^\s*[a-zA-Z]+:\s*[a-zA-Z]+$$' | sort

clean: # remove generated files
	-rm -r bin releases

compile: # compile program
	mkdir -p bin
	rsync -a --include '*.py' src/ bin
	chmod +x bin/main.py
	mv bin/main.py bin/nudgy

compile-ui: # compile ui
	for f in $$(find src -name '*.ui' | sed 's/\.[^\/]*$$//g'); do \
		pyuic5 -o "$${f}_init.py" "$$f.ui"; \
	done

release: compile # compile and compress program
	mkdir -p releases
	tar -c -f releases/main.tar.gz bin/
	mv releases/main.tar.gz "releases/main-$$(date +%s).tar.gz"

run: compile # compile and run program
	bin/nudgy
