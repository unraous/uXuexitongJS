use anyhow::Result;
use base64::engine::general_purpose::STANDARD;
use base64::Engine;
use regex::Regex;
use scraper::{Html, Selector};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Question {
    #[serde(rename = "题号")]
    pub id: String,
    #[serde(rename = "题型")]
    pub kind: String,
    #[serde(rename = "题干")]
    pub stem: String,
    #[serde(rename = "选项")]
    pub options: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct HtmlExtractPayload {
    pub questions: Vec<Question>,
    pub font: Option<Vec<u8>>,
}

fn extract_font(html: &str) -> Option<Vec<u8>> {
    let re = Regex::new(
        r#"@font-face\s*\{[^}]*font-family\s*:\s*['\"]font-cxsecret['\"][^}]*src\s*:\s*url\(\s*['\"]data:application/font-ttf[^,]*,([^'\"\\)]+)['\"]\s*\)"#,
    ).unwrap();

    re.captures(html).and_then(|cap| {
        let b64str = cap.get(1)?.as_str();
        STANDARD.decode(b64str).ok()
    })
}

fn trim(s: &str) -> String {
    s.split_whitespace()
        .collect::<Vec<_>>()
        .join(" ")
        .trim()
        .to_string()
}

fn select_options(elem: &scraper::element_ref::ElementRef) -> Vec<String> {
    Selector::parse("li")
        .ok()
        .map(|sel| {
            elem.select(&sel)
                .map(|li| trim(&li.text().collect::<String>()))
                .filter(|t| !t.is_empty())
                .collect()
        })
        .unwrap_or_default()
}

fn select_text(elem: &scraper::element_ref::ElementRef, selector: &str) -> Option<String> {
    Selector::parse(selector)
        .ok()
        .and_then(|sel| elem.select(&sel).next())
        .map(|e| trim(&e.text().collect::<String>()))
}

fn extract_questions(html: &str) -> Vec<Question> {
    let document = Html::parse_document(html);

    document
        .select(&Selector::parse("div.TiMu.newTiMu").unwrap())
        .enumerate()
        .map(|(idx, qelem)| Question {
            id: select_text(&qelem, "i.fl").unwrap_or_else(|| (idx + 1).to_string()),
            kind: select_text(&qelem, "span.newZy_TItle").unwrap_or_default(),
            stem: select_text(&qelem, "div.fontLabel").unwrap_or_default(),
            options: select_options(&qelem),
        })
        .collect()
}

#[cfg(test)]
pub fn load_test_html(compressed: &[u8]) -> String {
    use flate2::read::GzDecoder;
    use std::io::Read;

    let mut decoder = GzDecoder::new(compressed);
    let mut html = String::new();
    decoder
        .read_to_string(&mut html)
        .expect("failed to decompress test HTML resource");
    html
}

impl HtmlExtractPayload {
    pub fn new(html: &str) -> Result<Self> {
        let font = extract_font(html);
        let questions = extract_questions(html);
        if questions.is_empty() {
            anyhow::bail!("NoQuestionsFound")
        } else {
            Ok(Self { questions, font })
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn normalize_whitespace(value: &mut serde_json::Value) {
        match value {
            serde_json::Value::String(text) => {
                *text = text.split_whitespace().collect::<Vec<_>>().join(" ");
            }
            serde_json::Value::Array(items) => {
                for item in items {
                    normalize_whitespace(item);
                }
            }
            serde_json::Value::Object(fields) => {
                for (key, item) in fields.iter_mut() {
                    normalize_whitespace(item);
                    if key == "选项" {
                        if let serde_json::Value::Array(options) = item {
                            for option in options {
                                if let serde_json::Value::String(text) = option {
                                    let mut chars = text.chars();
                                    if let Some(label @ 'A'..='D') = chars.next() {
                                        *text = format!("{}{}", label, chars.as_str().trim_start());
                                    }
                                }
                            }
                        }
                    }
                }
            }
            _ => {}
        }
    }

    #[test]
    fn test_extraction() {
        let compressed = include_bytes!("../../../tests/assets/course-page/webpage.html.gz");
        let html = load_test_html(compressed);
        let raw = HtmlExtractPayload::new(&html).expect("Failed to parse HTML");

        let expected_json: serde_json::Value = serde_json::from_str(include_str!(
            "../../../tests/assets/course-page/questions.json"
        ))
        .expect("Invalid expected questions.json");
        let mut actual_json =
            serde_json::to_value(&raw.questions).expect("Serialize parsed questions failed");
        let mut expected_json = expected_json;
        normalize_whitespace(&mut expected_json);
        normalize_whitespace(&mut actual_json);
        assert_eq!(
            expected_json, actual_json,
            "Parsed questions differ from questions.json after whitespace normalization"
        );

        let expected_ttf = include_bytes!("../../../tests/assets/course-page/cxs-font.ttf");
        let actual_ttf = raw.font.as_ref().expect("No font extracted from HTML");
        assert_eq!(
            expected_ttf,
            actual_ttf.as_slice(),
            "Extracted font bytes differ from cxs-font.ttf"
        );

        let blank = HtmlExtractPayload::new("");
        assert!(blank.is_err(), "Empty HTML should return an error");
    }
}
