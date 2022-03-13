class WordWrap:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        pass

    def get_paragraph(self, text):
        # 所有文字的段落
        paragraph = ""
        # 宽度总和
        sum_width = 0
        # 几行
        line_count = 1
        # 行高
        line_height = 0
        for char in text:
            width, height = self.draw.textsize(char, self.font)
            sum_width += width
            if sum_width > self.width:  # 超过预设宽度就修改段落 以及当前行数
                line_count += 1
                sum_width = 0
                paragraph += '\n'
            paragraph += char
            line_height = max(height, line_height)
        if not paragraph.endswith('\n'):
            paragraph += '\n'
        return paragraph, line_height, line_count

    def split_text(self):
        # 按规定宽度分组
        max_line_height, total_lines = 0, 0
        allText = []
        for text in self.text.split('\n'):
            paragraph, line_height, line_count = self.get_paragraph(text)
            max_line_height = max(line_height, max_line_height)
            total_lines += line_count
            allText.append((paragraph, line_count))
        line_height = max_line_height
        total_height = total_lines * line_height
        return allText, total_height, line_height

    def draw_text(self, xy, text, font, draw, width):
        self.draw = draw
        self.font = font
        self.width = width
        self.text = text
        # 段落 , 行数, 行高
        self.paragraph, self.note_height, self.line_height = self.split_text()
        x, y = xy[0], xy[1]
        line_count = 0
        for paragraph, line_count in self.paragraph:
            self.draw.text((x, y), paragraph, 0, font=self.font)
            y += self.line_height * line_count
        return line_count , y