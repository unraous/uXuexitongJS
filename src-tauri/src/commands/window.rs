use crate::config::CONFIG;

use std::time::Duration;
use tauri::{window, Emitter, Manager};

/// Close the application window with a fade-out animation.
#[tauri::command]
#[specta::specta]
pub async fn close(window: window::Window) {
    if let Some(mask) = window.get_webview("mask") {
        log::debug!("执行关闭动画并关闭窗口");
        mask.show().ok();
        if let Err(e) = mask.emit("close-event", &()) {
            log::error!("发送关闭动画事件失败: {}", e);
        }

        log::debug!("关闭动画执行完毕");
    } else {
        log::error!("未找到遮罩Webview，无法执行关闭动画");
    }

    let sleep = tokio::time::sleep(Duration::from_millis(750));
    let cleanup = async {
        CONFIG.save().ok();
        log::debug!("配置成功保存");
    };

    tokio::join!(sleep, cleanup);
    window.close().ok();
}

/// Minimize the application window.
#[tauri::command]
#[specta::specta]
pub fn minimize(window: window::Window) {
    log::debug!("正在最小化窗口");
    window.minimize().ok();
}
