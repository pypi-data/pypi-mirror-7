from .. import *
from ..core import *
from ..core import dc_color, dc_base, dc_vec, dc_point, dc_cs, dc_line, dc_mesh, dc_pgon, dc_xform, dc_intersection
from .rhino_in import *
if VERBOSE_FS: print "gh_in loaded"

import Rhino.Geometry as rg
import System.Drawing.Color

#TODO: figure out how to hack the code completion thingo to display decodes geometry after gh geom has been translated



class GrasshopperIn():
    """innie for pulling stuff from grasshopper"""
    primitive_types = ["bool", "int", "float", "str"]
    structure_types = ["classobj", "instance", "function", "class"]
    friendly_types = ["DHr"]
    
    def __init__(self):
        pass
        
    @staticmethod
    def get(gh_in_str, gh_in):
        # main function for processing incoming data from Grasshopper into Decodes geometry
        # incoming may be a sigleton, a list, or a datatree
        # variable in GH script component will be replaced by whatever is returned here

        if gh_in is None : return None
        if type(gh_in) is list: return [GrasshopperIn.get(gh_in_str+"["+str(i)+"]",item) for i, item in enumerate(gh_in)]
        
        if type(gh_in) is rg.Interval: return Interval(gh_in.T0,gh_in.T1)

        if type(gh_in) is rg.Rectangle3d :  gh_in = gh_in.ToPolyline()

        if type(gh_in) is rg.Vector3d : return from_rgvec(gh_in)
        elif type(gh_in)is rg.Point3d : return from_rgpt(gh_in)
        elif type(gh_in)is rg.Plane : 
            return CS(from_rgpt(gh_in.Origin), from_rgvec(gh_in.XAxis), from_rgvec(gh_in.YAxis))
        elif type(gh_in) is rg.Line : 
            return Segment(Point(gh_in.FromX,gh_in.FromY,gh_in.FromZ),Point(gh_in.ToX,gh_in.ToY,gh_in.ToZ))
        elif type(gh_in) is rg.LineCurve : 
            return Segment(Point(gh_in.PointAtStart.X,gh_in.PointAtStart.Y,gh_in.PointAtStart.Z),Point(gh_in.PointAtEnd.X,gh_in.PointAtEnd.Y,gh_in.PointAtEnd.Z))
        elif type(gh_in) is System.Drawing.Color : 
            return Color(float(gh_in.R)/255,float(gh_in.G)/255,float(gh_in.B)/255)

        elif type(gh_in)is rg.Circle :
            pln = Plane( from_rgpt(gh_in.Center), from_rgvec(gh_in.Plane.Normal))
            return Circle(pln,gh_in.Radius)
            
        elif type(gh_in)is rg.Arc :
            x_axis = Vec(from_rgpt(gh_in.Center),from_rgpt(gh_in.StartPoint))
            y_axis = from_rgvec(gh_in.Plane.Normal).cross(x_axis)
            cs = CS( from_rgpt(gh_in.Center), x_axis, y_axis )
            swp_ang = abs(gh_in.EndAngle - gh_in.StartAngle)
            return Arc(cs,gh_in.Radius,swp_ang)

        elif type(gh_in) is rg.PolylineCurve: 
            ispolyline, gh_polyline = gh_in.TryGetPolyline()
            if (ispolyline) : return from_rgpolyline(gh_polyline)
        elif type(gh_in) is rg.Polyline:
            return from_rgpolyline(gh_in)
        elif type(gh_in) is rg.NurbsCurve : 
            #TODO: check if gh_in can be described as a line first...
            ispolyline, gh_polyline = gh_in.TryGetPolyline()
            if (ispolyline) : return from_rgpolyline(gh_polyline)
        elif type(gh_in) is rg.Mesh : 
            verts = [Point(rh_pt.X,rh_pt.Y,rh_pt.Z) for rh_pt in gh_in.Vertices]
            faces = []
            for rh_fc in gh_in.Faces :
                if rh_fc[2] == rh_fc[3] : faces.append([rh_fc[0],rh_fc[1],rh_fc[2]]) #add this triangle
                else : faces.append([rh_fc[0],rh_fc[1],rh_fc[2],rh_fc[3]]) #add this quad
            return Mesh(verts,faces)

        elif any(p in str(type(gh_in)) for p in GrasshopperIn.primitive_types) : return gh_in
        elif any(p in str(type(gh_in)) for p in GrasshopperIn.friendly_types) : return gh_in
        elif any(p in str(type(gh_in)) for p in GrasshopperIn.structure_types) : return gh_in
        else :
            print "UNKNOWN TYPE: "+gh_in_str+" is an "+ str(type(gh_in))
            return gh_in
            #print inspect.getmro(gh_in.__class__)
            #if issubclass(gh_in.__class__, rg.GeometryBase ) : print "this is geometry"
            #print gh_incoming.TypeHint
            #print gh_incoming.Description


'''
for reference: the following code is injected before and after a user's script in grasshopper components
## -- BEGIN DECODES HEADER -- ##
import decodes as dc
from decodes.core import *
from decodes.io.gh_in import *
from decodes.io.gh_out import *
exec(io.gh_in.component_header_code)
exec(io.gh_out.component_header_code)
## -- END DECODES HEADER -- ##

## -- BEGIN DECODES FOOTER -- ##
exec(io.gh_in.component_footer_code)
exec(io.gh_out.component_footer_code)
## -- END DECODES FOOTER -- ##
'''
        
#TODO: make this into a proper innie instead
component_header_code = """
inputs = ghenv.Component.Params.Input
import Rhino.Geometry as rg
import System.Drawing.Color
for input in inputs : 
        gh_in_str = input.Name
        vars()[gh_in_str] = GrasshopperIn.get(gh_in_str, eval(gh_in_str))
"""

component_footer_code = ""