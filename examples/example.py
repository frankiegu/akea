#!/usr/bin/env python
# -*-coding:utf-8-*-


from nlp.segment import Segment

test_string = '广州性价比不错的中档粤式酒楼，广州大桥脚、客村附近，望江地段好金贵，二沙岛过条桥就到了，不过地铁不方便是硬伤。声名鹊起是源于他家的两位老板是来自白天鹅酒店有多年丰富经验的大厨。有很高的粤菜功底，加上本身做哩行对选料的严格掌控，仲经常抛头露面出来客串部长，难怪开业至今生意节节高、口碑唔错啦。住宅区的裙楼，门面比较大气，旋转楼梯上二楼，不是包房的话坐大厅以4-8人桌为主，人多的话提前电话约比较稳妥。来过几次，随意挑几道菜品点评下。烧鹅（58元/例）：烧鹅唔算肥，皮烧得好干净、甘香，部位几好。有另外配的酸梅汁。面筋豆腐炆火腩（43元）：热辣辣的煲仔菜是粤菜的精华之一，荤素搭配的面筋豆腐炆火腩，火腩肥而不腻，搭配吸味噶面筋和豆腐，重口味挚爱。法国鹅肝粒炒饭（43元）：鹅肝讲真真系无咩存在感，分量大约6-8人左右啦。饭身比较干身，味道唔会特别重，简单的一道原味炒饭，点击率听说挺高的。石锅煎焗脆鱼嘴（43元）：走油炸过嘎鱼嘴（类似鱼头），用蒜头炆翻热放落保温的石锅里面，辣辣最适合冬日啦。松花银丝饼（29元）：听闻是招牌的银丝饼，好考验师傅的手艺，传统手工菜，宜家外面好难食到嘎啦。银丝饼卖相不错，单单饼本身是没有什么味道的，全凭借炼奶添味。'

seg2 = Segment(load_catering_dict=False)

res2 = seg2.cut(test_string)

res2 = list(res2)

seg = Segment()

res = seg.cut(test_string)

res = list(res)

for item in res2:
    if item in res:
        pass
    else:
        print(item)
print('###############')
for item in res:
    if item in res2:
        pass
    else:
        print(item)

print(res2)


print(res)