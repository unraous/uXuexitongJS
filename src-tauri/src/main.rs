// Release 模式下用于隐藏 Windows 控制台附加窗口的标志，请勿移除！
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    uxs_lib::run()
}
