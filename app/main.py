#coding=utf-8
import requests
# v1.0+引用方式

from pyecharts import options as opts
from pyecharts.charts import Bar, Grid, Line, Scatter
import numpy as np
import json
# 导入输出图片工具
from pyecharts.render import make_snapshot
# 使用snapshot-selenium 渲染图片
from snapshot_selenium import snapshot
# from snapshot_phantomjs import snapshot

def loadData(url):
    r = requests.get(url)
    if r.status_code == 200:
        return convertJson(r.text)
    return None

def convertJson(content):
    jsDict = json.loads(content)
    return jsDict

def pickData(jsonDict):
    '''
        [{"y":143,"o":9,"a":0,"t":0},{"y":143,"o":9,"a":0,"t":0}...]
        y: 胎心率
        o: 宫内压力
        a：""
        t：胎动
    '''
    data = json.loads(jsonDict["data"]["data"])
    duration = int(jsonDict["data"]["duration"])
    return data, duration

def showPlot(data, duration):
    taixin_yaxis = []
    yali_yaxis = []
    td_yaxis = []

    for item in data:
        taixin_yaxis.append(item["y"])
        yali_yaxis.append(item["o"])
        if item["t"] == 1:
            item["t"] = 100
        else:
            item["t"] = None
        td_yaxis.append(item["t"])
    xaxis = np.arange(0, duration/1000, duration/len(data)/1000)

    grid_vertical(xaxis, taixin_yaxis, yali_yaxis, td_yaxis)

def grid_vertical(xaxis, taixin_yaxis, yali_yaxis, td_yaxis):
    max_taixin = max(taixin_yaxis) + 20
    min_taixin = min(taixin_yaxis)-60
    if min_taixin <=0:
        min_taixin = 0

    line1 = (
        Line()
        .add_xaxis(xaxis)
        .add_yaxis(
            "胎心率",
            taixin_yaxis,
            label_opts=opts.LabelOpts(is_show=False),
            is_symbol_show=False,
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="average", name="胎心率平均值")]
            ),
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="胎心率最大值"),
                ]
            ),
        )
        .add_yaxis("下限",
                   [120, 120],
                   markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")])
        )
        .add_yaxis("上限",
                   [160, 160],
                   markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")])
        )
        .add_yaxis("胎动",
                   td_yaxis,
                   label_opts=opts.LabelOpts(is_show=False),
                   markpoint_opts=opts.MarkPointOpts(
                       data=[
                           opts.MarkPointItem(type_="None", name="胎动"),
                       ]
                   ),
        )
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_='value',
                interval= 120,
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axislabel_opts=opts.LabelOpts(formatter="{value}秒"),
            ),
            yaxis_opts=opts.AxisOpts(
                type_='value',
                interval=10,
                min_= min_taixin,
                max_= max_taixin,
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            title_opts=opts.TitleOpts(title="eFM-60超声多普勒胎儿监护仪监测曲线图"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
            ),
        )
        .set_series_opts(
             label_opts=opts.LabelOpts(is_show=False),
            markarea_opts=opts.MarkAreaOpts(
                data=[
                    opts.MarkAreaItem(name="合理区间", y=(120, 160), itemstyle_opts=opts.ItemStyleOpts(color="#A0D897", opacity=0.2)),
                ]
            )
        )
    )
    line2 = (
        Line()
        .add_xaxis(xaxis)
        .add_yaxis(
            "宫内压力",
            yali_yaxis,
            label_opts=opts.LabelOpts(is_show=False),
            is_symbol_show=False
        )
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_='value',
                interval=120,
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axislabel_opts=opts.LabelOpts(formatter="{value}秒"),
            ),
            yaxis_opts=opts.AxisOpts(
                type_='value',
                interval=10,
                min_=0,
                max_=100,
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            # title_opts=opts.TitleOpts(title="")
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
            legend_opts=opts.LegendOpts(pos_top="50%"),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
        )
    )

    # 把上面生成的两个图放进grid中并通过pos_top，pos_bottom, pos_left, pos_right设置其位置
    grid = (
        Grid(init_opts=opts.InitOpts(width="3000px", height="600px"))
        .add(line2, grid_opts=opts.GridOpts(pos_top='60%', pos_left='2%'))
        .add(line1, grid_opts=opts.GridOpts(pos_bottom="60%", pos_left='2%'))
    )
    # 生成到本地网页形式打开，也可自己设置保存成png图片，因为网页的使用更方便，自己按情况使用
    grid.render('1.html')
    # 输出保存为图片
    make_snapshot(snapshot, grid.render(), "1.png")
    print(">>图表生成完毕！")

def generateChart(url):
    print(">>数据加载中...")
    jsonDict =  loadData(url)
    data_list,duration  = pickData(jsonDict)
    print(">>图表生成中...")
    showPlot(data_list,duration)



if __name__ == "__main__":
    data_code = "YourCode"
    url = f"https://share.ihealthbaby.cn/taiyin/index.php?ac=share&op=fetus&data={data_code}"
    generateChart(url)