use proc_macro::TokenStream;
use quote::quote;
use std::env;
use std::fs;
use std::path::PathBuf;
use syn::{visit::Visit, ItemFn};
use walkdir::WalkDir;

struct CommandEntry {
    path: syn::Path,
    name: String,
    cfgs: Vec<syn::Attribute>,
    is_specta: bool,
}

struct CommandVisitor {
    module_name: String,
    commands: Vec<CommandEntry>,
}

impl<'ast> Visit<'ast> for CommandVisitor {
    fn visit_item_fn(&mut self, node: &'ast ItemFn) {
        let is_command = node.attrs.iter().any(|attr| {
            let path = attr.path();
            path.segments.len() == 2
                && path.segments[0].ident == "tauri"
                && path.segments[1].ident == "command"
        });

        if is_command {
            let is_specta = node.attrs.iter().any(|attr| {
                let path = attr.path();
                path.segments.last().is_some_and(|s| s.ident == "specta")
            });

            let fn_name = &node.sig.ident;
            let command_name = fn_name.to_string();
            let full_path = format!("crate::commands::{}::{}", self.module_name, fn_name);
            let cfgs: Vec<syn::Attribute> = node
                .attrs
                .iter()
                .filter(|attr| attr.path().is_ident("cfg"))
                .cloned()
                .collect();

            if let Ok(path) = syn::parse_str::<syn::Path>(&full_path) {
                self.commands.push(CommandEntry {
                    path,
                    name: command_name,
                    cfgs,
                    is_specta,
                });
            }
        }

        syn::visit::visit_item_fn(self, node);
    }
}

#[proc_macro]
pub fn register(_: TokenStream) -> TokenStream {
    let manifest_dir = env::var("CARGO_MANIFEST_DIR").unwrap_or_else(|_| ".".to_string());
    let manifest_path = PathBuf::from(&manifest_dir);

    let commands_dir = manifest_path.join("src").join("commands");
    let perm_file = manifest_path.join("permissions").join("commands-main.json");

    let mut commands: Vec<CommandEntry> = Vec::new();
    let mut tracked_files = Vec::new();

    if commands_dir.exists() {
        for entry in WalkDir::new(&commands_dir)
            .into_iter()
            .filter_map(|e| e.ok())
        {
            let path = entry.path();
            if !path.is_file() || path.extension().and_then(|s| s.to_str()) != Some("rs") {
                continue;
            }

            tracked_files.push(path.to_string_lossy().into_owned());

            let relative = match path.strip_prefix(&commands_dir) {
                Ok(r) => r.with_extension(""),
                Err(_) => continue,
            };

            let components: Vec<&str> = relative
                .components()
                .filter_map(|c| c.as_os_str().to_str())
                .collect();

            if components.is_empty() {
                continue;
            }

            let module_name = components.join("::");

            let content = fs::read_to_string(path).expect("auto_handler: failed to read file");
            let syntax_tree =
                syn::parse_file(&content).expect("auto_handler: failed to parse file");

            let mut visitor = CommandVisitor {
                module_name,
                commands: Vec::new(),
            };
            visitor.visit_file(&syntax_tree);

            commands.extend(visitor.commands);
        }
    }

    let mut all_command_names: Vec<String> = commands.iter().map(|c| c.name.clone()).collect();
    all_command_names.sort();
    all_command_names.dedup();

    if perm_file.exists() {
        if let Ok(content) = fs::read_to_string(&perm_file) {
            if let Ok(mut json) = serde_json::from_str::<serde_json::Value>(&content) {
                if let Some(allow) = json.pointer_mut("/permission/0/commands/allow") {
                    *allow = serde_json::json!(all_command_names);
                    if let Ok(new_content) = serde_json::to_string_pretty(&json) {
                        if new_content != content {
                            let _ = fs::write(&perm_file, new_content);
                        }
                    }
                }
            }
        }
    }

    let all_command_tokens: Vec<_> = commands
        .iter()
        .map(|c| {
            let path = &c.path;
            let cfgs = &c.cfgs;
            quote! { #(#cfgs)* #path }
        })
        .collect();

    let specta_command_tokens: Vec<_> = commands
        .iter()
        .filter(|c| c.is_specta)
        .map(|c| {
            let path = &c.path;
            let cfgs = &c.cfgs;
            quote! { #(#cfgs)* #path }
        })
        .collect();

    let expanded = quote! {
        {
            #( const _: &[u8] = include_bytes!(#tracked_files); )*
            #[cfg(debug_assertions)]
            {
                tauri_specta::Builder::<tauri::Wry>::new()
                    .commands(tauri_specta::collect_commands![
                        #(#specta_command_tokens),*
                    ])
                    .export(
                        specta_typescript::Typescript::default(),
                        "../src/services/cmds.ts",
                    )
                    .expect("auto_handler: failed to export typescript bindings");
            }
            tauri::generate_handler![
                #(#all_command_tokens),*
            ]
        }
    };

    expanded.into()
}

#[cfg(test)]
mod tests {
    use super::*;
    use quote::ToTokens;

    /// Helper: run CommandVisitor on a source string and return collected path strings.
    fn collect_commands(module_name: &str, source: &str) -> Vec<String> {
        let syntax_tree = syn::parse_file(source).expect("failed to parse test source");
        let mut visitor = CommandVisitor {
            module_name: module_name.to_string(),
            commands: Vec::new(),
        };
        visitor.visit_file(&syntax_tree);
        visitor
            .commands
            .iter()
            .map(|c| c.path.to_token_stream().to_string())
            .collect()
    }

    #[test]
    fn detects_tauri_command() {
        let src = r#"
            #[tauri::command]
            pub fn hello() -> String {
                "hello".to_string()
            }
        "#;
        let cmds = collect_commands("greeter", src);
        assert_eq!(cmds, vec!["crate :: commands :: greeter :: hello"]);
    }

    #[test]
    fn skips_plain_functions() {
        let src = r#"
            pub fn not_a_command() -> i32 { 42 }

            fn private_helper() {}
        "#;
        let cmds = collect_commands("utils", src);
        assert!(cmds.is_empty(), "plain functions should be skipped");
    }

    #[test]
    fn collects_multiple_commands() {
        let src = r#"
            #[tauri::command]
            pub fn foo() {}

            pub fn bar() {}

            #[tauri::command]
            pub fn baz() -> bool { true }
        "#;
        let cmds = collect_commands("multi", src);
        assert_eq!(cmds.len(), 2);
        assert!(cmds[0].contains("foo"));
        assert!(cmds[1].contains("baz"));
    }

    #[test]
    fn ignores_other_attributes() {
        let src = r#"
            #[derive(Debug)]
            pub struct Foo;

            #[inline]
            pub fn inlined() {}

            #[allow(dead_code)]
            fn suppressed() {}
        "#;
        let cmds = collect_commands("attrs", src);
        assert!(cmds.is_empty(), "non-tauri attributes should be ignored");
    }

    #[test]
    fn rejects_bare_command_attribute() {
        // Bare #[command] should NOT match — only #[tauri::command] is valid.
        let src = r#"
            #[command]
            pub fn sneaky() {}
        "#;
        let cmds = collect_commands("edge", src);
        assert!(cmds.is_empty(), "bare #[command] should not be matched");
    }

    #[test]
    fn supports_nested_module_path() {
        // Verify that nested module names (from subdirectories) work correctly
        let src = r#"
            #[tauri::command]
            pub fn list_users() {}
        "#;
        let cmds = collect_commands("admin::users", src);
        assert_eq!(
            cmds,
            vec!["crate :: commands :: admin :: users :: list_users"]
        );
    }

    #[test]
    fn module_name_appears_in_path() {
        let src = r#"
            #[tauri::command]
            pub fn action() {}
        "#;
        let cmds = collect_commands("my_module", src);
        assert_eq!(cmds.len(), 1);
        assert!(
            cmds[0].contains("my_module"),
            "generated path should include the module name"
        );
    }

    #[test]
    fn preserves_cfg_attributes() {
        let src = r#"
            #[cfg(target_os = "windows")]
            #[tauri::command]
            pub fn win_cmd() {}
        "#;
        let syntax_tree = syn::parse_file(src).expect("failed to parse test source");
        let mut visitor = CommandVisitor {
            module_name: "cfg_mod".to_string(),
            commands: Vec::new(),
        };
        visitor.visit_file(&syntax_tree);
        assert_eq!(visitor.commands.len(), 1);
        assert_eq!(visitor.commands[0].cfgs.len(), 1);
        assert!(visitor.commands[0].cfgs[0].path().is_ident("cfg"));
    }
}
