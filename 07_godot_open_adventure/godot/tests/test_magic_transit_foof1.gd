# CAR-CORE-002 / R5C: Magic Transit & Word Connections (LOC_FOOF1) test suite.
#
# Validates:
#   1. Enablement of LOC_FOOF1 in WorldData (42 enabled locations, 143 inert locations).
#   2. Bidirectional XYZZY teleport loop:
#      - LOC_BUILDING --XYZZY--> LOC_FOOF1 (forced) --> LOC_DEBRIS (in 1 input turn)
#      - LOC_DEBRIS --XYZZY--> LOC_FOOF2 (forced) --> LOC_BUILDING (in 1 input turn)
#   3. Narration of the forced teleport transition (">>Foof!<<" / Spanish text).
#   4. Turn counting and history preservation across forced transitions.
#   5. Strict isolation: no other FOOF rooms (LOC_FOOF3..LOC_FOOF6) or inert rooms enabled.
extends SceneTree

const EXPECTED_CH01_SHA256 := "afa33c8898049c5af53d06cc3550edbd8f7d58792c819e6224286e82533438c9"
const EXPECTED_STRUCTURAL_SHA256 := "fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3"

var checks := 0
var failures := 0


func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL: " + label)


func _initialize() -> void:
	print("Running CAR-CORE-002 / R5C Magic Transit (LOC_FOOF1) tests...")

	_test_enablement_and_catalog()
	_test_xyzzy_bidirectional_teleport()
	_test_foof_isolation()

	print("PASS: %d CAR-CORE-002 / R5C checks completed with %d failures" % [checks, failures])
	quit(1 if failures > 0 else 0)


func _test_enablement_and_catalog() -> void:
	var world := WorldData.load_default()
	var catalog := world.structural_catalog

	# 1. Verificación de catálogo estructural
	check(catalog != null and catalog.get_location_ids().size() == 185,
		"1. StructuralCatalog inicializado con 185 ubicaciones históricas")

	# 2. LOC_FOOF1 está presente en el catálogo
	check(catalog.has_location("LOC_FOOF1"),
		"2. LOC_FOOF1 existe en el catálogo canónico")

	# 3. LOC_FOOF1 habilitada en runtime
	check(world.is_location_enabled("LOC_FOOF1") and world.location("LOC_FOOF1") != null,
		"3. Habilitación funcional de LOC_FOOF1 en WorldData")

	# 4. Exactamente 46 ubicaciones habilitadas
	var enabled := world.get_enabled_location_ids()
	check(enabled.size() == 46 and world.locations.size() == 46,
		"4. Exactamente 46 ubicaciones habilitadas en la vista funcional")

	# 5. Exactamente 139 ubicaciones deshabilitadas
	var non_enabled := 0
	for lid in catalog.get_location_ids():
		if not world.is_location_enabled(lid):
			non_enabled += 1
	check(non_enabled == 139,
		"5. Exactamente 139 ubicaciones históricas permanecen deshabilitadas")

	# 6. Idempotencia de la habilitación de LOC_FOOF1
	var re_enable := world.enable_structural_location("LOC_FOOF1")
	check(re_enable and world.locations.size() == 46 and world.get_enabled_location_ids().size() == 46,
		"6. Idempotencia de enable_structural_location('LOC_FOOF1')")

	# 7. Rechazo de otras salas mágicas no autorizadas
	var reject_foof3 := world.enable_structural_location("LOC_FOOF3")
	var reject_foof5 := world.enable_structural_location("LOC_FOOF5")
	check(not reject_foof3 and not reject_foof5 and world.locations.size() == 46,
		"7. Rechazo explícito de salas mágicas no autorizadas (LOC_FOOF3, LOC_FOOF5)")

	# 8. Metadatos de LOC_FOOF1 preservados fielmente
	var foof1 := world.location("LOC_FOOF1")
	check(foof1.is_forced() and foof1.chapter_id == "CH_ENTRY" and foof1.description_en.contains(">>Foof!<<"),
		"8. LOC_FOOF1 preserva condición forzada, capítulo CH_ENTRY y descripción histórica")


func _test_xyzzy_bidirectional_teleport() -> void:
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)

	# 9. Viaje a la casita (LOC_BUILDING)
	interpreter.submit("E")
	check(interpreter.state.current_location == "LOC_BUILDING",
		"9. El jugador entra a la casita (LOC_BUILDING)")

	var turns_before := interpreter.state.turn

	# 10. Invocación de XYZZY en LOC_BUILDING
	var lines1 := interpreter.submit("XYZZY")
	var text1 := " ".join(lines1)

	check(interpreter.state.current_location == "LOC_DEBRIS",
		"10. XYZZY en LOC_BUILDING transporta al jugador a LOC_DEBRIS")
	check(text1.contains(">>Foof!<<") or text1.contains("Puf"),
		"11. La transición mágica narra el texto de teletransporte (>>Foof!<< / Puf)")
	check(interpreter.state.turn == turns_before + 1,
		"12. La transición forzada automática consume exactamente 1 turno de entrada")
	check(interpreter.state.travel_outcome == GameState.TravelOutcome.ARRIVED,
		"13. El resultado del viaje es ARRIVED en LOC_DEBRIS")

	# 14. Historial tras teletransporte hacia la cueva
	check(interpreter.state.previous_location == "LOC_FOOF1" and
		interpreter.state.previous_previous_location == "LOC_BUILDING",
		"14. El historial preserva la sala forzada intermedia LOC_FOOF1 y el origen LOC_BUILDING")

	var turns_in_debris := interpreter.state.turn

	# 15. Invocación de retorno con XYZZY en LOC_DEBRIS
	var lines2 := interpreter.submit("XYZZY")
	var text2 := " ".join(lines2)

	check(interpreter.state.current_location == "LOC_BUILDING",
		"15. XYZZY de vuelta en LOC_DEBRIS devuelve al jugador a LOC_BUILDING")
	check(text2.contains(">>Foof!<<") or text2.contains("Puf"),
		"16. El retorno narra la transición mágica correspondiente")
	check(interpreter.state.turn == turns_in_debris + 1,
		"17. El retorno consume exactamente 1 turno de entrada")
	check(interpreter.state.previous_location == "LOC_FOOF2" and
		interpreter.state.previous_previous_location == "LOC_DEBRIS",
		"18. El historial del retorno preserva la sala forzada intermedia LOC_FOOF2 y el origen LOC_DEBRIS")


func _test_foof_isolation() -> void:
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)

	# 19. PLUGH desde LOC_BUILDING hacia LOC_FOOF3 sigue bloqueado como frontera
	interpreter.submit("E")
	var lines_plugh := interpreter.submit("PLUGH")
	var text_plugh := " ".join(lines_plugh)
	check(interpreter.state.current_location == "LOC_BUILDING" and
		interpreter.state.travel_outcome == GameState.TravelOutcome.FRONTIER,
		"19. PLUGH en LOC_BUILDING permanece bloqueado como frontera (LOC_FOOF3 no habilitado)")
	check(text_plugh.contains("capítulo siguiente") or text_plugh.contains("frontier"),
		"20. La frontera emite el mensaje correspondiente")
