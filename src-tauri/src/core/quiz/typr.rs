//! Compatibility helpers for the glyph-path format produced by Typr.js.
//!
//! The hash table is built from Typr.js paths, so this intentionally mirrors its
//! TrueType simple-glyph parsing and path construction instead of using a generic
//! outline representation.

use serde::Serialize;
use ttf_parser::Face;

#[derive(Serialize)]
struct TyprPath {
    cmds: Vec<&'static str>,
    crds: Vec<i32>,
}

impl TyprPath {
    fn point(&mut self, x: i32, y: i32) {
        self.crds.extend([x, y]);
    }

    fn qcurve(&mut self, control_x: i32, control_y: i32, end_x: i32, end_y: i32) {
        self.crds.extend([control_x, control_y, end_x, end_y]);
    }
}

fn midpoint(a: i32, b: i32) -> i32 {
    ((a + b) as f64 * 0.5).floor() as i32
}

fn delta(data: &[u8], offset: &mut usize, flag: u8, short_flag: u8, same_flag: u8) -> Option<i32> {
    if flag & short_flag != 0 {
        let delta = *data.get(*offset)? as i32;
        *offset += 1;
        Some(if flag & same_flag != 0 { delta } else { -delta })
    } else if flag & same_flag == 0 {
        let delta = i16::from_be_bytes(data.get(*offset..*offset + 2)?.try_into().ok()?) as i32;
        *offset += 2;
        Some(delta)
    } else {
        Some(0)
    }
}

fn end_points(data: &[u8], contour_count: usize) -> Option<(Vec<u16>, usize)> {
    let mut offset = 10;
    let mut end_points = Vec::with_capacity(contour_count);
    for _ in 0..contour_count {
        end_points.push(u16::from_be_bytes(
            data.get(offset..offset + 2)?.try_into().ok()?,
        ));
        offset += 2;
    }
    Some((end_points, offset))
}

fn skip_instr(data: &[u8], offset: usize) -> Option<usize> {
    let instruction_length =
        u16::from_be_bytes(data.get(offset..offset + 2)?.try_into().ok()?) as usize;
    offset.checked_add(2 + instruction_length)
}

fn flags(data: &[u8], mut offset: usize, point_count: usize) -> Option<(Vec<u8>, usize)> {
    let mut flags = Vec::with_capacity(point_count);
    while flags.len() < point_count {
        let flag = *data.get(offset)?;
        offset += 1;
        flags.push(flag);
        if flag & 0x08 != 0 {
            let repeat_count = *data.get(offset)? as usize;
            offset += 1;
            flags.extend(std::iter::repeat_n(flag, repeat_count));
        }
    }
    (flags.len() == point_count).then_some((flags, offset))
}

fn coordinates(data: &[u8], mut offset: usize, flags: &[u8]) -> Option<Vec<(i32, i32)>> {
    let mut coordinates = Vec::with_capacity(flags.len());
    let mut x = 0;
    for &flag in flags {
        x += delta(data, &mut offset, flag, 0x02, 0x10)?;
        coordinates.push((x, 0));
    }

    let mut y = 0;
    for (coordinate, &flag) in coordinates.iter_mut().zip(flags) {
        y += delta(data, &mut offset, flag, 0x04, 0x20)?;
        coordinate.1 = y;
    }
    Some(coordinates)
}

fn contour(
    path: &mut TyprPath,
    flags: &[u8],
    coordinates: &[(i32, i32)],
    first_point: usize,
    last_point: usize,
) {
    for point in first_point..=last_point {
        let previous = if point == first_point {
            last_point
        } else {
            point - 1
        };
        let next = if point == last_point {
            first_point
        } else {
            point + 1
        };
        let (x, y) = coordinates[point];
        let previous_on_curve = flags[previous] & 1 != 0;
        let on_curve = flags[point] & 1 != 0;
        let next_on_curve = flags[next] & 1 != 0;

        if point == first_point {
            let (move_x, move_y) = if on_curve && !previous_on_curve {
                (x, y)
            } else if previous_on_curve {
                coordinates[previous]
            } else {
                let (previous_x, previous_y) = coordinates[previous];
                (midpoint(previous_x, x), midpoint(previous_y, y))
            };
            path.cmds.push("M");
            path.point(move_x, move_y);
            if on_curve && !previous_on_curve {
                continue;
            }
        }

        if on_curve && previous_on_curve {
            path.cmds.push("L");
            path.point(x, y);
        } else if !on_curve {
            path.cmds.push("Q");
            if next_on_curve {
                let (next_x, next_y) = coordinates[next];
                path.qcurve(x, y, next_x, next_y);
            } else {
                let (next_x, next_y) = coordinates[next];
                path.qcurve(x, y, midpoint(x, next_x), midpoint(y, next_y));
            }
        }
    }
}

fn path(end_points: &[u16], flags: &[u8], coordinates: &[(i32, i32)]) -> Option<TyprPath> {
    let mut path = TyprPath {
        cmds: Vec::new(),
        crds: Vec::new(),
    };
    let mut first_point = 0;

    for &last_point in end_points {
        let last_point = last_point as usize;
        if first_point > last_point || last_point >= coordinates.len() {
            return None;
        }
        contour(&mut path, flags, coordinates, first_point, last_point);
        path.cmds.push("Z");
        first_point = last_point + 1;
    }
    Some(path)
}

fn parse(data: &[u8]) -> Option<TyprPath> {
    let contour_count = i16::from_be_bytes(data.get(..2)?.try_into().ok()?);
    if contour_count <= 0 || data.len() < 10 {
        return None;
    }

    let (end_points, mut offset) = end_points(data, contour_count as usize)?;
    offset = skip_instr(data, offset)?;
    let point_count = *end_points.last()? as usize + 1;
    let (flags, offset) = flags(data, offset, point_count)?;
    let coordinates = coordinates(data, offset, &flags)?;

    path(&end_points, &flags, &coordinates)
}

fn glyph<'a>(font_data: &'a [u8], loca_offsets: &[usize], gid: usize) -> Option<&'a [u8]> {
    let start = loca_offsets.get(gid).copied()?;
    let end = loca_offsets.get(gid + 1).copied()?;
    font_data.get(start..end)
}

fn hash(path: &TyprPath) -> Option<String> {
    let md5 = format!("{:x}", md5::compute(serde_json::to_vec(path).ok()?));
    Some(md5[24..].to_owned())
}

pub fn glyph_hash(font_data: &[u8], loca_offsets: &[usize], gid: usize) -> Option<String> {
    let data = glyph(font_data, loca_offsets, gid)?;
    let path = parse(data)?;
    hash(&path)
}

pub fn loca_offsets(font_data: &[u8]) -> Option<Vec<usize>> {
    let face = Face::parse(font_data, 0).ok()?;
    let is_32bit = format!("{:?}", face.tables().head.index_to_location_format) == "Long";
    let loca_bytes = face
        .raw_face()
        .table(ttf_parser::Tag::from_bytes(b"loca"))?;
    let glyf_bytes = face
        .raw_face()
        .table(ttf_parser::Tag::from_bytes(b"glyf"))?;
    let glyf_offset = (glyf_bytes.as_ptr() as usize) - (font_data.as_ptr() as usize);
    let num_glyphs = face.number_of_glyphs() as usize;

    let entry_size = if is_32bit { 4 } else { 2 };
    let mut offsets = Vec::with_capacity(num_glyphs + 1);
    for i in 0..=num_glyphs {
        let index = i * entry_size;
        let entry = match loca_bytes.get(index..index + entry_size) {
            Some(entry) => entry,
            None => break,
        };
        let offset = if is_32bit {
            u32::from_be_bytes(entry.try_into().ok()?) as usize
        } else {
            (u16::from_be_bytes(entry.try_into().ok()?) as usize) * 2
        };
        offsets.push(glyf_offset + offset);
    }
    Some(offsets)
}
