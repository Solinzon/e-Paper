import os
import random
import json

from main.utils.singleton import Singleton

data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                         "assets/paragraph_src/paragraph.json")
read_id_file = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                            "assets/paragraph_src/paragraph_read_id.json")

class ParagraphManager(object):
    def __init__(self):
        pass

    paragraph_data = {}

    def get_paragraph(self, refresh = False) -> dict:
        if not refresh :
            print("get_paragraph : " + refresh.__str__() + ", content = "+ str(self.paragraph_data) )
            return ParagraphManager.paragraph_data
        ids = []
        read_ids = self.load_read_id()
        data = self.load_data()
        for id in data:
            ids.append(id)
        if len(ids) <= 0:
            return {
                "content":"没有了对高处的恐惧，就体会不到高处之美。",
                "from":"三体II·黑暗森林"
            }

        i = 0
        while True:
            index = random.randint(0, len(ids) - 1)
            id = ids[index]
            if id not in read_ids:
                read_ids.append(id)
                self.save_read_id(read_ids)
                break
            if i > 10000:
                id = ids[0]
                print("内容显示完了")
                break
            i = i + 1
        ParagraphManager.paragraph_data = {
            "content": data.get(id).get("hitokoto"),
            "from": data.get(id).get("from")
        }
        print("get_paragraph : " + refresh.__str__() + ", content = " + str(ParagraphManager.paragraph_data))
        return ParagraphManager.paragraph_data

    def save_read_id(self, ids):
        with open(read_id_file, "w") as f:
            json.dump(ids, f)

    def load_read_id(self) -> []:
        with open(read_id_file, "r") as f:
            json_read_id = json.loads(f.read())
            return json_read_id

    def load_data(self):
        with open(data_file, "r") as f:
            json_data = json.loads(f.read())
            return json_data
