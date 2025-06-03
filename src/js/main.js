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

if (typeof DEFAULT_TEST_OPTION === 'undefined') { // 检测是否由selenium注入
    console.log('检测为极简模式')
    var DEFAULT_TEST_OPTION = 0; 
}

const DEFAULT_SLEEP_TIME = 400 + Math.floor(Math.random() * 200); // 默认延迟400-600ms
const DEFAULT_INTERVAL_TIME = 85 + Math.floor(Math.random() * 30); // 默认轮询间隔85-115ms

const DEFAULT_TRY_COUNT = 50; // 默认最大尝试次数50次

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
const IFRAME_MAIN_FEATURE_CLASS = '.left';




let allTaskDown = false; 
let courseTree = [];
let courseTreeIndex = 0;
let nextLock = false; 
let skipSign = 0;
let answerTable = []; 
let handleIframeLock = false;
let nextCooldown = false;
let videoLock = false; // 视频锁，防止多次点击播放按钮

if (DEFAULT_TEST_OPTION === 1) {
    console.log('已开启课后答题功能,正在创建端口连接...');
    window._ws = new WebSocket("ws://localhost:8765");
    window._ws.onopen = function() {
        console.log("WebSocket已连接Python端口");
    };
    window._ws.onerror = function(e) {
        console.warn("WebSocket连接失败", e);
    };
    window._ws.onclose = function() {
        console.warn("WebSocket已关闭");
    };
}



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
            const pending = node.querySelector('.orangeNew'); 
            if (pending) {
                return 'Pending';
            } else {
                return 'Finished';
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
    time = time + Math.floor(Math.random() * 50);
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

function continueToNextChapter() {
    if (nextLock || nextCooldown) {
        console.log('[锁] 跳转冷却中，跳过本次 continueToNextChapter');
        return;
    }
    nextLock = true;
    nextCooldown = true; // 进入冷却

    // ...原有跳转逻辑...

    // 跳转后冷却，比如5秒
    setTimeout(() => {
        nextCooldown = false;
        console.log('章节跳转冷却结束');
    }, 10 * DEFAULT_SLEEP_TIME); 

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
        if(!nextCourseNode) {
            break;
        }
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
                    if(!aimNode) {
                        confirm('未找到下一个课程节点, 可能是课程已全部完成或结构异常,脚本已退出');
                        allTaskDown = true;
                        nextLock = false; 
                        return;
                    }
                    skippedCount++; 
                }
                if(!aimNode) {
                    confirm
                }
                nextChapter = aimNode.querySelector(COURSE_TREE_NODE_INTERACT_FEATURE_CLASS); 
                console.log('循环执行完毕，正在跳转到下一课程:', nextChapter.title);           
            }  
            if (nextChapter) {
                timeSleep(DEFAULT_SLEEP_TIME).then(() => { 
                    console.log('即将跳转到下一章节');
                    nextChapter.click();
                    console.log('已点击章节:', nextChapter.title);
                    nextLock = false; 
                });
            } else {
                confirm('未找到下一个课程节点, 可能是课程已全部完成或结构异常,脚本已退出');
                allTaskDown = true;
                nextLock = false; 
            }
        } else {
            confirm('课程已完成');
            allTaskDown = true;
            nextLock = false; 
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

function findInnerDocs(outerDoc) {
    const innerIframes = outerDoc.querySelectorAll(INNER_COURSE_IFRAME_ID);
    const result = [];
    innerIframes.forEach(innerIframe => {
        let Type = '';
        if (innerIframe.classList.contains(VIDEO_IFRAME_FEATURE_CLASS)) {
            Type = 'Video';
        } else if (innerIframe.classList.contains(PDF_DOC_FEATURE_CLASS)) {
            Type = 'Pdf';
        } else {
            Type = 'Unknown';
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
        }
        result.push({ innerDoc, Type });
    });
    if (result.length === 0) {
        console.log('[调试] 尝试检测测验题目');
        // 备用手段：尝试查找 src 包含 /ananas/modules/work/ 的 iframe
        const workIframe = Array.from(outerDoc.querySelectorAll('iframe')).find(
            iframe => iframe.src && iframe.src.includes('/ananas/modules/work/')
        );
        if (workIframe) {
            try {
                let workDoc;
                try {
                    workDoc = workIframe.contentDocument || workIframe.contentWindow.document;
                } catch (e) {
                    console.warn('[备用] 获取 workDoc 失败', e);
                    return null;
                }
                console.log('[备用] workDoc:', workDoc);
                if (!workDoc) {
                    console.warn('[备用] workDoc 为 null');
                    return null;
                } else if (workDoc.location.href === IFRAME_LOADING_URL) {
                    console.warn('[备用] workDoc 仍为 about:blank');
                    return null;
                } else {
                    console.log('[备用] 通过 src 查找到了 work iframe innerDoc');
                    result.push({ innerDoc: workDoc, Type: 'Work' });
                }
            } catch (e) {
                console.warn('[备用] 跨域, 无法访问 work iframe 内容');
                return null;
            }
        } else {
            console.log('[备用] 未找到 work iframe');
            return null;
        }
        
    }
    return result;
}


function muteVideo (muteBtn) {
    if (muteBtn) {
    if (muteBtn.title === '取消静音') {
        console.log('已是静音状态，跳过');
    } else if (muteBtn.title === '静音') {
        muteBtn.click();
        console.log('已自动点击静音按钮');
    } else {
        console.warn('静音按钮的title未知:', muteBtn.title);
    }
} else {
    console.warn('未找到静音按钮元素');
}
}

function selectMenuItem(paceList) {
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
    console.log('开始处理互动题目:', target);
    videoLock = true; // 锁定视频处理，防止多次点击
    try {
        if (target) {
            //let lastVisibility = target.style.visibility;
            let pollCount = 0;
            const maxPoll = DEFAULT_TRY_COUNT; 
            const poll = async () => {
                if (target.style.visibility === '') {
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
                            console.log('正在提交多选题目');
                            innerDoc.querySelector(VIDEO_QUESTION_SUBMIT_FEATURE_CLASS).click();
                            const over = await waitForSubmitAndContinue(innerDoc);
                            if (over) return;
                        }
                    } else if (radios.length > 0) {
                        // 单选
                        for (let i = 0; i < radios.length; i++) {
                            radios[i].click();
                            console.log('正在提交单选题目');
                            innerDoc.querySelector(VIDEO_QUESTION_SUBMIT_FEATURE_CLASS).click();
                            const over = await waitForSubmitAndContinue(innerDoc);
                            if (over) return;
                        }
                    }
                } else if (pollCount < maxPoll) {
                    pollCount++;
                    setTimeout(poll, DEFAULT_SLEEP_TIME);
                }
                //lastVisibility = target.style.visibility;
            };
            poll();
        } else {
            console.error("没有找到目标元素");
        }
    } catch (e) {
        console.warn('autoQuestionDeal 执行异常:', e);
    }
    videoLock = false; // 解除视频处理锁
}

function findVideoElement(innerDoc) {
    const videoDiv = innerDoc.getElementById(VIDEO_IFRAME_ID); //视频主元素
    const target = innerDoc.getElementById(VIDEO_QUESTION_ID); // 互动答题元素

    const launchBtn = innerDoc.querySelector(VIDEO_LAUNCH_FEATURE_CLASS); // 视频启动按钮
    const playControlBtn = innerDoc.querySelector(VIDEO_PLAY_FEATURE_CLASS); // 视频播放按钮
    const paceList = innerDoc.querySelectorAll(VIDEO_PACELIST_FEATURE_CLASS); // 倍速播放列表
    const muteBtn = innerDoc.querySelector(VIDEO_MUTEBTN_FEATURE_CLASS); // 静音按钮

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

        if (muteBtn) {
            console.log('[调试] 找到静音按钮:', muteBtn);
        } else {
            console.log('[调试] 未找到静音按钮');
        }

        if (paceList.length === 0) {
            console.log('[调试] 未找到任何菜单项'); 
        } else {
            console.log('[调试] 找到菜单项:', paceList);
        }

        if (videoDiv) {
            return { innerDoc, videoDiv, launchBtn, target, playControlBtn, paceList, muteBtn };
        }
    }  
    return null;
}

async function tryStartVideo(videoDiv, launchBtn, paceList, muteBtn) {
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
    muteVideo(muteBtn);
}

function autoPlayVideo(innerDoc, videoDiv, launchBtn, target, playControlBtn, paceList, muteBtn) {
    return new Promise((resolve) => {
        if (!videoDiv) {
            console.error('请求超时,请检查网络或与作者联系');
            resolve(false);
            return;
        }
        let pauseFreeze = false;
        console.log('debug successfully');
        let observer = null;
        const checkClass = () => {
            if (videoDiv.classList.contains(VIDEO_ENDED_FEATURE_CLASS)) {
                console.log('class 已包含 vjs-ended');
                //continueToNextChapter(); 
                observer && observer.disconnect();
                resolve(true);
                return;
            } else if (!videoDiv.classList.contains(VIDEO_HAS_LAUNCHED_FEATURE_CLASS)) {       
                tryStartVideo(videoDiv, launchBtn, paceList, muteBtn);
                if (target && target.style.visibility !== 'hidden') {
                            console.log('检测为互动题目,正在处理');
                            autoQuestionDeal(target, innerDoc);
                            pauseFreeze = true;
                            setTimeout(() => {
                                pauseFreeze = false; // 5秒后解除暂停冻结
                            }, 10 * DEFAULT_SLEEP_TIME);
                }
            } else if (videoDiv.classList.contains(VIDEO_PAUSED_FEATURE_CLASS)) {
                console.log('课程被暂停,正在检测原因');
                timeSleep(DEFAULT_SLEEP_TIME).then(() => {
                    if (videoDiv.classList.contains(VIDEO_PAUSED_FEATURE_CLASS)) {
                        if (videoDiv.classList.contains(VIDEO_ENDED_FEATURE_CLASS)) { //由于视频结束时有暂停属性，由于延迟会产生分支跳跃到此处的情况，此步为防止一个视频循环播放
                            return;
                        }
                        if (target && target.style.visibility !== 'hidden') {
                            console.log('检测为互动题目,正在处理');
                            autoQuestionDeal(target, innerDoc);
                            pauseFreeze = true;
                            setTimeout(() => {
                                pauseFreeze = false; // 5秒后解除暂停冻结
                            }, 10 * DEFAULT_SLEEP_TIME);
                        } else if (playControlBtn) {
                            if (!pauseFreeze) {
                                console.log('未检测到互动题目,已自动点击播放按钮');
                                let tryCount = 0;
                                const maxTry = DEFAULT_TRY_COUNT - 10;
                                const tryPlay = () => {
                                    if (!videoDiv.classList.contains(VIDEO_PAUSED_FEATURE_CLASS) || tryCount >= maxTry || videoLock) {
                                        if (tryCount >= maxTry) {
                                            console.warn('多次尝试点击播放按钮未成功，请手动处理');
                                        }
                                        return;
                                    }
                                    if (!videoLock) {
                                        playControlBtn.click();
                                    }
                                    tryCount++;
                                    setTimeout(tryPlay, DEFAULT_SLEEP_TIME);
                                };
                                tryPlay();
                            } else {
                                console.warn('暂停状态已冻结,请用户手动点击播放按钮');
                            }
                             //同时兼顾后台播放功能，因为学习通只会在你鼠标离开页面时触发一次暂停，此后无检测
                        } else {
                            console.warn('未找到播放控制按钮,请用户手动点击播放');
                        }
                    } else {
                        console.log('暂停状态已自动恢复,无需处理');
                    }
                }); 
            } else {
                if (target && target.style.visibility !== 'hidden') {
                    console.log('检测为互动题目,正在处理');
                    autoQuestionDeal(target, innerDoc);
                    pauseFreeze = true;
                    setTimeout(() => {
                        pauseFreeze = false; // 5秒后解除暂停冻结
                    }, 10 * DEFAULT_SLEEP_TIME);
                } else {
                    console.log('视频正在播放中，继续检测');
                }
            }
        };
        observer = new MutationObserver(checkClass);
        observer.observe(videoDiv, { attributes: true, attributeFilter: ['class'] });
        checkClass();
    });
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
        return null;
    }

    console.log('已找到 pdf 元素:', pdfHtml);
    return { pdfHtml };
}

function scrollPdfToBottom(pdfHtml, maxTries = Math.floor(DEFAULT_TRY_COUNT / 10)) { //有时候不灵，未知原因
    return new Promise(async (resolve) => {
        let lastTop = pdfHtml.scrollTop;
        let tries = 0;
        while (tries < maxTries) {
            pdfHtml.scrollTo({
                top: pdfHtml.scrollHeight,
                behavior: 'smooth'
            });
            await timeSleep(4 * DEFAULT_SLEEP_TIME); // 等待滚动动画
            if (pdfHtml.scrollTop !== lastTop && pdfHtml.scrollTop > 0) {
                resolve(true); // 滚动成功
                return;
            }
            lastTop = pdfHtml.scrollTop;
            tries++;
        }
        resolve(false); // 多次尝试后仍未滚动
    });
}


function findWorkElement(innerDoc) {
    const testIframe = innerDoc.getElementById('frame_content');
    if (!testIframe) {
        console.log('[调试] 未找到 frame_content 元素');
        return null;
    }
    let testDoc;
    try {
        testDoc = testIframe.contentDocument || testIframe.contentWindow.document;
    } catch (e) {
        console.log('[调试] 获取 frame_content 的 document 失败', e);
        return null;
    }
    
    const testList = testDoc.querySelectorAll('.singleQuesId');
    if (testList.length === 0) {
        console.log('[调试] 未找到任何测试题目');
        return null;
    }
    console.log('已找到测试题目:', testList);

    const submitBtn = testDoc.querySelector('.btnSubmit');
    if (!submitBtn) {
        console.log('[调试] 未找到提交按钮');
        return null;
    }
    return { testDoc, testList , submitBtn };
}

function autoFillAnswers(testList, answerJson) {
    answerJson.forEach(item => {
        const qNum = item["题号"];
        const ans = item["答案"];
        for (const quesDiv of testList) {
            const iTag = quesDiv.querySelector('i');
            if (iTag && iTag.textContent.trim() === qNum) {
                // 判断题型
                const titleSpan = quesDiv.querySelector('.newZy_TItle');
                let type = '';
                if (titleSpan) {
                    if (titleSpan.textContent.includes('多选')) type = 'multi';
                    else if (titleSpan.textContent.includes('判断')) type = 'judge';
                    else if (titleSpan.textContent.includes('单选')) type = 'single';
                }
                // 多选题
                if (type === 'multi') {
                    // 先清除之前选中的多选项
                    const checkedSpans = quesDiv.querySelectorAll('span.check_answer_dx');
                    checkedSpans.forEach(span => span.click());

                    let ansArr = [];
                    if (typeof ans === "string") {
                        if (ans.includes(',')) {
                            ansArr = ans.split(',').map(s => s.trim());
                        } else {
                            ansArr = ans.split('').map(s => s.trim());
                        }
                    } else if (Array.isArray(ans)) {
                        ansArr = ans;
                    }
                    for (const ch of ansArr) {
                        const optSpan = quesDiv.querySelector(`span.num_option_dx[data="${ch}"]`);
                        if (optSpan) optSpan.click();
                        else console.warn(`题号${qNum}未找到选项${ch}`);
                    }
                } else if (type === 'judge') {
                    // 先清除之前选中的判断项
                    const checkedSpans = quesDiv.querySelectorAll('span.check_answer');
                    checkedSpans.forEach(span => span.click());

                    let val = ans;
                    if (val[0] === "A" || val[0] === "对" || val[0] === "t" || val === true) val = "true";
                    else if (val[0] === "B" || val[0] === "错" || val[0] === "f" || val === false) val = "false";
                    const optSpan = quesDiv.querySelector(`span.num_option[data="${val}"]`);
                    if (optSpan) optSpan.click();
                    else console.warn(`题号${qNum}未找到判断选项${val}`);
                } else {
                    // 单选题，先清除之前选中的
                    const checkedSpans = quesDiv.querySelectorAll('span.check_answer');
                    checkedSpans.forEach(span => span.click());

                    for (const ch of ans) {
                        const optSpan = quesDiv.querySelector(`span.num_option[data="${ch}"]`);
                        if (optSpan) optSpan.click();
                        else console.warn(`题号${qNum}未找到选项${ch}`);
                    }
                }
                break;
            }
        }
    });
}

function answerFixes(testList, answerHistory) {
    console.log('开始修补答案');
    const answerJson = []; 
    testList.forEach(quesDiv => {
        const iTag = quesDiv.querySelector('i');
        const qNum = iTag ? iTag.textContent.trim() : '';
        const qIndex = Number(qNum); // 变成数字类型
        if (!answerTable[qIndex]) {
            answerTable[qIndex] = [];
        }
        const titleSpan = quesDiv.querySelector('.newZy_TItle');
        let type = '';
        if (titleSpan) {
            if (titleSpan.textContent.includes('多选')) type = 'multi';
            else if (titleSpan.textContent.includes('判断')) type = 'judge';
            else if (titleSpan.textContent.includes('单选')) type = 'single';
        }

        if (type === 'multi') { // 多选题
            const options = quesDiv.querySelectorAll('span.num_option_dx');
            console.log('多选题修补之初的table:', answerTable);
            if (answerTable[qIndex].length === 0) {
                console.log('进入初始化')
                answerTable[qIndex] = Array(options.length).fill(-1);
            }
            
            if (
                answerHistory[qIndex] &&
                answerHistory[qIndex].some(record => record.mark === 'right')
            ) {
                answerJson.push({
                    "题号": qNum,
                    "答案": answerHistory[qIndex][0]?.answer || ""
                });
                return;
            } else if (
                answerHistory[qIndex] &&
                answerHistory[qIndex].some(record => record.mark === 'half')
            ) {
                // 存在半对的答案
                const ansArr = answerHistory[qIndex]
                    .map(record => record.answer.trim())
                    .flatMap(str => str.includes(',') ? str.split(',').map(s => s.trim()) : str.split(''));
                ansArr.forEach(ch => {
                    answerTable[qIndex][ch.charCodeAt(0) - 'A'.charCodeAt(0)] = 1; 
                });
            } else {
                console.log('before修补的answerTable:', answerTable);
                const ansArr = answerHistory[qIndex]
                    .map(record => record.answer.trim())
                    .flatMap(str => str.includes(',') ? str.split(',').map(s => s.trim()) : str.split(''));
                console.log('ansArr:', ansArr);
                const filteredArr = ansArr.filter(ch => answerTable[qIndex][ch.charCodeAt(0) - 'A'.charCodeAt(0)] !== 1);
                console.log('filteredArr:', filteredArr);
                if (filteredArr.length === 1) {
                    answerTable[qIndex][filteredArr[0].charCodeAt(0) - 'A'.charCodeAt(0)] = 0;
                }
                console.log('answerTable:', answerTable);
                //confirm('debug: 可能存在多选题答案修补问题，请检查控制台输出');
            }
            let tryAnother = true;
            let ansStr = "";
            for (let i = 0; i < options.length; i++) {
                if (answerTable[qIndex][i] === -1) {
                    if (tryAnother) {
                        ansStr += options[i].getAttribute('data');
                        tryAnother = false; 
                    } 
                } else if (answerTable[qIndex][i] === 1) {
                    ansStr += options[i].getAttribute('data');
                }
            }
            if (ansStr.length > 0) {
                answerJson.push({
                    "题号": qNum,
                    "答案": ansStr
                });
            } else {
                confirm(`题号${qNum}未找到任何有效答案`);
            }

        } else if (type === 'judge') { // 判断题
            const options = quesDiv.querySelectorAll('span.num_option_dx');
            if (answerTable[qIndex].length === 0) {
                answerTable[qIndex] = Array(options.length).fill(-1);
            }

            if (
                answerHistory[qIndex] &&
                answerHistory[qIndex].some(record => record.mark === 'right')
            ) {
                answerJson.push({
                    "题号": qNum,
                    "答案": answerHistory[qIndex][0]?.answer || ""
                });
                return;
            } else {
                let ansStr = answerHistory[qIndex][0]?.answer;
                ansStr = (ansStr[0] === '对' || ansStr[0] === 'A' || ansStr === 'true') ? 'false' : 'true';
                if (ansStr) {
                    answerJson.push({
                        "题号": qNum,
                        "答案": ansStr
                    });
                } else {
                    confirm(`题号${qNum}未找到任何有效答案`);
                }
            }
        } else { // 单选题
            const options = quesDiv.querySelectorAll('span.num_option_dx');
            if (answerTable[qIndex].length === 0) {
                answerTable[qIndex] = Array(options.length).fill(-1);
            }

            if (
                answerHistory[qIndex] &&
                answerHistory[qIndex].some(record => record.mark === 'right')
            ) {
                answerJson.push({
                    "题号": qNum,
                    "答案": answerHistory[qIndex][0]?.answer || ""
                });
                return;
            } else {
                let ansStr = answerHistory[qIndex][0]?.answer;
                const copy = ansStr;
                answerTable[qIndex][ansStr[0].charCodeAt(0) - 'A'.charCodeAt(0)] = 0;
                while(answerTable[qIndex][ansStr[0].charCodeAt(0) - 'A'.charCodeAt(0)] === 0) {
                    ansStr = String.fromCharCode((ansStr[0].charCodeAt(0) - 'A'.charCodeAt(0) + 1) % 4 + 'A'.charCodeAt(0));
                }
                if (ansStr && ansStr !== '\u0000') {
                    answerJson.push({
                        "题号": qNum,
                        "答案": ansStr
                    });
                } else {
                    console.log('copy:', copy);
                    console.log('ansStr:', ansStr);
                    confirm(`题号${qNum}未找到任何有效答案`);
                }
            }
        }
    });
    console.log('修补答案完成:', answerJson);
    return answerJson;
}

async function handleIframeChange(prama = DEFAULT_TEST_OPTION) { 
    if (allTaskDown) return;


    if (handleIframeLock) {
        console.log('handleIframeChange 已加锁，跳过本次调用');
        return;
    }
    handleIframeLock = true;

    // 唯一性控制，防止异步出bug（事实上确实会出很多bug）
    let firstLayerCancel = null;
    let secondLayerCancel = null;
    let thirdLayerCancel = null;
    let FourthLayerCancel = null;

    (function firstLayer() {  //抓取三层iframe
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
                            return findInnerDocs(outerDoc);
                        },
                        (InnerDocs = []) => {
                        (async function thirdLayer() {
                            if (!Array.isArray(InnerDocs) || InnerDocs.length === 0) {
                                console.warn('内层Docs为空，尝试跳过');
                                console.log('所有章节任务已完成，准备跳转到下一章节');
                                console.log('检查是否有学习测验');
                                await timeSleep(10 * DEFAULT_SLEEP_TIME);
                                const learningTest = document.getElementById('dct2');
                                if (learningTest && prama === 1) {
                                    const unfinished = document.querySelector('.ans-job-icon[aria-label="任务点未完成"]');
                                    if (unfinished) {
                                        // 存在未完成任务点
                                        console.log('有未完成的任务点');
                                    } else {
                                        // 没有未完成任务点
                                        console.log('所有任务点已完成');
                                        learningTest.click();
                                        await timeSleep(DEFAULT_SLEEP_TIME);
                                        handleIframeLock = false; //
                                        await handleIframeChange(1);  
                                    }   
                                    return;
                                } else {
                                    console.log('此章节学习测验已处理');
                                    if (prama !== 2) answerTable = [];
                                    console.log('已处理完所有章节任务，准备跳转到下一章节');
                                    await timeSleep(25 * DEFAULT_SLEEP_TIME);
                                    const unfinished = document.querySelector('.ans-job-icon[aria-label="任务点未完成"]');
                                    if (unfinished) {
                                        // 存在未完成任务点
                                        console.log('有未完成的任务点');

                                    } else {
                                        // 没有未完成任务点
                                        console.log('所有任务点已完成');
                                        continueToNextChapter();
                                    }
                                    
                                }
                                return;
                            }
                            // 第三层
                            console.log('第三层回调执行');
                            console.log('找到的内层文档数目:', InnerDocs.length);
                            const needSkip = outerDoc.querySelectorAll('.ans-job-icon');
                            let taskCount = 0;
                            async function runTasksSerially() {
                                for (const { innerDoc, Type } of InnerDocs) { // for...of 防错乱
                                    console.log(`处理 ${Type} 任务点...`);
                                    if (taskCount >= needSkip.length) {
                                        console.log('已处理完所有任务点，准备跳转到下一章节');
                                        if (Type === 'Work') prama = 0; 
                                    } else if (needSkip[taskCount].getAttribute('aria-label') === '任务点已完成') {
                                        console.log('任务点已完成，跳过');
                                        if (Type === 'Work') prama = 0; 
                                    } else if (Type === 'Video') {
                                        console.log('该章节为VIDEO,进行参数捕获');
                                        await new Promise((resolve) => {
                                            if (FourthLayerCancel) FourthLayerCancel();
                                            FourthLayerCancel = waitForElement(
                                                () => {
                                                    if (allTaskDown) return;
                                                    console.log('第四层回调执行');
                                                    return findVideoElement(innerDoc);
                                                },
                                                async (innerParam) => {
                                                    if (!innerParam) {
                                                        console.warn('页面异常加载，尝试跳过');
                                                        resolve();
                                                        return;
                                                    }
                                                    const { videoDiv, launchBtn, target, playControlBtn, paceList , muteBtn } = innerParam;
                                                    await autoPlayVideo(
                                                        innerDoc,
                                                        videoDiv,
                                                        launchBtn,
                                                        target,
                                                        playControlBtn,
                                                        paceList,
                                                        muteBtn
                                                    );
                                                    resolve();
                                                }
                                            );
                                        });
                                    } else if (Type === 'Pdf') {
                                        console.log('该章节为PDF,进行参数捕获');
                                        await new Promise((resolve) => {
                                            if (thirdLayerCancel) thirdLayerCancel();
                                            thirdLayerCancel = waitForElement(
                                                () => {
                                                    return findPdfElement(innerDoc);
                                                },
                                                async ({ pdfHtml } = {}) => {
                                                    if (!pdfHtml) {
                                                        console.error('请求超时, 请检查网络或与作者联系');
                                                        resolve();
                                                        return;
                                                    }
                                                    const toBottom = await scrollPdfToBottom(pdfHtml);
                                                    if (toBottom) {
                                                        console.log('PDF滚动成功！');
                                                    } else {
                                                        console.warn('PDF多次滚动无效，可能页面未加载完全');
                                                    }
                                                    await timeSleep(2 * DEFAULT_SLEEP_TIME);
                                                    console.log('章节处理完毕');
                                                    resolve();
                                                }
                                            );
                                        });
                                    } else if (Type === 'Work') {
                                        console.log('该章节为WORK,进行参数捕获');
                                        await new Promise((resolve) => {
                                            if (thirdLayerCancel) thirdLayerCancel();
                                            thirdLayerCancel = waitForElement(
                                                () => {
                                                    return findWorkElement(innerDoc);
                                                },
                                                async ({ testDoc, testList, submitBtn } = {}) => {
                                                    if (!testList || testList.length === 0) {
                                                        console.error('请求超时, 请检查网络或与作者联系');
                                                        resolve();
                                                        return;
                                                    }
                                                    console.log('已找到测试题目:', testList);
                                                    if (prama === 2) {
                                                        console.warn('检测为不及格，开始修补模式');
                                                        const answerBasicList = testDoc.querySelectorAll('.newAnswerBx');
                                                        if (answerBasicList.length === 0) {
                                                            console.warn('未找到答案列表，可能是页面加载异常');
                                                            resolve();
                                                            return;
                                                        }
                                                        let index = 0;
                                                        let answerHistory = [];
                                                        for (const answerBasic of answerBasicList) {
                                                            index++;
                                                            if (!answerHistory[index]) {
                                                                answerHistory[index] = [];
                                                            }
                                                            const answerCon = answerBasic.querySelector('.answerCon');
                                                            let answerMark;
                                                            const wrong = answerBasic.querySelector('.marking_cuo');
                                                            const half = answerBasic.querySelector('.marking_bandui');
                                                            if (wrong) {
                                                                answerMark = 'wrong';
                                                            } else if (half) {
                                                                answerMark = 'half';
                                                            } else {
                                                                answerMark = 'right';
                                                            }
                                                            answerHistory[index].push({
                                                                answer: answerCon.textContent.trim(),
                                                                mark: answerMark
                                                            });
                                                        }
                                                        console.log('已获取到答案历史:', answerHistory);
                                                        //confirm('[调试],已获取到答案历史，准备修补');
                                                        let answerJson = answerFixes(testList, answerHistory);
                                                        if (answerJson.length === 0) {
                                                            confirm('fix答案失败');
                                                            resolve();
                                                            return;
                                                        } else {
                                                            autoFillAnswers(testList, answerJson);
                                                            console.log('已自动填充答案');
                                                            resolve();
                                                        }
                                                        //confirm('已修补答案，准备提交');
                                                        submitBtn.click();
                                                        await timeSleep(DEFAULT_SLEEP_TIME);
                                                        const configElement = document.getElementById('workpop');
                                                        const configBtn = document.getElementById('popok');
                                                        if (configElement && window.getComputedStyle(configElement).display !== 'none') {
                                                            if (configBtn) {
                                                                configBtn.click();
                                                                console.log('已自动点击确定按钮');
                                                            } else {
                                                                console.warn('未找到确定按钮');
                                                            }
                                                        }
                                                        await timeSleep(2 * DEFAULT_SLEEP_TIME);
                                                        //confirm ('已提交测试题目，等待结果');
                                                        const configContent = document.getElementById('popcontent');
                                                        if (configContent && configContent.textContent.includes('未达到及格线')) {
                                                            console.warn('检测到未及格，需重做！');
                                                            configBtn.click();
                                                            await timeSleep(DEFAULT_SLEEP_TIME);
                                                            handleIframeLock = false; //
                                                            await handleIframeChange(2); 
                                                            return;
                                                        } else {
                                                            console.log('已成功提交测试题目');
                                                            answerTable = [];
                                                            console.log('已处理完所有章节任务，准备跳转到下一章节');
                                                            await timeSleep(25 * DEFAULT_SLEEP_TIME);
                                                            const unfinished = document.querySelector('.ans-job-icon[aria-label="任务点未完成"]');
                                                            if (unfinished) {
                                                                // 存在未完成任务点
                                                                console.log('有未完成的任务点');
                                                            } else {
                                                                // 没有未完成任务点
                                                                console.log('所有任务点已完成');
                                                                continueToNextChapter();
                                                            }
                                                            
                                                        }
                                                    } else if (window._ws && window._ws.readyState === 1) {
                                                        window._ws.send('已找到题目，开始传输');
                                                        const htmlStr = testDoc.documentElement.outerHTML;
                                                        if (answerTable) answerTable = [];
                                                        window._ws.send(JSON.stringify({
                                                            type: 'testDocHtml',
                                                            html: htmlStr
                                                        }));
                                                        await new Promise(resolve => {
                                                            function onMessage(event) {
                                                                try {
                                                                    // 判断是否收到的是答案json（一般不是"收到"而是json字符串）
                                                                    let answerJson;
                                                                    try {
                                                                        answerJson = JSON.parse(event.data);
                                                                    } catch (e) {
                                                                        // 不是json就忽略
                                                                        if (event.data === '收到') {
                                                                            window._ws.removeEventListener('message', onMessage);
                                                                            console.log('收到Python回信，继续后续流程');
                                                                            resolve();
                                                                        }
                                                                        return;
                                                                    }
                                                                    // 如果能解析为json，自动填答
                                                                    autoFillAnswers(testList, answerJson);
                                                                    window._ws.removeEventListener('message', onMessage);
                                                                    console.log('已自动填充答案');
                                                                    resolve();
                                                                } catch (e) {
                                                                    console.warn('处理回信时出错', e);
                                                                }
                                                            }
                                                            window._ws.addEventListener('message', onMessage);
                                                        });
                                                        //confirm('已创建答案，准备提交');
                                                        submitBtn.click();
                                                        await timeSleep(DEFAULT_SLEEP_TIME);
                                                        const configElement = document.getElementById('workpop');
                                                        const configBtn = document.getElementById('popok');
                                                        if (configElement && window.getComputedStyle(configElement).display !== 'none') {
                                                            if (configBtn) {
                                                                configBtn.click();
                                                                console.log('已自动点击确定按钮');
                                                            } else {
                                                                console.warn('未找到确定按钮');
                                                            }
                                                        }
                                                        await timeSleep(2 * DEFAULT_SLEEP_TIME);
                                                        const configContent = document.getElementById('popcontent');
                                                        if (configContent && configContent.textContent.includes('未达到及格线')) {
                                                            configBtn.click();
                                                            await timeSleep(DEFAULT_SLEEP_TIME);
                                                            console.warn('检测到未及格，需重做！');
                                                            handleIframeLock = false; 
                                                            await handleIframeChange(2); 
                                                            return;
                                                        } else {
                                                            console.log('已成功提交测试题目');
                                                            answerTable = [];
                                                            console.log('已处理完所有章节任务，准备跳转到下一章节');
                                                            await timeSleep(25 * DEFAULT_SLEEP_TIME);
                                                            const unfinished = document.querySelector('.ans-job-icon[aria-label="任务点未完成"]');
                                                            if (unfinished) {
                                                                // 存在未完成任务点
                                                                console.log('有未完成的任务点');
                                                            } else {
                                                                // 没有未完成任务点
                                                                console.log('所有任务点已完成');
                                                                continueToNextChapter();
                                                            }
                                                                                                                        
                                                        }
                                                        
                                                    } else {
                                                        console.warn('WebSocket未连接，无法发送测试题目');
                                                    }

                                                }
                                            );
                                        });
                                        
                                    }
                                    taskCount++;
                                }
                                // 所有任务完成后
                                console.log('所有章节任务已完成，准备跳转到下一章节');
                                console.log('检查是否有学习测验');
                                await timeSleep(10 * DEFAULT_SLEEP_TIME);
                                const learningTest = document.getElementById('dct2');
                                if (learningTest && prama === 1) {
                                    const unfinished = document.querySelector('.ans-job-icon[aria-label="任务点未完成"]');
                                    if (unfinished) {
                                        // 存在未完成任务点
                                        console.log('有未完成的任务点');
                                    } else {
                                        // 没有未完成任务点
                                        console.log('所有任务点已完成');
                                        learningTest.click();
                                        await timeSleep(DEFAULT_SLEEP_TIME);
                                        handleIframeLock = false; //
                                        await handleIframeChange(1);  
                                    }                                   
                                    return;
                                } else {
                                    console.log('此章节学习测验已处理');
                                    if (prama !== 2) answerTable = [];
                                    console.log('已处理完所有章节任务，准备跳转到下一章节');
                                    await timeSleep(25 * DEFAULT_SLEEP_TIME);
                                    const unfinished = outerDoc.querySelector('.ans-job-icon[aria-label="任务点未完成"]');
                                    if (unfinished) {
                                        // 存在未完成任务点
                                        console.log('有未完成的任务点');
                                    } else {
                                        // 没有未完成任务点
                                        console.log('所有任务点已完成');
                                        continueToNextChapter();
                                    }      
                                }
                            }

                            // 调用
                            runTasksSerially();
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
            if(skipSign % 2 === 0) {
                handleIframeLock = false; // 每次检测到变动后解锁
                handleIframeChange(); 
            }
        });
        leftObserver.observe(leftEl, { childList: true, subtree: true });
        handleIframeChange();
    } else {
        console.error('未找到 class 为 lefaramt 的元素');
    }
}

Object.defineProperty(document, 'visibilityState', { get: () => 'visible' });
Object.defineProperty(document, 'hidden', { get: () => false });

document.addEventListener('visibilitychange', function(e) {
    e.stopImmediatePropagation();
}, true);

window.onblur = null;
window.onfocus = null;
window.addEventListener = new Proxy(window.addEventListener, {
    apply(target, thisArg, args) {
        if (['blur', 'focus'].includes(args[0])) return;
        return Reflect.apply(target, thisArg, args);
    }
});

findCourseTree(); // 初始化课程树
initializeTreeIndex();

// 启动入口
startScriptWithMask(main);
