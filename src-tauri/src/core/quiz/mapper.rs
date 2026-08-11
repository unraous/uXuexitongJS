use rayon::prelude::*;
use std::collections::HashMap;

use super::html::{HtmlExtractPayload, Question};
use super::recognizer::CRNN;
use super::render::render_glyphs;

fn map_font(font: &[u8]) -> HashMap<char, char> {
    let glyphs = render_glyphs(font).unwrap_or_default();

    let font_map: HashMap<char, char> = glyphs
        .into_par_iter()
        .map(|glyph| {
            let recognized_char = CRNN
                .predict(glyph.image)
                .unwrap_or_default()
                .chars()
                .next()
                .unwrap_or('?');
            (glyph.original_char, recognized_char)
        })
        .collect();

    log::debug!("成功解析并识别 {} 个字形", font_map.len());
    font_map
}

fn map(text: &str, font_map: &HashMap<char, char>) -> String {
    text.chars()
        .map(|c| font_map.get(&c).cloned().unwrap_or(c))
        .collect()
}

pub fn decrypt(payload: HtmlExtractPayload) -> Vec<Question> {
    if let Some(font_data) = payload.font {
        log::info!("检测到加密字体，正在尝试解密...");
        let font_map = map_font(&font_data);
        payload
            .questions
            .into_iter()
            .map(|q| Question {
                id: map(&q.id, &font_map),
                kind: map(&q.kind, &font_map),
                stem: map(&q.stem, &font_map),
                options: q
                    .options
                    .into_iter()
                    .map(|opt| map(&opt, &font_map))
                    .collect(),
            })
            .collect()
    } else {
        log::info!("未检测到加密字体，跳过解密步骤");
        payload.questions
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::to_value;
    use std::collections::HashMap;

    #[test]
    fn test_map_basic() {
        let mut font_map = HashMap::new();
        font_map.insert('a', 'x');
        font_map.insert('b', 'y');
        let out = map("abc", &font_map);
        assert_eq!(out, "xyc");
    }

    #[test]
    fn test_map_unmapped_chars_unchanged() {
        let font_map = HashMap::new();
        let out = map("héllo", &font_map);
        assert_eq!(out, "héllo");
    }

    #[test]
    fn test_decrypt_no_font_returns_same_questions() {
        let q1 = Question {
            id: "1".into(),
            kind: "single".into(),
            stem: "What is 1+1?".into(),
            options: vec!["A. 1".into(), "B. 2".into()],
        };
        let q2 = Question {
            id: "2".into(),
            kind: "multi".into(),
            stem: "Choose colors".into(),
            options: vec!["Red".into(), "Blue".into()],
        };

        let questions = vec![q1.clone(), q2.clone()];
        let payload = HtmlExtractPayload {
            questions: questions.clone(),
            font: None,
        };
        let decrypted = decrypt(payload);

        let expected = to_value(&questions).expect("serialize expected failed");
        let actual = to_value(&decrypted).expect("serialize actual failed");
        assert_eq!(expected, actual);
    }

    #[test]
    fn test_decrypt_flow() {
        let html = include_str!("../../../tests/assets/course-page/webpage.html");
        let raw = HtmlExtractPayload::new(html).expect("Failed to parse HTML");
        let start = std::time::Instant::now();
        let decrypted = decrypt(raw);
        println!("🚀 字体 OCR 解密解析 256 个字形总耗时: {:?}", start.elapsed());

        let f = std::fs::File::create("tests/assets/course-page/decrypted.json")
            .expect("create output file failed");
        serde_json::to_writer_pretty(f, &decrypted).expect("write decrypted json failed");
    }
}
