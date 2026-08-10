mod html;
mod mapper;
mod recognizer;
mod render;

pub mod llm;

use html::HtmlExtractPayload;
use llm::AnswerItem;
use mapper::decrypt;

use crate::config::CONFIG;
use anyhow::Result;

/// 使用 CRNN ONNX 模型动态解析与解密混淆题目，并结合当前全局配置的大语言模型自动生成测验答案。
pub async fn solve(html: &str) -> Result<Vec<AnswerItem>> {
    let decrypted = decrypt(HtmlExtractPayload::new(html)?);
    CONFIG.llm.current().solve(decrypted).await
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::llm::BigModelConfig;
    use llm::LLM;
    use std::fs;
    use std::path::PathBuf;

    #[tokio::test]
    async fn test_solve_html_integration() {
        dotenv::dotenv().ok();
        let api_key = std::env::var("BIGMODEL_API_KEY")
            .expect("请在 .env 文件或环境变量中设置 BIGMODEL_API_KEY");

        let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        path.push("tests/assets/course-page/webpage.html");
        let html_content = fs::read_to_string(&path)
            .unwrap_or_else(|_| panic!("Failed to find test webpage.html at {:?}", path));

        let payload =
            HtmlExtractPayload::new(&html_content).expect("Failed to parse HTML questions");
        let decrypted = decrypt(payload);
        assert!(!decrypted.is_empty(), "解密后的题目列表不应为空");

        let local_solver = BigModelConfig {
            api_key: parking_lot::Mutex::new(api_key),
            ..Default::default()
        };

        println!("正在使用内存局部配置变量调用 BigModel 求解器...");
        match local_solver.solve(decrypted).await {
            Ok(answers) => {
                assert!(!answers.is_empty(), "返回的答案列表不应为空");
                for (i, item) in answers.iter().enumerate() {
                    println!("[{}] 题号: {}, 答案: {}", i + 1, item.index, item.content);
                    println!("    解析: {}", item.explanation);
                }
            }
            Err(e) => {
                panic!("无状态局部求解器执行测试失败: {}", e);
            }
        }
    }
}
