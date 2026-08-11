//! CRNN (Convolutional Recurrent Neural Network) recognizer for Chinese OCR.
//!
//! The model used in this module is based on the chineseocr_lite project:
//! https://github.com/DayBreak-u/chineseocr_lite
//!
//! This implementation provides character-level recognition capabilities
//! for processing images containing Chinese text.

use anyhow::{bail, Result};
use bytemuck::cast_slice;
use image::DynamicImage;
use std::sync::LazyLock;
use tract::prelude::*;

pub struct CrnnEngine {
    model: Runnable,
    labels: Vec<&'static str>,
}

impl Default for CrnnEngine {
    fn default() -> Self {
        let model = (|| -> Result<Runnable> {
            let model = tract::onnx()?
                .load_buffer(include_bytes!("../../../model/chineseocr_lite.onnx"))?
                .into_model()?
                .into_runnable()?;
            Ok(model)
        })()
        .expect("无法初始化 CRNN OCR 模型。请检查模型文件是否完整或硬件环境。");
        log::debug!("CRNN 模型与标签加载成功");
        let labels = include_str!("../../../model/keys.txt").lines().collect();

        CrnnEngine { model, labels }
    }
}

impl CrnnEngine {
    fn decode_output(&self, indices: &[usize], length: usize) -> Result<String> {
        Self::decode_output_with_labels(&self.labels, indices, length)
    }

    fn decode_output_with_labels(
        labels: &[&str],
        indices: &[usize],
        length: usize,
    ) -> Result<String> {
        let mut output = String::new();
        for i in 0..length {
            if indices[i] != 0 && !(i > 0 && indices[i - 1] == indices[i]) {
                if let Some(label) = labels.get(indices[i] - 1) {
                    output.push_str(label);
                }
            }
        }
        Ok(output)
    }

    pub fn predict(&self, image: DynamicImage) -> Result<String> {
        let img_rgb = image.to_rgb8();
        let (w, h) = img_rgb.dimensions();

        if w == 0 || h == 0 {
            bail!("图片为空，无法进行 OCR 识别。");
        }

        let scale = h as f32 / 32.0;
        let new_w = (w as f32 / scale) as u32;
        let img_resized =
            image::imageops::resize(&img_rgb, new_w, 32, image::imageops::FilterType::Triangle);

        // 构造 BCHW 格式的数据
        let mut data_bchw = vec![0.0; 96 * (new_w as usize)];

        for y in 0..32 {
            for x in 0..new_w {
                let pixel = img_resized.get_pixel(x, y);
                for c in 0..3 {
                    let val = pixel.0[c] as f32;
                    let normalized = (val / 127.5) - 1.0;
                    let idx =
                        c * 32 * (new_w as usize) + (y as usize) * (new_w as usize) + (x as usize);
                    data_bchw[idx] = normalized;
                }
            }
        }

        let input = Tensor::from_bytes(
            DatumType::F32,
            &[1, 3, 32, new_w as usize],
            cast_slice(&data_bchw),
        )?;
        let pred_tensor = &self.model.run([input])?[0];

        let (_dt, shape, raw_bytes) = pred_tensor.as_bytes()?;
        let pred_data: &[f32] = cast_slice(raw_bytes);

        let seq_len = shape[0];
        let num_classes = shape[2];

        let mut result = Vec::new();
        for t in 0..seq_len {
            let mut max_idx = 0;
            let mut max_val = f32::NEG_INFINITY;
            for c in 0..num_classes {
                let val = pred_data[t * num_classes + c];
                if val > max_val {
                    max_val = val;
                    max_idx = c;
                }
            }
            result.push(max_idx);
        }

        self.decode_output(&result, seq_len)
    }
}

pub static CRNN: LazyLock<CrnnEngine> = LazyLock::new(CrnnEngine::default);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ctc_decode_output_algorithm() {
        let labels = vec!["A", "B", "C", "D"];

        // 测试项 1: CTC Blank (0) 被滤除，连续重复字符被压缩
        // 索引序列: [1, 1, 0, 2, 2, 3, 0, 4] -> 对应 1(A), 2(B), 3(C), 4(D) -> 结果应为 "ABCD"
        let indices = vec![1, 1, 0, 2, 2, 3, 0, 4];
        let decoded =
            CrnnEngine::decode_output_with_labels(&labels, &indices, indices.len()).unwrap();
        assert_eq!(decoded, "ABCD");

        // 测试项 2: 空序列处理
        let decoded_empty = CrnnEngine::decode_output_with_labels(&labels, &[], 0).unwrap();
        assert_eq!(decoded_empty, "");

        // 测试项 3: 全为 CTC Blank (0) 索引
        let blanks = vec![0, 0, 0, 0];
        let decoded_blanks =
            CrnnEngine::decode_output_with_labels(&labels, &blanks, blanks.len()).unwrap();
        assert_eq!(decoded_blanks, "");
    }
}
