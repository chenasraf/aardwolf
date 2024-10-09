MUSHDIR=$(HOME)/Library/Application Support/CrossOver/Bottles/MushClient/drive_c/users/crossover/MUSHclient
PLUGDIR=$(MUSHDIR)/worlds/plugins

.PHONY: install/spellbook
install/spellbook:
	cp "./Spellbook/Spellbook.xml" "$(PLUGDIR)"
	@echo "Spellbook installed."
