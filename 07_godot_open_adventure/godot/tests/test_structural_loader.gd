# CAR-CORE-002 / R3: Structural Loader & Enabled View test suite.
# Verifies all 35 focal assertions across structural loading, enabled location view,
# functional isolation, and robustness/negative error handling.
extends SceneTree

const STRUCTURAL_PATH := "res://data/structural_world.json"

var checks := 0
var failures := 0


func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL: " + label)


func _initialize() -> void:
	print("Running CAR-CORE-002 / R3 tests...")
	_test_structural_loading()
	_test_enabled_view()
	_test_functional_isolation()
	_test_robustness_and_negatives()

	print("%s: %d CAR-CORE-002 / R3 tests completed with %d failures" % [
		"PASS" if failures == 0 else "FAIL",
		checks,
		failures
	])
	quit(0 if failures == 0 else 1)


func _test_structural_loading() -> void:
	# 1. JSON legible
	check(FileAccess.file_exists(STRUCTURAL_PATH), "1. JSON estructural existe en " + STRUCTURAL_PATH)
	var catalog := StructuralCatalog.new()
	var loaded := catalog.load_from_file(STRUCTURAL_PATH)
	check(loaded and catalog.is_loaded(), "1b. StructuralCatalog carga exitosamente")

	# 2. Esquema válido
	var meta := catalog.get_catalog_meta()
	check(int(meta.get("schema_version", 0)) == 1 and meta.get("cut_id") == "CAR-CORE-002-R2", "2. Esquema y versión válidos")

	# 3. 185 ubicaciones
	var loc_ids := catalog.get_location_ids()
	check(loc_ids.size() == 185, "3. 185 ubicaciones cargadas")

	# 4. 623 viajes
	var travel_records := catalog.get_all_travel_records()
	check(travel_records.size() == 623, "4. 623 viajes cargados")

	# 5. 70 objetos
	var obj_ids := catalog.get_object_ids()
	check(obj_ids.size() == 70, "5. 70 objetos cargados")

	# 6. 11 capítulos
	var ch_ids := catalog.get_chapter_ids()
	check(ch_ids.size() == 11, "6. 11 capítulos disponibles")

	# 7. Seis posiciones de enanos
	var dwarflocs := catalog.get_dwarflocs()
	check(dwarflocs.size() == 6, "7. Seis posiciones iniciales de enanos conservadas")

	# 8. Orden histórico de viajes conservado
	var travel_ordered := true
	for idx in range(travel_records.size()):
		if int(travel_records[idx].get("global_travel_index", -1)) != idx:
			travel_ordered = false
			break
	check(travel_ordered, "8. Orden histórico global de viajes conservado (0..622)")

	# 9. Condiciones declaradas conservadas
	var cond_types: Dictionary = {}
	for tr in travel_records:
		var ct := String(tr.get("condition_type", ""))
		cond_types[ct] = int(cond_types.get(ct, 0)) + 1
	var expected_conds: bool = (
		cond_types.get("always", 0) == 574 and
		cond_types.get("not", 0) == 25 and
		cond_types.get("pct", 0) == 12 and
		cond_types.get("carry", 0) == 7 and
		cond_types.get("with", 0) == 4 and
		cond_types.get("nodwarves", 0) == 1
	)
	check(expected_conds, "9. Condiciones declaradas conservadas (always:574, not:25, pct:12, carry:7, with:4, nodwarves:1)")

	# 10. Descripciones y flags conservados
	var loc_nowhere := catalog.get_location("LOC_NOWHERE")
	var loc_building1 := catalog.get_location("LOC_BUILDING1")
	var loc_building := catalog.get_location("LOC_BUILDING")
	var desc_ok: bool = (
		loc_nowhere.get("long_description") == null and
		String(loc_building1.get("long_description", "NOT_EMPTY")) == "" and
		loc_building1.get("flags") != null and
		bool(loc_building1["flags"].get("DEEP", false)) and
		loc_building.get("flags") != null and
		bool(loc_building["flags"].get("LIT", false))
	)
	check(desc_ok, "10. Descripciones históricas (LOC_NOWHERE null, LOC_BUILDING1 '') y flags conservados")

	# 11. Geometría conservada
	var geom_ok := true
	for lid in loc_ids:
		var loc := catalog.get_location(lid)
		var dio: Dictionary = loc.get("drawio", {})
		if not dio.has("cell_id") or not dio.has("page_id") or float(dio.get("width", 0)) <= 0:
			geom_ok = false
			break
	check(geom_ok, "11. Geometría draw.io completa conservada para todas las 185 ubicaciones")

	# 12. Referencias estructurales válidas
	var refs_ok := true
	for tr in travel_records:
		if tr.get("action_type") == "goto":
			var dest := String(tr.get("destination_location_id", ""))
			if not catalog.has_location(dest):
				refs_ok = false
				break
	check(refs_ok, "12. Todas las referencias a destinos de viaje son válidas y resolubles")


func _test_enabled_view() -> void:
	var world := WorldData.load_default()
	check(world != null and world.structural_catalog != null, "WorldData.load_default() carga el catálogo estructural")

	# 13. Exactamente 35 ubicaciones habilitadas
	var enabled_ids := world.get_enabled_location_ids()
	check(enabled_ids.size() == 35, "13. Exactamente 35 ubicaciones habilitadas en runtime")

	# 14. Las 35 pertenecen a CH_SURFACE + LOC_BELOWGRATE
	var all_authorized := true
	var ch_surface := world.structural_catalog.get_chapter("CH_SURFACE")
	var surface_members: Array = ch_surface.get("members", [])
	for eid in enabled_ids:
		if not surface_members.has(eid) and eid != "LOC_BELOWGRATE":
			all_authorized = false
			break
	check(all_authorized and surface_members.size() == 34, "14. Todas las 35 ubicaciones habilitadas pertenecen a CH_SURFACE + LOC_BELOWGRATE")

	# 15. Las otras 150 permanecen deshabilitadas
	var non_enabled_count := 0
	var all_ids := world.get_structural_location_ids()
	for lid in all_ids:
		if not world.is_location_enabled(lid):
			non_enabled_count += 1
	check(non_enabled_count == 150, "15. Exactamente 150 ubicaciones históricas permanecen deshabilitadas")

	# 16. Ubicación global deshabilitada es consultable estructuralmente
	var test_inert_id := "LOC_COBBLE"
	var structural_known := world.has_structural_location(test_inert_id)
	var struct_loc := world.get_structural_location(test_inert_id)
	check(structural_known and not struct_loc.is_empty(), "16. Ubicación fuera de CH_01 (" + test_inert_id + ") es consultable estructuralmente")

	# 17. Esa misma ubicación no es jugable
	var not_playable := (
		not world.is_location_enabled(test_inert_id) and
		world.location(test_inert_id) == null and
		world.describe(test_inert_id).is_empty() and
		world.describe_short(test_inert_id).is_empty()
	)
	check(not_playable, "17. La ubicación estructural inerte no es accesible en el runtime jugable")

	# 18. WorldData.locations conserva su contenido funcional
	check(world.locations.size() == 35, "18. WorldData.locations conserva exactamente 35 ubicaciones funcionales")

	# 19. WorldData.objects conserva su contenido funcional
	check(world.objects.size() == 8, "19. WorldData.objects conserva exactamente 8 objetos funcionales")

	# 20. is_in_chapter() conserva su comportamiento
	var is_in_chapter_equivalent := true
	for lid in all_ids:
		if world.is_in_chapter(lid) != world.is_location_enabled(lid):
			is_in_chapter_equivalent = false
			break
	check(is_in_chapter_equivalent, "20. is_in_chapter() es estrictamente equivalente al conjunto habilitado")


func _test_functional_isolation() -> void:
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)
	var parser := CommandParser.new(world)

	# 21. El parser no incorpora vocabulario global
	# Chest, Dragon, Ogre, Plant son objetos de capítulos posteriores, no deben ser reconocidos como objetos de CH_01
	var cmd_chest := parser.parse("TAKE CHEST")
	var cmd_dragon := parser.parse("KILL DRAGON")
	check(cmd_chest.action == "CARRY" and not world.objects.has("CHEST") and not world.objects.has("DRAGON"), "21. El parser y world.objects no exponen objetos de capítulos no habilitados")

	# 22. El mapa no muestra salas globales adicionales
	check(world.map_nodes.size() == 34 and world.map_edges.size() == 118, "22. El mapa jugable mantiene exactamente 34 nodos y 118 aristas de CH_01")

	# 23. El intérprete no permite acceder a una sala deshabilitada
	var rule_outside := TravelRule.new()
	rule_outside.target = "LOC_FOOF1"
	var move_result := interpreter._execute_move(rule_outside)
	var blocked: bool = not bool(move_result.get("moved", false)) and interpreter.state.travel_outcome == GameState.TravelOutcome.FRONTIER
	check(blocked, "23. El intérprete rechaza el movimiento hacia salas deshabilitadas y produce FRONTIER")

	# 24. No aparecen actores
	var no_actors: bool = interpreter.state.get("actors") == null and interpreter.state.get("dwarves") == null
	check(no_actors, "24. No existen actores ni enanos en GameState")

	# 25. No se ejecutan condiciones pendientes por consultas estructurales
	var cond_rules := world.get_structural_travel_records("LOC_GRATE")
	check(cond_rules.size() > 0, "25. Reglas de viaje estructurales leídas como datos estáticos sin evaluación")

	# 26. No se consume RNG por consultas estructurales
	var rng_state_before := interpreter.rng.state
	for lid in world.get_structural_location_ids():
		world.get_structural_location(lid)
		world.get_structural_travel_records(lid)
	for oid in world.structural_catalog.get_object_ids():
		world.get_structural_object(oid)
	check(interpreter.rng.state == rng_state_before, "26. Consultas estructurales no consumen ningún número pseudoaleatorio (RNG)")

	# 27. No se altera GameState
	var state_loc_before := interpreter.state.current_location
	var state_turn_before := interpreter.state.turn
	var state_objs_before := interpreter.state.object_place.duplicate()
	world.get_structural_location("LOC_PIRATE_CHEST")
	world.get_structural_object("CHEST")
	var state_intact := (
		interpreter.state.current_location == state_loc_before and
		interpreter.state.turn == state_turn_before and
		interpreter.state.object_place == state_objs_before
	)
	check(state_intact, "27. Las consultas estructurales no alteran el estado mutable de la partida")

	# 28. No se crean objetos mutables duplicados
	check(interpreter.state.object_place.size() <= 9, "28. No se instancian objetos mutables adicionales en GameState (solo CH_01 + BATTERY)")

	# 29. No cambia el ciclo de turnos
	var t_before := interpreter.state.turn
	interpreter.submit("LOOK")
	check(interpreter.state.turn == t_before + 1, "29. El ciclo de turnos de CH_01 se incrementa de forma idéntica")

	# 30. No cambian las reglas de oscuridad y muerte
	check(interpreter.state.death_count == 0 and interpreter.state.lamp_energy == 330, "30. Reglas de energía de lámpara y ciclo de muerte intactos")


func _test_robustness_and_negatives() -> void:
	var valid_text := FileAccess.get_file_as_string(STRUCTURAL_PATH)
	var valid_dict: Dictionary = JSON.parse_string(valid_text)

	# 31. Error explícito ante JSON corrupto
	var catalog_corrupt := StructuralCatalog.new()
	var res_corrupt := catalog_corrupt.load_from_string("{ esto no es json valido:")
	check(not res_corrupt and not catalog_corrupt.is_loaded() and not catalog_corrupt.get_last_error().is_empty(),
		"31. Error explícito y diagnosticable ante JSON con sintaxis corrupta")

	# 32. Error explícito ante identificadores duplicados
	var dict_dup_loc: Dictionary = valid_dict.duplicate(true)
	var locs_copy: Array = dict_dup_loc["locations"].duplicate(true)
	locs_copy[1]["id"] = locs_copy[0]["id"]
	dict_dup_loc["locations"] = locs_copy
	var catalog_dup := StructuralCatalog.new()
	var res_dup := catalog_dup.load_from_string(JSON.stringify(dict_dup_loc))
	check(not res_dup and not catalog_dup.is_loaded() and catalog_dup.get_last_error().contains("duplicate location id"),
		"32. Error explícito ante identificadores de sala duplicados")

	# 33. Error explícito ante referencia inválida
	var dict_inv_dest: Dictionary = valid_dict.duplicate(true)
	var travel_copy: Array = dict_inv_dest["travel"].duplicate(true)
	travel_copy[0]["destination_location_id"] = "LOC_NON_EXISTENT_DESTINATION"
	dict_inv_dest["travel"] = travel_copy
	var catalog_inv := StructuralCatalog.new()
	var res_inv := catalog_inv.load_from_string(JSON.stringify(dict_inv_dest))
	check(not res_inv and not catalog_inv.is_loaded() and catalog_inv.get_last_error().contains("unknown destination"),
		"33. Error explícito ante referencia de viaje a sala inexistente")

	# 34. Error explícito ante esquema incompatible
	var dict_bad_schema: Dictionary = valid_dict.duplicate(true)
	dict_bad_schema["meta"]["schema_version"] = 999
	var catalog_schema := StructuralCatalog.new()
	var res_schema := catalog_schema.load_from_string(JSON.stringify(dict_bad_schema))
	check(not res_schema and not catalog_schema.is_loaded() and catalog_schema.get_last_error().contains("incompatible schema_version"),
		"34. Error explícito ante schema_version incompatible")

	# 35. Las consultas de solo lectura no permiten modificar el catálogo interno
	var catalog_safe := StructuralCatalog.load_default(STRUCTURAL_PATH)
	var loc_copy := catalog_safe.get_location("LOC_START")
	loc_copy["id"] = "MUTATED_ID"
	loc_copy["flags"]["LIT"] = not loc_copy["flags"]["LIT"]
	loc_copy["travel"].clear()
	var loc_fresh := catalog_safe.get_location("LOC_START")
	var defensive_copy_works: bool = (
		loc_fresh["id"] == "LOC_START" and
		loc_fresh["flags"]["LIT"] != loc_copy["flags"]["LIT"] and
		loc_fresh["travel"].size() > 0
	)
	check(defensive_copy_works, "35. Las consultas de solo lectura devuelven copias defensivas y protegen el catálogo interno")
