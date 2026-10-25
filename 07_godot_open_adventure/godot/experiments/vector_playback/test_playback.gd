extends SceneTree

const Playback = preload("res://experiments/vector_playback/playback.gd")
const View = preload("res://experiments/vector_playback/playback_view.gd")
var checks := 0
var failures := 0


func _initialize() -> void:
	call_deferred("_run")


func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures += 1
		push_error(message)


func digest(bytes: PackedByteArray) -> String:
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(bytes)
	return hash.finish().hex_encode()


func _run() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://experiments/vector_playback/loc_start.json"))
	var model := Playback.new()
	model.configure(data)
	check(data.room == "LOC_START" and data.format == "CAR-ART-002-experimental-v1", "Experimental dataset identity")
	check(model.grid == Vector2i(640, 400) and model.lines.size() == 43 and model.regions.size() == 17, "Full C/START geometry retained")
	var before := Time.get_ticks_usec()
	var steps := 0
	var max_prepare := 0
	while not model.prepared and model.error.is_empty() and steps < 10000:
		var tick := Time.get_ticks_usec()
		model.prepare_step(4096)
		max_prepare = maxi(max_prepare, Time.get_ticks_usec() - tick)
		steps += 1
	check(model.prepared and model.error.is_empty(), "Preparation must succeed: " + model.error)
	if not model.prepared:
		quit(1)
		return
	print("PREPARE: %.3f s CPU, %d calls, max %d us (4096 cell budget)" % [(Time.get_ticks_usec()-before)/1000000.0, steps, max_prepare])
	for i in model.regions.size():
		var order: PackedInt32Array = model.regions[i].order
		var sorted := order.duplicate()
		sorted.sort()
		check(order.size() == int(data.regions[i].raster_area) and digest(sorted.to_byte_array()) == data.regions[i].mask_sha256, "Region %d exact independent Python mask: no leak or missing pixels" % i)
		var seen: Dictionary = {}
		var connected := order[0] == int(data.regions[i].seed[1])*640+int(data.regions[i].seed[0])
		for cell in order:
			if not seen.is_empty():
				connected = connected and (seen.has(cell-640) or seen.has(cell+640) or (cell%640>0 and seen.has(cell-1)) or (cell%640<639 and seen.has(cell+1)))
			connected = connected and not seen.has(cell)
			seen[cell] = true
		check(connected, "Region %d grows through adjacent unique cells from its seed" % i)
	var path := PackedVector2Array([Vector2(0, 0), Vector2(3, 0), Vector2(3, 4)])
	var partial := Playback.partial_path(path, 5.0)
	check(partial.size() == 3 and partial[-1].is_equal_approx(Vector2(3, 2)), "Interpolation traverses intermediate segments at arc distance")
	check(Playback.partial_path(path, 1.5)[-1].is_equal_approx(Vector2(1.5, 0)), "Interpolation reveals a partial first segment")
	model.replay()
	model.advance(0.1)
	check(not model.visible_paths().is_empty() and model.visible_paths().size() < model.lines.size(), "Partial contour before details")
	check(model.image.get_data() != model.final_fill.get_data(), "Fill not already final during contour phase")
	model.advance(2.2)
	check(model.last_painted > 0 and model.last_painted <= Playback.PAINT_BUDGET, "Spatial fill begins with bounded work")
	var occlusion_ok := true
	for cell in model.owners.size():
		if model.owners[cell] > 0 and model.image.get_pixel(cell%640, cell/640) != Color(String(data.background)):
			occlusion_ok = false
	check(occlusion_ok, "Initial sky front cannot paint inside any later foreground region")
	var max_paint := 0
	var schedule: Array[float] = [1.0/24, 1.0/60, 1.0/144]
	for dt in schedule:
		model.replay()
		var simulated := 0.0
		var frames := 0
		while model.running and frames < 2000:
			var tick := Time.get_ticks_usec()
			model.advance(dt)
			max_paint = maxi(max_paint, Time.get_ticks_usec() - tick)
			simulated += dt
			frames += 1
		check(model.complete and absf(simulated-model.duration) <= dt*1.01, "Duration at %.0f FPS: %.6f s, target %.3f" % [1.0/dt, simulated, model.duration])
		check(model.image.get_data() == model.final_fill.get_data(), "Full playback equals direct final fill at %.0f FPS" % (1.0/dt))
		print("CLOCK: %.0f FPS / %d frames / %.6f s" % [1.0/dt, frames, simulated])
	var final_paths := var_to_bytes(model.visible_paths())
	for at: float in [0.0, 1.1, 2.5, 3.4]:
		model.replay()
		model.advance(at)
		model.skip()
		check(model.complete and model.image.get_data() == model.final_fill.get_data() and var_to_bytes(model.visible_paths()) == final_paths, "Skip at %.1f produces same fill and contour geometry" % at)
	model.replay()
	model.advance(2.8)
	model.advance(10.0)
	check(model.last_painted <= Playback.PAINT_BUDGET and model.running, "Large time jump retains bounded backlog instead of skipping fill")
	var catchup := 0
	while model.running and catchup < 100:
		model.advance(0.0)
		catchup += 1
	check(model.complete and model.image.get_data() == model.final_fill.get_data(), "Backlog drains without losing final pixels")
	model.replay()
	model.advance(2.8)
	model.cancel()
	var blank := model.image.get_data()
	model.advance(9.0)
	check(not model.active and model.visible_paths().is_empty() and model.image.get_data() == blank, "Cancel clears picture and rejects stale advances")
	var view := View.new()
	root.add_child(view)
	view.set_process(false)
	while not view.model.prepared and view.model.error.is_empty():
		view.model.prepare_step()
	view.show_room("NO_ART")
	view.show_room("LOC_START")
	check(view.model.running, "First visit starts playback")
	view.model.advance(0.8)
	view.show_room("LOC_START")
	check(is_equal_approx(view.model.elapsed, 0.8), "Same-room presentation refresh does not restart")
	view.show_room("NO_ART")
	check(not view.model.active and view.paths.is_empty(), "Room change removes old geometry")
	view.show_room("LOC_START")
	check(view.model.complete and not view.model.running, "Repeated visit shows final without waiting")
	view.replay()
	check(view.model.running and is_zero_approx(view.model.elapsed), "Replay remains voluntary")
	view.skip()
	check(view.model.complete, "Presentation skip works")
	root.remove_child(view)
	view.free()
	print("PAINT: max %d us per advance; no more than %d cells per call" % [max_paint, Playback.PAINT_BUDGET])
	print("CAR-ART-002: %d checks, %d failures; visual acceptance NOT tested" % [checks, failures])
	quit(1 if failures > 0 else 0)
