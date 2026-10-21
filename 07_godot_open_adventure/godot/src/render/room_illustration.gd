# Renders a room illustration from the line-and-fill data format.
#
# The illustration is stored as data, following the decision recorded in
# 03_reinterpretation/CREATIVE_BIBLE.md: first the lines are traced, then the
# zones are filled with a flood fill.  The renderer only consumes that data.
class_name RoomIllustration
extends RefCounted

var grid: Vector2i = Vector2i(64, 40)
var background: Color = Color.BLACK
var lines: Array[Dictionary] = []
var fills: Array[Dictionary] = []
var palette: Dictionary = {}


static func from_dict(data: Dictionary, palette: Dictionary) -> RoomIllustration:
	var illustration := RoomIllustration.new()
	illustration.palette = palette
	var size: Array = data.get("grid", [64, 40])
	illustration.grid = Vector2i(int(size[0]), int(size[1]))
	illustration.background = illustration._color(String(data.get("background", "night")))
	illustration.lines.clear()
	for line in data.get("lines", []):
		illustration.lines.append(line)
	illustration.fills.clear()
	for fill in data.get("fills", []):
		illustration.fills.append(fill)
	return illustration


func _color(name: String) -> Color:
	if palette.has(name):
		return Color(String(palette[name]))
	return Color.MAGENTA


## Render the scene into a pixel-art texture (one pixel per grid cell).
func render() -> ImageTexture:
	return ImageTexture.create_from_image(render_image())


## Render the scene into a raw image, one pixel per grid cell.
func render_image() -> Image:
	var width := grid.x
	var height := grid.y
	var image := Image.create(width, height, false, Image.FORMAT_RGBA8)
	image.fill(background)

	var ink := PackedByteArray()
	ink.resize(width * height)
	ink.fill(0)

	for line in lines:
		var color := _color(String(line.get("color", "night")))
		var points: Array = line.get("points", [])
		for index in range(points.size() - 1):
			var from := Vector2i(int(points[index][0]), int(points[index][1]))
			var to := Vector2i(int(points[index + 1][0]), int(points[index + 1][1]))
			_draw_line(image, ink, from, to, color)

	for fill in fills:
		var color := _color(String(fill.get("color", "night")))
		var seed_value: Array = fill.get("seed", [0, 0])
		var seed := Vector2i(int(seed_value[0]), int(seed_value[1]))
		_fill_region(image, ink, seed, color)

	return image


func _draw_line(image: Image, ink: PackedByteArray, from: Vector2i, to: Vector2i, color: Color) -> void:
	var x0 := from.x
	var y0 := from.y
	var x1 := to.x
	var y1 := to.y
	var dx := absi(x1 - x0)
	var dy := -absi(y1 - y0)
	var sx := 1 if x0 < x1 else -1
	var sy := 1 if y0 < y1 else -1
	var error := dx + dy
	var guard := 0
	while guard < 10000:
		guard += 1
		if x0 >= 0 and x0 < grid.x and y0 >= 0 and y0 < grid.y:
			ink[y0 * grid.x + x0] = 1
			image.set_pixel(x0, y0, color)
		if x0 == x1 and y0 == y1:
			break
		var doubled := error * 2
		if doubled >= dy:
			error += dy
			x0 += sx
		if doubled <= dx:
			error += dx
			y0 += sy


func _fill_region(image: Image, ink: PackedByteArray, seed: Vector2i, color: Color) -> void:
	var start := _find_free_cell(ink, seed)
	if start.x < 0:
		return
	var width := grid.x
	var height := grid.y
	var visited := PackedByteArray()
	visited.resize(width * height)
	visited.fill(0)

	var stack := PackedInt32Array()
	stack.append(start.y * width + start.x)
	visited[start.y * width + start.x] = 1

	while stack.size() > 0:
		var index := stack[stack.size() - 1]
		stack.remove_at(stack.size() - 1)
		var x := index % width
		var y := index / width
		image.set_pixel(x, y, color)
		var offsets: Array[Vector2i] = [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]
		for offset: Vector2i in offsets:
			var nx := x + offset.x
			var ny := y + offset.y
			if nx < 0 or nx >= width or ny < 0 or ny >= height:
				continue
			var neighbour := ny * width + nx
			if visited[neighbour] == 1 or ink[neighbour] == 1:
				continue
			visited[neighbour] = 1
			stack.append(neighbour)


## The seed may land on a traced line; look for the closest free cell.
func _find_free_cell(ink: PackedByteArray, seed: Vector2i) -> Vector2i:
	if seed.x < 0 or seed.x >= grid.x or seed.y < 0 or seed.y >= grid.y:
		return Vector2i(-1, -1)
	if ink[seed.y * grid.x + seed.x] == 0:
		return seed
	for radius in range(1, 8):
		for dy in range(-radius, radius + 1):
			for dx in range(-radius, radius + 1):
				if absi(dx) != radius and absi(dy) != radius:
					continue
				var nx := seed.x + dx
				var ny := seed.y + dy
				if nx < 0 or nx >= grid.x or ny < 0 or ny >= grid.y:
					continue
				if ink[ny * grid.x + nx] == 0:
					return Vector2i(nx, ny)
	return Vector2i(-1, -1)
