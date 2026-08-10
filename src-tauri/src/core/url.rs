/// 提供基于 URL 结构与域名分类判定及脚本匹配功能的核心模块。
/// 基于结构与域名特征进行归类的 URL 类型枚举。
#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum Type {
    Course,
    Login,
    MainSpace,
    Mask,
    Other,
    Unknown,
}

/// 判定传入 URL 是否属于超星域名并返回其具体分类类型。
pub fn classify(url: &tauri::Url) -> Type {
    let host = url.host_str().unwrap_or_default();

    if url.as_str() == "about:blank" {
        return Type::Mask;
    }

    if host != "chaoxing.com" && !host.ends_with(".chaoxing.com") {
        return Type::Unknown;
    }

    let sub = host.split('.').next().unwrap_or_default();
    let result = match sub {
        "i" => Type::MainSpace,
        "mooc1" if url.path().starts_with("/mycourse/") => Type::Course,
        "passport2" if url.path().starts_with("/login") => Type::Login,
        _ => Type::Other,
    };

    result
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_classify_urls() {
        let url = "https://i.chaoxing.com".parse().unwrap();
        assert_eq!(classify(&url), Type::MainSpace);

        let url = "https://mooc1.chaoxing.com/mycourse/...".parse().unwrap();
        assert_eq!(classify(&url), Type::Course);

        let url = "https://passport2.chaoxing.com/login?refer=https://www.chaoxing.com"
            .parse()
            .unwrap();
        assert_eq!(classify(&url), Type::Login);

        let url = "about:blank".parse().unwrap();
        assert_eq!(classify(&url), Type::Mask);

        let url = "https://example.com".parse().unwrap();
        assert_eq!(classify(&url), Type::Unknown);
    }
}
