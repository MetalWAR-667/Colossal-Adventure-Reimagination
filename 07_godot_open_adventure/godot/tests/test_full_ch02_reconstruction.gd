# CAR-CORE-002 / R7: Full CH_02 Hall of Mists Reconstruction test suite.
#
# Validates:
#   1. Complete enablement of all 12 locations of CH_ENTRY:
#      - LOC_BELOWGRATE, LOC_COBBLE, LOC_DEBRIS, LOC_AWKWARD, LOC_BIRDCHAMBER,
#        LOC_PITTOP, LOC_CRACK, LOC_FOOF1, LOC_MISTHALL, LOC_NUGGET, LOC_EASTBANK, LOC_WESTBANK.
#      - Exactly 46 functional locations enabled in WorldData (34 CH_SURFACE + 12 CH_ENTRY).
#      - Exactly 139 locations remaining inert and safely unenabled.
#   2. Bi-directional historical navigation in the Hall of Mists:
#      - LOC_PITTOP --DOWN--> LOC_MISTHALL
#      - LOC_MISTHALL --UP--> LOC_PITTOP
#      - LOC_MISTHALL --SOUTH/LEFT--> LOC_NUGGET
#      - LOC_NUGGET --NORTH/OUT/HALL--> LOC_MISTHALL
#      - LOC_MISTHALL --WEST/HALL/FORWARD--> LOC_EASTBANK
#      - LOC_EASTBANK --EAST/HALL--> LOC_MISTHALL
#      - LOC_EASTBANK --OVER--> LOC_WESTBANK
#      - LOC_WESTBANK --OVER--> LOC_EASTBANK
#   3. Fissure bridge puzzle condition evaluation:
#      - FISSURE unbridged state: JUMP says "CROSS_BRIDGE" (too wide to jump)
#      - FORWARD / CROSS: guarded by FISSURE state
#   4. Historical note and nugget room mechanics:
#      - NUGGET weight restriction rule: LOC_MISTHALL --UP/STEPS (carry NUGGET) --> LOC_DOME
#   5. Strict boundary isolation:
#      - Cross-chapter exits to CH_CENTRAL (LOC_KINGHALL), CH_SPECIAL (LOC_DOME, LOC_NOMAKE),
#        CH_Y2_WINDOWS (LOC_JUMBLE) and CH_MAZE_ALIKE (LOC_PARALLEL1, LOC_MISTWEST)
#        remain protected as FRONTIER portals without leaking unenabled rooms.
#   6. Objects of CH_01 preserved (8 functional items in WorldData.objects, no leaky actors).
#   7. MapView debug projection includes all 12 CH_ENTRY rooms with authentic Draw.io geometry.
extends SceneTree

const EXPECTED_CH01_SHA256 := "afa33c8898049c5af53d06cc3550edbd8f7d58792c819e6224286e82533438c9"
const EXPECTED_STRUCTURAL_SHA256 := "fda199af43cfdc94aca46a4012033da7bdc062b1d28122b6f586f77b0fa30df3"

const CH_ENTRY_ALL_12: PackedStringArray = [
	"LOC_BELOWGRATE",
	"LOC_COBBLE",
	"LOC_DEBRIS",
	"LOC_AWKWARD",
	"LOC_BIRDCHAMBER",
	"LOC_PITTOP",
	"LOC_CRACK",
	"LOC_FOOF1",
	"LOC_MISTHALL",
	"LOC_NUGGET",
	"LOC_EASTBANK",
	"LOC_WESTBANK"
]

var checks := 0
var failures := 0


func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL: " + label)


func _initialize() -> void:
	print("Running CAR-CORE-002 / R7 Full CH_02 Hall of Mists Reconstruction tests...")

	_test_enablement_and_inventory()
	_test_hall_of_mists_navigation()
	_test_fissure_and_nugget_rules()
	_test_frontier_boundary_isolation()
	_test_map_view_full_ch_entry()

	print("PASS: %d CAR-CORE-002 / R7 checks completed with %d failures" % [checks, failures])
	quit(1 if failures > 0 else 0)


func _test_enablement_and_inventory() -> void:
	var world := WorldData.load_default()
	var catalog := world.structural_catalog

	# 1. Structural catalog cargado
	check(catalog != null and catalog.get_counts().get("locations", 0) == 185,
		"1. Catálogo estructural íntegro con 185 ubicaciones")

	# 2. Las 12 salas de CH_ENTRY existen en el catálogo
	var all_in_cat := true
	for id in CH_ENTRY_ALL_12:
		if not catalog.has_location(id):
			all_in_cat = false
			break
	check(all_in_cat, "2. Todas las 12 salas de CH_ENTRY existen en el catálogo")

	# 3. Las 12 salas habilitadas funcionalmente en WorldData
	var all_enabled := true
	for id in CH_ENTRY_ALL_12:
		if not world.is_location_enabled(id) or world.location(id) == null:
			all_enabled = false
			break
	check(all_enabled, "3. Todas las 12 salas de CH_ENTRY habilitadas funcionalmente")

	# 4. Exactamente 46 ubicaciones habilitadas en runtime (34 superficie + 12 cueva)
	check(world.locations.size() == 46 and world.get_enabled_location_ids().size() == 46,
		"4. Exactamente 46 ubicaciones funcionales (34 CH_SURFACE + 12 CH_ENTRY)")

	# 5. Exactamente 139 ubicaciones estructurales permanecen inertes
	var disabled_count := 0
	for id in catalog.get_location_ids():
		if not world.is_location_enabled(id):
			disabled_count += 1
	check(disabled_count == 139, "5. Exactamente 139 salas permanecen deshabilitadas")

	# 6. Idempotencia de habilitación
	var re_enable := world.enable_structural_location("LOC_MISTHALL")
	check(re_enable and world.locations.size() == 46, "6. Habilitación de LOC_MISTHALL es idempotente")

	# 7. Rechazo de salas fuera de CH_ENTRY autorizadas
	var reject_kinghall := world.enable_structural_location("LOC_KINGHALL")
	var reject_dome := world.enable_structural_location("LOC_DOME")
	check(not reject_kinghall and not reject_dome and world.locations.size() == 46,
		"7. Rechazo explícito de salas externas no autorizadas (LOC_KINGHALL, LOC_DOME)")

	# 8. Contenido de objetos funcionales de CH_01 preservado (8 objetos)
	check(world.objects.size() == 8, "8. Exactamente 8 objetos funcionales de CH_01 preservados sin fuga")


func _test_hall_of_mists_navigation() -> void:
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)

	# 9. Descender a la cueva y llegar a LOC_PITTOP
	var prep_moves := [
		"E", "TAKE KEYS", "TAKE LAMP", "OUT",
		"DEPRESSION", "UNLOCK GRATE", "OPEN GRATE", "LIGHT LAMP",
		"ENTER",      # -> LOC_BELOWGRATE
		"COBBLE",     # -> LOC_COBBLE
		"DEBRIS",     # -> LOC_DEBRIS
		"W",          # -> LOC_AWKWARD
		"W",          # -> LOC_BIRDCHAMBER
		"W"           # -> LOC_PITTOP
	]
	for cmd in prep_moves:
		interpreter.submit(cmd)
	check(interpreter.state.current_location == "LOC_PITTOP", "9. Llegada verificada a LOC_PITTOP")

	# 10. Bajar a LOC_MISTHALL por los escalones
	interpreter.submit("D")
	check(interpreter.state.current_location == "LOC_MISTHALL", "10. LOC_PITTOP --D--> LOC_MISTHALL exitoso")

	# 11. Regresar a LOC_PITTOP
	interpreter.submit("U")
	check(interpreter.state.current_location == "LOC_PITTOP", "11. LOC_MISTHALL --U--> LOC_PITTOP exitoso")

	# 12. Regresar a LOC_MISTHALL
	interpreter.submit("D")
	check(interpreter.state.current_location == "LOC_MISTHALL", "12. Reentrada a LOC_MISTHALL")

	# 13. Ir al sur a la sala del nugget (LOC_NUGGET)
	interpreter.submit("S")
	check(interpreter.state.current_location == "LOC_NUGGET", "13. LOC_MISTHALL --S--> LOC_NUGGET exitoso")

	# 14. Regresar al norte a LOC_MISTHALL
	interpreter.submit("N")
	check(interpreter.state.current_location == "LOC_MISTHALL", "14. LOC_NUGGET --N--> LOC_MISTHALL exitoso")

	# 15. Avanzar al oeste hacia la orilla este de la fisura (LOC_EASTBANK)
	interpreter.submit("W")
	check(interpreter.state.current_location == "LOC_EASTBANK", "15. LOC_MISTHALL --W--> LOC_EASTBANK exitoso")

	# 16. Regresar al este a LOC_MISTHALL
	interpreter.submit("E")
	check(interpreter.state.current_location == "LOC_MISTHALL", "16. LOC_EASTBANK --E--> LOC_MISTHALL exitoso")

	# 17. Volver a LOC_EASTBANK
	interpreter.submit("W")
	check(interpreter.state.current_location == "LOC_EASTBANK", "17. Reentrada a LOC_EASTBANK")

	# 18. Sin puente: comando CROSS emite mensaje de no poder cruzar
	var cross_lines := interpreter.submit("CROSS")
	check(interpreter.state.current_location == "LOC_EASTBANK" and
		interpreter.state.travel_outcome == GameState.TravelOutcome.SPOKE,
		"18. LOC_EASTBANK --CROSS--> sin puente emite mensaje NO_CROSS")

	# 19. Simulación del puente cristalino tendido (FISSURE = BRIDGED) y cruce a LOC_WESTBANK
	interpreter.state.set_state("FISSURE", "BRIDGED")
	interpreter.submit("CROSS")
	check(interpreter.state.current_location == "LOC_WESTBANK",
		"19. LOC_EASTBANK --CROSS--> con puente cruza a LOC_WESTBANK exitoso")

	# 19b. Retorno con puente a LOC_EASTBANK
	interpreter.submit("CROSS")
	check(interpreter.state.current_location == "LOC_EASTBANK",
		"19b. LOC_WESTBANK --CROSS--> con puente regresa a LOC_EASTBANK")


func _test_fissure_and_nugget_rules() -> void:
	var world := WorldData.load_default()
	var misthall: WorldLocation = world.location("LOC_MISTHALL")
	var eastbank: WorldLocation = world.location("LOC_EASTBANK")
	var nugget_room: WorldLocation = world.location("LOC_NUGGET")
	var westbank: WorldLocation = world.location("LOC_WESTBANK")

	# 20. Reglas de viaje de LOC_MISTHALL presentes
	check(misthall != null and misthall.travel.size() == 6, "20. LOC_MISTHALL posee exactamente 6 reglas de viaje históricas")

	# 21. Regla con condición NUGGET hacia LOC_DOME en LOC_MISTHALL
	var dome_rule: TravelRule = null
	for r in misthall.travel:
		if r.target == "LOC_DOME":
			dome_rule = r
			break
	check(dome_rule != null and dome_rule.cond_type == "carry" and dome_rule.cond_object == "NUGGET",
		"21. Regla condicional de llevar NUGGET hacia LOC_DOME presente en LOC_MISTHALL")

	# 22. Reglas de fisura en LOC_EASTBANK
	var jump_rule: TravelRule = null
	for r in eastbank.travel:
		if r.verbs.has("JUMP"):
			jump_rule = r
			break
	check(jump_rule != null and jump_rule.action_type == TravelRule.ActionType.SPEAK,
		"22. Regla JUMP en LOC_EASTBANK es de tipo SPEAK ('CROSS_BRIDGE')")

	# 23. Salida incondicional de LOC_NUGGET hacia LOC_MISTHALL
	var nugget_exit: TravelRule = nugget_room.travel[0]
	check(nugget_exit.target == "LOC_MISTHALL" and nugget_exit.cond_type == "always",
		"23. Salida de LOC_NUGGET hacia LOC_MISTHALL es incondicional")

	# 24. Conexiones de LOC_WESTBANK
	check(westbank != null and westbank.travel.size() == 6,
		"24. LOC_WESTBANK posee exactamente 6 reglas de viaje históricas")


func _test_frontier_boundary_isolation() -> void:
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)

	# Ubicarse en LOC_MISTHALL
	interpreter.state.current_location = "LOC_MISTHALL"

	# 25. Intento de movimiento hacia LOC_KINGHALL (CH_CENTRAL no habilitado)
	var king_lines := interpreter.submit("NORTH")
	check(interpreter.state.current_location == "LOC_MISTHALL" and
		interpreter.state.travel_outcome == GameState.TravelOutcome.FRONTIER,
		"25. Salida norte a LOC_KINGHALL detenida de forma segura como FRONTIER")

	# 26. Intento de comando Y2 hacia LOC_JUMBLE (CH_Y2_WINDOWS no habilitado)
	interpreter.submit("Y2")
	check(interpreter.state.current_location == "LOC_MISTHALL" and
		interpreter.state.travel_outcome == GameState.TravelOutcome.FRONTIER,
		"26. Salida Y2 a LOC_JUMBLE detenida como FRONTIER")

	# Ubicarse en LOC_WESTBANK
	interpreter.state.current_location = "LOC_WESTBANK"

	# 27. Intento de movimiento al norte hacia LOC_PARALLEL1 (CH_MAZE_ALIKE no habilitado)
	interpreter.submit("NORTH")
	check(interpreter.state.current_location == "LOC_WESTBANK" and
		interpreter.state.travel_outcome == GameState.TravelOutcome.FRONTIER,
		"27. Salida norte a LOC_PARALLEL1 detenida como FRONTIER")

	# 28. Intento de movimiento al oeste hacia LOC_MISTWEST (CH_MAZE_ALIKE no habilitado)
	interpreter.submit("WEST")
	check(interpreter.state.current_location == "LOC_WESTBANK" and
		interpreter.state.travel_outcome == GameState.TravelOutcome.FRONTIER,
		"28. Salida oeste a LOC_MISTWEST detenida como FRONTIER")


func _test_map_view_full_ch_entry() -> void:
	var world := WorldData.load_default()
	var map_view := MapView.new(world)

	# 29. MapView en LOC_MISTHALL incluye las 12 salas de CH_ENTRY
	map_view.set_location("LOC_MISTHALL", {"LOC_MISTHALL": true})
	var active_nodes := map_view._get_active_nodes()
	var ids: Array[String] = []
	for n in active_nodes:
		ids.append(String(n.get("id", "")))

	var all_12_present := true
	for entry_id in CH_ENTRY_ALL_12:
		if not ids.has(entry_id):
			all_12_present = false
			break
	check(all_12_present, "29. MapView incluye todas las 12 salas de CH_ENTRY al visualizar LOC_MISTHALL")

	# 30. Nodos frontera detectados en MapView desde LOC_MISTHALL (LOC_KINGHALL)
	var has_kinghall_frontier := false
	for n in active_nodes:
		if String(n.get("id", "")) == "LOC_KINGHALL" and bool(n.get("is_frontier", false)):
			has_kinghall_frontier = true
			break
	check(has_kinghall_frontier, "30. MapView proyecta LOC_KINGHALL como nodo frontera desde LOC_MISTHALL")
	map_view.free()
