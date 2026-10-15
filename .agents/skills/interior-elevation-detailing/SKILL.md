---
name: interior-elevation-detailing
description: Deepen interior bedroom elevations from authoritative CAD plans and design-reference PDFs, using native dimensions, hatches, blocks, cabinet sections, source records and explicit unresolved items. Use for this project's elevation revisions and detail coordination.
---

# 室内立面深化（本项目定制技能）

这是本项目新增的本地技能，不是第三方专业设计认证，也不是 AutoCAD MCP 服务。
先读仓库 `CAD_CONVENTIONS.md`。用相邻 `cad-drawings` 技能完成原图检索、测量、对比。

## 输入与依据

1. 原平面对象、尺寸链、门窗和柜体坐标是平面几何依据。记录文件 SHA256、句柄、单位。
2. 效果 PDF 用于确认设计意向：面层分区、分格、线脚、软包、柜门、灯光与收口关系。
3. 朋友图册只借鉴绘图深度；不借用其项目的标高或构造尺寸。
4. 为每个参数记录 P/I/D/U 状态。区分原始测绘层高、结构净高与完成吊顶净高。

## 每面立面的内容

- 与平面对应的墙面范围、转角和门窗定位，统一从同一完成面基准展开。
- 总体、定位、分格三层尺寸；竖向以地面、窗台、台面、柜体、吊顶建立尺寸链。
  未知高度不能用折断后的示意几何假称完整等比例立面。
- 面材编号与做法表一一对应；材料表至少区分饰面、基层、厚度、收口与状态。
- 柜体区分外尺寸、板厚、净空、门缝和五金；不能把等分门宽直接当作内部净空。
- 画出有设计依据的门扇开启、柜体内部分隔和实际可见细节；不要堆随机纹理增加复杂度。
- 桌面与窗台、窗扇、空调、插座、灯带的相邻关系需明确校核，缺依据就记录待协调。

## 节点

先选影响安装的剖切部位：柜脚与踢脚、柜顶与吊顶、门板/侧封板、桌面与窗台、
软包与木饰面、窗帘盒与灯带。表达基层/面层、固定、留缝、边部、标高和索引。
尺寸与连接做法不能凭一般经验标成现场已确认；示意节点需明确标成设计建议。

## 原生 CAD 工作流

- 新模型与细节均 1:1 毫米；用图纸空间视口安排不同比例，不放大模型伪作详图。
- 使用 ezdxf 的 `add_linear_dim(...).render()`，保留 DIMENSION 与显示块。
  标注文字为自动测量；D/U 说明放在关联注记，不用手写数字覆盖实测值。
- 使用闭合边界的 HATCH；使用命名 BLOCK/INSERT 表示重复五金或标高符号。
- 参数变更后重建并读回；不能声称非关联 DIMENSION 自动追踪任意手工修改的轮廓。
- 分清可编辑的 DXF 与已验证的 DWG。DWG 原生复杂对象的回读不通过时，不降级后冒充通过。

## 当前可执行验证

```bash
python .agents/skills/interior-elevation-detailing/scripts/native_cad_smoke.py \
  --out /workspace/cad-skill-validation/native
```

脚本生成女孩房 2565 宽衣柜的技术测试图，保留原生尺寸、填充、带属性的图块、引线及
两个不同比例视口，并改变宽度再生成一次，核对自动尺寸读数。柜高等采用 D 建议值。
这是工具能力测试，不是新版本立面交付，也不解决现场待定高度。

## 交付检查

1. 审计最终读回文件，检查原生对象和尺寸显示块确实存在。
2. 几何实测、来源记录与尺寸链闭合交叉核对。不要把实体数量当作质量证据。
3. 全张与局部渲染检查文字、线宽、遮挡与打印可读性。
4. 列出未解决参数与冲突；签章、现场复核与设计审核状态如实表达。

## 已验证的 DWG 输出路径

R04 已使用官方 ODA File Converter 27.9.0.0 完成 AutoCAD 2013 DWG 往返。
`/workspace/bedroom-elevations-r04/DWG_roundtrip_R04.json` 记录尺寸显示值、
HATCH、WIPEOUT遮挡、图块属性、材质引线、绘图顺序和视口参数的比对。
这是程序回读校核，不是桌面 AutoCAD 人工打开或打印验证。
使用仓库 `tools/oda-convert` 调用当前环境保留的转换器；它启动并清理自己的
临时 X 显示，不需要常驻服务。不要改回旧版 LibreDWG 写出器造成对象降级。
