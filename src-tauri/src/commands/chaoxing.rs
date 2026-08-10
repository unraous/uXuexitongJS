use super::CommandsResult;

use crate::core::quiz::{llm::AnswerItem, solve};

use anyhow::anyhow;
use specta::Type;
use tauri::Emitter;

#[tauri::command]
pub async fn solve_quiz(html: String) -> CommandsResult<Vec<AnswerItem>> {
    match solve(&html).await {
        Ok(answers) => {
            log::info!("solve_quiz 答题成功，获得答案数量: {}", answers.len());
            Ok(answers)
        }
        Err(e) => {
            log::error!("solve_quiz 答题失败，详细原因: {:?}", e);
            Err(e.into())
        }
    }
}

#[derive(Debug, serde::Serialize, serde::Deserialize, Type, Clone)]
#[serde(rename_all = "camelCase")]
pub struct TaskStatus {
    pub total: i32,
    pub completed: i32,
    pub title: String,
}

#[tauri::command]
#[specta::specta]
pub fn send_chapter_status(webview: tauri::Webview, status: TaskStatus) -> CommandsResult<()> {
    if webview.label() == "main" {
        log::warn!("[send_task_status] 拒绝由 [main] 界面发起的非法调用");
        return Err(anyhow!("指令 send_task_status 禁止由 [main] 界面调用").into());
    }
    log::info!(
        "接收到来自 [{}] 的章节完成状态: {:?}",
        webview.label(),
        status
    );
    webview
        .emit_to("main", "chapter-status-update", status)
        .ok();
    Ok(())
}
