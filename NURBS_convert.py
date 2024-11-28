from OCC.Core.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.BRepTools import breptools_Write
import os

from OCC.Core.BRep import BRep_Tool
from OCC.Core.GeomConvert import geomconvert_SurfaceToBSplineSurface
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE


def read_step_file(step_file_path):
    """
    Reads a STEP file and returns its shape.
    """
    reader = STEPControl_Reader()
    status = reader.ReadFile(step_file_path)
    if status != 1:
        raise ValueError(f"Failed to read STEP file: {step_file_path}")
    
    reader.TransferRoots()
    shape = reader.OneShape()
    return shape


def convert_shape_to_nurbs(shape):
    """
    Converts the entire shape to NURBS using BRepBuilderAPI_NurbsConvert.
    """
    nurbs_converter = BRepBuilderAPI_NurbsConvert()
    nurbs_converter.Perform(shape, False)  # Perform the conversion
    return nurbs_converter.Shape()


def save_shape_to_step(shape, file_path):
    """
    Save a shape to a STEP file in standard format.
    """
    writer = STEPControl_Writer()
    Interface_Static.SetCVal("write.step.schema", "AP214") # Set the STEP schema to AP214
    writer.Transfer(shape, STEPControl_AsIs)
    status = writer.Write(file_path)
    if status != 1:
        raise RuntimeError(f"Failed to write STEP file: {file_path}")


def convert_surface_to_bspline(face):
    """
    Converts a surface of a TopoDS_Face to a B-Spline surface using GeomConvert.
    """
    # Extract the geometric surface from the TopoDS_Face
    geom_surface = BRep_Tool.Surface(face)
    
    # Convert to B-Spline surface
    bspline_surface = geomconvert_SurfaceToBSplineSurface(geom_surface)
    
    return bspline_surface


def extract_bspline_data(bspline_surface):
    """
    Extract NURBS data (poles, weights, U/V knot sequences) from a B-Spline surface.
    
    Parameters:
        bspline_surface: Handle to a B-Spline surface.
        
    Returns:
        poles: A 2D list of control points.
        weights: A 2D list of weights (or None if not rational).
        u_knots: List of U direction knot sequence.
        v_knots: List of V direction knot sequence.
    """
    # Extract poles
    poles = [
        [
            bspline_surface.Pole(u, v)
            for v in range(1, bspline_surface.NbVPoles() + 1)
        ]
        for u in range(1, bspline_surface.NbUPoles() + 1)
    ]

    # Extract weights
    weights = [
        [
            bspline_surface.Weight(u, v)
            for v in range(1, bspline_surface.NbVPoles() + 1)
        ]
        for u in range(1, bspline_surface.NbUPoles() + 1)
    ]

    # Check if surface is rational
    is_rational = any(weight != 1.0 for row in weights for weight in row)
    if not is_rational:
        weights = None  # Set weights to None if not rational

    # Extract U and V knot sequences
    u_knots = [
        bspline_surface.UKnot(i)
        for i in range(1, bspline_surface.NbUKnots() + 1)
    ]
    v_knots = [
        bspline_surface.VKnot(i)
        for i in range(1, bspline_surface.NbVKnots() + 1)
    ]

    return poles, weights, u_knots, v_knots



def main():
    input_step_file = "./step_files/Knurled_screws.stp"  # STEP file path
    output_step_file = "./output_file.stp"  # Desired output STEP file path
    
    if not os.path.exists(input_step_file):
        print(f"Input STEP file not found: {input_step_file}")
        return
    
    print("Reading STEP file...")
    shape = read_step_file(input_step_file)
    
    print("Converting shape to NURBS...")
    nurbs_shape = convert_shape_to_nurbs(shape)
    
    
    print("Extracting B-Spline data from faces...")
    explorer = TopExp_Explorer(nurbs_shape, TopAbs_FACE)
    while explorer.More():
        face = explorer.Current()
        # try:
        # Convert face surface to B-Spline
        bspline_surface = convert_surface_to_bspline(face)
        # Extract B-Spline data
        poles, weights, u_knots, v_knots = extract_bspline_data(bspline_surface)
        # Print the extracted data
        print("Control Points (Poles):")
        for row in poles:
            print([f"({p.X():.2f}, {p.Y():.2f}, {p.Z():.2f})" for p in row])
        print("Weights:")
        if weights:
            for row in weights:
                print(row)
        else:
            print("Non-rational surface, no weights.")
        print("U Knot Sequence:", u_knots)
        print("V Knot Sequence:", v_knots)
        print("-" * 80)
        # except Exception as e:
        #     print(f"Failed to process face: {e}")
        explorer.Next()
        
    print("Saving converted STEP file...")
    save_shape_to_step(nurbs_shape, output_step_file)
    print(f"Converted STEP file saved to: {output_step_file}")


if __name__ == "__main__":
    main()
