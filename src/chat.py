from openai import OpenAI

ark_client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="93a67648-c2cd-4a51-99ba-c51114b537ee",
)


def ark_deepseek_v3_2(prompt, max_new_tokens=8192):
    messages = [
        {'role': 'user', 'content': prompt}
    ]

    ***REMOVED*** tools = [{
    ***REMOVED***     "type": "web_search",
    ***REMOVED***     "max_keyword": 2,
    ***REMOVED*** }]

    response = ark_client.responses.create(
        model="ep-20251209150604-gxb42", ***REMOVED*** deepseek-v3-2-251201
        input=messages,
        ***REMOVED*** tools=tools,
        ***REMOVED*** temperature=0.7,
    )
    ***REMOVED*** print(response)

    try:
        reasoning_content = ''
        content = response.output[0].content[0].text
    except:
        reasoning_content = ''
        content = ''

    return reasoning_content, content


def ark_doubao_seed_1_6(prompt, image_urls=None, max_new_tokens=8192):
    content = []
    if image_urls is not None:
        for image_url in image_urls:
            content.append({
                "type": "input_image",
                "image_url": image_url
            })
    content.append({
        "type": "input_text",
        "text": prompt
    })
    messages = [
        {
            "role": "user",
            "content": content
        }
    ]
    response = ark_client.responses.create(
        model="ep-20251209160332-dshv6", ***REMOVED*** doubao-seed-1-6
        input=messages
    )
    ***REMOVED*** print(response)

    try:
        reasoning_content = response.output[0].summary[0].text
        content = response.output[1].content[0].text
    except:
        reasoning_content = ''
        content = ''

    return reasoning_content, content


if __name__ == "__main__":
    text = '''春游浩荡，是年年寒食，梨花时节。白锦无纹香烂漫，玉树琼苞堆雪。静夜沉沉，浮光霭霭，冷浸溶溶月。人间天上，烂银霞照通彻。
浑似姑射真人，天姿灵秀，意气殊高洁。万蕊参差谁信道，不与群芳同列。浩气清英，仙才卓荦，下土难分别。瑶台归去，洞天方看清绝。
作这一首《无俗念》词的，乃南宋末年一位武学名家，有道之士。此人姓丘，名处机，道号长春子，名列全真七子之一，是全真教中出类拔萃的人物。《词品》评论此词道：“长春，世之所谓仙人也，而词之清拔如此。”这首词诵的似是梨花，其实词中真意却是赞誉一位身穿白衣的美貌少女，说她“浑似姑射真人，天姿灵秀，意气殊高洁”，又说她“浩气清英，仙才卓荦”，“不与群芳同列”。词中所颂这美女，乃古墓派传人小龙女。她一生爱穿白衣，当真如风拂玉树，雪裹琼苞，兼之生性清冷，实当得起“冷浸溶溶月”的形容，以“无俗念”三字赠之，可说十分贴切。长春子丘处机和她在终南山上比邻而居，当年一见，赞叹人间竟有如斯绝世美女，便写下这首词来。
这时丘处机逝世已久，小龙女也已嫁与神雕大侠杨过为妻，同隐终南山古墓。在河南少室山山道之上，却另有一个少女，正在低低念诵此词。！
这少女十八九岁年纪，身穿淡黄衣衫，骑着一头青驴，正沿山道缓缓而上，心中默想：“也只有龙姊姊这样的人物，才配得上他。”这一个“他”字，指的自然是神雕大侠杨过了。她也不拉缰绳，任由那青驴信步而行，一路上山。过了良久，她又低声吟道：“欢乐趣，离别苦，就中更有痴儿女。君应有语，渺万里层云，千山暮雪，只影向谁去？”
她腰悬短剑，脸上颇有风尘之色，显是远游已久；韶华如花，正当喜乐无忧之年，可是容色间却隐隐有惆怅意，似是愁思袭人，眉间心上，无计回避。
这少女姓郭，单名一个襄字，乃大侠郭靖和女侠黄蓉的次女，有个外号叫做“小东邪”。她一驴一剑，只身漫游，原想排遣心中愁闷，岂知酒入愁肠固然愁上加愁，而名山独游，一般的也是愁闷徒增。
河南少室山山势雄峻，山道却是一长列宽大的石级，规模宏伟，工程着实不小，那是唐朝高宗为临幸少林寺而开凿，共长八里。郭襄骑着青驴委折而上，见对面山上五道瀑布飞珠溅玉，奔泻而下，再俯视群山，已如蚁蛭。顺着山道转过一个弯，遥见黄墙碧瓦，好大一座寺院。
她望着连绵屋宇出了一会儿神，心想：“少林寺向为天下武学之源，但华山两次论剑，怎地五绝之中并无少林寺高僧？难道寺中武学好手自忖并无把握，生怕堕了威名，索性便不去与会？又难道众僧修为精湛，名心尽去，武功虽高，却不去和旁人争强赌胜？”
她下了青驴，缓步走向寺前，只见树木森森，荫着一片碑林。石碑大半已经毁破，字迹模糊，不知写着些什么。心想：“便是刻凿在石碑上的字，年深月久之后也须磨灭，如何刻在我心上的，却是时日越久反越加清晰？”瞥眼只见一块大碑上刻着唐太宗敕赐少林寺寺僧的御札，嘉许少林寺僧立功平乱。碑文中说唐太宗为秦王时，带兵讨伐王世充，少林寺和尚投军立功，最著者共一十三人。其中只昙宗一僧受封为大将军，其余十二僧不愿为官，唐太宗各赐紫罗袈裟一袭。她神驰想象广当隋唐之际，少林寺武功便已名驰天下，数百年来精益求精，这寺中卧虎藏龙，不知有多少好手？
郭襄自和杨过、小龙女夫妇在华山绝顶分手后，三年来没得到他二人半点音讯。她常自思念，于是禀明父母，说要出来游山玩水，料想他夫妇当在终南山古墓隐居，便径往古墓求见。墓中出来两名侍女，说道杨过夫妇出外未归，招待郭襄在古墓中住了三天等候。但杨过夫妇未说明归期，郭襄便又出来随意行走，她自北而南，又从东至西，几乎踏遍了大半个中原，始终没听到有人说起神雕大侠杨过的近讯。
这一日她到了河南，想起少林寺中有一位僧人无色禅师是杨过的好友，自己十六岁生日之时，无色瞧在杨过的面上，曾托人送来一件礼物，虽从未和他见过面，不妨去向他打听打听，说不定他会知道杨过的踪迹，这才上少林寺来。'''
    prompt = f'解析小说《倚天屠龙记》第一章部分内容的人物关系和情节发展，并给出人物关系图和情节发展图。\n***REMOVED******REMOVED*** 小说内容：{text}'
    
    reasoning_content, content = ark_deepseek_v3_2(prompt)

    ***REMOVED*** reasoning_content, content = ark_doubao_seed_1_6(prompt)

    print(f'reasoning_content:\n{reasoning_content}\ncontent:\n{content}')
