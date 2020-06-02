"""
/**
 *@file Translate.py
 *@brief 菜鸡翻译软件
 *@detials 1、利用百度翻译API的翻译功能和有道云词典实现一个翻译软件。
           2、有图形界面供用户输入。界面相对美化
           3、可以查询单词，只支持汉英互译
           4、可以翻译句子，支持多种语言互译
           5、将用户查询的英文词保存在生词本里，有排序功能
           6、(已注释该功能)支持截图翻译--需安装Tesseract-ORC.exe，仅支持识别英文
 *@author caiji
 *@version V1.0
 *@date start:2020/4/9 17:51 ---- end:2020/4/11 16:19
 */

 # 开发平台: Pycharm 2019.1
 # 库: wxPython--GUI, urllib--链接API, hashlib--生成API所需数字MD5数字签名
       json--处理返回字段, bs4--将网页requests得到的网页信息转换成HTML
       requests--链接有道词典 csv--存放本地单词本 PIL--获取截图
       pyautogui--获取鼠标点击坐标 tesseract--识别图片文本
       keyboard--获取按键输入
"""

import csv
import wx
import urllib.parse
import hashlib
import random
import http.client
import json
import requests
import bs4
import re
# import PIL.Image
# import PIL.ImageGrab
# import pytesseract
# import keyboard
# from pyautogui import position

class MyFrame(wx.Frame):

    # 主窗体初始化
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, "菜鸡翻译软件", size=(800, 600))  # 设置窗体标题及尺寸

        self.leftpanel = wx.Panel(self)    # 创建左画布
        self.rightpanel1 = wx.Panel(self)   # 创建右画布--用于词典界面
        self.rightpanel2 = wx.Panel(self)  # 创建右画布--用于翻译界面
        self.rightpanel3 = wx.Panel(self)  # 创建右画布--用于单词本界面
        self.set_panel()

        # 文本格式设置
        self.font_style = wx.Font(20, wx.MODERN, wx.NORMAL, wx.NORMAL, False, '楷体')  # 设置文本格式
        self.label_font_style = wx.Font(15, wx.MODERN, wx.NORMAL, wx.NORMAL, False, '楷体')
        self.text_style = wx.Font(17, wx.MODERN, wx.NORMAL, wx.NORMAL, False, '新宋体')

        # 按钮初始化
        self.swbutton1 = wx.Button(self.leftpanel, -1, "查词", (70, 200), style=wx.BORDER_NONE)    # 创建按钮
        self.swbutton2 = wx.Button(self.leftpanel, -1, "翻译", (70, 300), style=wx.BORDER_NONE)
        self.swbutton3 = wx.Button(self.leftpanel, -1, "单词本", (70, 400), style=wx.BORDER_NONE)
        # 位图按钮初始化
        bit_bmpbutton = wx.Image("./Picture/转换.PNG").ConvertToBitmap()
        self.bmpbutton1 = wx.BitmapButton(self.rightpanel1, -1, bit_bmpbutton, pos=(260, 20),
                                          style=wx.BORDER_NONE)
        self.bmpbutton2 = wx.BitmapButton(self.rightpanel2, -1, bit_bmpbutton, pos=(260, 20),
                                          style=wx.BORDER_NONE)
        # 功能按钮初始化
        self.fubutton1 = wx.Button(self.rightpanel1, -1, "查询", (460, 275))
        self.fubutton2 = wx.Button(self.rightpanel2, -1, "开始翻译", (390, 275))
        self.fubutton3 = wx.Button(self.rightpanel2, -1, "截屏翻译", (100, 275), style=wx.BORDER_NONE)
        self.fubutton4 = wx.Button(self.rightpanel1, -1, "添加至单词本", (100, 275), style=wx.BORDER_NONE)
        self.set_button()
        self.set_button_event()

        # 位图创建
        bit_pitcure1 = wx.Image("./Picture/词典.PNG").ConvertToBitmap()  # 设置按钮对应的图标
        wx.StaticBitmap(self.leftpanel, -1, bit_pitcure1, pos=(15, 225))
        bit_pitcure2 = wx.Image("./Picture/翻译.PNG").ConvertToBitmap()
        wx.StaticBitmap(self.leftpanel, -1, bit_pitcure2, pos=(15, 325))
        bit_pitcure3 = wx.Image("./Picture/单词本.PNG").ConvertToBitmap()
        wx.StaticBitmap(self.leftpanel, -1, bit_pitcure3, pos=(15, 425))
        bit_pitcure = wx.Image("./Picture/图标.PNG").ConvertToBitmap()  # 设置软件图标
        wx.StaticBitmap(self.leftpanel, -1, bit_pitcure, pos=(35, 30))
        bit_pitcure4 = wx.Image("./Picture/相机.PNG").ConvertToBitmap()  # 设置软件图标
        wx.StaticBitmap(self.rightpanel2, -1, bit_pitcure4, pos=(60, 280))
        bit_pitcure5 = wx.Image("./Picture/添加.PNG").ConvertToBitmap()  # 设置软件图标
        wx.StaticBitmap(self.rightpanel1, -1, bit_pitcure5, pos=(60, 277))
        self.soft_name = wx.StaticText(self.leftpanel, -1, "菜鸡词典\n  V1.0")  # 创建软件名称
        self.soft_name.SetFont(self.label_font_style)
        self.soft_name.SetPosition((60, 160))

        # 文本输入框和显示框创建
        self.cd_input_text = wx.TextCtrl(self.rightpanel1, -1, "", size=(500, 200),
                                         style=wx.TE_MULTILINE | wx.TE_NO_VSCROLL)
        self.cd_output_text = wx.TextCtrl(self.rightpanel1, -1, "", size=(500, 200),
                                          style=wx.TE_MULTILINE | wx.BORDER_NONE | wx.TE_NO_VSCROLL | wx.TE_READONLY)
        self.fy_input_text = wx.TextCtrl(self.rightpanel2, -1, "", size=(500, 200),
                                         style=wx.TE_MULTILINE)
        self.fy_output_text = wx.TextCtrl(self.rightpanel2, -1, "", size=(500, 200),
                                          style=wx.TE_MULTILINE | wx.BORDER_NONE | wx.TE_READONLY)
        self.disply_text = wx.TextCtrl(self.rightpanel3, -1, "", size=(590, 500),
                                       style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.set_text()

        # 标签创建
        self.cd_source_label = wx.StaticText(self.rightpanel1, -1, "源语言")  # 标签创建
        self.cd_target_label = wx.StaticText(self.rightpanel1, -1, "目标语言")
        self.fy_source_label = wx.StaticText(self.rightpanel2, -1, "源语言")  # 标签创建
        self.fy_target_label = wx.StaticText(self.rightpanel2, -1, "目标语言")
        self.sort_label = wx.StaticText(self.rightpanel3, -1, "排序方式")
        self.set_label()

        # 下拉列表创建
        word_list = ["中文", "英文"]
        sentence_list_src = ["中文", "英文", "日语", "法语", "德语", "俄语", "繁体中文", "自动检测"]
        sentence_list_tar = ["中文", "英文", "日语", "法语", "德语", "俄语", "繁体中文"]
        sort_ways = ["A-Z", "Z-A", "乱序", "最近添加"]
        self.cd_source_word = wx.Choice(self.rightpanel1, -1, (100, 35), (100, 50), word_list)  # 下拉列表创建
        self.cd_target_word = wx.Choice(self.rightpanel1, -1, (370, 35), (100, 50), word_list)
        self.fy_source_word = wx.Choice(self.rightpanel2, -1, (100, 35), (100, 50), sentence_list_src)
        self.fy_target_word = wx.Choice(self.rightpanel2, -1, (370, 35), (100, 50), sentence_list_tar)
        self.sort_book = wx.Choice(self.rightpanel3, -1, (100, 17), (150, 100), sort_ways)
        self.set_choice()

        # 定义链接API所需字段
        self.api_url = "http://api.fanyi.baidu.com/api/trans/vip/translate"
        # 以下两个为百度翻译API提供的账户和密钥，鉴于隐私，这里不予提供，请自行添加
        self.my_appid = "" 
        self.my_key = ""

        # 定义翻译语言字典
        self.languages = {
            "中文": "zh",
            "英文": "en",
            "日语": "jp",
            "法语": "fra",
            "德语": "de",
            "俄语": "ru",
            "繁体中文": "cht",
            "自动检测": "auto"
        }

        # 定义有道翻译汉译英Find字符串
        liststr = ["font-weight: bold;",
                   " color: #959595; margin-right:",
                   " .5em; width : 36px; display: inline-block;"]
        self.find_style = ''.join(liststr)

        # 定义正则表达式，判断单词添加时是否是英译汉
        self.re_zh = re.compile(u'[\u4e00-\u9fa5]')
        self.re_en = re.compile(r'[a-z]')

        # 创建.csv文件路径
        self.csv_file = "./csv/words.csv"

        # 定义排序字典
        self.sortway = {
            "A-Z": 0,
            "Z-A": 1,
            "乱序": 2,
            "最近添加": 3
        }

    # 画布参数设置
    def set_panel(self):
        self.leftpanel.SetPosition((0, 0))  # 设置画布位置
        self.rightpanel1.SetPosition((200, 0))
        self.rightpanel2.SetPosition((200, 0))
        self.rightpanel3.SetPosition((200, 0))
        self.leftpanel.SetSize((200, 600))  # 设置画布大小
        self.rightpanel1.SetSize((600, 600))
        self.rightpanel2.SetSize((600, 600))
        self.rightpanel3.SetSize((600, 600))
        self.leftpanel.SetBackgroundColour("LIGHT GREY")  # 设置画布颜色
        self.rightpanel1.SetBackgroundColour("WHEAT")
        self.rightpanel2.SetBackgroundColour("WHEAT")
        self.rightpanel3.SetBackgroundColour("WHEAT")
        self.rightpanel2.Hide()     # 隐藏单词本和翻译界面，默认显示词典界面
        self.rightpanel3.Hide()

    # 按钮参数设置
    def set_button(self):
        # 界面切换按钮参数设置
        self.swbutton1.SetSize((80, 100))  # 设置按钮尺寸
        self.swbutton1.SetBackgroundColour("LIGHT GREY")  # 设置按钮背景颜色
        self.swbutton1.SetFont(self.font_style)  # 设置按钮文本格式
        self.swbutton2.SetSize((80, 100))
        self.swbutton2.SetBackgroundColour("LIGHT GREY")
        self.swbutton2.SetFont(self.font_style)
        self.swbutton3.SetSize((80, 100))
        self.swbutton3.SetBackgroundColour("LIGHT GREY")
        self.swbutton3.SetFont(self.font_style)
        # 位图按钮
        self.bmpbutton1.SetSize((50, 50))
        self.bmpbutton1.SetBackgroundColour("WHEAT")
        self.bmpbutton2.SetSize((50, 50))
        self.bmpbutton2.SetBackgroundColour("WHEAT")
        # 功能按钮
        self.fubutton1.SetSize((80, 40))
        self.fubutton1.SetBackgroundColour("WHEAT")
        self.fubutton1.SetFont(self.label_font_style)
        self.fubutton2.SetSize((150, 40))
        self.fubutton2.SetBackgroundColour("WHEAT")
        self.fubutton2.SetFont(self.label_font_style)
        self.fubutton3.SetSize((120, 40))
        self.fubutton3.SetBackgroundColour("WHEAT")
        self.fubutton3.SetFont(self.label_font_style)
        self.fubutton4.SetSize((120, 40))
        self.fubutton4.SetBackgroundColour("WHEAT")
        self.fubutton4.SetFont(self.label_font_style)

    # 按钮触发事件绑定
    def set_button_event(self):
        # 界面切换按钮
        self.Bind(wx.EVT_BUTTON, self.swbutton1evt, self.swbutton1)  # 绑定按钮事件
        self.Bind(wx.EVT_BUTTON, self.swbutton2evt, self.swbutton2)
        self.Bind(wx.EVT_BUTTON, self.swbutton3evt, self.swbutton3)
        self.swbutton1.SetDefault()
        self.swbutton2.SetDefault()
        self.swbutton3.SetDefault()
        # 位图按钮
        self.Bind(wx.EVT_BUTTON, self.bmpbutton1evt, self.bmpbutton1)
        self.bmpbutton1.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.bmpbutton2evt, self.bmpbutton2)
        self.bmpbutton2.SetDefault()
        # 功能按钮
        self.Bind(wx.EVT_BUTTON, self.fubutton1evt, self.fubutton1)
        self.fubutton1.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.fubutton2evt, self.fubutton2)
        self.fubutton2.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.fubutton3evt, self.fubutton3)
        self.fubutton3.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.fubutton4evt, self.fubutton4)
        self.fubutton4.SetDefault()

    # 文本框参数设置
    def set_text(self):
        self.cd_input_text.SetPosition((40, 70))    # 设置文本框位置
        self.cd_output_text.SetPosition((40, 320))
        self.cd_input_text.SetBackgroundColour("LIGHT BLUE")    # 设置背景颜色
        self.cd_output_text.SetBackgroundColour("WHEAT")
        self.cd_input_text.SetFont(self.text_style)
        self.cd_output_text.SetFont(self.text_style)
        self.fy_input_text.SetPosition((40, 70))
        self.fy_output_text.SetPosition((40, 320))
        self.fy_input_text.SetBackgroundColour("LIGHT BLUE")
        self.fy_output_text.SetBackgroundColour("WHEAT")
        self.fy_input_text.SetFont(self.text_style)
        self.fy_output_text.SetFont(self.text_style)
        self.disply_text.SetPosition((0, 60))
        self.disply_text.SetBackgroundColour("WHEAT")
        self.disply_text.SetFont(self.text_style)

    # 文本标签参数设置
    def set_label(self):
        self.cd_source_label.SetFont(self.label_font_style)  # 设置文本格式
        self.cd_source_label.SetPosition((120, 10))  # 设置标签位置
        self.cd_target_label.SetFont(self.label_font_style)
        self.cd_target_label.SetPosition((380, 10))
        self.fy_source_label.SetFont(self.label_font_style)
        self.fy_source_label.SetPosition((120, 10))
        self.fy_target_label.SetFont(self.label_font_style)
        self.fy_target_label.SetPosition((380, 10))
        self.sort_label.SetFont(self.label_font_style)
        self.sort_label.SetPosition((10, 20))

    # 下拉列表参数设置
    def set_choice(self):
        self.cd_source_word.SetStringSelection("英文")  # 设置初始值
        self.cd_target_word.SetStringSelection("中文")
        self.fy_source_word.SetStringSelection("英文")  # 设置初始值
        self.fy_target_word.SetStringSelection("中文")
        self.sort_book.SetStringSelection("最近添加")
        self.sort_book.Bind(wx.EVT_CHOICE, self.sortevt)  # 绑定下拉列表触发事件
        self.sort_book.SetFont(self.label_font_style)  # 设置文本格式

    # 按钮触发事件
    def swbutton1evt(self, nouse):
        self.rightpanel1.Show()
        self.rightpanel2.Hide()
        self.rightpanel3.Hide()

    def swbutton2evt(self, nouse):
        self.rightpanel1.Hide()
        self.rightpanel2.Show()
        self.rightpanel3.Hide()

    def swbutton3evt(self, nouse):
        self.rightpanel1.Hide()
        self.rightpanel2.Hide()
        self.rightpanel3.Show()
        self.disply_text.SetValue("")
        self.show_words()

    def bmpbutton1evt(self, nouse):
        temp_source = self.cd_source_word.GetStringSelection()
        temp_target = self.cd_target_word.GetStringSelection()
        self.cd_target_word.SetStringSelection(temp_source)
        self.cd_source_word.SetStringSelection(temp_target)

    def bmpbutton2evt(self, nouse):
        temp_source = self.fy_source_word.GetStringSelection()
        temp_target = self.fy_target_word.GetStringSelection()
        if temp_source == "自动检测":
            wx.MessageBox("目标语言不支持自动检测", "Warning", wx.OK)
        else:
            self.fy_target_word.SetStringSelection(temp_source)
            self.fy_source_word.SetStringSelection(temp_target)

    def fubutton1evt(self, nouse):
        temp_intext = self.cd_input_text.GetValue()
        src_word = self.cd_source_word.GetStringSelection()
        tar_word = self.cd_target_word.GetStringSelection()
        if temp_intext:
            if len(temp_intext.split(" ")) > 1:
                wx.MessageBox("请勿输入句子", "ERROR", wx.OK)
            else:
                if src_word == tar_word:
                    self.cd_output_text.SetValue(temp_intext)
                elif src_word == '中文':
                    self.zh_to_en(temp_intext)
                elif src_word == '英文':
                    self.en_to_zh(temp_intext)
        else:
            wx.MessageBox("请输入单词", "ERROR", wx.OK)

    def fubutton2evt(self, nouse):
        temp_intext = self.fy_input_text.GetValue()
        if temp_intext:
            src_langue = self.languages.get(self.fy_source_word.GetStringSelection())
            tar_langue = self.languages.get(self.fy_target_word.GetStringSelection())
            temp_outtext = self.request_to_api(temp_intext, src_langue, tar_langue)
            self.fy_output_text.SetValue(temp_outtext)
        else:
            wx.MessageBox("单词或句子不能为空", "Error", wx.OK)

    def fubutton3evt(self, nouse):
        messages = ["------------------该功能的代码已注释--------------------\n",
                    "由于PyautoGui会自动缩小GUI界面，导致GUI界面错位\n",
                    "故不提供该功能！\n (╯‵□′)╯︵┻━┻ (╯‵□′)╯︵┻━┻\n"
                    ]
        message = ''.join(messages)
        wx.MessageBox(message, "Error", wx.OK)
        # self.get_screen()

    def fubutton4evt(self, nouse):
        src_text = self.cd_input_text.GetValue()
        tar_text = self.cd_output_text.GetValue()
        if self.re_en.search(src_text):
            if self.re_zh.search(tar_text):
                self.add_word()
        else:
            wx.MessageBox("格式错误，仅支持添加英语单词", "Warning", wx.OK)

    def sortevt(self, nouse):
        self.disply_text.SetValue("")
        self.sort_words()

    def request_to_api(self, sendword, srclang, tarlang):
        q = sendword  # 设置要发送的句子或单词
        fromlang = srclang   # 设置源语言
        tolang = tarlang  # 设置目标语言
        salt = random.randint(32768, 65536)  # 生成随机码
        sign = self.my_appid + q + str(salt) + self.my_key  # 生成数字签名
        sign = hashlib.md5(sign.encode()).hexdigest()  # 对数字签名进行md5码转化
        myurl = self.api_url + '?appid=' + self.my_appid + '&q=' + urllib.parse.quote(
            q) + '&from=' + fromlang + '&to=' + tolang + '&salt=' + str(
            salt) + '&sign=' + sign
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')  # 链接至API
        httpClient.request('GET', myurl)
        response = httpClient.getresponse()
        jsonResponse = response.read().decode("utf-8")  # 获得返回的结果，结果为json格式
        js = json.loads(jsonResponse)  # 将json格式的结果转换字典结构
        dst = str(js["trans_result"][0]["dst"])  # 取得翻译后的文本结果
        return dst

    def en_to_zh(self, sendword):
        try:    # 启用异常处理，避免因单词拼写错误而引发的错误
            get_result = requests.get(url='http://dict.youdao.com/w/%s/#keyfrom=dict2.top' % sendword)  # 向有道词典查询单词
            get_result.raise_for_status()  # 防止 ERROR:404
            soup = bs4.BeautifulSoup(get_result.text, "html.parser")    # 将网页信息转换成html代码
            trans_result = soup.find(class_='trans-container')('ul')[0]('li')  # 查找翻译结果所在位置的字典
            self.cd_output_text.SetValue("")  # 清空翻译结果
            for item in trans_result:
                if item.text:
                    self.cd_output_text.AppendText(item.text+"\n")  # 显示翻译结果
        except Exception:
            wx.MessageBox("没有查询到结果，请检查单词是否正确", "ERROR", wx.OK)

    def zh_to_en(self, sendword):
        try:  # 启用异常处理，避免因汉字拼写错误而引发的错误
            get_result = requests.get(url='http://dict.youdao.com/w/%s/#keyfrom=dict2.top' % sendword)  # 向有道词典查询单词
            get_result.raise_for_status()  # 防止 ERROR:404
            soup = bs4.BeautifulSoup(get_result.text, "html.parser")  # 将网页信息转换成html代码
            # 查找翻译结果所在位置的字典
            results = soup.find(class_="trans-container")('p')
            self.cd_output_text.SetValue("")  # 清空查询结果
            for result in results:
                for style_item in result.find_all(style="%s" % self.find_style):  # 查找所有表示词性的文本
                    self.cd_output_text.AppendText(style_item.text + "\t")
                for trans_item in result.find_all(class_="search-js"):      # 查找所有存放单词的文本
                    if trans_item == result.find_all(class_="search-js")[-1]:
                        self.cd_output_text.AppendText(trans_item.text + "\n")
                    else:
                        self.cd_output_text.AppendText(trans_item.text + " ; ")
        except Exception:
            wx.MessageBox("没有查询到结果，请检查单词是否正确", "ERROR", wx.OK)

    def add_word(self):
        word = self.cd_input_text.GetValue()  # 获取单词
        result = self.cd_output_text.GetValue()  # 获取单词翻译
        # 读取词典，判断是否有重复单词
        with open(self.csv_file, 'r') as csv_read:
            judge_temp = csv.reader(csv_read)
            for item in judge_temp:
                # 判断是否存在重复单词
                if word in item:
                    write_flag = 0
                else:
                    write_flag = 1
        # 如果单词不重复，则写入，反之不写入
        if write_flag:
            with open(self.csv_file, 'a', newline="") as csv_stream:
                csv_writer = csv.writer(csv_stream)
                csv_writer.writerow([word, result])

    def show_words(self):
        # 读取CSV文件
        with open(self.csv_file, 'r') as csv_stream:
            temp_word = csv.reader(csv_stream)
            for item in temp_word:
                for i in range(0, len(item)):
                    self.disply_text.AppendText(item[i]+"\n")  # 按格式显示单词本
        self.disply_text.ShowPosition(0)  # 排序完返回第一行

    def sort_words(self):
        # 读取CSV文件
        dict_word = {}
        with open(self.csv_file, 'r') as csv_stream:
            temp_word = csv.reader(csv_stream)  # 将数据转换成字典，方便排序
            for items in temp_word:
                dict_word[items[0]] = items[1]
        sort_select = self.sort_book.GetStringSelection()  # 获得排序方式
        number = self.sortway[sort_select]  # 判断排序方式对应的数字
        if number == 0:
            dict_temp = sorted(dict_word)  # A-Z
            self.update_disply(dict_temp, dict_word)
        elif number == 1:
            dict_temp = sorted(dict_word, reverse=True)  # Z-A
            self.update_disply(dict_temp, dict_word)
        elif number == 2:
            self.sort_ra(dict_word)  # 乱序
        else:
            self.sort_re(dict_word)  # 最近添加
        self.disply_text.ShowPosition(0)  # 排序完返回第一行

    def sort_re(self, dictin):
        dict_key = list(dictin.keys())  # 获取字典所有键
        for i in range(0, len(dict_key)):
            item = dict_key[len(dict_key)-1-i]  # 获取从新到旧的键
            self.disply_text.AppendText(item + "\n")    # 显示按最新添加排序的单词本
            self.disply_text.AppendText(dictin[item]+"\n")

    def sort_ra(self, dictin):
        dict_key = list(dictin.keys())  # 获取字典所有键
        random.shuffle(dict_key)  # 乱序字典的键
        for item in dict_key:
            self.disply_text.AppendText(item + "\n")  # 显示乱序后的结果
            self.disply_text.AppendText(dictin[item] + "\n")

    def update_disply(self, listin, dictin):
        for item in listin:
            self.disply_text.AppendText(item + "\n")  # 更新单词本
            self.disply_text.AppendText(dictin[item]+"\n")

    # 由于pyautogui会自动修改wxpython的GUI,且翻译效果不好，故注释此功能
    # def get_screen(self):
    #     flag = 1    # 设置标志位
    #     # 循环直到按键按下，用以选择截图区域
    #     while flag:
    #         while keyboard.is_pressed('shift'):
    #             flag = 0
    #         if flag == 0:
    #             x1, y1 = position()  # 获取坐标
    #             print(x1, y1)
    #     flag = 1
    #     while flag:
    #         while keyboard.is_pressed('shift'):
    #             flag = 0
    #         if flag == 0:
    #             x2, y2 = position()
    #             print(x2, y2)
    #     mouse_xy = (x1, y1, x2, y2)  # 设置截图坐标
    #     img = PIL.ImageGrab.grab(mouse_xy)  # 截图
    #     img.save('screen.PNG')
    #     text = pytesseract.image_to_string(img)  # 文字识别
    #     self.fy_input_text.SetValue(text)  # 在输入框显示识别结果


app = wx.App()
frame = MyFrame(None, -1)
frame.Show()
frame.Center()
app.MainLoop()
