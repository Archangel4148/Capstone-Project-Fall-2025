ifeq ($(OS),Windows_NT)
	include make\\win.mk
else
	include make/unix.mk
endif
