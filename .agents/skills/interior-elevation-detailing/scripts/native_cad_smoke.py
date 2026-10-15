"""Executable native-object check; this is a tooling sample, not a construction issue."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment


def text(space, value, point, height=45, layer="A-TEXT"):
    return space.add_text(value, dxfattribs={"height": height, "style": "NOTE", "layer": layer}).set_placement(point)


def rect(space, x, y, w, h, layer="A-OUTLINE"):
    return space.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h)], close=True,
                                dxfattribs={"layer":layer})


def hatch(space, x, y, w, h):
    obj=space.add_hatch(dxfattribs={"layer":"A-HATCH"})
    obj.set_pattern_fill("ANSI31", scale=2)
    obj.paths.add_polyline_path([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],is_closed=True)
    return obj


def dimension(space, p1, p2, base, angle=0, scale=20):
    dim=space.add_linear_dim(base=base,p1=p1,p2=p2,angle=angle,dimstyle="EZDXF",
        override={"dimtxt":2.5,"dimasz":2,"dimgap":0.8,"dimexo":1,"dimexe":1.5,
                  "dimscale":scale,"dimdec":0,"dimzin":8,"dimlfac":1,"dimpost":""},dxfattribs={"layer":"A-DIM"})
    dim.render()
    return dim.dimension


def build(path: Path, width: int):
    doc=ezdxf.new("R2010",setup=True);doc.units=units.MM
    doc.header["$MEASUREMENT"]=1;doc.header["$LWDISPLAY"]=True
    doc.styles.new("NOTE",dxfattribs={"font":"DejaVuSans.ttf"})
    for name,weight in [("A-OUTLINE",35),("A-DETAIL",18),("A-HATCH",9),("A-DIM",13),
                        ("A-TEXT",13),("A-SYMBOL",18),("A-OPEN",9),("A-FRAME",35)]:
        doc.layers.new(name,dxfattribs={"color":7,"lineweight":weight,
                                       "linetype":"DASHED" if name=="A-OPEN" else "Continuous"})
    m=doc.modelspace();h=2400;b=18;kick=80
    rect(m,0,0,width,h)
    for yy in [kick,kick+b,1980,1980+b,h-b]:
        m.add_line((0,yy),(width,yy),dxfattribs={"layer":"A-DETAIL"})
    module=width/5
    for i in range(1,5):
        xx=i*module
        m.add_line((xx,80),(xx,h),dxfattribs={"layer":"A-OUTLINE"})
    handle=doc.blocks.new("HANDLE_D")
    handle.add_circle((0,0),8)
    for yy in [-32,32]: handle.add_line((0,0),(0,yy))
    handle.add_attdef("STATUS",(12,0),text="D",height=25)
    for i in range(5):
        xx=i*module
        for yy in [98,1980]:
            m.add_line((xx+12,yy),(xx+module-12,1050),dxfattribs={"layer":"A-OPEN"})
        ins=m.add_blockref("HANDLE_D",(xx+module-45,1050),dxfattribs={"layer":"A-SYMBOL"})
        ins.add_auto_attribs({"STATUS":"D"})
        text(m,f"{i+1:02}",(xx+module/2-25,2150))
        dimension(m,(xx,0),(xx+module,0),(0,-140))
    dimension(m,(0,0),(width,0),(0,-350))
    dimension(m,(width,0),(width,h),(width+210,0),90)
    text(m,"01  CABINET FRONT / TOOLING SAMPLE",(0,2670),60)
    text(m,"P: width 2565, depth 620 from source plan",(0,2570),40)
    text(m,"D: H2400, board18, kick80; site ceiling U",(0,2490),40)
    # Section is drawn in actual millimetres, not enlarged model geometry.
    sx=4500;depth=620
    rect(m,sx,0,depth,500)
    for x,y,w,hh in [(sx,80,depth,18),(sx,340,depth,18),(sx+602,80,18,420),
                     (sx+50,0,18,80),(sx+120,80,18,260)]:
        rect(m,x,y,w,hh,"A-DETAIL");hatch(m,x,y,w,hh)
    dimension(m,(sx,0),(sx+depth,0),(sx,-75),scale=5)
    dimension(m,(sx,0),(sx,80),(sx-55,0),90,5)
    dimension(m,(sx+depth,80),(sx+depth,98),(sx+depth+55,0),90,5)
    text(m,"D01 BASE SECTION - D",(sx,580),20)
    text(m,"MT01: finish and substrate pending",(sx+80,535),12)
    m.add_leader([(sx+300,90),(sx+360,525),(sx+80,525)],
                 dxfattribs={"layer":"A-SYMBOL","dimstyle":"EZDXF"})
    text(m,"D: setback / fixing requires review",(sx, -145),15)
    # Paper-space frame and viewports, each referencing true-size geometry.
    doc.layouts.rename("Layout1","A3-CAD-TEST");ps=doc.layouts.get("A3-CAD-TEST")
    ps.page_setup(size=(420,297),margins=(0,0,0,0),units="mm")
    rect(ps,10,10,400,277,"A-FRAME")
    text(ps,"NATIVE CAD CAPABILITY TEST / NOT A CONSTRUCTION DRAWING",(16,276),3)
    vp1=ps.add_viewport(center=(117,166),size=(185,190),view_center_point=(width/2,1150),
                       view_height=3800,status=2,dxfattribs={"layer":"A-FRAME"})
    vp2=ps.add_viewport(center=(310,166),size=(170,190),view_center_point=(sx+310,225),
                       view_height=950,status=3,dxfattribs={"layer":"A-FRAME"})
    vp1.dxf.flags|=16384;vp2.dxf.flags|=16384
    text(ps,"FRONT 1:20",(35,62),3)
    text(ps,"BASE SECTION 1:5",(250,62),3)
    text(ps,"P = plan source; D = design proposal; U = unresolved",(16,47),2.5)
    text(ps,"Native DIMENSION / HATCH / INSERT / ATTRIB / LEADER",(16,39),2.5)
    text(ps,"Model geometry 1:1 mm. Dimensions are NOT fully associative.",(16,31),2.5)
    text(ps,"Technical validation only; existing R03 and DWG are unchanged.",(16,23),2.5)
    doc.saveas(path)


def inspect(path: Path, width: int):
    d=ezdxf.readfile(path);audit=d.audit();assert not audit.errors and not audit.fixes
    m=d.modelspace();counts=Counter(e.dxftype() for e in m)
    assert counts["DIMENSION"]==10 and counts["HATCH"]==5
    assert counts["INSERT"]==5 and counts["LEADER"]==1
    assert sum(len(i.attribs) for i in m.query("INSERT"))==5
    values=[]
    for dim in m.query("DIMENSION"):
        assert dim.dxf.text in ["", "<>"]
        assert dim.dxf.geometry in d.blocks and len(d.blocks[dim.dxf.geometry])>0
        value=round(dim.get_measurement(),6)
        display=[t.plain_text() if t.dxftype()=="MTEXT" else t.dxf.text
                 for t in d.blocks[dim.dxf.geometry].query("TEXT MTEXT")]
        assert display==[str(round(value))],(value,display)
        values.append(value)
    expected=sorted([width/5]*5+[width,2400,620,80,18])
    assert sorted(values)==expected,(values,expected)
    vp=[v for v in d.layouts.get("A3-CAD-TEST").query("VIEWPORT") if v.dxf.id>1]
    scales=sorted(round(v.dxf.height/v.dxf.view_height,8) for v in vp)
    assert scales==[0.05,0.2],scales
    assert all(v.dxf.flags&16384 for v in vp)
    return {"file":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "native_model_objects":dict(counts),"attribute_count":5,"dimension_values":values,
            "audit_errors":0,"audit_fixes":0,"viewport_scales":scales,"units":"mm",
            "native_dimensions_have_display_blocks":True,"displayed_values_match_geometry":True,
            "fully_associative_dimensions":False}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    if any(args.out.glob("*")):raise SystemExit("Choose an empty output directory; existing results preserved.")
    results=[]
    for width in [2565,2575]:
        p=args.out/f"cabinet_native_{width}.dxf";build(p,width);results.append(inspect(p,width))
    assert results[0]["dimension_values"][0]==513 and results[1]["dimension_values"][0]==515
    report={"purpose":"tool capability validation, not a revised construction issue", "status":"passed",
            "parameter_regeneration":"2565 -> 2575; 5 equal modules: 513 -> 515",
            "source_width":{"value":2565,"status":"P","source_handle":"91CE"},
            "proposal_parameters":{"height":2400,"board":18,"kick":80},
            "unresolved":["finished ceiling","fabrication details","DWG native-object write fidelity"],
            "files":results}
    (args.out/"validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False))


if __name__=="__main__": main()
