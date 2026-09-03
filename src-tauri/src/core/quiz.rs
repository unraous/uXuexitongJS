mod html;
mod mapper;
mod typr;

pub mod llm;

use html::HtmlExtractPayload;
use llm::AnswerItem;
use mapper::decrypt;

use crate::config::CONFIG;
use anyhow::Result;

/// 使用字体哈希字典解密混淆题目，并结合当前全局配置的大语言模型自动生成测验答案。
pub async fn solve(html: &str) -> Result<Vec<AnswerItem>> {
    let decrypted = decrypt(HtmlExtractPayload::new(html)?);
    if decrypted.is_empty() {
        anyhow::bail!("题目解析失败");
    }

    let active_id = CONFIG.llm.active_provider.lock().clone();
    let provider = CONFIG
        .llm
        .providers
        .lock()
        .get(&active_id)
        .cloned()
        .ok_or_else(|| anyhow::anyhow!("大模型提供商 [{}] 不存在", active_id))?;
    llm::solve(&provider, decrypted).await
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    #[ignore = "requires network and BIGMODEL_API_KEY"]
    async fn test_solve_html_integration() {
        dotenv::dotenv().ok();
        let api_key = std::env::var("BIGMODEL_API_KEY")
            .expect("请在 .env 文件或环境变量中设置 BIGMODEL_API_KEY");

        let compressed = include_bytes!("../../tests/assets/course-page/webpage.html.gz");
        let html_content = super::html::load_test_html(compressed);

        let payload =
            HtmlExtractPayload::new(&html_content).expect("Failed to parse HTML questions");
        let decrypted = decrypt(payload);
        assert!(!decrypted.is_empty(), "解密后的题目列表不应为空");

        let mut provider = CONFIG
            .llm
            .providers
            .lock()
            .get("bigmodel")
            .cloned()
            .unwrap();
        provider.api_key = Some(crate::config::llm::ApiKey::new(api_key).unwrap());

        println!("正在使用内存局部配置变量调用 BigModel 求解器...");
        match llm::solve(&provider, decrypted).await {
            Ok(answers) => {
                assert!(!answers.is_empty(), "返回的答案列表不应为空");
                for (i, item) in answers.iter().enumerate() {
                    println!("[{}] 题号: {}, 答案: {}", i + 1, item.index, item.content);
                    println!("    解析: {}", item.explanation);
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if err_msg.contains("429") || err_msg.contains("速率限制") {
                    println!(
                        "BigModel HTML 集成测试跳过 (触发 API 速率限制 429): {}",
                        err_msg
                    );
                } else {
                    panic!("无状态局部求解器执行测试失败: {}", e);
                }
            }
        }
    }
}
