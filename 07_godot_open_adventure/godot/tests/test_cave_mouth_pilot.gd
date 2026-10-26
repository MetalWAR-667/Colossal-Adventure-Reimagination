# CAR-CORE-002 / R5A: Cave Mouth Pilot (LOC_BELOWGRATE) integration suite.
#
# Validates the atomic enablement of LOC_BELOWGRATE from the StructuralCatalog,
# ensuring the player can unlock the grate, descend, view historical English
# descriptions, return, use BACK, while maintaining all inner exits blocked as
# frontiers, exactly 35 enabled rooms, and 0 regressions on CUT A-D.
extends SceneTree

const EXPECTED_CH01_SHA256 := "afa33c8898049c5af53d06cc3550edbd8f7d58792c819e6224286e82533438c9"
const EXPECTED_STRUCTURAL_SHA256 := "fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3"
const STRUCTURAL_PATH := "res://data/structural_world.json"
const CH01_DATASET_PATH := "res://data/chapter_01_surface.json"

var checks := 0
var failures := 0


func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL: " + label)


func _initialize() -> void:
	print("Running CAR-CORE-002 / R5A Cave Mouth Pilot tests...")

	_test_enablement_and_catalog()
	_test_navigation_and_grate_frontier()
	_test_isolation_and_objects()
	_test_contracts_and_immutability()
	_test_integrated_journey()

	if failures == 0:
		print("PASS: %d CAR-CORE-002 / R5A checks completed with 0 failures" % checks)
		quit(0)
	else:
		printerr("FAILED: %d failures out of %d checks" % [failures, checks])
		quit(1)


# ---------------------------------------------------------------------------
# 1. Habilitación y Catálogo (checks 1-9)
# ---------------------------------------------------------------------------
func _test_enablement_and_catalog() -> void:
	var world := WorldData.load_default()
	var catalog := world.structural_catalog

	# 1. Carga de las 185 ubicaciones estructurales
	check(catalog != null and catalog.get_location_ids().size() == 185,
		"1. Carga completa de las 185 ubicaciones estructurales en StructuralCatalog")

	# 2. Existencia estructural de LOC_BELOWGRATE
	check(world.has_structural_location("LOC_BELOWGRATE") and catalog.has_location("LOC_BELOWGRATE"),
		"2. Existencia de LOC_BELOWGRATE en el catálogo estructural")

	# 3. Habilitación funcional de LOC_BELOWGRATE
	check(world.is_location_enabled("LOC_BELOWGRATE") and world.location("LOC_BELOWGRATE") != null,
		"3. Habilitación funcional de LOC_BELOWGRATE en WorldData")

	# 4. Exactamente 41 ubicaciones habilitadas
	var enabled := world.get_enabled_location_ids()
	check(enabled.size() == 41 and world.locations.size() == 41,
		"4. Exactamente 41 ubicaciones habilitadas en la vista funcional")

	# 5. Exactamente 144 ubicaciones deshabilitadas
	var non_enabled := 0
	for lid in catalog.get_location_ids():
		if not world.is_location_enabled(lid):
			non_enabled += 1
	check(non_enabled == 144, "5. Exactamente 144 ubicaciones históricas permanecen deshabilitadas")

	# 6. Ausencia de habilitación accidental: 34 CH_SURFACE + autorizadas
	var ch_surface := catalog.get_chapter("CH_SURFACE")
	var surface_members: Array = ch_surface.get("members", [])
	var accidental := false
	for eid in enabled:
		if not WorldData.AUTHORIZED_ADDITIONAL_LOCATIONS.has(eid) and not surface_members.has(eid):
			accidental = true
			break
	check(not accidental, "6. Ausencia de habilitación accidental fuera de CH_SURFACE + autorizadas")

	# 7. Idempotencia de la habilitación
	var re_enable := world.enable_structural_location("LOC_BELOWGRATE")
	check(re_enable and world.locations.size() == 41 and world.get_enabled_location_ids().size() == 41,
		"7. Idempotencia de enable_structural_location('LOC_BELOWGRATE')")

	# 8. Rechazo de identificadores no autorizados o inválidos
	var reject_misthall := world.enable_structural_location("LOC_MISTHALL")
	var reject_fake := world.enable_structural_location("LOC_NONEXISTENT")
	check(not reject_misthall and not reject_fake and world.locations.size() == 41,
		"8. Rechazo explícito de salas no autorizadas (LOC_MISTHALL) o inválidas")

	# 9. Conservación del catálogo original (185 salas inalteradas)
	check(catalog.get_counts().get("locations", 0) == 185,
		"9. Conservación intacta del catálogo estructural global")


# ---------------------------------------------------------------------------
# 2. Navegación y Frontera de la Reja (checks 10-20)
# ---------------------------------------------------------------------------
func _test_navigation_and_grate_frontier() -> void:
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)

	# 10. Reja cerrada bloquea el descenso
	interpreter.state.current_location = "LOC_GRATE"
	interpreter.state.set_state("GRATE", "GRATE_CLOSED")
	var lines_closed := interpreter.submit("ENTER")
	check(interpreter.state.current_location == "LOC_GRATE" and
		(lines_closed.has(world.message("GRATE_NOWAY")) or "\n".join(lines_closed).contains("reja")),
		"10. Reja cerrada bloquea el descenso hacia LOC_BELOWGRATE")

	# 11. Reja abierta permite el descenso
	interpreter.state.set_state("GRATE", "GRATE_OPEN")
	var lines_enter := interpreter.submit("ENTER")
	check(interpreter.state.current_location == "LOC_BELOWGRATE",
		"11. Reja abierta permite el descenso por ENTER a LOC_BELOWGRATE")

	# 12. Descripción histórica visible (inglés histórico por fallback)
	var below := world.location("LOC_BELOWGRATE")
	check(below != null and not below.description_en.is_empty() and
		world.describe("LOC_BELOWGRATE").contains("steel grate") and
		world.describe_short("LOC_BELOWGRATE").contains("below the grate"),
		"12. Descripción histórica en inglés de LOC_BELOWGRATE accesible y fiel")

	# 13. Regreso con reja abierta por OUT
	var lines_out := interpreter.submit("OUT")
	check(interpreter.state.current_location == "LOC_GRATE",
		"13. Regreso exitoso desde LOC_BELOWGRATE hacia LOC_GRATE por OUT con reja abierta")

	# 14. Regreso bloqueado con reja cerrada desde abajo
	interpreter.state.current_location = "LOC_BELOWGRATE"
	interpreter.state.previous_location = "LOC_GRATE"
	interpreter.state.set_state("GRATE", "GRATE_CLOSED")
	var lines_ret_closed := interpreter.submit("OUT")
	check(interpreter.state.current_location == "LOC_BELOWGRATE" and
		(lines_ret_closed.has(world.message("GRATE_NOWAY")) or "\n".join(lines_ret_closed).contains("reja")),
		"14. Regreso bloqueado si la reja está cerrada desde abajo")

	# 15. BACK conserva su semántica histórica
	interpreter.state.set_state("GRATE", "GRATE_OPEN")
	interpreter.state.current_location = "LOC_GRATE"
	interpreter.state.previous_location = "LOC_START"
	interpreter.submit("ENTER") # llega a LOC_BELOWGRATE, previous_location pasa a LOC_GRATE
	check(interpreter.state.current_location == "LOC_BELOWGRATE", "Descenso a LOC_BELOWGRATE verificado")
	var lines_back := interpreter.submit("BACK")
	check(interpreter.state.current_location == "LOC_GRATE",
		"15. BACK desde LOC_BELOWGRATE regresa fielmente a LOC_GRATE")

	# 16. Salida hacia el interior habilitada en R5B
	interpreter.submit("DOWN") # vuelve a LOC_BELOWGRATE
	check(interpreter.state.current_location == "LOC_BELOWGRATE", "Vuelta a LOC_BELOWGRATE")
	interpreter.submit("WEST")
	var at_cobble: bool = (interpreter.state.current_location == "LOC_COBBLE")
	interpreter.submit("EAST")
	check(at_cobble and interpreter.state.current_location == "LOC_BELOWGRATE",
		"16. Salida WEST desde LOC_BELOWGRATE accede a LOC_COBBLE y retorno con EAST")

	# 17. Ubicación actual coherente
	check(interpreter.state.current_location == "LOC_BELOWGRATE",
		"17. Coherencia de GameState.current_location")

	# 18. Historial coherente
	check(not interpreter.state.previous_location.is_empty(),
		"18. Coherencia de historial en GameState")

	# 19. Turnos coherentes
	var turns_before := interpreter.state.turn
	interpreter.submit("LOOK")
	check(interpreter.state.turn == turns_before + 1, "19. Consumo coherente de turnos de juego")

	# 20. Sin rutas artificiales (5 reglas originales preservadas)
	var below_loc := world.location("LOC_BELOWGRATE")
	check(below_loc != null and below_loc.travel.size() == 5 and
		below_loc.travel[0].target == "LOC_GRATE" and
		below_loc.travel[1].target == "GRATE_NOWAY" and
		below_loc.travel[2].target == "LOC_COBBLE" and
		below_loc.travel[3].target == "LOC_PITTOP" and
		below_loc.travel[4].target == "LOC_DEBRIS",
		"20. Conservación exacta de las 5 reglas de viaje históricas de LOC_BELOWGRATE")


# ---------------------------------------------------------------------------
# 3. Aislamiento y Objetos (checks 21-30)
# ---------------------------------------------------------------------------
func _test_isolation_and_objects() -> void:
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)
	var parser := CommandParser.new(world)

	# 21. Ocho objetos funcionales
	check(world.objects.size() == 8, "21. Exactamente 8 objetos funcionales en WorldData.objects")

	# 22. Parser sin vocabulario global no autorizado
	var cmd_chest := parser.parse("TAKE CHEST")
	var cmd_nugget := parser.parse("TAKE NUGGET")
	check(not world.objects.has("CHEST") and not world.objects.has("NUGGET") and
		cmd_chest.action == "CARRY" and cmd_nugget.action == "CARRY",
		"22. El parser no incorpora objetos de capítulos posteriores en world.objects")

	# 23. RNG no alterado por habilitación
	var rng_init := interpreter.rng.state
	world.enable_structural_location("LOC_BELOWGRATE")
	check(interpreter.rng.state == rng_init, "23. Habilitación estructural no consume números de RNG")

	# 24. Sin actores activos
	check(world.get_structural_dwarflocs().size() == 6 and not world.objects.has("DWARF"),
		"24. Actores enanos inactivos en runtime")

	# 25. Sin puzles nuevos incorporados
	check(not world.objects.has("TROLL") and not world.objects.has("SNAKE") and not world.objects.has("PLANT"),
		"25. Puzles de capítulos 02-11 ausentes de runtime")

	# 26. Sin cambios en lámpara
	check(interpreter.state.lamp_energy == 330 and interpreter.state.state_of("LAMP") == "LAMP_DARK",
		"26. Integridad del ciclo de linterna CUT C")

	# 27. Sin cambios en oscuridad (LOC_BELOWGRATE tiene LIT=true)
	var below := world.location("LOC_BELOWGRATE")
	check(below != null and below.has_condition("LIT") and below.conditions.get("LIT", false) == true,
		"27. LOC_BELOWGRATE posee iluminación natural (LIT=true)")

	# 28. Sin cambios en ciclo de muerte
	check(interpreter.state.death_count == 0 and world.num_deaths == 3,
		"28. Preservación del subsistema de muertes CUT D")

	# 29. Sin cambios en reencarnación
	check(world.obituaries.size() == 3, "29. Preservación de obituarios históricos CUT D")

	# 30. Sin cambios en ilustraciones de CH_01
	check(world.art.has("scenes") and world.art["scenes"].has("LOC_START") and world.art["scenes"].has("LOC_GRATE"),
		"30. Preservación del subsistema de arte vectorial CH_01")


# ---------------------------------------------------------------------------
# 4. Contratos y Defensas (checks 31-36)
# ---------------------------------------------------------------------------
func _test_contracts_and_immutability() -> void:
	var world := WorldData.load_default()

	# 31. SHA-256 de chapter_01_surface.json
	var ch01_sha256 := FileAccess.get_sha256(CH01_DATASET_PATH)
	check(ch01_sha256 == EXPECTED_CH01_SHA256,
		"31. Preservación íntegra del SHA-256 de chapter_01_surface.json (%s)" % EXPECTED_CH01_SHA256)

	# 32. SHA-256 de structural_world.json
	var struct_bytes := FileAccess.get_file_as_bytes(STRUCTURAL_PATH)
	var struct_sha256 := ""
	if not struct_bytes.is_empty():
		var ctx := HashingContext.new()
		ctx.start(HashingContext.HASH_SHA256)
		ctx.update(struct_bytes)
		struct_sha256 = ctx.finish().hex_encode()
	check(struct_sha256 == EXPECTED_STRUCTURAL_SHA256,
		"32. Preservación íntegra del SHA-256 de structural_world.json (%s)" % EXPECTED_STRUCTURAL_SHA256)

	# 33. Determinismo del catálogo estructural
	check(world.structural_catalog.is_loaded() and world.get_structural_location_ids().size() == 185,
		"33. Integridad y determinismo del catálogo estructural v1")

	# 34. Integridad de contratos CUT A-D
	var cut_a_ok := (world.objects.size() == 8 and world.classes.size() >= 10)
	check(cut_a_ok, "34. Integridad de los contratos históricos CUT A-D")

	# 35. Copias defensivas del catálogo estructural
	var struct_loc := world.get_structural_location("LOC_BELOWGRATE")
	struct_loc["corrupt_key"] = "leak"
	var struct_loc_clean := world.get_structural_location("LOC_BELOWGRATE")
	check(not struct_loc_clean.has("corrupt_key"),
		"35. Copias defensivas profundas previenen mutaciones del catálogo estructural")

	# 36. Fallo explícito ante datos inválidos
	check(world.enable_structural_location("NON_EXISTENT") == false and
		world.location("NON_EXISTENT") == null,
		"36. Fallo explícito y fail-closed ante solicitudes de salas inválidas")


# ---------------------------------------------------------------------------
# 5. Recorrido Integrado Legítimo (inicio -> llaves -> reja -> descenso -> regreso)
# ---------------------------------------------------------------------------
func _test_integrated_journey() -> void:
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)

	# Inicio legítimo en LOC_START
	check(interpreter.state.current_location == "LOC_START", "Inicio legítimo en LOC_START")

	# Ir a BUILDING y tomar llaves
	interpreter.submit("BUILDING")
	check(interpreter.state.current_location == "LOC_BUILDING", "Entra al edificio")
	var take_out := interpreter.submit("TAKE KEYS")
	check(interpreter.state.is_carried("KEYS"), "Recoge las llaves legítimamente")

	# Salir e ir a la reja
	interpreter.submit("OUT")
	interpreter.submit("DEPRESSION")
	check(interpreter.state.current_location == "LOC_GRATE", "Llega a la reja exterior")

	# Probar entrar con reja cerrada
	var enter_locked := interpreter.submit("ENTER")
	check(interpreter.state.current_location == "LOC_GRATE", "La reja cerrada bloquea el paso")

	# Abrir reja con llaves
	var unlock_out := interpreter.submit("UNLOCK GRATE")
	check(interpreter.state.state_of("GRATE") == "GRATE_OPEN", "Reja abierta con las llaves")

	# Descender a la cueva
	var enter_open := interpreter.submit("ENTER")
	check(interpreter.state.current_location == "LOC_BELOWGRATE", "Descenso legítimo a LOC_BELOWGRATE")
	check("\n".join(enter_open).to_lower().contains("below the grate"), "Visualización de la descripción histórica breve en inglés")
	var look_out := interpreter.submit("LOOK")
	check("\n".join(look_out).to_lower().contains("steel grate"), "LOOK muestra la descripción histórica completa en inglés")

	# Regresar con BACK a la superficie inmediatamente (preservando historial sin movimientos fallidos intermedios)
	var back_out := interpreter.submit("BACK")
	check(interpreter.state.current_location == "LOC_GRATE", "Regreso legítimo a LOC_GRATE mediante BACK")

	# Volver a descender con DOWN
	var down_out := interpreter.submit("DOWN")
	check(interpreter.state.current_location == "LOC_BELOWGRATE", "Segundo descenso mediante DOWN")

	# Probar avanzar hacia el interior de la cueva (LOC_COBBLE habilitada en R5B)
	var try_west := interpreter.submit("WEST")
	check(interpreter.state.current_location == "LOC_COBBLE",
		"Avanzar al interior accede a LOC_COBBLE")

	# Regresar a LOC_BELOWGRATE y salir con OUT
	interpreter.submit("EAST")
	var out_out := interpreter.submit("OUT")
	check(interpreter.state.current_location == "LOC_GRATE", "Salida legítima mediante OUT")
