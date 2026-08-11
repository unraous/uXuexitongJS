use tauri::window::Window;
/// 带有渐隐过渡效果的应用窗口关闭指令。
#[tauri::command]
#[specta::specta]
pub async fn close(window: Window) {
    window.close().ok();
}

/// 应用窗口最小化处理指令。
#[tauri::command]
#[specta::specta]
pub fn minimize(window: Window) {
    window.minimize().ok();
}
