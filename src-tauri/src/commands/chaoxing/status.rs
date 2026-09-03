use serde::{Deserialize, Serialize};
use specta::Type;

#[derive(Debug, Serialize, Deserialize, Type, Clone)]
#[serde(rename_all = "camelCase")]
pub struct ChapterProgressPayload {
    pub title: String,
    pub index: i32,
    pub completed: i32,
    pub total: i32,
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
#[serde(rename_all = "camelCase", tag = "kind", content = "payload")]
pub enum CourseStatus {
    Waiting(()),
    Start(()),
    Chapter(ChapterProgressPayload),
    Tab(TabProgressPayload),
    Task(TaskProgressPayload),
    Cancel(()),
    Finish(()),
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_course_status_serde() {
        for (status, expected) in [
            (
                CourseStatus::Waiting(()),
                "{\"kind\":\"waiting\",\"payload\":null}",
            ),
            (
                CourseStatus::Start(()),
                "{\"kind\":\"start\",\"payload\":null}",
            ),
            (
                CourseStatus::Cancel(()),
                "{\"kind\":\"cancel\",\"payload\":null}",
            ),
            (
                CourseStatus::Finish(()),
                "{\"kind\":\"finish\",\"payload\":null}",
            ),
        ] {
            let json = serde_json::to_string(&status).unwrap();
            assert_eq!(json, expected);
            let deserialized: CourseStatus = serde_json::from_str(expected).unwrap();
            assert_eq!(
                std::mem::discriminant(&deserialized),
                std::mem::discriminant(&status)
            );
        }

        let status = CourseStatus::Finish(());
        let json = serde_json::to_string(&status).unwrap();
        assert_eq!(json, "{\"kind\":\"finish\",\"payload\":null}");
        let deserialized: CourseStatus = serde_json::from_str(&json).unwrap();
        assert!(matches!(deserialized, CourseStatus::Finish(())));

        let status = CourseStatus::Task(TaskProgressPayload {
            index: 1,
            category: "Video".into(),
        });
        let json = serde_json::to_string(&status).unwrap();
        assert_eq!(
            json,
            "{\"kind\":\"task\",\"payload\":{\"index\":1,\"category\":\"Video\"}}"
        );

        let status = CourseStatus::Chapter(ChapterProgressPayload {
            title: "第一章".into(),
            index: 2,
            completed: 1,
            total: 10,
        });
        assert_eq!(
            serde_json::to_string(&status).unwrap(),
            "{\"kind\":\"chapter\",\"payload\":{\"title\":\"第一章\",\"index\":2,\"completed\":1,\"total\":10}}"
        );

        let status = CourseStatus::Tab(TabProgressPayload { total: 3, index: 1 });
        assert_eq!(
            serde_json::to_string(&status).unwrap(),
            "{\"kind\":\"tab\",\"payload\":{\"total\":3,\"index\":1}}"
        );

        let deserialized: CourseStatus = serde_json::from_str(
            "{\"payload\":{\"index\":1,\"category\":\"Video\"},\"kind\":\"task\"}",
        )
        .unwrap();
        assert!(matches!(
            deserialized,
            CourseStatus::Task(TaskProgressPayload { index: 1, category }) if category == "Video"
        ));
    }
}
