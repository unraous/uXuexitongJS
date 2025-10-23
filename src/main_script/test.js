/**使用说明：
 * uXuexitong 学习通一键全自动刷课脚本
 * 
 * 功能简介：
 * - 自动识别课程树结构，自动切换章节
 * - 自动播放视频、自动回答互动题目、自动切换倍速
 * - 自动检测 PDF 文档并自动翻页
 * 
 * 注意事项：
 * - 目前单一章节只识别第一个视频/PDF元素，可能会漏刷
 * - 仅支持学习通网页版，目前仅在FireFox验证，理论上不同浏览器均兼容（IE除外）（真有人用IE？？）
 * - 对于非视频/PDF类型的课程，脚本会尝试直接跳过
 * - 欢迎Issue反馈bug或建议，但请一定一定给出详细信息
 * 
 * 使用说明：
 * 1. 仅在学习通平台页面使用，具体用法参见README.md。
 * 2. 启动脚本后，需手动点击页面以激活脚本。
 * 3. 如需停止，刷新页面即可。
 * 4. 请勿用于商业用途或违反相关法律法规。
 * 
 * 作者：unraous
 * 邮箱：unraous@qq.com
 * 日期：2025-06-16
 * 版本：v1.2.2
 */


const DEFAULT_TEST_OPTION = globalThis.LAUNCH_OPTION ?? 0;
const DEFAULT_SPEED_OPTION = globalThis.FORCE_SPEED ?? false;
const DEFAULT_SPEED = globalThis.SPEED ?? 2;

const DEFAULT_SLEEP_TIME = 400 + Math.floor(Math.random() * 200); // 默认延迟400-600ms
const DEFAULT_INTERVAL_TIME = 85 + Math.floor(Math.random() * 30); // 默认轮询间隔85-115ms

const DEFAULT_TRY_COUNT = 50; // 默认最大尝试次数50次


const VIDEO_IFRAME_ID = 'video';
const VIDEO_QUESTION_ID = 'ext-comp-1046'; 
const VIDEO_QUESTION_COMPLETE_ID = 'videoquiz-continue';
const VIDEO_QUESTION_SUBMITTING_ID = 'videoquiz-submitting';
const VIDEO_PLAY_FEATURE_CLASS = '.vjs-play-control';
const VIDEO_ENDED_FEATURE_CLASS = 'vjs-ended';
const VIDEO_IFRAME_FEATURE_CLASS = 'ans-insertvideo-online';
const VIDEO_LAUNCH_FEATURE_CLASS = '.vjs-big-play-button';
const VIDEO_PAUSED_FEATURE_CLASS = 'vjs-paused';
const VIDEO_MUTEBTN_FEATURE_CLASS = '.vjs-mute-control';
const VIDEO_PACELIST_FEATURE_CLASS = 'li.vjs-menu-item';
const VIDEO_HAS_LAUNCHED_FEATURE_CLASS = 'vjs-has-started';
const VIDEO_PACE_SELECTED_FEATURE_CLASS = 'vjs-menu-item-selected';
const VIDEO_QUESTION_SUBMIT_FEATURE_CLASS = '.ans-videoquiz-submit';
const VIDEO_QUESTION_RADIOS_FEATURE_CLASSES = '.tkItem_ul .ans-videoquiz-opt input[type="radio"]';
const VIDEO_QUESTION_CHECKBOXES_FEATURE_CLASSES = '.tkItem_ul .ans-videoquiz-opt input[type="checkbox"]';

const PDF_IFRAME_ID = 'panView';
const PDF_DOC_FEATURE_CLASS = 'insertdoc-online-pdf';

const IFRAME_LOADING_URL= 'about:blank';
const NEXTBTN_ID = 'prevNextFocusNext';
const OUTER_IFRAME_ID = 'iframe'; 
const INNER_COURSE_IFRAME_ID = 'iframe.ans-attach-online';
const INNER_COURSE_IFRAME_FEATURE_CLASS = 'ans-attach-online';
const IFRAME_MAIN_FEATURE_CLASS = '.left';




let allTaskDown = false; 
let courseTreeIndex = 0;
let nextLock = false; 
let skipSign = 0;
let answerTable = []; 
let handleIframeLock = false;
let nextCooldown = false;
let videoLock = false; // 视频锁，防止多次点击播放按钮


/** @returns {Element[]} 课程树 */
function initCourseTree() {
    const container = document.getElementById('coursetree');
    if (!container)
        return [];

    const chapters = container.querySelectorAll('div.posCatalog_select');
    if (chapters.length > 0) {
        console.info(`已找到课程树节点, 数量: ${chapters.length}`);
        return Array.from(chapters).filter(
            (chapter) => {
                const chapterType = queryChapterType(chapter);  
                return chapterType === 'Blocking' || chapterType === 'Pending';
            }
        );
    }

    console.warn('课程树节点为空');
    return [];
}

/**
 * @param {Element} chapter 章节点
 * @returns {string} 节点类型：Blocked、Pending、Title、Finished
 */
function queryChapterType(chapter) {
    if (!chapter)
        return 'Unknown';
    if (chapter.querySelector('span.posCatalog_name')?.onclick === null)
        return 'Blocking';
    if (chapter.querySelector('.orangeNew'))
        return 'Pending';
    if (chapter.querySelector('span.posCatalog_title'))
        return 'Title';
    return 'Finished';    
}

function chapterHandler() {

}

const courseTree = initCourseTree();
console.info(courseTree);

for (const chapter of courseTree) {
    const type = queryChapterType(chapter);
    console.info(`节点${chapter.querySelector('span.posCatalog_name')?.textContent}类型: ${type}`);
}