help:
	@powershell.exe -command "select-string '^[a-z]' make\\win.mk | foreach {$$_.line -replace ':[^:#]*#\s+', """`t"""}"
