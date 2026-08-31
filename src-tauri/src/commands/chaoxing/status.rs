use serde::{Deserialize, Serialize};
use specta::Type;

#[derive(Debug, Serialize, Deserialize, Type, Clone)]
#[serde(rename_all = "camelCase")]
pub struct TotalProgressPayload {
    pub total: i32,
    pub title: String,
}

#[derive(Debug, Serialize, Deserialize, Type, Clone)]
#[serde(rename_all = "camelCase")]
pub struct ChapterProgressPayload {
    pub index: i32,
    pub completed: i32,
    pub title: String,
}

#[derive(Debug, Serialize, Deserialize, Type, Clone)]
#[serde(rename_all = "camelCase")]
pub struct TabProgressPayload {
    pub total: i32,
    pub index: i32,
}

#[derive(Debug, Serialize, Deserialize, Type, Clone)]
#[serde(rename_all = "camelCase")]
pub struct TaskProgressPayload {
    pub index: i32,
    pub category: String,
}

#[derive(Debug, Serialize, Deserialize, Type, Clone)]
#[serde(rename_all = "camelCase")]
pub enum CourseStatus {
    Waiting,
    Started,
    TotalProgress(TotalProgressPayload),
    ChapterProgress(ChapterProgressPayload),
    TabProgress(TabProgressPayload),
    TaskProgress(TaskProgressPayload),
    Cancelled,
    Finished,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_course_status_serde() {
        for (status, expected) in [
            (CourseStatus::Started, "\"started\""),
            (CourseStatus::Cancelled, "\"cancelled\""),
        ] {
            let json = serde_json::to_string(&status).unwrap();
            assert_eq!(json, expected);
            let deserialized: CourseStatus = serde_json::from_str(expected).unwrap();
            assert_eq!(
                std::mem::discriminant(&deserialized),
                std::mem::discriminant(&status)
            );
        }

        let status = CourseStatus::Finished;
        let json = serde_json::to_string(&status).unwrap();
        assert_eq!(json, "\"finished\"");
        let deserialized: CourseStatus = serde_json::from_str(&json).unwrap();
        assert!(matches!(deserialized, CourseStatus::Finished));

        let status = CourseStatus::TotalProgress(TotalProgressPayload {
            total: 10,
            title: "高等数学".into(),
        });
        let json = serde_json::to_string(&status).unwrap();
        assert_eq!(
            json,
            "{\"totalProgress\":{\"total\":10,\"title\":\"高等数学\"}}"
        );

        let status = CourseStatus::TaskProgress(TaskProgressPayload {
            index: 1,
            category: "Video".into(),
        });
        let json = serde_json::to_string(&status).unwrap();
        assert_eq!(
            json,
            "{\"taskProgress\":{\"index\":1,\"category\":\"Video\"}}"
        );
    }
}
