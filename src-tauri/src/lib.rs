// 关于 Tauri 命令调用的详细文档请参考：https://tauri.app/develop/calling-rust/
pub mod app;
pub mod commands;
pub mod config;
pub mod core;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    use app::webview::UrlStack;
    use app::window;

    core::logger::init().expect("Failed to initialize logger");

    // 禁用 WebView2 硬件 GPU 加速以降低 100MB+ 内存占用并提升性能
    std::env::set_var("WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS", "--disable-gpu");

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .on_window_event(window::listener)
        .manage(UrlStack::default())
        .invoke_handler(commands_collector::register!())
        .setup(window::init)
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
