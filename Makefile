MUSHDIR=$(HOME)/Library/Application Support/CrossOver/Bottles/MushClient/drive_c/users/crossover/MUSHclient
PLUGDIR=$(MUSHDIR)/worlds/plugins

.PHONY: copydb
copydb:
	cp "$(MUSHDIR)/Aardwolf.db" "MapGenerator/Aardwolf.db"
	@echo "Aardwolf.db copied to MapGenerator."

.PHONY: install/spellbook
install/spellbook:
	cp "./Spellbook/Spellbook.xml" "$(PLUGDIR)"
	@echo "Spellbook installed."

.PHONY: watch/spellbook
watch/spellbook:
	@echo "Watching for changes in Spellbook..."
	@fswatch -o "./Spellbook/Spellbook.xml" | xargs -n1 -I{} make install/spellbook

.PHONY: install/spellrotation
install/spellrotation:
	cp "./SpellRotation/SpellRotation.xml" "$(PLUGDIR)"
	@echo "SpellRotation installed."

.PHONY: watch/spellrotation
watch/spellrotation:
	@echo "Watching for changes in SpellRotation..."
	@fswatch -o "./SpellRotation/SpellRotation.xml" | xargs -n1 -I{} make install/spellrotation
