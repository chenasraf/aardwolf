MUSHDIR=$(HOME)/Library/Application Support/CrossOver/Bottles/MushClient/drive_c/users/crossover/MUSHclient
PLUGDIR=$(MUSHDIR)/worlds/plugins

.PHONY: install/spellbook
install/spellbook:
	cp "./Spellbook/Spellbook.xml" "$(PLUGDIR)"
	@echo "Spellbook installed."

.PHONY: watch/spellbook
watch/spellbook:
	@echo "Watching for changes in Spellbook..."
	@fswatch -o "./Spellbook/Spellbook.xml" | xargs -n1 -I{} make install/spellbook
