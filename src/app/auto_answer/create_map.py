"""生成字体映射的工具, 通过图像哈希比对字形相似度"""
# pyright: reportAttributeAccessIssue=false
import concurrent.futures
import json
from pathlib import Path

import imagehash
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

COMMON_CHARS = set(
    "的一是了我不人在他有这个上们来到时大地为子中你说生国年着就那和要她出也得里后自以会家可下而过天去能对小多然于心学么之都好看起发当没成只如事把还用第样道想作种开美总从无情己面最女但现前些所同日手又行意动方期它头经长儿回位分爱老因很给名法间斯知世什两次使身者被高已亲其进此话常与活正感见明问力理尔点文几定本公特做外孩相西果走将月十实向声车全信重三机工物气每并别真打太新比才便夫再书部水像眼等体却加电主界门利海受听表德少克代员许稜先口由死安写性马光白或住难望教命花结乐色更拉东神记处让母父应直字场平报友关放至张认接告入笑内英军候民岁往何度山觉路带万男边风解叫任金快原吃妈变通师立象数四失满战远格士音轻目条呢病始达深完今提求清王化空业思切怎非找片罗钱紶吗语元喜曾离飞科言干流欢约各即指合反题必该论交终林请医晚制球决窢传画保读运及则房早院量苦火布品近坐产答星精视五连司巴奇管类未朋且婚台夜青北队久乎越观落尽形影红爸百令周吧识步希亚术留市半热送兴造谈容极随演收首根讲整式取照办强石古华諣拿计您装似足双妻尼转诉米称丽客南领节衣站黑刻统断福城故历惊脸选包紧争另建维绝树系伤示愿持千史谁准联妇纪基买志静阿诗独复痛消社算算义竟确酒需单治卡幸兰念举仅钟怕共毛句息功官待究跟穿室易游程号居考突皮哪费倒价图具刚脑永歌响商礼细专黄块脚味灵改据般破引食仍存众注笔甚某沉血备习校默务土微娘须试怀料调广蜖苏显赛查密议底列富梦错座参八除跑亮假印设线温虽掉京初养香停际致阳纸李纳验助激够严证帝饭忘趣支春集丈木研班普导顿睡展跳获艺六波察群皇段急庭创区奥器谢弟店否害草排背止组州朝封睛板角况曲馆育忙质河续哥呼若推境遇雨标姐充围案伦护冷警贝著雪索剧啊船险烟依斗值帮汉慢佛肯闻唱沙局伯族低玩资屋击速顾泪洲团圣旁堂兵七露园牛哭旅街劳型烈姑陈莫鱼异抱宝权鲁简态级票怪寻杀律胜份汽右洋范床舞秘午登楼贵吸责例追较职属渐左录丝牙党继托赶章智冲叶胡吉卖坚喝肉遗救修松临藏担戏善卫药悲敢靠伊村戴词森耳差短祖云规窗散迷油旧适乡架恩投弹铁博雷府压超负勒杂醒洗采毫嘴毕九冰既状乱景席珍童顶派素脱农疑练野按犯拍征坏骨余承置臓彩灯巨琴免环姆暗换技翻束增忍餐洛塞缺忆判欧层付阵玛批岛项狗休懂武革良恶恋委拥娜妙探呀营退摇弄桌熟诺宣银势奖宫忽套康供优课鸟喊降夏困刘罪亡鞋健模败伴守挥鲜财孤枪禁恐伙杰迹妹藸遍盖副坦牌江顺秋萨菜划授归浪听凡预奶雄升碃编典袋莱含盛济蒙棋端腿招释介烧误"
)

def glyph_to_img(ttf_path: Path, char, size=64):
    """将单个字形渲染为图像"""
    font = ImageFont.truetype(ttf_path, size)
    img = Image.new('L', (size, size), 255)
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), char, font=font, fill=0)
    return img

def multi_hash(img):
    """计算图像的多种哈希值"""
    return (
        imagehash.phash(img),
        imagehash.dhash(img),
        imagehash.average_hash(img)
    )

def hash_distance(h1, h2):
    """计算多种哈希值的距离"""
    return sum(a - b for a, b in zip(h1, h2, strict=False))

def std_worker(std_code, std_font_path):
    """预处理标准字体哈希"""
    char = chr(std_code)
    if char not in COMMON_CHARS:
        return None
    img = glyph_to_img(std_font_path, char)
    return (char, multi_hash(img))

def enc_worker(enc_code, enc_font_path: Path, std_hashes):
    """为加密字体字形找最相近的标准字形"""
    enc_char = chr(enc_code)
    img = glyph_to_img(enc_font_path, enc_char)
    h = multi_hash(img)
    # 找最相近的标准字形
    min_dist = float('inf')
    min_char = None
    for std_char, std_hash in std_hashes.items():
        dist = hash_distance(h, std_hash)
        if dist < min_dist:
            min_dist = dist
            min_char = std_char
    if min_char is not None:
        return (enc_char, min_char)
    return None

def create_font_mapping(
    enc_font_path: Path,
    std_font_path: Path,
    output_json: Path
) -> dict[str, str]:
    """生成加密字体到标准字体的映射, 并可选保存为json文件"""
    enc_font: TTFont = TTFont(enc_font_path)
    std_font: TTFont = TTFont(std_font_path)
    enc_cmap = enc_font['cmap'].getBestCmap()
    std_cmap = std_font['cmap'].getBestCmap()

    # 预处理标准字体哈希(多线程+多哈希)
    std_hashes = {}
    def std_worker_wrapper(std_code):
        return std_worker(std_code, std_font_path)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(std_worker_wrapper, std_cmap)
        for res in results:
            if res:
                std_hashes[res[0]] = res[1]

    mapping = {}
    def enc_worker_wrapper(enc_code):
        return enc_worker(enc_code, enc_font_path, std_hashes)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(enc_worker_wrapper, enc_cmap)
        for res in results:
            if res:
                mapping[res[0]] = res[1]

    if output_json:
        with output_json.open('w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        print(f"映射已保存到 {output_json}")
    return mapping
