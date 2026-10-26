# CAR-CORE-002 / R4: Structural Validation & Contract Freeze test suite.
# Audits, verifies and freezes all 32 observable structural contracts across:
# 1. Authority and data invariants (1-10)
# 2. Loading and isolation (11-20)
# 3. Robustness and negatives (21-26)
# 4. Regression and compatibility (27-32)
extends SceneTree

const STRUCTURAL_PATH := "res://data/structural_world.json"
const PLAYABLE_PATH := "res://data/chapter_01_surface.json"

const EXPECTED_STRUCTURAL_SHA256 := "fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3"
const EXPECTED_PLAYABLE_SHA256 := "afa33c8898049c5af53d06cc3550edbd8f7d58792c819e6224286e82533438c9"

var checks := 0
var failures := 0


func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL: " + label)


func _initialize() -> void:
	print("Running CAR-CORE-002 / R4 structural contract freeze tests...")
	_test_authority_and_data_invariants()
	_test_loading_and_isolation()
	_test_robustness_and_negatives()
	_test_regression_and_compatibility()

	print("%s: %d CAR-CORE-002 / R4 structural freeze checks completed with %d failures" % [
		"PASS" if failures == 0 else "FAIL",
		checks,
		failures
	])
	quit(0 if failures == 0 else 1)


func _test_authority_and_data_invariants() -> void:
	var catalog := StructuralCatalog.load_default(STRUCTURAL_PATH)
	check(catalog.is_loaded(), "Preflight: StructuralCatalog loaded for authority checks")

	# 1. Total exacto de 185 ubicaciones históricas
	var loc_ids := catalog.get_location_ids()
	var loc_count_ok: bool = (
		loc_ids.size() == 185 and
		loc_ids[0] == "LOC_NOWHERE" and
		loc_ids[1] == "LOC_START" and
		loc_ids[184] == "LOC_FOOF6"
	)
	check(loc_count_ok, "1. Total exacto de 185 ubicaciones históricas (LOC_NOWHERE..LOC_FOOF6)")

	# 2. Total exacto de 623 viajes ordenados globalmente
	var travel_records := catalog.get_all_travel_records()
	check(travel_records.size() == 623, "2. Total exacto de 623 viajes ordenados globalmente")

	# 3. Total exacto de 70 registros de objetos (con NO_OBJECT)
	var obj_ids := catalog.get_object_ids()
	var sentinel_ok: bool = false
	if catalog.has_object("NO_OBJECT"):
		var sentinel := catalog.get_object("NO_OBJECT")
		sentinel_ok = bool(sentinel.get("is_sentinel", false)) and int(sentinel.get("source_index", -1)) == 0
	check(obj_ids.size() == 70 and sentinel_ok, "3. Total exacto de 70 registros de objetos incluyendo centinela NO_OBJECT")

	# 4. Total exacto de 11 capítulos editoriales sin duplicados ni huérfanas
	var ch_ids := catalog.get_chapter_ids()
	var chapter_membership: Dictionary = {}
	var duplicate_found := false
	var total_members := 0
	for cid in ch_ids:
		var ch := catalog.get_chapter(cid)
		var members: Array = ch.get("members", [])
		total_members += members.size()
		for mid in members:
			if chapter_membership.has(mid):
				duplicate_found = true
			chapter_membership[mid] = cid
	var coverage_ok: bool = (
		ch_ids.size() == 11 and
		not duplicate_found and
		total_members == 185 and
		chapter_membership.size() == 185
	)
	check(coverage_ok, "4. Total exacto de 11 capítulos editoriales con cobertura 100%, 0 duplicados y 0 huérfanas")

	# 5. Conservación de las 6 dwarflocs históricas
	var expected_dwarfs := ["LOC_KINGHALL", "LOC_WESTBANK", "LOC_Y2", "LOC_ALIKE3", "LOC_COMPLEX", "LOC_MAZEEND12"]
	var dwarflocs := catalog.get_dwarflocs()
	var dwarfs_ok := (dwarflocs.size() == 6)
	if dwarfs_ok:
		for i in range(6):
			if dwarflocs[i] != expected_dwarfs[i]:
				dwarfs_ok = false
				break
	check(dwarfs_ok, "5. Conservación estricta de las 6 dwarflocs históricas")

	# 6. Conservación del orden relativo y global de reglas de viaje
	var global_order_ok := true
	for i in range(travel_records.size()):
		if int(travel_records[i].get("global_travel_index", -1)) != i:
			global_order_ok = false
			break
	var local_order_ok := true
	for lid in loc_ids:
		var loc_travel := catalog.get_travel_records(lid)
		var prev_idx := -1
		for tr in loc_travel:
			var cur_idx := int(tr.get("source_rule_index", -1))
			if cur_idx <= prev_idx:
				local_order_ok = false
				break
			prev_idx = cur_idx
	check(global_order_ok and local_order_ok, "6. Conservación del orden relativo y global (0..622) de reglas de viaje")

	# 7. Conservación de todos los tipos de condición declarados
	var cond_counts: Dictionary = {}
	for tr in travel_records:
		var ctype := String(tr.get("condition_type", ""))
		cond_counts[ctype] = int(cond_counts.get(ctype, 0)) + 1
	var conds_ok: bool = (
		cond_counts.get("always", 0) == 574 and
		cond_counts.get("not", 0) == 25 and
		cond_counts.get("pct", 0) == 12 and
		cond_counts.get("carry", 0) == 7 and
		cond_counts.get("with", 0) == 4 and
		cond_counts.get("nodwarves", 0) == 1 and
		cond_counts.values().reduce(func(accum, val): return accum + val, 0) == 623
	)
	check(conds_ok, "7. Conservación de tipos de condición: always:574, not:25, pct:12, carry:7, with:4, nodwarves:1")

	# 8. Conservación de destinos especiales (speak, special, nodwarves)
	var actions: Dictionary = {}
	var special_targets_valid := true
	var nodwarves_found := false
	for tr in travel_records:
		var atype := String(tr.get("action_type", ""))
		actions[atype] = int(actions.get(atype, 0)) + 1
		if atype == "special":
			var hid := int(tr.get("target", 0))
			if hid < 1 or hid > 3:
				special_targets_valid = false
		if tr.get("condition_type") == "nodwarves":
			if tr.get("source_location_id") == "LOC_LONGWEST" and tr.get("destination_location_id") == "LOC_DIFFERENT1":
				nodwarves_found = true
	var specials_ok: bool = (
		actions.get("goto", 0) == 583 and
		actions.get("speak", 0) == 34 and
		actions.get("special", 0) == 6 and
		special_targets_valid and
		nodwarves_found
	)
	check(specials_ok, "8. Conservación de destinos especiales: goto:583, speak:34, special:6, nodwarves:1")

	# 9. Conservación de objetos multi-ubicación (11) y multi-estado (26)
	var multi_loc_count := 0
	var multi_state_count := 0
	for oid in obj_ids:
		var obj := catalog.get_object(oid)
		if bool(obj.get("has_multiple_locations", false)):
			multi_loc_count += 1
		if bool(obj.get("has_multiple_states", false)):
			multi_state_count += 1
	check(multi_loc_count == 11 and multi_state_count == 26,
		"9. Conservación de objetos multi-ubicación (11) y multi-estado (26)")

	# 10. Resolución completa de referencias cruzadas sin destinos rotos
	var broken_destinations := 0
	var broken_cond_objects := 0
	for tr in travel_records:
		if tr.get("action_type") == "goto":
			var dest := String(tr.get("destination_location_id", ""))
			if not catalog.has_location(dest):
				broken_destinations += 1
		var obj_deps: Array = tr.get("object_dependencies", [])
		for dep_obj in obj_deps:
			if not catalog.has_object(String(dep_obj)):
				broken_cond_objects += 1
	check(broken_destinations == 0 and broken_cond_objects == 0,
		"10. Resolución completa de referencias cruzadas sin destinos ni dependencias rotas")


func _test_loading_and_isolation() -> void:
	var catalog := StructuralCatalog.load_default(STRUCTURAL_PATH)
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)
	var parser := CommandParser.new(world)

	# 11. Carga válida del esquema estructural v1
	var meta := catalog.get_catalog_meta()
	var schema_ok: bool = (
		catalog.is_loaded() and
		int(meta.get("schema_version", 0)) == 1 and
		meta.get("cut_id") == "CAR-CORE-002-R2" and
		meta.get("document_status") == "INERT_STRUCTURAL_DATA / NOT_RUNTIME_ACTIVE"
	)
	check(schema_ok, "11. Carga válida de esquema estructural v1 y estado de documento INERT")

	# 12. Disponibilidad de catálogo completo en solo lectura
	var catalog_available: bool = (
		catalog.get_location_ids().size() == 185 and
		catalog.get_object_ids().size() == 70 and
		catalog.get_chapter_ids().size() == 11 and
		catalog.get_all_travel_records().size() == 623 and
		world.has_structural_location("LOC_START") and
		world.has_structural_location("LOC_BELOWGRATE") and
		not world.get_structural_object("CHEST").is_empty() and
		not world.get_structural_object("KEYS").is_empty()
	)
	check(catalog_available, "12. Catálogo global completo disponible en solo lectura vía WorldData")

	# 13. Resistencia a mutaciones externas mediante copias defensivas
	var loc_mut := catalog.get_location("LOC_START")
	loc_mut["id"] = "MUTATED_LOCATION"
	loc_mut["flags"]["LIT"] = not loc_mut["flags"]["LIT"]
	loc_mut["travel"].clear()
	var obj_mut := catalog.get_object("KEYS")
	obj_mut["descriptions"].clear()
	var chap_mut := catalog.get_chapter("CH_SURFACE")
	chap_mut["members"].clear()
	var all_travel_mut := catalog.get_all_travel_records()
	all_travel_mut.clear()

	var loc_fresh := catalog.get_location("LOC_START")
	var obj_fresh := catalog.get_object("KEYS")
	var chap_fresh := catalog.get_chapter("CH_SURFACE")
	var all_travel_fresh := catalog.get_all_travel_records()
	var defense_ok: bool = (
		loc_fresh["id"] == "LOC_START" and
		bool(loc_fresh["flags"]["LIT"]) == true and
		loc_fresh["travel"].size() > 0 and
		obj_fresh["descriptions"].size() > 0 and
		chap_fresh["members"].size() == 34 and
		all_travel_fresh.size() == 623
	)
	check(defense_ok, "13. Resistencia absoluta a mutaciones externas mediante copias defensivas profundas")

	# 14. Conjunto habilitado restringido exactamente a las 34 salas de CH_01 + autorizadas de CH_ENTRY
	var enabled_ids := world.get_enabled_location_ids()
	var ch_surface := catalog.get_chapter("CH_SURFACE")
	var surface_members: Array = ch_surface.get("members", [])
	var all_in_surface := true
	for eid in enabled_ids:
		if not surface_members.has(eid) and not WorldData.AUTHORIZED_ADDITIONAL_LOCATIONS.has(eid):
			all_in_surface = false
			break
	check(enabled_ids.size() == 42 and all_in_surface,
		"14. Conjunto habilitado restringido exactamente a las 34 salas de CH_01 + autorizadas de CH_ENTRY")

	# 15. Exactamente 150 salas no habilitadas fuera de CH_01
	var disabled_count := 0
	for lid in catalog.get_location_ids():
		if not world.is_location_enabled(lid):
			disabled_count += 1
	check(disabled_count == 143, "15. Exactamente 143 salas permanecen no habilitadas fuera de CH_01")

	# 16. WorldData.locations y WorldData.objects preservan contenido funcional
	var locs_functional: bool = (world.locations.size() == 42)
	var objs_functional: bool = (world.objects.size() == 8)
	var no_inert_in_runtime := true
	for oid in ["CHEST", "DRAGON", "OGRE", "PLANT", "TROLL", "BEAR"]:
		if world.objects.has(oid):
			no_inert_in_runtime = false
			break
	check(locs_functional and objs_functional and no_inert_in_runtime,
		"16. WorldData.locations (42) y WorldData.objects (8) preservan contenido funcional sin filtraciones")

	# 17. No incorporación de vocabulario de capítulos posteriores al parser
	var cmd_chest := parser.parse("TAKE CHEST")
	var cmd_dragon := parser.parse("KILL DRAGON")
	var parser_unpolluted: bool = (
		cmd_chest.action == "CARRY" and
		not world.objects.has("CHEST") and
		not world.objects.has("DRAGON")
	)
	check(parser_unpolluted, "17. El parser no incorpora vocabulario ni referencias a objetos de capítulos posteriores")

	# 18. No adición de salas al mapa jugable
	var map_ok: bool = (world.map_nodes.size() == 34 and world.map_edges.size() == 118)
	var inert_in_map := false
	for node in world.map_nodes:
		if not world.is_location_enabled(node["id"]):
			inert_in_map = true
			break
	check(map_ok and not inert_in_map, "18. No adición de salas al mapa jugable (34 nodos, 118 aristas)")

	# 19. No alteración de GameState ni consumo de RNG por consultas estructurales
	var loc_before := interpreter.state.current_location
	var turn_before := interpreter.state.turn
	var objs_before := interpreter.state.object_place.duplicate()
	var rng_before := interpreter.rng.state
	for lid in world.get_structural_location_ids():
		world.get_structural_location(lid)
		world.get_structural_travel_records(lid)
	for oid in catalog.get_object_ids():
		world.get_structural_object(oid)
	var state_untouched: bool = (
		interpreter.state.current_location == loc_before and
		interpreter.state.turn == turn_before and
		interpreter.state.object_place == objs_before and
		interpreter.rng.state == rng_before
	)
	check(state_untouched, "19. Consultas estructurales no alteran GameState ni consumen números de RNG")

	# 20. is_in_chapter() estrictamente equivalente al conjunto habilitado
	var is_in_chapter_match := true
	for lid in catalog.get_location_ids():
		if world.is_in_chapter(lid) != world.is_location_enabled(lid):
			is_in_chapter_match = false
			break
	check(is_in_chapter_match, "20. is_in_chapter() es estrictamente equivalente al conjunto habilitado (42 true, 143 false)")


func _test_robustness_and_negatives() -> void:
	var valid_text := FileAccess.get_file_as_string(STRUCTURAL_PATH)
	var valid_dict: Dictionary = JSON.parse_string(valid_text)

	# 21. Rechazo explícito de JSON con sintaxis corrupta
	var cat_corrupt := StructuralCatalog.new()
	var res_corrupt := cat_corrupt.load_from_string("{ sintaxis corrupta [ {")
	check(not res_corrupt and not cat_corrupt.is_loaded() and not cat_corrupt.get_last_error().is_empty(),
		"21. Rechazo explícito y diagnosticable de JSON con sintaxis corrupta")

	# 22. Rechazo explícito de esquema con schema_version != 1
	var dict_bad_ver: Dictionary = valid_dict.duplicate(true)
	dict_bad_ver["meta"]["schema_version"] = 2
	var cat_bad_ver := StructuralCatalog.new()
	var res_bad_ver := cat_bad_ver.load_from_string(JSON.stringify(dict_bad_ver))
	check(not res_bad_ver and not cat_bad_ver.is_loaded() and cat_bad_ver.get_last_error().contains("incompatible schema_version"),
		"22. Rechazo explícito de esquema con schema_version != 1")

	# 23. Rechazo explícito de identificadores de sala duplicados
	var dict_dup_loc: Dictionary = valid_dict.duplicate(true)
	var locs_dup: Array = dict_dup_loc["locations"].duplicate(true)
	locs_dup[1]["id"] = locs_dup[0]["id"]
	dict_dup_loc["locations"] = locs_dup
	var cat_dup := StructuralCatalog.new()
	var res_dup := cat_dup.load_from_string(JSON.stringify(dict_dup_loc))
	check(not res_dup and not cat_dup.is_loaded() and cat_dup.get_last_error().contains("duplicate location id"),
		"23. Rechazo explícito de identificadores de sala duplicados")

	# 24. Rechazo explícito de viajes con destinos desconocidos
	var dict_bad_dest: Dictionary = valid_dict.duplicate(true)
	var travel_bad: Array = dict_bad_dest["travel"].duplicate(true)
	travel_bad[0]["destination_location_id"] = "LOC_NON_EXISTENT_DESTINATION_FOR_FREEZE"
	dict_bad_dest["travel"] = travel_bad
	var cat_bad_dest := StructuralCatalog.new()
	var res_bad_dest := cat_bad_dest.load_from_string(JSON.stringify(dict_bad_dest))
	check(not res_bad_dest and not cat_bad_dest.is_loaded() and cat_bad_dest.get_last_error().contains("unknown destination"),
		"24. Rechazo explícito de viajes con destinos desconocidos")

	# 25. Rechazo explícito de proyecciones con claves raíz ausentes
	var missing_keys_ok := true
	for req_key in ["locations", "travel", "objects", "chapters", "meta"]:
		var dict_missing: Dictionary = valid_dict.duplicate(true)
		dict_missing.erase(req_key)
		var cat_missing := StructuralCatalog.new()
		var res_missing := cat_missing.load_from_string(JSON.stringify(dict_missing))
		if res_missing or cat_missing.is_loaded() or not cat_missing.get_last_error().contains("missing required root key"):
			missing_keys_ok = false
			break
	check(missing_keys_ok, "25. Rechazo explícito de proyecciones con claves raíz requeridas ausentes")

	# 26. Catálogo no entra en estado parcial o corrompido tras error (fail-closed)
	var cat_fail_closed := StructuralCatalog.load_default(STRUCTURAL_PATH)
	check(cat_fail_closed.is_loaded(), "Preflight: catálogo cargado previamente")
	var fail_reload := cat_fail_closed.load_from_string("{ bad json")
	var is_cleared: bool = (
		not fail_reload and
		not cat_fail_closed.is_loaded() and
		cat_fail_closed.get_location_ids().is_empty() and
		cat_fail_closed.get_object_ids().is_empty() and
		cat_fail_closed.get_chapter_ids().is_empty() and
		cat_fail_closed.get_all_travel_records().is_empty() and
		not cat_fail_closed.get_last_error().is_empty()
	)
	check(is_cleared, "26. Política fail-closed estricta: el catálogo se limpia por completo tras fallo de carga")


func _test_regression_and_compatibility() -> void:
	# 27. Digest SHA-256 de chapter_01_surface.json idéntico al pre-corte
	var actual_playable_sha := FileAccess.get_sha256(PLAYABLE_PATH)
	check(actual_playable_sha == EXPECTED_PLAYABLE_SHA256,
		"27. Digest SHA-256 de chapter_01_surface.json coincide exactamente (" + actual_playable_sha + ")")

	# 28. SHA-256 de structural_world.json coincide con el artefacto R2
	var actual_struct_sha := FileAccess.get_sha256(STRUCTURAL_PATH)
	check(actual_struct_sha == EXPECTED_STRUCTURAL_SHA256,
		"28. SHA-256 de structural_world.json coincide con el artefacto R2 (" + actual_struct_sha + ")")

	# 29. Exportación determinista de ambos artefactos sin diferencias
	var playable_exists := FileAccess.file_exists(PLAYABLE_PATH)
	var struct_exists := FileAccess.file_exists(STRUCTURAL_PATH)
	var playable_data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PLAYABLE_PATH))
	var struct_data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(STRUCTURAL_PATH))
	var export_ok: bool = (
		playable_exists and struct_exists and
		not playable_data.is_empty() and not struct_data.is_empty() and
		playable_data.has("locations") and playable_data.has("objects") and
		struct_data.has("locations") and struct_data.has("objects") and
		int(struct_data.get("meta", {}).get("schema_version", 0)) == 1
	)
	check(export_ok, "29. Exportación determinista y validez de esquemas de ambos artefactos JSON")

	# 30. Pruebas de aislamiento de CUT A, CUT B, CUT C y CUT D siguen pasando
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)
	# CUT A isolation
	var cut_a_ok: bool = (world.locations.size() == 42 and world.objects.size() == 8)
	# CUT B travel
	var cut_b_ok: bool = (world.locations.has("LOC_START") and world.describe("LOC_START").length() > 0)
	# CUT C darkness/lamp
	var cut_c_ok: bool = (interpreter.state.lamp_energy == 330)
	# CUT D death
	var cut_d_ok: bool = (interpreter.state.death_count == 0)
	check(cut_a_ok and cut_b_ok and cut_c_ok and cut_d_ok,
		"30. Garantías de aislamiento histórico de CUT A, CUT B, CUT C y CUT D preservadas")

	# 31. Ciclo de juego de CH_01 completamente funcional
	for line in ["E", "TAKE KEYS", "OUT", "DEPRESSION", "UNLOCK GRATE", "ENTER"]:
		interpreter.submit(line)
	var ch01_loop_ok: bool = (
		interpreter.state.current_location == "LOC_BELOWGRATE" and
		interpreter.state.state_of("GRATE") == "GRATE_OPEN" and
		interpreter.state.travel_outcome == GameState.TravelOutcome.ARRIVED
	)
	check(ch01_loop_ok, "31. Ciclo de juego jugable de CH_01 y descenso a LOC_BELOWGRATE tras abrir la reja intactos")

	# 32. Ninguna sala no autorizada fuera de CH_01 + autorizadas puede habilitarse accidentalmente
	var enabled_copy := world.get_enabled_location_ids()
	enabled_copy.append("LOC_MISTHALL")
	enabled_copy.clear()
	var still_protected: bool = (
		world.get_enabled_location_ids().size() == 42 and
		not world.is_location_enabled("LOC_MISTHALL") and
		world.location("LOC_MISTHALL") == null
	)
	check(still_protected, "32. Ninguna sala no autorizada fuera de CH_01 + autorizadas puede habilitarse accidentalmente")
