use crate::config::CONFIG;

use chrono::Local;
use fern::Dispatch;
use log::info;
use std::{fs::OpenOptions, io::Write, sync::mpsc, thread};

/// 基于 `fern` 框架与 `mpsc` 通道后台线程实现的非阻塞日志系统初始化处理。
pub fn init() -> Result<(), fern::InitError> {
    CONFIG.paths.ensure()?;

    let log_file =
        CONFIG.paths.dirs["logs"].join(format!("{}.log", Local::now().format("%Y-%m-%d_%H-%M-%S")));

    let (sender, receiver) = mpsc::channel::<String>();

    let thread_log_file = log_file.clone();
    thread::spawn(move || {
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&thread_log_file)
            .ok();

        while let Ok(msg) = receiver.recv() {
            println!("{}", msg);
            if let Some(ref mut f) = file {
                let _ = writeln!(f, "{}", msg);
            }
        }
    });

    Dispatch::new()
        .format(|out, message, record| {
            out.finish(format_args!(
                "[{} {} {}] {}",
                Local::now().format("%Y-%m-%d %H:%M:%S"),
                record.level(),
                record.target(),
                message
            ))
        })
        .chain(fern::Output::sender(sender, ""))
        .level(log::LevelFilter::Info)
        .level_for("uxs_lib", CONFIG.metadata.log_level)
        .apply()?;

    info!("日志系统初始化成功，日志文件路径: {}", log_file.display());
    Ok(())
}
