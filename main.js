/**
 * uXuexitong 学习通一键全自动刷课脚本
 * 
 * 功能简介：
 * - 自动识别课程树结构，自动切换章节
 * - 自动播放视频、自动回答互动题目、自动切换倍速
 * - 自动检测 PDF 文档并自动翻页
 * - 1nm的容错处理
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
 * 4. 请勿用于商业用途或违反相关法律法规。（这坨玩意有人商用？？？）
 * 
 * 作者：unraous
 * 邮箱：unraous@qq.com
 * 日期：2025-05-28
 * 版本：v1.0.0
 */


const COURSE_TREE_ID = 'coursetree'; 
const COURSE_TREE_NODE_FEATURE_CLASS = 'div.posCatalog_select';
const COURSE_TREE_NODE_TITLE_FEATURE_CLASS = 'span.posCatalog_title';
const COURSE_TREE_NODE_CURRENT_FEATURE_CLASS = 'posCatalog_active';
const COURSE_TREE_NODE_INTERACT_FEATURE_CLASS = 'span.posCatalog_name';
const COURSE_TREE_NODE_UNFINISHED_FEATURE_CLASS = '.jobUnfinishCount';

const VIDEO_IFRAME_ID = 'video';
const VIDEO_QUESTION_ID = 'ext-comp-1046'; 
const VIDEO_QUESTION_COMPLETE_ID = 'videoquiz-continue';
const VIDEO_QUESTION_SUBMITTING_ID = 'videoquiz-submitting';
const VIDEO_PLAY_FEATURE_CLASS = '.vjs-play-control';
const VIDEO_ENDED_FEATURE_CLASS = 'vjs-ended';
const VIDEO_IFRAME_FEATURE_CLASS = 'ans-insertvideo-online';
const VIDEO_LAUNCH_FEATURE_CLASS = '.vjs-big-play-button';
const VIDEO_PAUSED_FEATURE_CLASS = 'vjs-paused';
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
const IFRAME_MAIN_FEATURE_CLASS = '.left';

const DEFAULT_SLEEP_TIME = 500; // 默认缓冲时间500ms，嫌慢可改小（未知后果）
const DEFAULT_INTERVAL_TIME = 100; // 默认轮询间隔100ms

const DEFAULT_TRY_COUNT = 50; // 默认最大尝试次数50次

let allTaskDown = false; 
let courseTree = [];
let courseTreeIndex = 0;
let nextLock = false; 
let skipSign = 0;

function getCourseTree() {
    const courseTree = [];
    const treeDiv = document.getElementById(COURSE_TREE_ID);
    if (!treeDiv) {
        console.warn(`未找到id为${COURSE_TREE_ID}的div`);
        return courseTree;
    }
    const nodes = treeDiv.querySelectorAll(COURSE_TREE_NODE_FEATURE_CLASS);
    nodes.forEach(node => {
        courseTree.push(node);
    });

    // Debug
    /*courseTree.forEach((node, idx) => {
        const span = node.querySelector(COURSE_TREE_NODE_INTERACT_FEATURE_CLASS);
        if (span) {
            console.log(`第${idx + 1}项: ${span.title}`);
        } else {
            console.log(`第${idx + 1}项: 未找到span.posCatalog_name`);
        }
        console.log(`类型: ${nodeType(node)}`);
    });*/

    return courseTree;
}

function findCourseTree() {
    courseTree = getCourseTree();
    if (courseTree.length === 0) {
        console.error('未找到课程树, 请检查页面结构或联系作者');
    }
}

function nodeType(node) {
    const span = node.querySelector(COURSE_TREE_NODE_INTERACT_FEATURE_CLASS);
    if (!span) {
        console.warn('未找到span.posCatalog_name');
        const titleSpan = node.querySelector(COURSE_TREE_NODE_TITLE_FEATURE_CLASS);
        if (titleSpan) {
            console.log('使用span.posCatalog_title作为标题');
            return 'Title';
        }
        return 'Unknown';
    } else {
        if (span.onclick == null) {
            return 'Block';

        } else {
            const value = node.querySelector(COURSE_TREE_NODE_UNFINISHED_FEATURE_CLASS)?.value ?? '';
            /*if (node.classList.contains(COURSE_TREE_NODE_CURRENT_FEATURE_CLASS)) { //跳过当前章节
                return 'Active';
            } */
            if (value === '') {
                return 'Finished';
            } else {
                return 'Pending';
            }
        }
    }
}

function nextCourse() {
    if (courseTreeIndex < courseTree.length) {
        return courseTree[courseTreeIndex++];
    } else {
        return null; 
    }
}

function initializeTreeIndex() {
    let node;
    courseTreeIndex = 0;
    while(node = nextCourse()) {
        if(node.classList.contains(COURSE_TREE_NODE_CURRENT_FEATURE_CLASS)) {
            console.log('已找到当前激活的课程节点:', node.querySelector(COURSE_TREE_NODE_INTERACT_FEATURE_CLASS).title);
            courseTreeIndex--;
            return node.querySelector(COURSE_TREE_NODE_INTERACT_FEATURE_CLASS).title;
        } 
    }
    console.error('初始化错误, 未找到激活的课程节点');
}

function timeSleep(time) {
    return new Promise(resolve => setTimeout(resolve, time));
}

function waitForElement(getter, callback, interval = DEFAULT_INTERVAL_TIME, maxTry = DEFAULT_TRY_COUNT) {
    let tryCount = 0;
    let stopped = false;
    function tryFind() {
        if (stopped) return;
        let el = null;
        try {
            el = getter();
        } catch (e) {
            // 捕获 DeadObject 或跨域等异常
            console.warn('[waitForElement] getter 异常，终止本轮检测', e);
            stopped = true;
            callback(null);
            return;
        }
        if (el) {
            callback(el);
        } else if (tryCount < maxTry) {
            tryCount++;
            setTimeout(tryFind, interval);
        } else {
            callback(null);
        }
    }
    tryFind();
    // 返回一个停止函数，供外部取消
    return () => { stopped = true; };
}

async function selectMenuItem(paceList) {
    // 2x > 1.5x > 1.25x
    const targets = ["2x", "1.5x", "1.25x"];
    let found = null;
    for (const speed of targets) {
        found = Array.from(paceList).find(li => li.textContent.includes(speed));
        if (found) break;
    }
    if (found) {
        found.click();
        timeSleep(DEFAULT_SLEEP_TIME).then(() => {
            if (found.classList.contains(VIDEO_PACE_SELECTED_FEATURE_CLASS)) {
                console.log('已自动选择菜单项:', found);
            } else {
                console.warn('点击后未能成功选择菜单项:', found);
            }
        });
    } else {
        console.warn('未找到目标倍速菜单项');
    }
}

function waitForSubmitAndContinue(innerDoc) {
    return new Promise(resolve => {
        const interval = setInterval(function() {
            const submitting = innerDoc.getElementById(VIDEO_QUESTION_SUBMITTING_ID);
            if (submitting && submitting.style.display === 'none') {
                clearInterval(interval);
                // 检查“继续学习”按钮
                const contBtn = innerDoc.getElementById(VIDEO_QUESTION_COMPLETE_ID);
                if (contBtn && contBtn.style.display === 'block') {
                    contBtn.click();
                    const contInterval = setInterval(() => {
                        if (contBtn.style.display !== 'block') {
                            clearInterval(contInterval);
                            resolve(true);
                        }
                    }, 200);
                } else {
                    resolve(false);
                }
            }
        }, 200);
    });
}

function autoQuestionDeal(target, innerDoc) {
    try {
        
        if (target) {
            const observer = new MutationObserver(async (mutationsList) => {
                for (const mutation of mutationsList) {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                        if (target.style.visibility == '') {
                            console.log('visi has been changed:', target.style.visibility);
                            const radios = innerDoc.querySelectorAll(VIDEO_QUESTION_RADIOS_FEATURE_CLASSES);
                            const checkboxes = innerDoc.querySelectorAll(VIDEO_QUESTION_CHECKBOXES_FEATURE_CLASSES);

                            if (checkboxes.length > 0) {
                                // 多选
                                const n = checkboxes.length;
                                for (let mask = 1; mask < (1 << n); mask++) {
                                    checkboxes.forEach(cb => cb.checked = false);
                                    for (let j = 0; j < n; j++) {
                                        if (mask & (1 << j)) {
                                            checkboxes[j].click();
                                        }
                                    }
                                    innerDoc.querySelector(VIDEO_QUESTION_SUBMIT_FEATURE_CLASS).click();
                                    const over = await waitForSubmitAndContinue(innerDoc);
                                    if (over) break;
                                }
                            } else if (radios.length > 0) {
                                // 单选
                                for (let i = 0; i < radios.length; i++) {
                                    radios[i].click();
                                    innerDoc.querySelector(VIDEO_QUESTION_SUBMIT_FEATURE_CLASS).click();
                                    const over = await waitForSubmitAndContinue(innerDoc);
                                    if (over) break;
                                }
                            }
                        }
                    }
                }
            });
            observer.observe(target, { attributes: true, attributeFilter: ['style'] });
        } else {
            console.error("没有找到目标元素");
        }
    } catch (e) {
        console.warning('autoQuestionDeal 执行异常:', e);
    }
}

function continueToNextChapter() {
    if (nextLock) {
        console.log('[锁] 上一次流程未结束，跳过本次 continueToNextChapter');
        return;
    }
    nextLock = true; 

    const nextBtn = document.getElementById(NEXTBTN_ID);

    if (nextBtn) {
        if (nextBtn.style.display === 'none') {
            confirm('课程已完成');
            allTaskDown = true;
            nextLock = false;
            return;
        }
    } else {
        nextLock = false;
        throw new Error('元素缺失, 已终止');
    }

    findCourseTree(); //由于此时课程树有元素变化（主要是COURSE_TREE_NODE_CURRENT_FEATURE_CLASS），需要刷新
    let currentTitle = initializeTreeIndex();
    let nextCourseNode = nextCourse();
    let skippedCount = 0;
    while(nodeType(nextCourseNode) !== 'Unknown' && nodeType(nextCourseNode) !== 'Pending') {
        const nameSpan = nextCourseNode.querySelector(COURSE_TREE_NODE_INTERACT_FEATURE_CLASS);
        const titleSpan = nextCourseNode.querySelector(COURSE_TREE_NODE_TITLE_FEATURE_CLASS);
        const title = nameSpan?.title ?? titleSpan?.title ?? '未知标题';
        console.log('跳过已完成和锁定课程/目录:', title);
        nextCourseNode = nextCourse();
        skippedCount++;
    }
    if (nextCourseNode) {
        let nextChapter = nextCourseNode.querySelector(COURSE_TREE_NODE_INTERACT_FEATURE_CLASS);
        console.log('正在跳转到下一课程:', nextChapter.title);
        if (nextChapter) {
            if (currentTitle === nextChapter.title) {
                aimNode = nextCourse();
                console.log('当前章节已激活，跳过');
                while(nodeType(aimNode) !== 'Unknown' && nodeType(aimNode) !== 'Pending') {
                    console.log('执行章节跳转循环中...')
                    aimNode = nextCourse();
                    skippedCount++; 
                }
                nextChapter = aimNode.querySelector(COURSE_TREE_NODE_INTERACT_FEATURE_CLASS); 
                console.log('循环执行完毕，正在跳转到下一课程:', nextChapter.title);           
            }  
            if (nextChapter) {
                timeSleep(DEFAULT_SLEEP_TIME).then(() => { 
                    console.log('即将跳转到下一章节');
                    nextChapter.click();
                    console.log('已点击章节:', nextChapter.title);
                    nextLock = false; // 解锁
                });
            } else {
                confirm('未找到下一个课程节点, 可能是课程已全部完成或结构异常,脚本已退出');
                allTaskDown = true;
                nextLock = false; // 解锁
            }
        } else {
            confirm('课程已完成');
            allTaskDown = true;
            nextLock = false; // 解锁
        }
    } else {
        confirm('未找到下一个课程节点, 可能是课程已全部完成或结构异常,脚本已退出');
        allTaskDown = true;
        nextLock = false; 
    }
}

function findOuterDoc() {
    const outerIframe = document.getElementById(OUTER_IFRAME_ID);
        if (!outerIframe) return null;
        let outerDoc;
        try {
            outerDoc = outerIframe.contentDocument || outerIframe.contentWindow.document;
        } catch (e) {
            console.warn('跨域, 无法访问iframe内容');
            return null;
        }
        if (!outerDoc) {
            console.log('[调试] 未找到 outerDoc');
            return null;
        }
        if (outerDoc.location.href === IFRAME_LOADING_URL) {
            console.log('[调试] outerDoc 仍为 about:blank,等待加载');
            return null;
        }
        console.log('已找到 outerDoc:', outerDoc);
        return outerDoc;
}

function findInnerDoc(outerDoc) {
    const innerIframe = outerDoc.querySelector(INNER_COURSE_IFRAME_ID);
    let Type = '';
    if (!innerIframe) {
        console.log('[调试] 未找到 innerIframe');
        return null;
    }
    else if (innerIframe.classList.contains(VIDEO_IFRAME_FEATURE_CLASS)) {
        console.log('课程为VIDEO类型:');
        Type = 'Video';
    }
    else if (innerIframe.classList.contains(PDF_DOC_FEATURE_CLASS)) {
        console.log('课程为PDF类型:');
        Type = 'Pdf';
    }
    else {
        console.error('[调试] 不支持的课程类型,脚本已终止,请联系作者并说明信息', innerIframe);
    }
    let innerDoc;
    try {
        innerDoc = innerIframe.contentDocument || innerIframe.contentWindow.document;
    } catch (e) {
        console.warn('跨域, 无法访问内层iframe内容');
        return null;
    }
    if (!innerDoc) {
        console.log('[调试] 未找到 innerDoc');
        return null;
    }
    if (innerDoc.location.href === IFRAME_LOADING_URL) {
        console.log('[调试] innerDoc 仍为 about:blank,等待加载');
        return null;  
    } else {
        console.log('已找到 innerDoc:', innerDoc);
        return { innerDoc, Type };
    }
}

function findVideoElement(innerDoc) {
    const videoDiv = innerDoc.getElementById(VIDEO_IFRAME_ID); //视频主元素
    const target = innerDoc.getElementById(VIDEO_QUESTION_ID); // 互动答题元素

    const launchBtn = innerDoc.querySelector(VIDEO_LAUNCH_FEATURE_CLASS); // 视频启动按钮
    const playControlBtn = innerDoc.querySelector(VIDEO_PLAY_FEATURE_CLASS); // 视频播放按钮
    const paceList = innerDoc.querySelectorAll(VIDEO_PACELIST_FEATURE_CLASS); // 倍速播放列表
    
    if (!videoDiv) {
        console.log('[调试] 未找到 video 元素');
    } else {
        console.log('该章节为video,进行参数捕获', videoDiv);
        if (!launchBtn) {
            console.log('[调试] 未找到播放按钮');
        } else {
            console.log('[调试] 找到播放按钮:', launchBtn);
        }
        if (!playControlBtn) {
            console.log('[调试] 未找到播放控制按钮');
        } else {
            console.log('[调试] 找到播放控制按钮:', playControlBtn);
        }
        if (!target) {
            console.log('[调试] 未找到目标元素 ext-comp-1046');
        } else {
            console.log('[调试] 找到目标元素 ext-comp-1046:', target);
        }
        if (paceList.length === 0) {
            console.log('[调试] 未找到任何菜单项'); 
        } else {
            console.log('[调试] 找到菜单项:', paceList);
        }

        if (videoDiv) {
            return { innerDoc, videoDiv, launchBtn, target, playControlBtn, paceList };
        }
    }  
    return null;
}

async function tryStartVideo(videoDiv, launchBtn, paceList) {
    let tryCount = 0;
    while (!videoDiv.classList.contains(VIDEO_HAS_LAUNCHED_FEATURE_CLASS) && tryCount < 10) {
        if (launchBtn) {
            launchBtn.click();
        } else {
            console.warn('未找到启动按钮,请用户手动点击');
            break;
        }
        tryCount++;
        await timeSleep(DEFAULT_SLEEP_TIME);
    }
    await timeSleep(DEFAULT_SLEEP_TIME);
    selectMenuItem(paceList);
}

function autoPlayVideo( innerDoc, videoDiv, launchBtn, target, playControlBtn, paceList ) {
    if (!videoDiv) {
        console.error('请求超时,请检查网络或与作者联系');
        return;
    }
    console.log('debug successfully');
    let observer = null;
    const checkClass = () => {
        if (videoDiv.classList.contains(VIDEO_ENDED_FEATURE_CLASS)) {
            console.log('class 已包含 vjs-ended');
            continueToNextChapter(); 
            observer && observer.disconnect();
        } else if (!videoDiv.classList.contains(VIDEO_HAS_LAUNCHED_FEATURE_CLASS)) {       
            tryStartVideo(videoDiv, launchBtn, paceList);
        } else if (videoDiv.classList.contains(VIDEO_PAUSED_FEATURE_CLASS)) {
            console.log('课程被暂停,正在检测原因');
            timeSleep(DEFAULT_SLEEP_TIME).then(() => {
                if (videoDiv.classList.contains(VIDEO_PAUSED_FEATURE_CLASS)) {
                    if (videoDiv.classList.contains(VIDEO_ENDED_FEATURE_CLASS)) { //由于视频结束时有暂停属性，由于延迟会产生分支跳跃到此处的情况，此步为防止一个视频循环播放
                        console.log('class 已包含 vjs-ended');
                        continueToNextChapter(); 
                        observer && observer.disconnect();
                        return;
                    } if (playControlBtn) {
                        playControlBtn.click();
                        console.log('未检测到互动题目,已自动点击播放按钮'); //同时兼顾后台播放功能，因为学习通只会在你鼠标离开页面时触发一次暂停，此后无检测
                    } else {
                        console.warn('未找到播放控制按钮,请用户手动点击播放');
                    }
                } else {
                    console.log('暂停状态已自动恢复,无需处理');
                }
            }); 
        } else {
            autoQuestionDeal(target, innerDoc);
        }
    };
    observer = new MutationObserver(checkClass);
    observer.observe(videoDiv, { attributes: true, attributeFilter: ['class'] });
    checkClass();
}

function findPdfElement(innerDoc) {
    const finalIframe = innerDoc.getElementById(PDF_IFRAME_ID);
    if (!finalIframe) {
        console.log('[调试] 未找到 panView 元素');
        return null;
    }
    let finalDoc;
    try {
        finalDoc = finalIframe.contentDocument || finalIframe.contentWindow.document;
    } catch (e) {
        console.log('[调试] 获取 panView 的 document 失败', e);
        return null;
    }
    
    const pdfHtml = finalDoc.documentElement;
    
    if (!pdfHtml) {
        console.log('[调试] 未找到 pdf 元素');
    } else {
        return { pdfHtml };
    }
    
    return null;
}

function handleIframeChange() {
    if (allTaskDown) return;

    // 唯一性控制，防止异步出bug（事实上确实会出很多bug）
    let firstLayerCancel = null;
    let secondLayerCancel = null;
    let thirdLayerCancel = null;

    (function firstLayer() { //整体分为三层回调，以抓取三层iframe
        if (firstLayerCancel) firstLayerCancel();
        firstLayerCancel = waitForElement(
            () => {
                if (allTaskDown) return;
                console.log('第一层回调执行');
                return findOuterDoc();
            },
            (outerDoc) => {
                // 第二层
                (function secondLayer() {
                    if (secondLayerCancel) secondLayerCancel();
                    secondLayerCancel = waitForElement(
                        () => {
                            if (allTaskDown) return;
                            console.log('第二层回调执行');
                            return findInnerDoc(outerDoc);
                        },
                        (param = {}) => {
                            (function thirdLayer() {
                                if (!param || !param.innerDoc) {
                                    console.warn('内层Doc无法识别，尝试跳过');
                                    continueToNextChapter();
                                    return;
                                }
                                const { innerDoc, Type } = param;
                                if (Type === 'Video') {
                                    console.log('该章节为VIDEO,进行参数捕获');
                                    if (thirdLayerCancel) thirdLayerCancel();
                                    thirdLayerCancel = waitForElement(
                                        () => {
                                            if (allTaskDown) return;
                                            console.log('第三层回调执行');
                                            return findVideoElement(innerDoc);
                                        },
                                        (innerParam) => {
                                            if (!innerParam) {
                                                console.warn('页面异常加载，尝试跳过');
                                                continueToNextChapter();
                                                return;
                                            }
                                            const { videoDiv, launchBtn, target, playControlBtn, paceList } = innerParam;
                                            autoPlayVideo(
                                                innerDoc,
                                                videoDiv,
                                                launchBtn,
                                                target,
                                                playControlBtn,
                                                paceList
                                            );
                                        }
                                    );
                                } else if (Type === 'Pdf') {
                                    console.log('该章节为PDF,进行参数捕获');
                                    if (thirdLayerCancel) thirdLayerCancel();
                                    thirdLayerCancel = waitForElement(
                                        () => {
                                            return findPdfElement(innerDoc);
                                        },
                                        ({ pdfHtml }) => {
                                            if (!pdfHtml) {
                                                console.error('请求超时, 请检查网络或与作者联系');
                                                continueToNextChapter();
                                                return;
                                            }
                                            pdfHtml.scrollTop = pdfHtml.scrollHeight;
                                            timeSleep(1000).then(() => {
                                                console.log('已刷完');
                                                continueToNextChapter();
                                            });
                                        }
                                    );
                                } else {
                                    console.warn('[调试] 不支持的课程类型,尝试跳过', Type);
                                    continueToNextChapter();
                                }
                            })();
                        }
                    );
                })();
            }
        );
    })();
}

function startScriptWithMask(mainFunc) { // 启动脚本并创建遮罩，因为只有用户主动激活主页面脚本才能正常运行
    // 创建全屏透明遮罩
    const mask = document.createElement('div');
    mask.style.position = 'fixed';
    mask.style.left = 0;
    mask.style.top = 0;
    mask.style.width = '100vw';
    mask.style.height = '100vh';
    mask.style.zIndex = 99999;
    mask.style.background = 'rgba(0,0,0,0)';
    mask.style.cursor = 'pointer';
    mask.title = '启动器';
    document.body.appendChild(mask);

    confirm('本脚本仅供学习交流使用, 请遵守相关法律法规。\n\n请先关闭浏览器的开发者工具, 点击确定后单击页面任意处以运行脚本。\n\n如果想停止脚本, 随时刷新页面即可。');

    mask.addEventListener('click', function () { 
        document.body.removeChild(mask);
        mainFunc();
    });
}

function main() {
    console.log('脚本已启动, 开始刷课...');

    const leftEl = document.querySelector(IFRAME_MAIN_FEATURE_CLASS);
    if (leftEl) {
        const leftObserver = new MutationObserver(() => {
            skipSign++;
            if(skipSign % 2 === 0)handleIframeChange(); //由于每次变动章节IFRAME_MAIN_FEATURE_CLASS会稳定触发观察器两次，故而忽略掉一次
        });
        leftObserver.observe(leftEl, { childList: true, subtree: true });
        handleIframeChange();
    } else {
        console.error('未找到 class 为 left 的元素');
    }
}


findCourseTree(); // 初始化课程树
initializeTreeIndex();

// 启动入口
startScriptWithMask(main);
