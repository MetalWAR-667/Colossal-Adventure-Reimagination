# Experimental consumer of explicit polylines and closed regions. No game state.
# Fill order is an actual four-neighbour breadth-first flood inside each mask.
extends RefCounted

const PREPARE_BUDGET := 8192
const PAINT_BUDGET := 16000
var data: Dictionary
var grid := Vector2i(640, 400)
var regions: Array[Dictionary] = []
var lines: Array[Dictionary] = []
var prepared := false
var error := ""
var running := false
var active := false
var complete := false
var elapsed := 0.0
var duration := 3.5
var speed := 1.0
var image: Image
var final_fill: Image
var owners := PackedInt32Array()
var last_painted := 0
var _region := 0
var _row := 0
var _mask := PackedByteArray()
var _queue := PackedInt32Array()
var _head := 0
var _area := 0
var _flooding := false
var _filled := PackedInt32Array()


func configure(source: Dictionary) -> void:
	data = source
	grid = Vector2i(int(data.grid[0]), int(data.grid[1]))
	duration = float(data.seconds.contour) + float(data.seconds.detail) + float(data.seconds.fill)
	image = Image.create(grid.x, grid.y, false, Image.FORMAT_RGBA8)
	image.fill(Color(String(data.background)))
	final_fill = image.duplicate()
	owners.resize(grid.x * grid.y)
	owners.fill(-1)
	for record: Dictionary in data.lines:
		var points := _points(record.points)
		var length := 0.0
		for i in range(1, points.size()):
			length += points[i - 1].distance_to(points[i])
		lines.append({"points": points, "length": length, "width": float(record.width), "phase": record.phase})
	for record: Dictionary in data.regions:
		regions.append({"polygon": _points(record.polygon), "seed": Vector2i(int(record.seed[0]), int(record.seed[1])), "color": Color(String(record.color)), "order": PackedInt32Array()})
	_filled.resize(regions.size())
	_begin_region()


func _points(values: Array) -> PackedVector2Array:
	var result := PackedVector2Array()
	for pair: Array in values:
		result.append(Vector2(float(pair[0]), float(pair[1])))
	return result


func _begin_region() -> void:
	_mask = PackedByteArray()
	_mask.resize(grid.x * grid.y)
	_queue = PackedInt32Array()
	_row = 0
	_head = 0
	_area = 0
	_flooding = false


# Finite cell budget. One scanline may exceed the remainder by at most width.
func prepare_step(budget: int = PREPARE_BUDGET) -> void:
	if prepared or not error.is_empty():
		return
	var used := 0
	while used < budget and _region < regions.size():
		var region: Dictionary = regions[_region]
		if not _flooding:
			var crossings := PackedFloat64Array()
			var poly: PackedVector2Array = region.polygon
			var y := float(_row) + 0.5
			for i in range(1, poly.size()):
				var a := poly[i - 1]
				var b := poly[i]
				if (a.y > y) != (b.y > y):
					crossings.append(a.x + (y - a.y) * (b.x - a.x) / (b.y - a.y))
			crossings.sort()
			for i in range(0, crossings.size(), 2):
				for x in range(maxi(0, ceili(crossings[i] - 0.5)), mini(grid.x, ceili(crossings[i + 1] - 0.5))):
					_mask[_row * grid.x + x] = 1
					_area += 1
					used += 1
			_row += 1
			used += 1
			if _row == grid.y:
				var seed: Vector2i = region.seed
				var index := seed.y * grid.x + seed.x
				if index < 0 or index >= _mask.size() or _mask[index] != 1:
					error = "Seed outside region %d" % _region
					return
				_mask[index] = 2
				_queue.append(index)
				_flooding = true
		else:
			while _head < _queue.size() and used < budget:
				var index := _queue[_head]
				_head += 1
				var x := index % grid.x
				var y := index / grid.x
				final_fill.set_pixel(x, y, region.color)
				owners[index] = _region
				for next in [index - grid.x, index + grid.x, index - 1 if x > 0 else -1, index + 1 if x < grid.x - 1 else -1]:
					if next >= 0 and next < _mask.size() and _mask[next] == 1:
						_mask[next] = 2
						_queue.append(next)
				used += 1
			if _head == _queue.size():
				if _queue.size() != _area:
					error = "Disconnected raster region %d: %d / %d" % [_region, _queue.size(), _area]
					return
				regions[_region].order = _queue
				_region += 1
				if _region < regions.size():
					_begin_region()
	if _region == regions.size():
		prepared = true
		_mask.clear()
		_queue = PackedInt32Array()


func replay() -> void:
	if not prepared:
		return
	image.fill(Color(String(data.background)))
	_filled.fill(0)
	elapsed = 0.0
	active = true
	running = true
	complete = false


func skip() -> void:
	if not prepared:
		return
	image = final_fill.duplicate()
	for i in regions.size():
		_filled[i] = regions[i].order.size()
	elapsed = duration
	active = true
	running = false
	complete = true


func cancel() -> void:
	running = false
	active = false
	complete = false
	elapsed = 0.0
	image.fill(Color(String(data.background)))
	_filled.fill(0)


# Clock is independent of FPS. Backlog is drained without exceeding paint budget.
func advance(delta: float) -> void:
	last_painted = 0
	if not running:
		return
	elapsed = minf(duration, elapsed + maxf(0.0, delta) * speed)
	var fill_start := float(data.seconds.contour) + float(data.seconds.detail)
	var fraction := clampf((elapsed - fill_start) / float(data.seconds.fill), 0.0, 1.0)
	var total_weight := 0.0
	for region in regions:
		total_weight += sqrt(float(region.order.size()))
	var remaining := fraction * total_weight
	for i in regions.size():
		var order: PackedInt32Array = regions[i].order
		var weight := sqrt(float(order.size()))
		var target := order.size() if remaining >= weight else floori(order.size() * maxf(0.0, remaining) / weight)
		if elapsed >= duration:
			target = order.size()
		while _filled[i] < target and last_painted < PAINT_BUDGET:
			var index := order[_filled[i]]
			# Closed regions retain source painter order. Never temporarily paint
			# sky/ground over a foreground shape awaiting its own fill.
			if owners[index] == i:
				image.set_pixel(index % grid.x, index / grid.x, regions[i].color)
			_filled[i] += 1
			last_painted += 1
		if _filled[i] < order.size():
			break
		remaining -= weight
	if elapsed >= duration and _filled[-1] == regions[-1].order.size():
		running = false
		complete = true


func visible_paths() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	if not active:
		return result
	for phase: String in ["contour", "detail"]:
		var start := 0.0 if phase == "contour" else float(data.seconds.contour)
		var seconds := float(data.seconds[phase])
		var length := 0.0
		for line in lines:
			if line.phase == phase:
				length += float(line.length)
		var left := length * clampf((elapsed - start) / seconds, 0.0, 1.0)
		for line in lines:
			if line.phase != phase:
				continue
			if left <= 0.0:
				break
			var points := partial_path(line.points, minf(left, line.length))
			if points.size() > 1:
				result.append({"points": points, "width": line.width})
			left -= float(line.length)
	return result


static func partial_path(points: PackedVector2Array, distance: float) -> PackedVector2Array:
	var result := PackedVector2Array([points[0]])
	for i in range(1, points.size()):
		var length := points[i - 1].distance_to(points[i])
		if distance < length:
			result.append(points[i - 1].lerp(points[i], distance / length if length > 0 else 0.0))
			break
		result.append(points[i])
		distance -= length
	return result
