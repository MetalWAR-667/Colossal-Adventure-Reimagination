# Draws the chapter map and provides an interactive walkthrough navigation guide.
#
# The node geometry is the one published in
# 06_reconstruccion_drawio/output/Open_Adventure_World_V3.drawio (page
# "01 - Surface World"); the edges are rebuilt from the travel rules of the
# source YAML, so the picture and the rules agree.
#
# Offers two view modes:
#   - LOCAL: Centered on the current room and its direct reachable neighbors,
#     with legible cards, large arrow vectors and direction badges (N, S, E, W, etc.).
#   - GLOBAL: Panoramic overview of all 34 rooms, with passive edges softened and
#     outgoing exits from the player's room brightly highlighted.
#
# Also provides an interactive Walkthrough Guide bar with clickable buttons
# to trigger moves directly or reproduce paths step-by-step.
class_name MapView
extends VBoxContainer

signal exit_requested(command: String)

enum ViewMode {
	LOCAL,
	GLOBAL,
}

const NODE_COLOR := Color(0.35, 0.42, 0.52)
const NODE_COLOR_VISITED := Color(0.30, 0.55, 0.42)
const NODE_COLOR_CURRENT := Color(0.85, 0.72, 0.30)
const EDGE_COLOR := Color(0.55, 0.58, 0.62, 0.65)
const TEXT_COLOR := Color(0.85, 0.88, 0.92)

const COLOR_CANVAS_BG := Color(0.04, 0.05, 0.08, 0.95)
const COLOR_GRID := Color(0.12, 0.15, 0.22, 0.35)
const COLOR_EDGE_PASSIVE := Color(0.28, 0.32, 0.42, 0.30)
const COLOR_EDGE_ACTIVE := Color(0.96, 0.82, 0.28, 0.95)
const COLOR_EDGE_HOVER := Color(0.32, 0.92, 0.85, 1.0)
const COLOR_EDGE_BLOCKED := Color(0.95, 0.45, 0.25, 0.9)
const COLOR_EDGE_FRONTIER := Color(0.78, 0.48, 0.95, 0.9)
const COLOR_EDGE_OBSERVED := Color(1.0, 0.35, 0.82, 1.0)

const COLOR_NODE_CURRENT_FILL := Color(0.24, 0.20, 0.08, 0.95)
const COLOR_NODE_CURRENT_BORDER := Color(0.95, 0.82, 0.30, 1.0)
const COLOR_NODE_NEIGHBOR_FILL := Color(0.10, 0.16, 0.22, 0.95)
const COLOR_NODE_NEIGHBOR_BORDER := Color(0.35, 0.65, 0.88, 0.9)
const COLOR_NODE_VISITED_FILL := Color(0.08, 0.16, 0.12, 0.9)
const COLOR_NODE_VISITED_BORDER := Color(0.30, 0.55, 0.42, 0.8)
const COLOR_NODE_UNVISITED_FILL := Color(0.08, 0.10, 0.13, 0.85)
const COLOR_NODE_UNVISITED_BORDER := Color(0.22, 0.26, 0.32, 0.6)

const COLOR_TEXT_BRIGHT := Color(0.95, 0.96, 0.98)
const COLOR_TEXT_MUTED := Color(0.65, 0.70, 0.78)
const COLOR_TEXT_GOLD := Color(0.98, 0.88, 0.45)

var world: WorldData
var current_location: String = ""
var visited: Dictionary = {}
var current_state: GameState = null

var view_mode: ViewMode = ViewMode.LOCAL
var zoom_level: float = 1.0
var pan_offset: Vector2 = Vector2.ZERO
var is_panning: bool = false
var pan_start_pos: Vector2 = Vector2.ZERO
var pan_start_offset: Vector2 = Vector2.ZERO

var hovered_node_id: String = ""
var hovered_exit_target: String = ""
var navigation_enabled: bool = true
var observed_from: String = ""
var observed_to: String = ""
var observed_command: String = ""

# UI nodes
var _toolbar: HBoxContainer
var _mode_button: Button
var _center_button: Button
var _loc_title_label: Label
var _observed_label: Label

var _canvas: Control
var _guide_container: VBoxContainer
var _guide_header: Label
var _exit_buttons_flow: HFlowContainer


func _init(world_data: WorldData) -> void:
	world = world_data
	custom_minimum_size = Vector2(320, 320)
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_theme_constant_override("separation", 6)
	_build_ui()


func set_location(location_id: String, visited_locations: Dictionary, state: GameState = null) -> void:
	current_location = location_id
	visited = visited_locations
	current_state = state
	_update_header()
	_rebuild_guide_buttons()
	if _canvas != null:
		_canvas.queue_redraw()
	queue_redraw()


func set_navigation_enabled(enabled: bool) -> void:
	navigation_enabled = enabled
	if _guide_header != null:
		_guide_header.text = (
			"🧭 SALIDAS Y RECORRIDO (haz clic para moverte):"
			if navigation_enabled
			else "🧭 SALIDAS Y RECORRIDO (solo lectura en modo debug):"
		)
	if _exit_buttons_flow == null:
		return
	for child in _exit_buttons_flow.get_children():
		if child is Button:
			(child as Button).disabled = not navigation_enabled


func set_observed_transition(from_location: String, to_location: String, command: String) -> void:
	if from_location.is_empty() or to_location.is_empty() or from_location == to_location:
		return
	observed_from = from_location
	observed_to = to_location
	observed_command = command
	_update_observed_label()
	if _canvas != null:
		_canvas.queue_redraw()


func _build_ui() -> void:
	# Toolbar
	_toolbar = HBoxContainer.new()
	_toolbar.add_theme_constant_override("separation", 6)
	add_child(_toolbar)

	_mode_button = Button.new()
	_mode_button.text = "🔍 Vista Guía"
	_mode_button.tooltip_text = "Alternar entre Vista Guía (Local) y Mapa Completo (Global)"
	_mode_button.focus_mode = Control.FOCUS_NONE
	_mode_button.pressed.connect(_on_mode_toggled)
	_toolbar.add_child(_mode_button)

	_center_button = Button.new()
	_center_button.text = "🎯 Centrar"
	_center_button.tooltip_text = "Restablecer zoom y centrado en la sala actual"
	_center_button.focus_mode = Control.FOCUS_NONE
	_center_button.pressed.connect(_reset_view)
	_toolbar.add_child(_center_button)

	_loc_title_label = Label.new()
	_loc_title_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_loc_title_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_loc_title_label.add_theme_font_size_override("font_size", 11)
	_loc_title_label.add_theme_color_override("font_color", COLOR_TEXT_GOLD)
	_toolbar.add_child(_loc_title_label)

	_observed_label = Label.new()
	_observed_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_observed_label.clip_text = true
	_observed_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_observed_label.add_theme_font_size_override("font_size", 11)
	_observed_label.add_theme_color_override("font_color", COLOR_EDGE_OBSERVED)
	_observed_label.tooltip_text = "Movimiento real observado después de ejecutar un comando del parser"
	_toolbar.add_child(_observed_label)
	_update_observed_label()

	# Drawing Canvas
	_canvas = Control.new()
	_canvas.custom_minimum_size = Vector2(320, 180)
	_canvas.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_canvas.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_canvas.clip_contents = true
	_canvas.draw.connect(_on_canvas_draw)
	_canvas.gui_input.connect(_on_canvas_gui_input)
	_canvas.mouse_exited.connect(_on_canvas_mouse_exited)
	add_child(_canvas)

	# Walkthrough Guide Bar
	_guide_container = VBoxContainer.new()
	_guide_container.add_theme_constant_override("separation", 3)
	add_child(_guide_container)

	_guide_header = Label.new()
	_guide_header.text = "🧭 SALIDAS Y RECORRIDO (haz clic para moverte):"
	_guide_header.add_theme_font_size_override("font_size", 11)
	_guide_header.add_theme_color_override("font_color", Color(0.75, 0.82, 0.90))
	_guide_container.add_child(_guide_header)

	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(0, 48)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_guide_container.add_child(scroll)

	_exit_buttons_flow = HFlowContainer.new()
	_exit_buttons_flow.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_exit_buttons_flow.add_theme_constant_override("h_separation", 6)
	_exit_buttons_flow.add_theme_constant_override("v_separation", 4)
	scroll.add_child(_exit_buttons_flow)


func _on_mode_toggled() -> void:
	if view_mode == ViewMode.LOCAL:
		view_mode = ViewMode.GLOBAL
		_mode_button.text = "🌐 Mapa Global"
	else:
		view_mode = ViewMode.LOCAL
		_mode_button.text = "🔍 Vista Guía"
	_reset_view()
	if _canvas != null:
		_canvas.queue_redraw()


func _reset_view() -> void:
	zoom_level = 1.0
	pan_offset = Vector2.ZERO
	if _canvas != null:
		_canvas.queue_redraw()


func _update_header() -> void:
	if _loc_title_label != null:
		var name := current_location.replace("LOC_", "")
		_loc_title_label.text = "Sala: %s" % name


func _update_observed_label() -> void:
	if _observed_label == null:
		return
	if observed_from.is_empty() or observed_to.is_empty():
		_observed_label.text = "Última transición observada: —"
		return
	_observed_label.text = "Última transición observada: %s → %s · %s" % [
		observed_from.replace("LOC_", ""),
		observed_to.replace("LOC_", ""),
		observed_command,
	]


func _rebuild_guide_buttons() -> void:
	if _exit_buttons_flow == null:
		return
	for child in _exit_buttons_flow.get_children():
		child.queue_free()

	var exits := _get_exits_for(current_location)
	if exits.is_empty():
		var lbl := Label.new()
		lbl.text = "(Sin salidas conocidas)"
		lbl.add_theme_font_size_override("font_size", 11)
		lbl.add_theme_color_override("font_color", COLOR_TEXT_MUTED)
		_exit_buttons_flow.add_child(lbl)
		return

	for exit in exits:
		var btn := Button.new()
		btn.focus_mode = Control.FOCUS_NONE
		btn.disabled = not navigation_enabled
		var label_text: String = "[ %s ] → %s" % [exit.display_dir, exit.short_target_name]
		if exit.is_blocked:
			label_text += " ⚠️"
		elif exit.is_frontier:
			label_text += " 🚪"
		btn.text = label_text
		btn.add_theme_font_size_override("font_size", 11)

		var tooltip := "Comandos: %s\nDestino: %s (%s)" % [
			", ".join(exit.verbs),
			exit.target.replace("LOC_", ""),
			exit.target_name,
		]
		if not exit.cond_msg.is_empty():
			tooltip += "\nCondición: %s" % exit.cond_msg
		btn.tooltip_text = tooltip

		var verb_to_send: String = exit.best_verb
		var target_loc: String = exit.target
		btn.pressed.connect(func(): exit_requested.emit(verb_to_send))
		btn.mouse_entered.connect(func():
			hovered_exit_target = target_loc
			if _canvas != null:
				_canvas.queue_redraw()
		)
		btn.mouse_exited.connect(func():
			hovered_exit_target = ""
			if _canvas != null:
				_canvas.queue_redraw()
		)
		_exit_buttons_flow.add_child(btn)


func _get_exits_for(loc_id: String) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	if world == null or not world.locations.has(loc_id):
		return result
	var loc: WorldLocation = world.locations[loc_id]
	var grouped: Dictionary = {}

	for rule in loc.travel:
		if rule.action_type != TravelRule.ActionType.GOTO or rule.target.is_empty():
			continue
		var target := rule.target
		if not grouped.has(target):
			grouped[target] = {
				"target": target,
				"verbs": PackedStringArray(),
				"rules": []
			}
		grouped[target]["rules"].append(rule)
		for v in rule.verbs:
			if not grouped[target]["verbs"].has(v):
				grouped[target]["verbs"].append(v)

	for target_key in grouped.keys():
		var target: String = String(target_key)
		var data: Dictionary = grouped[target]
		var verbs: PackedStringArray = data["verbs"]
		var verb_info: Dictionary = _resolve_verbs(verbs, target)
		var is_blocked := false
		var cond_msg := ""
		var is_frontier := not world.is_in_chapter(target)

		if current_state != null:
			for rule_var in data["rules"]:
				var rule: TravelRule = rule_var
				if rule.cond_type == "not_state":
					var current_obj_state := current_state.state_of(rule.cond_object)
					if current_obj_state == rule.cond_state:
						is_blocked = true
						cond_msg = "Bloqueado: %s está %s" % [rule.cond_object, rule.cond_state]
				elif rule.cond_type == "carry":
					if not current_state.is_carried(rule.cond_object):
						is_blocked = true
						cond_msg = "Requiere llevar %s" % rule.cond_object

		var target_name: String = target.replace("LOC_", "")
		var short_desc := world.describe_short(target)
		if not short_desc.is_empty():
			target_name = short_desc.replace("Sigues ", "").replace("Estás ", "").strip_edges()

		result.append({
			"target": target,
			"best_verb": String(verb_info["best_verb"]),
			"dir_code": String(verb_info["dir_code"]),
			"display_dir": String(verb_info["display_dir"]),
			"verbs": verbs,
			"target_name": target_name,
			"short_target_name": target.replace("LOC_", ""),
			"is_blocked": is_blocked,
			"cond_msg": cond_msg,
			"is_frontier": is_frontier,
		})

	var order_map := {"N": 1, "NE": 2, "E": 3, "SE": 4, "S": 5, "SW": 6, "W": 7, "NW": 8, "U": 9, "D": 10}
	result.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		var oa: int = order_map.get(a["dir_code"], 99)
		var ob: int = order_map.get(b["dir_code"], 99)
		if oa != ob:
			return oa < ob
		return a["target"] < b["target"]
	)
	return result


func _resolve_verbs(verbs: PackedStringArray, target: String) -> Dictionary:
	# 1. Compass directions
	for v in verbs:
		var vu := v.to_upper()
		if vu == "NORTH" or vu == "N":
			return {"best_verb": "N", "dir_code": "N", "display_dir": "N · NORTE"}
		elif vu == "SOUTH" or vu == "S":
			return {"best_verb": "S", "dir_code": "S", "display_dir": "S · SUR"}
		elif vu == "EAST" or vu == "E":
			return {"best_verb": "E", "dir_code": "E", "display_dir": "E · ESTE"}
		elif vu == "WEST" or vu == "W":
			return {"best_verb": "W", "dir_code": "W", "display_dir": "W · OESTE"}
		elif vu == "NE":
			return {"best_verb": "NE", "dir_code": "NE", "display_dir": "NE · NORESTE"}
		elif vu == "NW":
			return {"best_verb": "NW", "dir_code": "NW", "display_dir": "NW · NOROESTE"}
		elif vu == "SE":
			return {"best_verb": "SE", "dir_code": "SE", "display_dir": "SE · SURESTE"}
		elif vu == "SW":
			return {"best_verb": "SW", "dir_code": "SW", "display_dir": "SW · SUROESTE"}
		elif vu == "UP" or vu == "UPWAR":
			return {"best_verb": "U", "dir_code": "U", "display_dir": "U · SUBIR"}
		elif vu == "DOWN" or vu == "DOWNS":
			return {"best_verb": "D", "dir_code": "D", "display_dir": "D · BAJAR"}

	# 2. Contextual and movement words
	for v in verbs:
		var vu := v.to_upper()
		if vu == "ENTER" or vu == "INWAR":
			return {"best_verb": "ENTER", "dir_code": "IN", "display_dir": "ENTRAR"}
		elif vu == "OUT" or vu == "OUTDO":
			return {"best_verb": "OUT", "dir_code": "OUT", "display_dir": "SALIR"}
		elif vu == "ROAD":
			return {"best_verb": "ROAD", "dir_code": "ROAD", "display_dir": "CAMINO"}
		elif vu == "GULLY":
			return {"best_verb": "GULLY", "dir_code": "GULLY", "display_dir": "VAGUADA"}
		elif vu == "STREA":
			return {"best_verb": "STREA", "dir_code": "ARROYO", "display_dir": "ARROYO"}
		elif vu == "FORES":
			return {"best_verb": "FOREST", "dir_code": "BOSQUE", "display_dir": "BOSQUE"}
		elif vu == "BUILD":
			return {"best_verb": "BUILD", "dir_code": "CASITA", "display_dir": "CASITA"}
		elif vu == "DEPRE":
			return {"best_verb": "DEPRE", "dir_code": "REJA", "display_dir": "DEPRESIÓN"}
		elif vu == "SLIT":
			return {"best_verb": "SLIT", "dir_code": "RANURA", "display_dir": "RANURA"}
		elif vu == "XYZZY":
			return {"best_verb": "XYZZY", "dir_code": "XYZZY", "display_dir": "XYZZY"}
		elif vu == "PLUGH":
			return {"best_verb": "PLUGH", "dir_code": "PLUGH", "display_dir": "PLUGH"}
		elif vu == "CRAWL":
			return {"best_verb": "CRAWL", "dir_code": "GATEAR", "display_dir": "GATEAR"}
		elif vu == "COBBL":
			return {"best_verb": "COBBLE", "dir_code": "COBBLE", "display_dir": "GUIJARROS"}
		elif vu == "DEBRI":
			return {"best_verb": "DEBRIS", "dir_code": "DEBRIS", "display_dir": "ESCOMBROS"}
		elif vu == "CANYO":
			return {"best_verb": "CANYON", "dir_code": "CAÑON", "display_dir": "CAÑÓN"}
		elif vu == "PASSA":
			return {"best_verb": "PASSAGE", "dir_code": "PASO", "display_dir": "PASADIZO"}
		elif vu == "PIT":
			return {"best_verb": "PIT", "dir_code": "FOSO", "display_dir": "FOSO"}
		elif vu == "STEPS" or vu == "STAIR":
			return {"best_verb": "STEPS", "dir_code": "ESCALERA", "display_dir": "ESCALONES"}
		elif vu == "HALL":
			return {"best_verb": "HALL", "dir_code": "SALA", "display_dir": "SALA"}
		elif vu == "CRACK":
			return {"best_verb": "CRACK", "dir_code": "GRIETA", "display_dir": "GRIETA"}
		elif vu == "SURFA":
			return {"best_verb": "SURFACE", "dir_code": "SUPERF", "display_dir": "SUPERFICIE"}
		elif vu == "DARK":
			return {"best_verb": "DARK", "dir_code": "OSCURO", "display_dir": "OSCURIDAD"}
		elif vu == "LOW":
			return {"best_verb": "LOW", "dir_code": "BAJO", "display_dir": "PASO BAJO"}
		elif vu == "ENTRA":
			return {"best_verb": "ENTRANCE", "dir_code": "ENTRADA", "display_dir": "ENTRADA"}
		elif vu == "JUMP":
			return {"best_verb": "JUMP", "dir_code": "SALTAR", "display_dir": "SALTAR"}
		elif vu == "CROSS" or vu == "ACROS" or vu == "OVER":
			return {"best_verb": "CROSS", "dir_code": "CRUZAR", "display_dir": "CRUZAR"}
		elif vu == "FORWA":
			return {"best_verb": "FORWARD", "dir_code": "ADELANTE", "display_dir": "ADELANTE"}
		elif vu == "LEFT":
			return {"best_verb": "LEFT", "dir_code": "IZQ", "display_dir": "IZQUIERDA"}
		elif vu == "Y2":
			return {"best_verb": "Y2", "dir_code": "Y2", "display_dir": "Y2"}

	if not verbs.is_empty():
		return {"best_verb": verbs[0], "dir_code": verbs[0], "display_dir": verbs[0]}
	var fallback := target.replace("LOC_", "")
	return {"best_verb": fallback, "dir_code": fallback, "display_dir": fallback}


func _is_in_surface(location_id: String) -> bool:
	if world == null:
		return false
	var loc := world.location(location_id)
	if loc != null and not loc.chapter_id.is_empty():
		return loc.chapter_id == "CH_SURFACE"
	return world.is_in_chapter(location_id) and not WorldData.AUTHORIZED_ADDITIONAL_LOCATIONS.has(location_id)


func _get_active_nodes() -> Array[Dictionary]:
	if world == null:
		return []
	if current_location.is_empty() or _is_in_surface(current_location) or world.structural_catalog == null:
		return world.map_nodes

	# When outside surface (e.g. CH_ENTRY safe subgraph), construct active nodes dynamically
	var catalog: StructuralCatalog = world.structural_catalog
	var nodes: Array[Dictionary] = []
	var visited_ids: Dictionary = {}

	# 1. Add all enabled locations in current chapter
	for loc_id in world.enabled_location_ids.keys():
		var id_str := String(loc_id)
		if _is_in_surface(id_str):
			continue
		var raw_loc := catalog.get_location(id_str)
		if raw_loc.is_empty():
			continue
		var dw: Dictionary = raw_loc.get("drawio", {})
		visited_ids[id_str] = true
		nodes.append({
			"id": id_str,
			"label": String(dw.get("label", id_str.replace("LOC_", ""))),
			"x": float(dw.get("x", 0.0)),
			"y": float(dw.get("y", 0.0)),
			"w": float(dw.get("width", 290.0)),
			"h": float(dw.get("height", 160.0)),
			"is_frontier": false,
		})

	# 2. Add reachable frontier / cross-chapter nodes if directly accessible
	var current_exits := _get_exits_for(current_location)
	for exit in current_exits:
		var target: String = exit.target
		if not visited_ids.has(target) and catalog.has_location(target):
			var raw_loc := catalog.get_location(target)
			var dw: Dictionary = raw_loc.get("drawio", {})
			visited_ids[target] = true
			nodes.append({
				"id": target,
				"label": String(dw.get("label", target.replace("LOC_", ""))),
				"x": float(dw.get("x", 0.0)),
				"y": float(dw.get("y", 0.0)),
				"w": float(dw.get("width", 290.0)),
				"h": float(dw.get("height", 160.0)),
				"is_frontier": true,
			})

	return nodes


func _get_active_edges() -> Array[Dictionary]:
	if world == null:
		return []
	if current_location.is_empty() or _is_in_surface(current_location) or world.structural_catalog == null:
		return world.map_edges

	var catalog: StructuralCatalog = world.structural_catalog
	var edges: Array[Dictionary] = []
	var active_nodes := _get_active_nodes()
	var active_ids := {}
	for n in active_nodes:
		active_ids[String(n.get("id", ""))] = true

	for loc_id in world.enabled_location_ids.keys():
		var id_str := String(loc_id)
		if _is_in_surface(id_str):
			continue
		var travels := catalog.get_travel_records(id_str)
		for tr in travels:
			if tr.get("action_type") == "goto":
				var dest := String(tr.get("destination_location_id", ""))
				if active_ids.has(dest):
					edges.append({
						"from": id_str,
						"to": dest,
						"verbs": tr.get("verbs", []),
					})
	return edges


func _on_canvas_draw() -> void:
	if world == null or _get_active_nodes().is_empty():
		return

	var canvas_rect := Rect2(Vector2.ZERO, _canvas.size)
	_canvas.draw_rect(canvas_rect, COLOR_CANVAS_BG)

	var bounds := _calculate_bounds()
	if bounds.size.x <= 0.0 or bounds.size.y <= 0.0:
		return

	var base_scale := minf(canvas_rect.size.x / bounds.size.x, canvas_rect.size.y / bounds.size.y)
	var scale := base_scale * zoom_level
	var offset := (canvas_rect.size - bounds.size * scale) * 0.5 - bounds.position * scale + pan_offset

	_draw_grid(canvas_rect)

	var current_exits := _get_exits_for(current_location)
	var active_target_map := {}
	for exit in current_exits:
		active_target_map[exit.target] = exit

	var reachable_neighbors := active_target_map.keys()
	var active_edges := _get_active_edges()
	var active_nodes := _get_active_nodes()

	var local_node_set := {}
	if view_mode == ViewMode.LOCAL:
		local_node_set[current_location] = true
		for t in reachable_neighbors:
			local_node_set[t] = true
		for edge in active_edges:
			if String(edge.get("to", "")) == current_location:
				local_node_set[String(edge.get("from", ""))] = true
		if not observed_from.is_empty():
			local_node_set[observed_from] = true
		if not observed_to.is_empty():
			local_node_set[observed_to] = true

	# 1. Background passive edges
	for edge in active_edges:
		var from_id := String(edge.get("from", ""))
		var to_id := String(edge.get("to", ""))
		if from_id == current_location:
			continue
		if view_mode == ViewMode.LOCAL:
			if not local_node_set.has(from_id) or not local_node_set.has(to_id):
				continue

		var p_from := _node_center(from_id)
		var p_to := _node_center(to_id)
		if p_from == Vector2.ZERO or p_to == Vector2.ZERO:
			continue
		var s_from := p_from * scale + offset
		var s_to := p_to * scale + offset
		_canvas.draw_line(s_from, s_to, COLOR_EDGE_PASSIVE, 1.0)

	# 2. Last transition actually observed from the interpreter state.
	if not observed_from.is_empty() and not observed_to.is_empty():
		var observed_from_pt := _node_center(observed_from)
		var observed_to_pt := _node_center(observed_to)
		if observed_from_pt != Vector2.ZERO and observed_to_pt != Vector2.ZERO:
			var observed_from_node := _get_node(observed_from)
			var observed_to_node := _get_node(observed_to)
			_draw_directed_arrow(
				observed_from_pt * scale + offset,
				observed_to_pt * scale + offset,
				_node_screen_box(observed_from_node, scale, offset),
				_node_screen_box(observed_to_node, scale, offset),
				COLOR_EDGE_OBSERVED,
				"OBS",
				true
			)

	# 3. Active outgoing directed edges from current_location
	for exit in current_exits:
		var target_id: String = exit.target
		var p_from := _node_center(current_location)
		var p_to := _node_center(target_id)
		if p_from == Vector2.ZERO or p_to == Vector2.ZERO:
			continue

		var is_hovered := (hovered_exit_target == target_id or hovered_node_id == target_id)
		var edge_color := COLOR_EDGE_ACTIVE
		if is_hovered:
			edge_color = COLOR_EDGE_HOVER
		elif exit.is_blocked:
			edge_color = COLOR_EDGE_BLOCKED
		elif exit.is_frontier:
			edge_color = COLOR_EDGE_FRONTIER

		var s_from := p_from * scale + offset
		var s_to := p_to * scale + offset

		var node_from := _get_node(current_location)
		var node_to := _get_node(target_id)
		var box_from := _node_screen_box(node_from, scale, offset)
		var box_to := _node_screen_box(node_to, scale, offset)

		_draw_directed_arrow(s_from, s_to, box_from, box_to, edge_color, exit.dir_code, is_hovered)

	# 4. Nodes
	for node in active_nodes:
		var id := String(node.get("id", ""))
		if view_mode == ViewMode.LOCAL and not local_node_set.has(id):
			continue

		var box := _node_screen_box(node, scale, offset)
		var is_current := (id == current_location)
		var is_neighbor := reachable_neighbors.has(id)
		var is_hovered := (id == hovered_node_id or id == hovered_exit_target)
		var is_vis := visited.has(id)

		_draw_node_card(node, box, is_current, is_neighbor, is_vis, is_hovered)



func _draw_directed_arrow(
	from_pt: Vector2,
	to_pt: Vector2,
	box_from: Rect2,
	box_to: Rect2,
	color: Color,
	badge_text: String,
	is_hovered: bool
) -> void:
	var delta := to_pt - from_pt
	var dist := delta.length()
	if dist < 12.0:
		return
	var dir := delta / dist

	var half_from := box_from.size * 0.5
	var half_to := box_to.size * 0.5
	var start_margin := minf(half_from.x, half_from.y) * 0.95
	var end_margin := minf(half_to.x, half_to.y) * 0.95

	if dist <= start_margin + end_margin + 15.0:
		start_margin = dist * 0.25
		end_margin = dist * 0.25

	var p_start := from_pt + dir * start_margin
	var p_end := to_pt - dir * end_margin

	var line_width := 2.6 if is_hovered else 2.0
	_canvas.draw_line(p_start, p_end, color, line_width)

	var arrow_size := 11.0 if is_hovered else 9.0
	var perp := Vector2(-dir.y, dir.x)
	var tip1 := p_end - dir * arrow_size + perp * (arrow_size * 0.55)
	var tip2 := p_end - dir * arrow_size - perp * (arrow_size * 0.55)
	_canvas.draw_colored_polygon(PackedVector2Array([p_end, tip1, tip2]), color)

	if not badge_text.is_empty():
		var font := ThemeDB.fallback_font
		var font_size := 10
		var badge_str := "[%s]" % badge_text
		var str_size := font.get_string_size(badge_str, HORIZONTAL_ALIGNMENT_CENTER, -1, font_size)
		var mid_pos := p_start + (p_end - p_start) * 0.38
		var badge_rect := Rect2(mid_pos - str_size * 0.5 - Vector2(3, 2), str_size + Vector2(6, 4))

		_canvas.draw_rect(badge_rect, Color(0.06, 0.08, 0.12, 0.96), true)
		_canvas.draw_rect(badge_rect, color, false, 1.2)
		_canvas.draw_string(
			font,
			Vector2(badge_rect.position.x + 3, badge_rect.position.y + str_size.y - 1),
			badge_str,
			HORIZONTAL_ALIGNMENT_CENTER,
			-1,
			font_size,
			COLOR_TEXT_BRIGHT if is_hovered else color
		)


func _draw_node_card(
	node: Dictionary,
	box: Rect2,
	is_current: bool,
	is_neighbor: bool,
	is_vis: bool,
	is_hovered: bool
) -> void:
	var id := String(node.get("id", ""))
	var fill_color := COLOR_NODE_UNVISITED_FILL
	var border_color := COLOR_NODE_UNVISITED_BORDER
	var border_width := 1.2

	if is_current:
		fill_color = COLOR_NODE_CURRENT_FILL
		border_color = COLOR_NODE_CURRENT_BORDER
		border_width = 2.6
	elif is_hovered:
		fill_color = Color(0.12, 0.22, 0.28, 0.98)
		border_color = COLOR_EDGE_HOVER
		border_width = 2.4
	elif is_neighbor:
		fill_color = COLOR_NODE_NEIGHBOR_FILL
		border_color = COLOR_NODE_NEIGHBOR_BORDER
		border_width = 2.0
	elif is_vis:
		fill_color = COLOR_NODE_VISITED_FILL
		border_color = COLOR_NODE_VISITED_BORDER
		border_width = 1.4

	_canvas.draw_rect(box, fill_color, true)
	_canvas.draw_rect(box, border_color, false, border_width)

	var font := ThemeDB.fallback_font
	var label_id := id.replace("LOC_", "")
	var font_size := 11 if view_mode == ViewMode.LOCAL else 9

	if is_current:
		var tag := "★ TÚ AQUÍ"
		_canvas.draw_string(font, box.position + Vector2(4, 11), tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, COLOR_TEXT_GOLD)
		_canvas.draw_string(font, box.position + Vector2(4, 24), label_id, HORIZONTAL_ALIGNMENT_LEFT, int(box.size.x - 8), font_size, COLOR_TEXT_BRIGHT)
	else:
		_canvas.draw_string(font, box.position + Vector2(4, 13), label_id, HORIZONTAL_ALIGNMENT_LEFT, int(box.size.x - 8), font_size, COLOR_TEXT_BRIGHT)

	if view_mode == ViewMode.LOCAL and box.size.y > 36.0:
		var desc := world.describe_short(id)
		if desc.is_empty():
			desc = id.replace("LOC_", "")
		desc = desc.replace("Sigues ", "").replace("Estás ", "").strip_edges()
		_canvas.draw_string(
			font,
			box.position + Vector2(4, 35),
			desc,
			HORIZONTAL_ALIGNMENT_LEFT,
			int(box.size.x - 8),
			9,
			COLOR_TEXT_MUTED
		)


func _calculate_bounds() -> Rect2:
	if view_mode == ViewMode.GLOBAL or current_location.is_empty():
		return _node_bounds()

	var current_exits := _get_exits_for(current_location)
	var local_ids: Dictionary = {current_location: true}
	for exit in current_exits:
		local_ids[exit.target] = true
	var active_edges := _get_active_edges()
	for edge in active_edges:
		if String(edge.get("to", "")) == current_location:
			local_ids[String(edge.get("from", ""))] = true
	if not observed_from.is_empty():
		local_ids[observed_from] = true
	if not observed_to.is_empty():
		local_ids[observed_to] = true

	var bounds := Rect2()
	var first := true
	for node in _get_active_nodes():
		var id := String(node.get("id", ""))
		if not local_ids.has(id):
			continue
		var box := Rect2(
			Vector2(float(node.get("x", 0.0)), float(node.get("y", 0.0))),
			Vector2(float(node.get("w", 0.0)), float(node.get("h", 0.0)))
		)
		if first:
			bounds = box
			first = false
		else:
			bounds = bounds.merge(box)

	if first:
		return _node_bounds()

	var pad := Vector2(240, 200)
	bounds.position -= pad
	bounds.size += pad * 2.0
	return bounds


func _node_screen_box(node: Dictionary, scale: float, offset: Vector2) -> Rect2:
	var orig := Rect2(
		Vector2(float(node.get("x", 0.0)), float(node.get("y", 0.0))),
		Vector2(float(node.get("w", 0.0)), float(node.get("h", 0.0)))
	)
	var box := Rect2(orig.position * scale + offset, orig.size * scale)
	if view_mode == ViewMode.LOCAL:
		box.size.x = maxf(box.size.x, 85.0)
		box.size.y = maxf(box.size.y, 44.0)
	else:
		box.size.x = maxf(box.size.x, 40.0)
		box.size.y = maxf(box.size.y, 20.0)
	return box


func _draw_grid(canvas_rect: Rect2) -> void:
	var step := 28.0
	var x := 0.0
	while x < canvas_rect.size.x:
		_canvas.draw_line(Vector2(x, 0), Vector2(x, canvas_rect.size.y), COLOR_GRID, 1.0)
		x += step
	var y := 0.0
	while y < canvas_rect.size.y:
		_canvas.draw_line(Vector2(0, y), Vector2(canvas_rect.size.x, y), COLOR_GRID, 1.0)
		y += step


func _on_canvas_gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_WHEEL_UP and mb.pressed:
			zoom_level = clampf(zoom_level * 1.15, 0.4, 4.0)
			_canvas.queue_redraw()
		elif mb.button_index == MOUSE_BUTTON_WHEEL_DOWN and mb.pressed:
			zoom_level = clampf(zoom_level / 1.15, 0.4, 4.0)
			_canvas.queue_redraw()
		elif mb.button_index == MOUSE_BUTTON_LEFT:
			if mb.pressed:
				is_panning = true
				pan_start_pos = mb.position
				pan_start_offset = pan_offset
			else:
				is_panning = false
				if pan_start_pos.distance_to(mb.position) < 6.0:
					_handle_click_at(mb.position)
		elif mb.button_index == MOUSE_BUTTON_RIGHT and mb.pressed:
			_on_mode_toggled()

	elif event is InputEventMouseMotion:
		var mm := event as InputEventMouseMotion
		if is_panning:
			pan_offset = pan_start_offset + (mm.position - pan_start_pos)
			_canvas.queue_redraw()
		else:
			_update_hover_at(mm.position)


func _on_canvas_mouse_exited() -> void:
	if not hovered_node_id.is_empty():
		hovered_node_id = ""
		_canvas.queue_redraw()


func _handle_click_at(pos: Vector2) -> void:
	if not navigation_enabled:
		return
	var bounds := _calculate_bounds()
	if bounds.size.x <= 0.0 or bounds.size.y <= 0.0:
		return
	var base_scale := minf(_canvas.size.x / bounds.size.x, _canvas.size.y / bounds.size.y)
	var scale := base_scale * zoom_level
	var offset := (_canvas.size - bounds.size * scale) * 0.5 - bounds.position * scale + pan_offset

	var current_exits := _get_exits_for(current_location)
	for node in _get_active_nodes():
		var id := String(node.get("id", ""))
		var box := _node_screen_box(node, scale, offset)
		if box.has_point(pos):
			for exit in current_exits:
				if exit.target == id:
					exit_requested.emit(exit.best_verb)
					return


func _update_hover_at(pos: Vector2) -> void:
	var bounds := _calculate_bounds()
	if bounds.size.x <= 0.0 or bounds.size.y <= 0.0:
		return
	var base_scale := minf(_canvas.size.x / bounds.size.x, _canvas.size.y / bounds.size.y)
	var scale := base_scale * zoom_level
	var offset := (_canvas.size - bounds.size * scale) * 0.5 - bounds.position * scale + pan_offset

	var found_id := ""
	for node in _get_active_nodes():
		var box := _node_screen_box(node, scale, offset)
		if box.has_point(pos):
			found_id = String(node.get("id", ""))
			break

	if found_id != hovered_node_id:
		hovered_node_id = found_id
		_canvas.queue_redraw()


func _node_bounds() -> Rect2:
	var bounds := Rect2()
	var first := true
	for node in _get_active_nodes():
		var box := Rect2(
			Vector2(float(node.get("x", 0.0)), float(node.get("y", 0.0))),
			Vector2(float(node.get("w", 0.0)), float(node.get("h", 0.0)))
		)
		if first:
			bounds = box
			first = false
		else:
			bounds = bounds.merge(box)
	return bounds


func _node_center(location_id: String) -> Vector2:
	for node in _get_active_nodes():
		if String(node.get("id", "")) == location_id:
			return Vector2(
				float(node.get("x", 0.0)) + float(node.get("w", 0.0)) * 0.5,
				float(node.get("y", 0.0)) + float(node.get("h", 0.0)) * 0.5
			)
	return Vector2.ZERO


func _get_node(location_id: String) -> Dictionary:
	for node in _get_active_nodes():
		if String(node.get("id", "")) == location_id:
			return node
	return {}
