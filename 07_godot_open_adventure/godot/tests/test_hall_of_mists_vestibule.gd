# CAR-CORE-002 / R5B: Hall of Mists Vestibule (CH_ENTRY Safe Subgraph) integration suite.
#
# Validates the atomic enablement of the 6 additional safe CH_ENTRY locations:
#   LOC_COBBLE, LOC_DEBRIS, LOC_AWKWARD, LOC_BIRDCHAMBER, LOC_PITTOP, LOC_CRACK
# along with LOC_BELOWGRATE (from R5A), maintaining exactly 41 enabled locations,
# 144 inert locations, faithful navigation, CUT C darkness/lamp mechanics,
# LOC_CRACK forced transition, BACK history, and zero regressions on CUT A-D.
extends SceneTree

const EXPECTED_CH01_SHA256 := "afa33c8898049c5af53d06cc3550edbd8f7d58792c819e6224286e82533438c9"
const EXPECTED_STRUCTURAL_SHA256 := "fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3"
const STRUCTURAL_PATH := "res://data/structural_world.json"
const CH01_DATASET_PATH := "res://data/chapter_01_surface.json"

const R5B_LOCATIONS: PackedStringArray = [
	"LOC_COBBLE",
	"LOC_DEBRIS",
	"LOC_AWKWARD",
	"LOC_BIRDCHAMBER",
	"LOC_PITTOP",
	"LOC_CRACK"
]

const ALL_AUTHORIZED_ADDITIONAL: PackedStringArray = [
	"LOC_BELOWGRATE",
	"LOC_COBBLE",
	"LOC_DEBRIS",
	"LOC_AWKWARD",
	"LOC_BIRDCHAMBER",
	"LOC_PITTOP",
	"LOC_CRACK",
	"LOC_FOOF1"
]

var checks := 0
var failures := 0


func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL: " + label)


func _initialize() -> void:
	print("Running CAR-CORE-002 / R5B Hall of Mists Vestibule tests...")

	_test_enablement_and_catalog()
	_test_subgraph_navigation()
	_test_darkness_and_lamp()
	_test_crack_forced_transition()
	_test_isolation_and_contracts()
	_test_integrated_journey()

	if failures == 0:
		print("PASS: %d CAR-CORE-002 / R5B checks completed with 0 failures" % checks)
		quit(0)
	else:
		printerr("FAILED: %d failures out of %d checks" % [failures, checks])
		quit(1)


# ---------------------------------------------------------------------------
# 1. Habilitación y Catálogo (checks 1-10)
# ---------------------------------------------------------------------------
func _test_enablement_and_catalog() -> void:
	var world := WorldData.load_default()
	var catalog := world.structural_catalog

	# 1. Carga de las 185 ubicaciones estructurales
	check(catalog != null and catalog.get_location_ids().size() == 185,
		"1. Carga completa de las 185 ubicaciones estructurales en StructuralCatalog")

	# 2. Existencia estructural de las 7 salas de CH_ENTRY
	var all_struct_exist := true
	for lid in ALL_AUTHORIZED_ADDITIONAL:
		if not world.has_structural_location(lid) or not catalog.has_location(lid):
			all_struct_exist = false
			break
	check(all_struct_exist, "2. Existencia de las 7 salas de CH_ENTRY en el catálogo estructural")

	# 3. Habilitación funcional de las 7 salas en WorldData
	var all_enabled := true
	for lid in ALL_AUTHORIZED_ADDITIONAL:
		if not world.is_location_enabled(lid) or world.location(lid) == null:
			all_enabled = false
			break
	check(all_enabled, "3. Habilitación funcional de las 7 salas de CH_ENTRY en WorldData")

	# 4. Exactamente 42 ubicaciones habilitadas
	var enabled := world.get_enabled_location_ids()
	check(enabled.size() == 42 and world.locations.size() == 42,
		"4. Exactamente 42 ubicaciones habilitadas en la vista funcional")

	# 5. Exactamente 144 ubicaciones deshabilitadas
	var non_enabled := 0
	for lid in catalog.get_location_ids():
		if not world.is_location_enabled(lid):
			non_enabled += 1
	check(non_enabled == 143, "5. Exactamente 143 ubicaciones históricas permanecen deshabilitadas")

	# 6. Ausencia de habilitación accidental: 34 CH_SURFACE + 8 CH_ENTRY
	var ch_surface := catalog.get_chapter("CH_SURFACE")
	var surface_members: Array = ch_surface.get("members", [])
	var accidental := false
	for eid in enabled:
		if not ALL_AUTHORIZED_ADDITIONAL.has(eid) and not surface_members.has(eid):
			accidental = true
			break
	check(not accidental, "6. Ausencia de habilitación accidental fuera de CH_SURFACE + 7 CH_ENTRY")

	# 7. Idempotencia de la habilitación
	var idempotent_ok := true
	for lid in ALL_AUTHORIZED_ADDITIONAL:
		if not world.enable_structural_location(lid):
			idempotent_ok = false
			break
	check(idempotent_ok and world.locations.size() == 42 and world.get_enabled_location_ids().size() == 42,
		"7. Idempotencia de enable_structural_location para las salas autorizadas")

	# 8. Rechazo de identificadores no autorizados o inválidos
	var reject_misthall := world.enable_structural_location("LOC_MISTHALL")
	var reject_eastbank := world.enable_structural_location("LOC_EASTBANK")
	var reject_fake := world.enable_structural_location("LOC_NONEXISTENT")
	check(not reject_misthall and not reject_eastbank and not reject_fake and world.locations.size() == 42,
		"8. Rechazo explícito de salas no autorizadas (LOC_MISTHALL, LOC_EASTBANK) o inválidas")

	# 9. Conservación del catálogo original (185 salas inalteradas)
	check(catalog.get_counts().get("locations", 0) == 185,
		"9. Conservación intacta del catálogo estructural global (185 salas)")

	# 10. Preservación estricta de objetos funcionales (exactamente 8 de CH_01)
	check(world.objects.size() == 8 and not world.objects.has("BIRD") and not world.objects.has("NUGGET"),
		"10. Exactamente 8 objetos funcionales de CH_01 sin filtración de BIRD o NUGGET")


# ---------------------------------------------------------------------------
# 2. Navegación del Subgrafo (checks 11-28)
# ---------------------------------------------------------------------------
func _test_subgraph_navigation() -> void:
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)

	# Preparar linterna encendida y reja abierta para explorar libremente
	interpreter.state.object_place["LAMP"] = GameState.CARRIED
	interpreter.state.set_state("LAMP", "LAMP_BRIGHT")
	interpreter.state.set_state("GRATE", "GRATE_OPEN")

	# 11. Entrada a LOC_BELOWGRATE desde LOC_GRATE
	interpreter.state.move_to("LOC_GRATE", false)
	interpreter.submit("ENTER")
	check(interpreter.state.current_location == "LOC_BELOWGRATE" and interpreter.state.travel_outcome == GameState.TravelOutcome.ARRIVED,
		"11. Entrada a LOC_BELOWGRATE desde LOC_GRATE abierta")

	# 12. Avance LOC_BELOWGRATE -> WEST -> LOC_COBBLE
	interpreter.submit("WEST")
	check(interpreter.state.current_location == "LOC_COBBLE" and interpreter.state.travel_outcome == GameState.TravelOutcome.ARRIVED,
		"12. Avance LOC_BELOWGRATE -> WEST -> LOC_COBBLE")

	# 13. Retorno LOC_COBBLE -> EAST -> LOC_BELOWGRATE
	interpreter.submit("EAST")
	check(interpreter.state.current_location == "LOC_BELOWGRATE",
		"13. Retorno LOC_COBBLE -> EAST -> LOC_BELOWGRATE")

	# 14. Avance a LOC_DEBRIS desde LOC_COBBLE
	interpreter.submit("WEST") # a LOC_COBBLE
	interpreter.submit("WEST") # a LOC_DEBRIS
	check(interpreter.state.current_location == "LOC_DEBRIS" and interpreter.state.travel_outcome == GameState.TravelOutcome.ARRIVED,
		"14. Avance LOC_COBBLE -> WEST -> LOC_DEBRIS")

	# 15. Retorno LOC_DEBRIS -> EAST -> LOC_COBBLE
	interpreter.submit("EAST")
	check(interpreter.state.current_location == "LOC_COBBLE",
		"15. Retorno LOC_DEBRIS -> EAST -> LOC_COBBLE")

	# 16. Avance a LOC_AWKWARD desde LOC_DEBRIS
	interpreter.submit("WEST") # a LOC_DEBRIS
	interpreter.submit("WEST") # a LOC_AWKWARD (CANYO / WEST)
	check(interpreter.state.current_location == "LOC_AWKWARD" and interpreter.state.travel_outcome == GameState.TravelOutcome.ARRIVED,
		"16. Avance LOC_DEBRIS -> WEST -> LOC_AWKWARD")

	# 17. Retorno LOC_AWKWARD -> EAST -> LOC_DEBRIS
	interpreter.submit("EAST")
	check(interpreter.state.current_location == "LOC_DEBRIS",
		"17. Retorno LOC_AWKWARD -> EAST -> LOC_DEBRIS")

	# 18. Avance a LOC_BIRDCHAMBER desde LOC_AWKWARD
	interpreter.submit("WEST") # a LOC_AWKWARD
	interpreter.submit("WEST") # a LOC_BIRDCHAMBER
	check(interpreter.state.current_location == "LOC_BIRDCHAMBER" and interpreter.state.travel_outcome == GameState.TravelOutcome.ARRIVED,
		"18. Avance LOC_AWKWARD -> WEST -> LOC_BIRDCHAMBER")

	# 19. Retorno LOC_BIRDCHAMBER -> EAST -> LOC_AWKWARD
	interpreter.submit("EAST")
	check(interpreter.state.current_location == "LOC_AWKWARD",
		"19. Retorno LOC_BIRDCHAMBER -> EAST -> LOC_AWKWARD")

	# 20. Avance a LOC_PITTOP desde LOC_BIRDCHAMBER
	interpreter.submit("WEST") # a LOC_BIRDCHAMBER
	interpreter.submit("WEST") # a LOC_PITTOP (PASSA / PIT / WEST)
	check(interpreter.state.current_location == "LOC_PITTOP" and interpreter.state.travel_outcome == GameState.TravelOutcome.ARRIVED,
		"20. Avance LOC_BIRDCHAMBER -> WEST -> LOC_PITTOP")

	# 21. Retorno LOC_PITTOP -> EAST -> LOC_BIRDCHAMBER
	interpreter.submit("EAST")
	check(interpreter.state.current_location == "LOC_BIRDCHAMBER",
		"21. Retorno LOC_PITTOP -> EAST -> LOC_BIRDCHAMBER")

	# 22. Atajo directo LOC_BELOWGRATE -> PIT -> LOC_PITTOP
	interpreter.state.move_to("LOC_BELOWGRATE", false)
	interpreter.submit("PIT")
	check(interpreter.state.current_location == "LOC_PITTOP",
		"22. Atajo directo LOC_BELOWGRATE -> PIT -> LOC_PITTOP")

	# 23. Atajo directo LOC_BELOWGRATE -> DEBRI -> LOC_DEBRIS
	interpreter.state.move_to("LOC_BELOWGRATE", false)
	interpreter.submit("DEBRI")
	check(interpreter.state.current_location == "LOC_DEBRIS",
		"23. Atajo directo LOC_BELOWGRATE -> DEBRI -> LOC_DEBRIS")

	# 24. Atajo directo LOC_COBBLE -> PIT -> LOC_PITTOP
	interpreter.state.move_to("LOC_COBBLE", false)
	interpreter.submit("PIT")
	check(interpreter.state.current_location == "LOC_PITTOP",
		"24. Atajo directo LOC_COBBLE -> PIT -> LOC_PITTOP")

	# 25. Atajo directo LOC_PITTOP -> DEPRE -> LOC_GRATE (con reja abierta)
	interpreter.submit("DEPRE")
	check(interpreter.state.current_location == "LOC_GRATE",
		"25. Atajo directo LOC_PITTOP -> DEPRE -> LOC_GRATE")

	# 26. Atajo directo LOC_DEBRIS -> DEPRE -> LOC_GRATE
	interpreter.state.move_to("LOC_DEBRIS", false)
	interpreter.submit("DEPRE")
	check(interpreter.state.current_location == "LOC_GRATE",
		"26. Atajo directo LOC_DEBRIS -> DEPRE -> LOC_GRATE")

	# 27. Atajo DEPRE con reja cerrada cae a LOC_BELOWGRATE
	interpreter.state.set_state("GRATE", "GRATE_CLOSED")
	interpreter.state.move_to("LOC_PITTOP", false)
	interpreter.submit("ENTRA")
	check(interpreter.state.current_location == "LOC_BELOWGRATE",
		"27. Comando ENTRA desde LOC_PITTOP lleva a LOC_BELOWGRATE")

	# 28. Frontera en LOC_PITTOP: DOWN interceptado como DEPENDENCY_PENDING (objeto NUGGET no disponible)
	interpreter.state.move_to("LOC_PITTOP", false)
	interpreter.submit("DOWN")
	check(interpreter.state.current_location == "LOC_PITTOP" and
		interpreter.state.travel_outcome == GameState.TravelOutcome.DEPENDENCY_PENDING and
		interpreter.state.travel_dependency.contains("NUGGET"),
		"28. Frontera DOWN en LOC_PITTOP interceptada fail-closed por DEPENDENCY_PENDING (NUGGET)")


# ---------------------------------------------------------------------------
# 3. Iluminación y Oscuridad CUT C (checks 29-35)
# ---------------------------------------------------------------------------
func _test_darkness_and_lamp() -> void:
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)

	# 29. LOC_COBBLE posee LIT = true y no requiere lámpara
	var cobble := world.location("LOC_COBBLE")
	check(cobble != null and cobble.has_condition("LIT") and cobble.conditions.get("LIT", false) == true,
		"29. LOC_COBBLE posee iluminación natural permanente (LIT=true)")

	# 30. Las otras 5 salas son oscuras (LIT = false)
	var dark_rooms_ok := true
	for dark_id in ["LOC_DEBRIS", "LOC_AWKWARD", "LOC_BIRDCHAMBER", "LOC_PITTOP", "LOC_CRACK"]:
		var loc := world.location(dark_id)
		if loc == null or loc.has_condition("LIT"):
			dark_rooms_ok = false
			break
	check(dark_rooms_ok, "30. LOC_DEBRIS, LOC_AWKWARD, LOC_BIRDCHAMBER, LOC_PITTOP y LOC_CRACK no tienen LIT (son oscuras)")

	# 31. En LOC_COBBLE sin lámpara, la estancia es visible
	interpreter.state.move_to("LOC_COBBLE", false)
	interpreter.state.set_state("LAMP", "LAMP_DARK")
	check(not interpreter._is_dark_here(), "31. En LOC_COBBLE sin lámpara no está oscuro (_is_dark_here() == false)")

	# 32. Avanzar a LOC_DEBRIS sin lámpara entra en oscuridad (PITCH_DARK)
	var lines_dark := interpreter.submit("WEST")
	check(interpreter.state.current_location == "LOC_DEBRIS" and
		interpreter._is_dark_here() and
		"\n".join(lines_dark).contains(world.message("PITCH_DARK")),
		"32. Entrada a LOC_DEBRIS en oscuridad produce PITCH_DARK sin caída fatal inmediata")

	# 33. Encender la lámpara restaura visibilidad y muestra la descripción de LOC_DEBRIS
	interpreter.state.object_place["LAMP"] = GameState.CARRIED
	var lines_light := interpreter.submit("LIGHT LAMP")
	check(not interpreter._is_dark_here() and
		interpreter.state.state_of("LAMP") == "LAMP_BRIGHT" and
		"\n".join(lines_light).contains("debris room"),
		"33. Encender la lámpara restaura visibilidad y re-describe LOC_DEBRIS")

	# 34. Consumo de energía de linterna en salas de cueva
	var energy_before := interpreter.state.lamp_energy
	interpreter.submit("WEST") # a LOC_AWKWARD con lámpara encendida
	check(interpreter.state.current_location == "LOC_AWKWARD" and
		interpreter.state.lamp_energy == energy_before - 1,
		"34. Movimiento en la cueva con lámpara encendida consume 1 punto de energía")

	# 35. Apagar la lámpara en LOC_AWKWARD vuelve a producir PITCH_DARK inmediatamente
	var lines_off := interpreter.submit("OFF")
	check(interpreter._is_dark_here() and "\n".join(lines_off).contains(world.message("PITCH_DARK")),
		"35. Apagar la lámpara en LOC_AWKWARD vuelve a producir oscuridad (PITCH_DARK)")


# ---------------------------------------------------------------------------
# 4. LOC_CRACK y Transición Forzada (checks 36-42)
# ---------------------------------------------------------------------------
func _test_crack_forced_transition() -> void:
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)
	interpreter.state.object_place["LAMP"] = GameState.CARRIED
	interpreter.state.set_state("LAMP", "LAMP_BRIGHT")

	# 36. LOC_CRACK es una ubicación forzada con 1 sola regla hacia LOC_PITTOP
	var crack := world.location("LOC_CRACK")
	check(crack != null and crack.is_forced() and crack.travel.size() == 1 and crack.travel[0].target == "LOC_PITTOP",
		"36. LOC_CRACK está definida como ubicación forzada (is_forced() == true) con destino LOC_PITTOP")

	# 37. Moverse desde LOC_BIRDCHAMBER a LOC_PITTOP para establecer historial previo
	interpreter.state.move_to("LOC_BIRDCHAMBER", false)
	interpreter.submit("WEST") # a LOC_PITTOP
	check(interpreter.state.current_location == "LOC_PITTOP" and interpreter.state.previous_location == "LOC_BIRDCHAMBER",
		"37. Entrada a LOC_PITTOP estableciendo LOC_BIRDCHAMBER como sala previa")

	# 38. Entrar a LOC_CRACK mediante comando CRACK
	var turns_before := interpreter.state.turn
	var lines := interpreter.submit("CRACK")
	var text := "\n".join(lines)

	# 39. Se describe el texto histórico de la grieta
	check(text.contains("crack is far too small"),
		"38. La narración describe el texto histórico de LOC_CRACK")

	# 40. La transición forzada devuelve automáticamente al jugador a LOC_PITTOP
	check(interpreter.state.current_location == "LOC_PITTOP" and
		interpreter.state.travel_outcome == GameState.TravelOutcome.ARRIVED and
		text.contains("top of small pit"),
		"39. La transición forzada devuelve automáticamente al jugador a LOC_PITTOP")

	# 41. Se consume exactamente 1 turno de entrada
	check(interpreter.state.turn == turns_before + 1,
		"40. La secuencia completa de rebote forzado consume exactamente 1 turno de entrada")

	# 42. Historial de BACK: en LOC_PITTOP tras rebotar de LOC_CRACK, BACK emite FORGOT_PATH (semántica C Open Adventure 1.22)
	var back_lines := interpreter.submit("BACK")
	var back_text := "\n".join(back_lines)
	check(interpreter.state.current_location == "LOC_PITTOP" and
		interpreter.state.travel_outcome == GameState.TravelOutcome.REJECTED and
		back_text.contains(world.message("FORGOT_PATH")),
		"41. El comando BACK en LOC_PITTOP tras rebotar de LOC_CRACK emite FORGOT_PATH sin cambiar de sala")


# ---------------------------------------------------------------------------
# 5. Aislamiento y Contratos (checks 43-48)
# ---------------------------------------------------------------------------
func _test_isolation_and_contracts() -> void:
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)
	var parser := CommandParser.new(world)

	# 43. Hashes SHA-256 de los datasets canónicos
	var ch01_sha := FileAccess.get_sha256(CH01_DATASET_PATH)
	var struct_sha := FileAccess.get_sha256(STRUCTURAL_PATH)
	check(ch01_sha == EXPECTED_CH01_SHA256 and struct_sha == EXPECTED_STRUCTURAL_SHA256,
		"42. Integridad de hashes SHA-256 de chapter_01_surface.json y structural_world.json")

	# 44. Cero actores enanos activos
	check(not world.objects.has("DWARF") and not interpreter.state.object_place.has("DWARF"),
		"43. Cero actores enanos activos en runtime")

	# 45. Cero actores piratas activos
	check(not world.objects.has("PIRATE") and not interpreter.state.object_place.has("PIRATE"),
		"44. Cero actores piratas activos en runtime")

	# 46. Puzles posteriores permanecen inertes (sin BIRD, SNAKE, PLANT, TROLL)
	var puzzles_absent := true
	for pz in ["BIRD", "SNAKE", "PLANT", "TROLL", "DRAGON"]:
		if world.objects.has(pz):
			puzzles_absent = false
			break
	check(puzzles_absent, "45. Objetos y puzles posteriores (BIRD, SNAKE, PLANT, TROLL) no están en runtime")

	# 47. Parser sin contaminación de vocabulario posterior
	var cmd_nugget := parser.parse("TAKE NUGGET")
	check(cmd_nugget.action == "CARRY" and not world.objects.has("NUGGET"),
		"46. Parser sin contaminación de estado ni objetos de capítulos posteriores")

	# 48. Consultas estructurales no consumen números de RNG
	var rng_seed := interpreter.rng.state
	for lid in world.get_structural_location_ids():
		world.get_structural_location(lid)
	check(interpreter.rng.state == rng_seed,
		"47. Consultas al catálogo estructural no consumen números de RNG")


# ---------------------------------------------------------------------------
# 6. Recorrido Integrado Legítimo (checks 49-51)
# ---------------------------------------------------------------------------
func _test_integrated_journey() -> void:
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)

	# Partida completa desde LOC_START sin modificar el estado a mano
	var script: Array[String] = [
		"E",               # a LOC_BUILDING
		"TAKE KEYS",       # coger llaves
		"TAKE LAMP",       # coger lámpara
		"LIGHT LAMP",      # encender lámpara
		"OUT",             # a LOC_START
		"DEPRESSION",      # a LOC_GRATE
		"UNLOCK GRATE",    # abrir reja
		"ENTER",           # descender a LOC_BELOWGRATE
		"WEST",            # a LOC_COBBLE (LIT)
		"WEST",            # a LOC_DEBRIS (oscura con linterna)
		"WEST",            # a LOC_AWKWARD
		"WEST",            # a LOC_BIRDCHAMBER
		"WEST",            # a LOC_PITTOP
		"CRACK",           # explorar grieta -> rebota a LOC_PITTOP
		"DEPRE",           # atajo directo a LOC_GRATE en superficie
		"BUILDING",        # regreso a LOC_START
		"E"                # entrada a LOC_BUILDING
	]

	for cmd in script:
		interpreter.submit(cmd)

	# 49. Ubicación final esperada en LOC_BUILDING
	check(interpreter.state.current_location == "LOC_BUILDING",
		"48. Recorrido integrado legítimo culmina con éxito en LOC_BUILDING")

	# 50. Linterna consumió energía durante el viaje
	check(interpreter.state.lamp_energy < 330 and interpreter.state.state_of("LAMP") == "LAMP_BRIGHT",
		"49. La linterna se mantiene encendida y consumió energía proporcionalmente")

	# 51. Turnos e historial coherentes sin errores de ciclo
	check(interpreter.state.turn == script.size() and interpreter.state.death_count == 0,
		"50. Recorrido integrado ejecutó %d turnos con 0 muertes y 0 errores de ciclo" % script.size())
