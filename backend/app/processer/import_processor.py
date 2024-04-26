from app.neo4j.query_service import Neo4jDatabaseInspector
from app.model.llm import ModelFactory
from langchain_core.messages import SystemMessage, HumanMessage,AIMessage
from langchain_core.prompts import PromptTemplate
import re


class ImportProcessor:
    def __init__(self, file_path, product_name):
        self.model = ModelFactory.get_gpt35_model(max_token=2500)
        self.file_path = file_path
        self.product_name = product_name
        self.rectify_code_string_template = '''
我现在有一些 cypher CODE 现在报错{error_message},
请帮我给出修正后完整正确的code ，只给出code 不要其他内容
下面是code:
{code}
'''
        self.example = [
        {
            "user": {
                'data': '''
基本参数
国内发布时间
2023年
电商报价
￥5488
产品型号
Mate 60
上市日期
2023年9月
机身颜色
雅川青，白沙银，南糯紫，雅丹黑  查看外观
支持蓝牙
支持

外形
长度
161.4mm
宽度
76mm
''',
                'product_name': 'HUAWEI Mate 60（12GB/256GB)',
                'relation_type': ''
            },
            'assistant': '''
```
CREATE (p:Product {name: "HUAWEI Mate 60（12GB/256GB)"})
MERGE (releaseYear:Parameter {name: "国内发布时间", value: 202300, unit: "month"})
MERGE (price:Parameter {name: "电商报价", value: 5488, unit: "￥"})
MERGE (model:Parameter {name: "产品型号", value: " HUAWEI mate 60"})
MERGE (marketDate:Parameter {name: "上市日期", value: 202309,unit: "month"})
MERGE (color1:Parameter {name: "机身颜色", value: "雅川青"})
MERGE (color2:Parameter {name: "机身颜色", value: "白沙银"})
MERGE (color3:Parameter {name: "机身颜色", value: "南糯紫"})
MERGE (color4:Parameter {name: "机身颜色", value: "雅丹黑"})
MERGE (bluetooth:Parameter {name: "支持蓝牙", value: true})

MERGE (length:Parameter {name: "长度", value: 161.4, unit: "mm"})
MERGE (width:Parameter {name: "宽度", value: 76, unit: "mm"})

CREATE (p)-[:value国内发布时间]->(releaseYear)
CREATE (p)-[:value电商报价]->(price)
CREATE (p)-[:has产品型号]->(model)
CREATE (p)-[:value上市日期]->(marketDate)
CREATE (p)-[:has机身颜色]->(color1)
CREATE (p)-[:has机身颜色]->(color2)
CREATE (p)-[:has机身颜色]->(color3)
CREATE (p)-[:has机身颜色]->(color4)
CREATE (p)-[:is支持蓝牙]->(bluetooth)
CREATE (p)-[:value长度]->(length)
CREATE (p)-[:value宽度]->(width)
```
'''
        },
            {
                "user": {
                    'data': '''
基本参数
国内发布时间
2024年
电商报价
￥5988
产品型号
XIAOMI 14S
上市日期
2024年9月
机身颜色
川青，沙银，糯紫 查看外观
是否支持NFC
是
是否支持蓝牙
是
5g网络
        ''',
                    'product_name': 'XIAOMI 14S（12GB/256GB）',
                    'relation_type': 'value国内发布时间,value电商报价,has产品型号,value上市日期,has机身颜色,is支持蓝牙,value宽度'
                },
                'assistant': '''
```
CREATE (p:Product {name: "XIAOMI 14S（12GB/256GB"})
MERGE (releaseYear:Parameter {name: "国内发布时间", value: 202400, unit:"month"})
MERGE (price:Parameter {name: "电商报价", value: 5988, unit: "￥"})
MERGE (model:Parameter {name: "产品型号", value: "xiaomi 14s"})
MERGE (marketDate:Parameter {name: "上市日期", value: 202409})
MERGE (color1:Parameter {name: "机身颜色", value: "雅青"})
MERGE (color2:Parameter {name: "机身颜色", value: "沙银"})
MERGE (color3:Parameter {name: "机身颜色", value: "糯紫"})
MERGE (bluetooth:Parameter {name: "支持蓝牙", value: true})
MERGE (nfc:Parameter {name: "支持NFC", value: true})
MERGE (network5g:Parameter {name: "5G网络", value: "联通5G"})

CREATE (p)-[:value国内发布时间]->(releaseYear)
CREATE (p)-[:value电商报价]->(price)
CREATE (p)-[:has产品型号]->(model)
CREATE (p)-[:value上市日期]->(marketDate)
CREATE (p)-[:has机身颜色]->(color1)
CREATE (p)-[:has机身颜色]->(color2)
CREATE (p)-[:has机身颜色]->(color3)
CREATE (p)-[:is支持蓝牙]->(bluetooth)
CREATE (p)-[:is支持NFC]->(nfc)
CREATE (p)-[:has5G网络]->(network5G)
```
'''
            }
        ]
        self.generate_code_sys_message = '''
我现在要你充当一位neo4j 的cypher语句编写人员，你需要通过我给你的一些从手机信息网址上查询出来的的产品信息 ，我需要你帮我生成neo4j的插入语句，将这些产品信息插入到 neo4j中
我会给你三个相关信息,现有的数据库的relation type,爬取的文本内容,产品的规格名称
在生成neo4j 语句时候有一下几个要求
1、产品名称与规格里面后面括号里面是他的规格,生成的语句必须建立一个关系是PRODUCT 关联产品的名称（不包括括号的部分）
2、爬取内容的第一行是这个参数的分类，不进入节点,每个参数要与产品关联，关联的逻辑应该是所有参数关联到一个产品的节点上,一个节点只包括一个name 和一个value，
如果value为number 类型，应该包含一个unit值
3、你需要判断这个参数是不是数字类型，比如价格,上市日期，插入节点时候转换成数字类型，如果是日期类型的字段，需要将月补全，比如 2023年9月 你需要补全到 202309，
你还需要判断这个参数是不是bool类型,比如支持，不支持，支持为true 不支持为false
4、如果一个参数有多个用逗号分隔的值，你需要将逗号分割的值以列表的形式存储到每一个节点里面
5、所有节点的属性值都是唯一的你在插入过程中要保证唯一性，如果插入一个节点时候这个节点已经存在，则不插入这个节点，但是要将这个节点与产品关联
6、请直接给出插入语句，只需要输出插入语句，不需要其他内容，只给我给出 cypher语句
7、爬取内容会出现多个参数分类用两个以上换行隔开
8、如果参数中出现英文字母，全部将英文字母转换成小写
9、所有的关系都用英文来表达，参数和产品的关系命名要遵循参数名字的含义，不能所有参数都用一个关系
10、 如果参数和产品的关系可以从现有的关系中找到，则使用现有的关系名称，如果不存在则依据参数的名字创建一个新的关系
11、生成的代码不要包含注释,一定要用markdown的代码语法输出,merge 语句后面的tag 的名字不能以数字开头
        '''
        self.generate_code_string_template = '''
下面是neo4j中已有的 relation type:
{relation_type}
下面是爬取内容 {data}
产品名称与规格是 {product_name}
在生成neo4j 语句时候有一下几个要求
'''
        self.generate_code_prompt_template = PromptTemplate(template=self.generate_code_string_template,
                                                            input_variables=['relation_type', 'data', 'product_name'])
        self.rectify_code_prompt_template = PromptTemplate(template=self.rectify_code_string_template,
                                                           input_variables=['error_message', 'code'])

    def format_prompt(self, text):
        relation = Neo4jDatabaseInspector.get_all_relationships()
        relation_string = ",".join(relation)

        messages = [SystemMessage(self.generate_code_sys_message)]
        for e in self.example:
            user_string = self.generate_code_prompt_template.format(**e['user'])
            messages.append(HumanMessage(user_string))
            messages.append(AIMessage(e['assistant']))
        messages.append(HumanMessage(self.generate_code_prompt_template.format(data=text,product_name=self.product_name,
                                                                               relation_type=relation_string)))
        return messages


    @staticmethod
    def extra_code(str):
        code_blocks_with_lang = re.findall(r"```(.*?)\n(.*?)```", str, re.DOTALL)
        for lang, code in code_blocks_with_lang:
            return code

    def generate_insert_code(self, text):
        res = self.model.invoke(self.format_prompt(text))
        print(str(res))
        return self.extra_code(res.content)

    def rectify_code(self, code, error_message):
        prompt_value = self.rectify_code_prompt_template.format_prompt(error_message=error_message, code=code)
        res = self.model.invoke(prompt_value.to_messages())
        return self.extra_code(res.content)

    def run(self):
        with open(self.file_path, mode='r', encoding='utf-8') as f:
            text = f.read()
        code = None
        try_count = 0
        max_try_Count = 10
        error_message = ""
        while try_count < max_try_Count:
            try:
                try_count += 1
                if code:
                    code = self.rectify_code(code, error_message)
                else:
                    code = self.generate_insert_code(text)
                if code:
                    Neo4jDatabaseInspector.execute(code)
                    return
            except Exception as e:
                print(e)
                code = None
                error_message = str(e)
        raise Exception(error_message)


if __name__ == "__main__":
    # p = ImportProcessor('./app/crawler/result.txt', 'HUAWEI Mate 60（12GB/256GB)')
    # p.run()
    # p = ImportProcessor('./app/crawler/result1.txt', 'Redmi K70(12GB/256GB)')
    # p.run()
    p = ImportProcessor('./app/crawler/result2.txt', '苹果iPhone 15 Pro（128GB）')
    p.run()
