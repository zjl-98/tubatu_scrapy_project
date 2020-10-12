import requests
from lxml import etree
import re
import os


# 判断目录是否存在
def is_exits(path):
    path = path.strip()
    path = path.rstrip('\\')

    is_exit = os.path.exists(path)
    if not is_exit:
        os.mkdir(path)
        print(path + '创建成功！')
    else:
        print(path + '已经存在！')


# 项目绝对路径
dir_name = os.path.dirname(os.path.dirname(__file__))

# 主页url
index_url = 'http://desk.zol.com.cn'
# 主页请求头
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
}
# 发起主页请求
response = requests.get(url=index_url + '/', headers=header)

# 将请求回来的数据lxml化，方便使用xpath获取数据
response_lxml = etree.HTML(response.text)
# 通过xpath获取定位到所有壁纸类型下载排行版
side_response = response_lxml.xpath("//div[@class='side']/div[@class='model mt15']")

# 通过循环操作每个壁纸类型下载排行版
for side_item in side_response:
    # 壁纸类型
    side_title = side_item.xpath("./div[@class='mod-header']/text()")[0]
    # 该类型下所有的壁纸专题
    li_response = side_item.xpath("./ul/li")
    # 通过循环操作每个壁纸专题
    for li_item in li_response:
        try:
            # 专题标题
            li_title = li_item.xpath("./a/text()")[0]
            # 专题独立页面url
            li_url = li_item.xpath("./a/@href")[0]
            # 拼接合成专题url
            desk_url = index_url + li_url

            # 发起专题页面内容请求
            desk_response = requests.get(url=desk_url, headers=header)
            # 将请求回来的数据lxml化，方便使用xpath获取数据
            desk_lxml = etree.HTML(desk_response.text)

            # 正则表达式匹配专题的图片展示数
            img_index_search = re.compile(r"/(\d+)）")
            img_index_xpath = desk_lxml.xpath("//h3/span/text()")[1]
            img_index = re.search(img_index_search, img_index_xpath).group(1)

            # 正则表达式匹配专题url的独特数字
            img_url_index_search = re.compile(r"_(.*?)_(.*?).html")
            img_url = index_url + desk_lxml.xpath("//dd[@id='tagfbl']/a[@id='1366x768']/@href")[0]
            img_url_index_1 = re.search(img_url_index_search, img_url).group(1)
            img_url_index_2 = re.search(img_url_index_search, img_url).group(2)

            # 调用is_exits判断目录是否存在，不存在则创建目录，存在则不做另外操作
            is_exits(dir_name + "\\handle_desk.zol\\wallpaper\\" + li_title + "\\")

            # 根据每个专题的图片数定义循环次数
            for index in range(int(img_index)):
                # 根据获取到的内容拼接每个图片独立的页面url
                img_install_html_url = 'http://desk.zol.com.cn/showpic/1366x768_' + str(int(img_url_index_1) + index) + '_' + img_url_index_2 + '.html'
                # 防止拼接的图片页面url
                try:
                    # 请求每个图片的独立页面
                    img_install_html_response = requests.get(url=img_install_html_url, headers=header)
                    # 将请求回来的数据lxml化，方便使用xpath获取数据
                    img_install_lxml = etree.HTML(img_install_html_response.text)
                    # 获取到页面中提高的图片下载url
                    img_install_url = img_install_lxml.xpath("//body/img[1]/@src")[0]
                    # 请求图片下载url
                    img_install_url_response = requests.get(url=img_install_url, headers=header)
                    # 实现图片下载操作，并进行归类
                    with open(dir_name + '\\handle_desk.zol\\wallpaper\\' + li_title + '\\' + str(int(img_url_index_1) + index) + '.jpg', 'wb') as f:
                        f.write(img_install_url_response.content)
                    print("排行版专题：" + side_title + "\n")
                    print("图片专题：" + li_title + "\n")
                    print("图片url：" + img_install_url + "\n")
                    print("下载成功~~~~~~~~")
                    print("---------------------------------------------------------")
                except:
                    print(side_title + "---->" + li_title + "中请求的图片页面url->" + img_install_html_url + "不存在")
                    print("---------------------------------------------------------")
                    print("---------------------------------------------------------")
                    continue
                break
        except Exception as e:
            print(e)