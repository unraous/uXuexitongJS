use super::CommandsResult;

use anyhow::anyhow;
use tauri::{window::Window, Emitter, Manager};

/// 显示主窗口并启动遮罩开屏动画。
#[tauri::command]
#[specta::specta]
pub fn start_mask(window: Window) -> CommandsResult<()> {
    window.show()?;
    let mask = window
        .get_webview("mask")
        .ok_or_else(|| anyhow!("未找到遮罩 Webview"))?;
    mask.emit("start-event", &())?;
    Ok(())
}

/// 显示已在后台加载完成的主界面和超星 Webview。
#[tauri::command]
#[specta::specta]
pub fn show_content(window: Window) -> CommandsResult<()> {
    let main = window
        .get_webview("main")
        .ok_or_else(|| anyhow!("未找到主界面 Webview"))?;
    let chaoxing = window
        .get_webview("chaoxing")
        .ok_or_else(|| anyhow!("未找到超星 Webview"))?;

    main.show()?;
    chaoxing.show()?;
    Ok(())
}

/// 异步隐藏遮罩，避免遮罩 Webview 在自身 IPC 调用链中等待可见性更新。
#[tauri::command]
#[specta::specta]
pub fn hide_mask(window: Window) -> CommandsResult<()> {
    let mask = window
        .get_webview("mask")
        .ok_or_else(|| anyhow!("未找到遮罩 Webview"))?;

    tauri::async_runtime::spawn(async move {
        if let Err(e) = mask.hide() {
            log::error!("隐藏遮罩 Webview 失败: {}", e);
        }
    });
    Ok(())
}
