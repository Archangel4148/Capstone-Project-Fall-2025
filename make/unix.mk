help: # print this help and exit
	@grep -E '^[a-zA-Z]' make/unix.mk | sed -E 's/:.*#\s*/\t/g' | grep -Ev '^\s*[a-zA-Z]+:\s*[a-zA-Z]+$$' | sort

clean: # remove generated files
	-rm -r bin

compile: # compile program
	mkdir -p bin
	rsync -a --include '*.py' src/ bin
	chmod +x bin/main.py
	mv bin/main.py bin/nudgy

compile-ui: # compile ui
	for f in $$(find src -name '*.ui' | sed 's/\.[^\/]*$$//g'); do \
		pyuic5 -o "$${f}_init.py" "$$f.ui"; \
	done

run: compile # compile and run program
	bin/nudgy
