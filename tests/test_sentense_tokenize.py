#!/usr/bin/env python
# -*-coding:utf-8-*-


def test_sentense_tokenize():
    doc = '来广州出差，住在附近的康莱德酒店，晚上开完会就慕名而来，大概七点四十分的样子到的，人还有很多。刚入座，服务员就热情地让我点各种前菜，什么黄瓜，目前，凤爪啥的，我们都很不钟意，他们就臭着脸走了，后面的服务，不知道是不是因为我们没接受他们的推销，他们的服务总是有点不让人那么愉快。我们想点很多推荐的菜，什么烧味腊味之类的，结果被告知全没了，各种心塞，然后就情绪爆发地点了一些乱七八糟的东西。黄金煎饺，一共十五个，很小一个，味道很不错。还有个什么汤，我忘记了，广州普通话不是很能适应，但是味道很不错，里面有丝瓜海鲜什么的。一份豆腐煲，豆腐很嫩很入味，我吃了里面很多黄瓜。一份油麦菜，无功无过，最后几乎都剩下了。亮点是他们家的鱼生，我们三个人要了个4.8斤的，量非常大，有很多酱料，要自己调。服务员说了很多先后顺序，我们愣是没懂，觉得复杂，所以我索性让服务员帮我弄了，就是先在特定的玻璃盘子上倒上耗油，抹抹盘底，然后放入鱼生，然后放上姜丝，柠檬草，葱丝等各种配料，任君挑选，然后淋上酱汁，拌一拌，就能吃了，我吃了口一点没吃出鱼腥味，还不错，但也没别人推荐的那么传神。鱼生之外的耍鱼肉做成了砂锅，鱼肉很苏很入味，蛮好吃的，但不是我的菜。鹅肠，非常入味，推荐，而且吃很多也不会很撑，没负罪感。饮料叫了份蔓越莓玫瑰汁，一般般吧。没啥推荐不推荐的。甜品叫了姜汁撞奶？本来就超爱吃，姜汁味非常浓郁，奶很滑嫩，温温的特别棒，是我最喜欢吃的一样。如果不是明天早上还有会，真想去点都德也尝尝早茶，唉，忧桑。'

    from nlp.tokenize.sentence import sentence_tokenize

    res = sentence_tokenize(doc)
    print(res)

    text = "Are you curious about tokenization? Let's see how it works! We need to analyze a couple of sentences with punctuations to see it in action."

    sent_tokenize_list = sentence_tokenize(text, language='english')

    print(sent_tokenize_list)


test_sentense_tokenize()