from OCC.Core.TopoDS import (
    TopoDS_Edge,
    TopoDS_Face,
    TopoDS_Shell,
    TopoDS_Solid,
    TopoDS_Vertex,
    TopoDS_Wire,
    TopoDS_Compound,
    TopoDS_CompSolid,
)

# occwl
from occwl.solid import Solid
from occwl.compound import Compound
from occwl.shell import Shell
from occwl.face import Face
from occwl.edge import Edge
from occwl.wire import Wire
from occwl.vertex import Vertex

def create_occwl(topo_ds_shape):
    if isinstance(topo_ds_shape, TopoDS_Edge):
        occwl_ent = Edge(topo_ds_shape)
    elif isinstance(topo_ds_shape, TopoDS_Face):
        occwl_ent = Face(topo_ds_shape)
    elif isinstance(topo_ds_shape, TopoDS_Shell):
        occwl_ent = Shell(topo_ds_shape)
    elif isinstance(topo_ds_shape, TopoDS_Solid):
        occwl_ent = Solid(topo_ds_shape)
    elif isinstance(topo_ds_shape, TopoDS_Vertex):
        occwl_ent = Vertex(topo_ds_shape)
    elif isinstance(topo_ds_shape, TopoDS_Wire):
        occwl_ent = Wire(topo_ds_shape)
    elif isinstance(topo_ds_shape, TopoDS_CompSolid) or isinstance(topo_ds_shape, TopoDS_Compound):
        occwl_ent = Compound(topo_ds_shape)
    else:
        assert False, f"Unsupported entity {type(topo_ds_shape)}. Cant convert to occwl"
    
    return occwl_ent

from OCC.Core.STEPControl import STEPControl_Reader

# Load a STEP file
reader = STEPControl_Reader()
reader.ReadFile("./output_file.stp")
reader.TransferRoots()
shape = reader.OneShape()
solid = create_occwl(shape)

from occwl.graph import face_adjacency
from occwl.graph import vertex_adjacency

face_graph = face_adjacency(solid, self_loops=False)
for edge in face_graph.edges(data=True):
    print(f"Face {edge[0]} is adjacent to Face {edge[1]} via edge {edge[2]['edge']}")

vertex_graph = vertex_adjacency(solid, self_loops=False)
for edge in vertex_graph.edges(data=True):
    print(f"Vertex {edge[0]} is connected to Vertex {edge[1]} via edge {edge[2]['edge']}")


