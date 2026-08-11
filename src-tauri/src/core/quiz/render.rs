use anyhow::Result;
use fontdue::Font;
use image::DynamicImage;
use ttf_parser::Face;

#[derive(Clone)]
pub struct GlyphImage {
    pub original_char: char,
    pub image: DynamicImage,
}

const PADDING: u32 = 16; // 白色padding的宽度（像素）

fn codepoint(glyph_id: u16, cmap: ttf_parser::cmap::Table) -> Option<u32> {
    for subtable in cmap.subtables {
        let mut result = None;
        subtable.codepoints(|cp| {
            if subtable.glyph_index(cp) == Some(ttf_parser::GlyphId(glyph_id)) {
                result = Some(cp);
            }
        });
        if result.is_some() {
            return result;
        }
    }
    None
}

use rayon::prelude::*;

pub fn render_glyphs(font_data: &[u8]) -> Result<Vec<GlyphImage>> {
    let face = Face::parse(font_data, 0)?;
    let font = Font::from_bytes(font_data, fontdue::FontSettings::default())
        .map_err(|e| anyhow::anyhow!(e))?;
    let cmap = face.tables().cmap;

    let num_glyphs = face.number_of_glyphs();
    let results: Vec<GlyphImage> = (0..num_glyphs)
        .into_par_iter()
        .filter_map(|glyph_id| {
            let cmap = cmap?;
            let cp = codepoint(glyph_id, cmap)?;
            let char_val = char::from_u32(cp)?;
            let (metrics, bitmap) = font.rasterize(char_val, 64.0);

            let orig_width = metrics.width as u32;
            let orig_height = metrics.height as u32;

            if orig_width == 0 || orig_height == 0 {
                return None;
            }

            let padded_width = orig_width + 2 * PADDING;
            let padded_height = orig_height + 2 * PADDING;
            let mut luma =
                image::ImageBuffer::<image::Luma<u8>, Vec<u8>>::new(padded_width, padded_height);

            for pixel in luma.pixels_mut() {
                *pixel = image::Luma([255u8]);
            }

            for (i, &b) in bitmap.iter().enumerate() {
                let x = (i % orig_width as usize) as u32 + PADDING;
                let y = (i / orig_width as usize) as u32 + PADDING;
                luma.put_pixel(x, y, image::Luma([255 - b]));
            }

            Some(GlyphImage {
                original_char: char_val,
                image: DynamicImage::ImageLuma8(luma),
            })
        })
        .collect();

    Ok(results)
}
