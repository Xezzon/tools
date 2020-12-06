# -*- coding: utf-8 -*-
'''
根据填充物构造边界
使用场景：地形图修补测入库时，通常会通过将已有CASS数据转换为gdb的方式实现。在该过程中会遇到一个问题：使用CASS画植被时没有保留边界，可以通过该程序构造植被面。
算法思想：分治法、哨兵思想
'''
import arcpy

# 检查该范围内是否只有一个编码，是的话返回该编码，否则返回None
def check(n, e, s, w):
    # 选择范围内的所有要素
    ## 在临时图层中新建一个要素
    cursor = arcpy.da.InsertCursor(temp_a, ['SHAPE@'])
    cursor.insertRow([arcpy.Polygon(arcpy.Array([arcpy.Point(e, s), arcpy.Point(e, n), arcpy.Point(w, n), arcpy.Point(w, s)]))])
    del cursor
    ## 按位置选择
    arcpy.SelectLayerByLocation_management(zbtzp_with_sentry_lyr, 'intersect', temp_a)
    ## 选择完成之后删除临时要素
    # 获取要素唯一值
    unique_value = set([x[0] for x in arcpy.da.TableToNumPyArray(zbtzp_with_sentry_lyr, ['SOUTH'])])
    ## 删除临时图层
    arcpy.DeleteFeatures_management(temp_a)
    # 判断编码
    if len(unique_value) > 1:
        return None
    elif len(unique_value) <1:
        return 0
    else:
        return unique_value.pop()

def generate_bound(n, e, s, w, code):
    cursor = arcpy.da.InsertCursor(r"E:\a\feature\bound.shp", ["SOUTH", "SHAPE@"])
    cursor.insertRow([code, arcpy.Polygon(arcpy.Array([arcpy.Point(e, s), arcpy.Point(e, n), arcpy.Point(w, n), arcpy.Point(w, s)]))])
    del cursor

def check_and_generate_bound(n, e, s, w):
    code = check(n, e, s, w)
    if (code is None):
        return False
    else:
        generate_bound(n, e, s, w, code)
        return True

# 若范围内只有一种编码，停止递归，生成要素，否则递归检测四个子区域。
def detect(n, e, s, w):
    code = check(n, e, s, w)
    if code is None:
        mid1 = (e + w)/2
        mid2 = (s + n)/2
        detect(n, mid1, mid2, w)
        detect(n, e, mid2, mid1)
        detect(mid2, mid1, s, w)
        detect(mid2, e, s, mid1)
    else:
        generate_bound(n, e, s, w, code)

def generate_sentry(n, e, s, w, interval):
    # 生成哨兵
    cursor = arcpy.da.InsertCursor(r"E:\a\feature\ZBTZP.shp", ["SOUTH", "SHAPE@XY"])
    x, y = (w, s)
    while (y < n + interval):
        while (x < e + interval):
            cursor.insertRow(['0', (x, y)])
            x = x + interval
        y = y + interval
        x = w
    ## 手动删除非哨兵节点 interval/2 范围内的哨兵  ### 此处可优化
    del x, y, interval, cursor

if __name__ == "__main__":
    # 获取四至
    desc = arcpy.Describe(r"E:\a\feature\ZBTZP.shp")
    n, e, s, w = [desc.extent.YMax, desc.extent.XMax, desc.extent.YMin, desc.extent.XMin]
    interval = 40
    # generate_sentry(n, e, s, w, interval)
    n = n + interval
    e = e + interval
    # 分治检测
    zbtzp_with_sentry = r"E:\a\feature\ZBTZP_with_sentry.shp"
    temp_a = arcpy.CreateFeatureclass_management('in_memory', 'temp_a', "POLYGON", None, "DISABLED", "DISABLED", "4547")
    zbtzp_with_sentry_lyr = arcpy.MakeFeatureLayer_management(zbtzp_with_sentry, "zbtzp_with_sentry_lyr")
    # 数据量太大，分块检测
    for i in range(0,8):
        for j in range(0, 8):
            xi, xa, yi, ya = w+(e-w)/8*i, w+(e-w)/8*(i+1), n-(n-s)/8*(j+1), n-(n-s)/8*j
            detect(ya, xa, yi, xi)