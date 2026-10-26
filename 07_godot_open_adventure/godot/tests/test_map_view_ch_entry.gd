# CAR-CORE-002 / R6: Visual Debug Graph in Godot (MapView multi-chapter projection)
#
# Validates:
#   1. Strict contract freeze preservation:
#      - WorldData.map_nodes.size() == 34
#      - WorldData.map_edges.size() == 118
#   2. In CH_SURFACE:
#      - MapView active nodes and edges match WorldData.map_nodes and map_edges
#   3. In CH_ENTRY (e.g. LOC_BELOWGRATE, LOC_DEBRIS, LOC_BIRDCHAMBER, LOC_FOOF1):
#      - MapView dynamically resolves active nodes from enabled structural locations
#      - Nodes retain correct Draw.io geometry (x, y, w, h)
#      - Cross-chapter frontier portals (e.g. LOC_GRATE when in LOC_BELOWGRATE) are included
#      - Navigation exits can be resolved and directions badge generated
#   4. Bounds calculation adapts to chapter coordinates without errors.
extends SceneTree

var checks := 0
var failures := 0


func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL: " + label)


func _initialize() -> void:
	print("Running CAR-CORE-002 / R6 Visual Debug Graph (MapView) tests...")

	_test_contract_freeze_preservation()
	_test_surface_rendering_mode()
	_test_ch_entry_active_graph()
	_test_frontier_portal_presence()
	_test_node_geometry_and_bounds()

	print("PASS: %d CAR-CORE-002 / R6 checks completed with %d failures" % [checks, failures])
	quit(1 if failures > 0 else 0)


func _test_contract_freeze_preservation() -> void:
	var world := WorldData.load_default()
	check(world.map_nodes.size() == 34, "1. Invariante: world.map_nodes conserva exactamente 34 nodos")
	check(world.map_edges.size() == 118, "2. Invariante: world.map_edges conserva exactamente 118 aristas")


func _test_surface_rendering_mode() -> void:
	var world := WorldData.load_default()
	var map_view := MapView.new(world)
	map_view.set_location("LOC_START", {"LOC_START": true})

	var active_nodes := map_view._get_active_nodes()
	var active_edges := map_view._get_active_edges()

	check(active_nodes.size() == 34, "3. En superficie (LOC_START), _get_active_nodes retorna los 34 nodos de CH_01")
	check(active_edges.size() == 118, "4. En superficie (LOC_START), _get_active_edges retorna las 118 aristas de CH_01")
	map_view.free()


func _test_ch_entry_active_graph() -> void:
	var world := WorldData.load_default()
	var map_view := MapView.new(world)
	map_view.set_location("LOC_BELOWGRATE", {"LOC_BELOWGRATE": true})

	var active_nodes := map_view._get_active_nodes()
	var active_edges := map_view._get_active_edges()

	check(active_nodes.size() >= 8, "5. En CH_ENTRY (LOC_BELOWGRATE), _get_active_nodes incluye al menos los 8 nodos seguros")
	check(active_edges.size() > 0, "6. En CH_ENTRY, _get_active_edges genera aristas internas de viaje")

	var ids := []
	for n in active_nodes:
		ids.append(String(n.get("id", "")))

	check(ids.has("LOC_BELOWGRATE"), "7. active_nodes contiene LOC_BELOWGRATE")
	check(ids.has("LOC_COBBLE"), "8. active_nodes contiene LOC_COBBLE")
	check(ids.has("LOC_DEBRIS"), "9. active_nodes contiene LOC_DEBRIS")
	check(ids.has("LOC_AWKWARD"), "10. active_nodes contiene LOC_AWKWARD")
	check(ids.has("LOC_BIRDCHAMBER"), "11. active_nodes contiene LOC_BIRDCHAMBER")
	check(ids.has("LOC_PITTOP"), "12. active_nodes contiene LOC_PITTOP")
	check(ids.has("LOC_CRACK"), "13. active_nodes contiene LOC_CRACK")
	check(ids.has("LOC_FOOF1"), "14. active_nodes contiene LOC_FOOF1")
	map_view.free()


func _test_frontier_portal_presence() -> void:
	var world := WorldData.load_default()
	var map_view := MapView.new(world)
	map_view.set_location("LOC_BELOWGRATE", {"LOC_BELOWGRATE": true})

	var active_nodes := map_view._get_active_nodes()
	var found_grate := false
	var grate_is_frontier := false

	for n in active_nodes:
		if String(n.get("id", "")) == "LOC_GRATE":
			found_grate = true
			grate_is_frontier = bool(n.get("is_frontier", false))
			break

	check(found_grate, "15. Nodo frontera LOC_GRATE presente al visualizar LOC_BELOWGRATE")
	check(grate_is_frontier, "16. LOC_GRATE marcado como is_frontier=true")

	var exits := map_view._get_exits_for("LOC_BELOWGRATE")
	var has_exit_to_grate := false
	for e in exits:
		if e.target == "LOC_GRATE":
			has_exit_to_grate = true
			break
	check(has_exit_to_grate, "17. Salida hacia LOC_GRATE identificada en LOC_BELOWGRATE")
	map_view.free()


func _test_node_geometry_and_bounds() -> void:
	var world := WorldData.load_default()
	var map_view := MapView.new(world)
	map_view.set_location("LOC_DEBRIS", {"LOC_DEBRIS": true})

	var n_debris := map_view._get_node("LOC_DEBRIS")
	check(n_debris.size() > 0, "18. _get_node('LOC_DEBRIS') retorna diccionario no vacío")
	check(float(n_debris.get("x", 0.0)) == 1400.0, "19. Coordenada X de LOC_DEBRIS coincide con Draw.io (1400.0)")
	check(float(n_debris.get("y", 0.0)) == 660.0, "20. Coordenada Y de LOC_DEBRIS coincide con Draw.io (660.0)")

	var bounds := map_view._calculate_bounds()
	check(bounds.size.x > 0.0 and bounds.size.y > 0.0, "21. Bounds de MapView en LOC_DEBRIS calculados con dimensiones positivas")

	var center := map_view._node_center("LOC_DEBRIS")
	check(center.x > 1400.0 and center.y > 660.0, "22. Centro de LOC_DEBRIS correctamente derivado de coordenadas Draw.io")
	map_view.free()
