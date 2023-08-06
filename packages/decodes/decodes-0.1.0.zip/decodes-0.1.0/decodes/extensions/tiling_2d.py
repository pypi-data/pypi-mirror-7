from decodes.core import *
from decodes.core import dc_base, dc_vec, dc_point, dc_cs, dc_line, dc_mesh, dc_pgon, dc_xform
import math

# according to Radin, the pinwheel tiling contains one prototyle 
# a triangle with the following edge lenghts: 1, 2, sqrt(5)
# (http://www.ma.utexas.edu/users/radin/papers/pinwheel.pdf)
# (http://www.michaelwhittaker.ca/fractalpinwheel.pdf)
# some nice variation (color) here: http://tilings.math.uni-bielefeld.de/substitution_rules/pinwheel_1_2_0

class PinwheelTile(object):    
      

    def __init__(self,xf=Xform(), lineage="RT",**kargs):
        self.lineage = lineage
        self.xf = xf

        self._xf_scale = Xform.scale(1/math.sqrt(5)) #the amount to scale down at each inflation = 0.447213595
        
        # the idealized base points for all pinwheel tiles
        self._base_pts= [
            Point(),
            Point(2.0, 0.0),
            Point(0.0, 1.0),
            Point(0.2, 0.4),
            Point(1.2, 0.4),
            Point(0.4, 0.8),
            Point(1.0, 0.0),
        ]

        # sets base colors for pinwheeel tiles
        self._colors=[
                      Color(0.41,0.34,0.13),
                      Color(0.76,0.63,0.24),
                      Color(0.11,0.22,0.41),
                      Color(0.25,0.43,0.71),
                      Color(1.00,0.25,0.25),
                      ]
        
    @property
    def base_pts(self):
        '''
        world base points for this tile
        returns the ideal Pinwheel Tile's base points transformed by this tile's xform
        '''
        return [p*self.xf for p in self._base_pts]

            
    def _cs_from_base_pts(self,pt_o=0,pt_x=1,pt_y=2):
        '''
        Returns a CS oriented to an idealized tile's base points.  
        Multiply result by this_tile.xf and you'll get a coordinate system oriented to the postition of this tile in the world
        pt_0: index of origin point
        pt_x: index of a point on the desired x-axis
        pt_y: index of a point on the desired y-axis
        '''
        return CS(self._base_pts[pt_o],self._base_pts[pt_x]-self._base_pts[pt_o],self._base_pts[pt_y]-self._base_pts[pt_o])
            
    def to_mesh(self, color=None, parent_color_inheritance=0.5):
        if color is None : 
            clr_list = self._lineage_to_colors()
            try:
                clr_list.reverse()
                color = clr_list[0]
                for parent_color in clr_list[1:]:
                    color = Color.interpolate(color,parent_color,parent_color_inheritance)
            except:
                color = clr_list

        msh = Mesh()
        msh.append(self._base_pts[0] * self.xf)
        msh.append(self._base_pts[1] * self.xf)
        msh.append(self._base_pts[2] * self.xf)
        msh.add_face(0,1,2)
        msh.set_name(self.lineage)
        msh.set_color(color)
        return msh
    
    def _lineage_to_colors(self):
        lin = self.lineage.split(',')
        if len(lin)==0 : return Color()
        return [self._colors[int(str)] for str in lin[1:]]

    @property
    def centroid(self): return Point.centroid(self.base_pts)
    
    def inflate(self):
        cs = self._cs_from_base_pts(3,6,5)
        tile0 = PinwheelTile(self.xf * cs.xform * self._xf_scale,self.lineage+",0")
                                                                                                                                                                                     
        cs = self._cs_from_base_pts(4,5,6)                                                                                                                
        tile1 = PinwheelTile(self.xf * cs.xform * self._xf_scale,self.lineage+",1")
                                                                                                                                                                                     
        cs = self._cs_from_base_pts(3,6,0)                                                                                                                
        tile2 = PinwheelTile(self.xf * cs.xform * self._xf_scale,self.lineage+",2" )
                                                                                                                                                                                     
        cs = self._cs_from_base_pts(5,0,2)                                                                                                                
        tile3 = PinwheelTile(self.xf * cs.xform * self._xf_scale,self.lineage+",3")
        
        cs = self._cs_from_base_pts(4,1,6)
        tile4 = PinwheelTile(self.xf * cs.xform * self._xf_scale , self.lineage+",4")
        
        return [tile0,tile1,tile2,tile3,tile4]

#= 1.61803399
tau = (1 + math.sqrt(5)) / 2   
class AmmannA3Tile(object):
    """
    Ammann A3
    http://tilings.math.uni-bielefeld.de/substitution_rules/ammann_a3
    """
    
    # Initiate the Ammann object
    def __init__(self,xf=Xform(), lineage="RT",scale=None):
        # Assign lineage to object
        self.lineage = lineage
        # Assign a xform to the object
        self.xf = xf
        #the amount to scale down at each inflation = 0.618033989
        self._xf_scale = Xform.scale(1/tau) 
        self.scale = scale
    
    def _cs_from_base_pts(self,pt_o=0,pt_x=1,pt_y=2):
        """
        Returns a CS oriented to an idealized tile's base points.  
        Multiply result by this_tile.xf and you'll get a coordinate system oriented to the postition of this tile in the world
        pt_0: index of origin point
        pt_x: index of a point on the desired x-axis
        pt_y: index of a point on the desired y-axis
        """
        return CS(self._base_pts[pt_o],self._base_pts[pt_x]-self._base_pts[pt_o],self._base_pts[pt_y]-self._base_pts[pt_o])
    
    @property
    def base_pts(self):
        """
        world base points for this tile
        returns the ideal Ammann Tile's base points transformed by this tile's xform
        """
        return [p*self.xf for p in self._base_pts]
        
class AmmannA3TileA(AmmannA3Tile):
    # Set the ideal base points for Ammann tile A
    @property
    def _base_pts(self):
        return [ 
            Point(0.0, 0.0),
            Point(tau**3, 0.0),
            Point(tau**3, tau**2),
            Point(tau**3-tau**2, tau**2),
            Point(tau**3-tau**2, tau),
            Point(0, tau),
            Point(tau**3-tau*tau,0)
            ]
            
    # Inflate the tile, scaling it down and subdividing into TileA and TileB
    def inflate(self):
        # TileB has its origin CS on _base_pts[0], the XAxis points towards _base_pts[1], and the YAxis points towards _base_pts[5]
        cs = self._cs_from_base_pts(0,1,5)
        # Create a TileB on the new CS and scale it down
        b0 = AmmannA3TileB(self.xf * cs.xform * self._xf_scale,self.lineage+",b0")
        
        # TileA has its origin CS on _base_pts[1], the XAxis points towards _base_pts[2], and the YAxis points towards _base_pts[0]
        cs = self._cs_from_base_pts(1,2,0)
        # Create a TileA on the new CS and scale it down
        a0 = AmmannA3TileA(self.xf * cs.xform * self._xf_scale,self.lineage+",a0")
        return [b0,a0]
        
    # Draw a PGon from the points
    def to_pgon(self):
        pg = PGon(self.base_pts[:6])
        pg.name = self.lineage
        return pg
    
    def to_lines(self):
        pg = PLine([self.base_pts[5],self.base_pts[6],self.base_pts[2]])
        return pg

class AmmannA3TileB(AmmannA3Tile):
    # Set the ideal base points for Ammann tile B
    @property
    def _base_pts(self):
        return [ 
            Point(0.0, 0.0),
            Point(tau**2-tau,0),
            Point(2*tau**2-(tau+1), 0.0),
            Point(2*tau**2, 0.0),
            Point(2*(tau**2), tau),
            Point((2*(tau**2))-1, tau),
            Point((2*(tau**2))-1, tau+tau**2),
            Point((2*(tau**2))-1-tau, tau+tau**2),
            Point((2*(tau**2))-1-tau, tau**2),
            Point(tau**2-tau, tau**2),
            Point(0, tau**2),
            Point(0,tau),
            Point(tau**2+tau-1, tau**2)
            ]
            
    # Inflate the tile, scaling it down and subdividing into TileA and TileB
    def inflate(self):
        # TileA0 has its origin CS on _base_pts[10], the XAxis points towards _base_pts[0], and the YAxis points towards _base_pts[9]
        cs = self._cs_from_base_pts(10,0,9)
        # Create a TileA0 on the new CS and scale it down
        a0 = AmmannA3TileA(self.xf * cs.xform * self._xf_scale,self.lineage+",a0")
        
        # TileA1 has its origin CS on _base_pts[2], the XAxis points towards _base_pts[3], and the YAxis points towards _base_pts[8]
        cs = self._cs_from_base_pts(2,3,8)
        # Create a Tile1A on the new CS and scale it down
        a1 = AmmannA3TileA(self.xf * cs.xform * self._xf_scale,self.lineage+",a1")
        
        # TileA2 has its origin CS on _base_pts[5], the XAxis points towards _base_pts[6], and the YAxis points towards _base_pts[11]
        cs = self._cs_from_base_pts(5,6,11)
        # Create a TileA2 on the new CS and scale it down
        a2 = AmmannA3TileA(self.xf * cs.xform * self._xf_scale,self.lineage+",a2")
        
        # TileC0 has its origin CS on _base_pts[12], the XAxis points towards _base_pts[10], and the YAxis points towards _base_pts[1]
        cs = self._cs_from_base_pts(12,10,1)
        # Create a TileC0 on the new CS and scale it down
        c0 = AmmannA3TileC(self.xf * cs.xform * self._xf_scale,self.lineage+",c0")
        return [a0,a1,a2,c0]
        
    # Draw a PGon from the points
    def to_pgon(self):
        pg = PGon(self.base_pts[:11])
        pg.name = self.lineage
        return pg
        
    def to_lines(self):
        pg = [Segment(self.base_pts[0],self.base_pts[6]),Segment(self.base_pts[3],self.base_pts[8])]
        return pg

class AmmannA3TileC(AmmannA3Tile):
    # Set the ideal base points for Ammann tile B
    @property
    def _base_pts(self):
        
        return [ 
            Point(1+tau**2, 0.0),
            Point(1+tau**2, tau),
            Point((1+tau**2)-1, tau),
            Point((1+tau**2)-1, tau+tau**2),
            Point((1+tau**2)-1-tau, tau+tau**2),
            Point((1+tau**2)-1-tau, tau+1),
            Point(1-tau, tau+1),
            Point(1-tau, tau),
            Point(0, tau),
            Point(0.0, 0.0),
            Point((1+tau**2)-(tau+1),0),
            Point((1+tau**2)-(tau+1)+(tau-1),tau+1)
                ]
                
    # Inflate the tile, scaling it down and subdividing into TileA and TileB
    def inflate(self):
        # TileA0 has its origin CS on _base_pts[10], the XAxis points towards _base_pts[0], and the YAxis points towards _base_pts[5]
        cs = self._cs_from_base_pts(10,0,5)
        # Create a TileA0 on the new CS and scale it down
        a0 = AmmannA3TileA(self.xf * cs.xform * self._xf_scale,self.lineage+",a0")
        
        # TileA1 has its origin CS on _base_pts[2], the XAxis points towards _base_pts[3], and the YAxis points towards _base_pts[7]
        cs = self._cs_from_base_pts(2,3,7)
        # Create a TileA1 on the new CS and scale it down
        a1 = AmmannA3TileA(self.xf * cs.xform * self._xf_scale,self.lineage+",a1")
               
        # TileC0 has its origin CS on _base_pts[11], the XAxis points towards _base_pts[5], and the YAxis points towards _base_pts[10]
        cs = self._cs_from_base_pts(11,5,10)
        # Create a TileC0 on the new CS and scale it down
        c0 = AmmannA3TileC(self.xf * cs.xform * self._xf_scale,self.lineage+",c0")
        
        return [a0,a1,c0]
        
    # Draw a PGon from the points
    def to_pgon(self):
        pg = PGon(self.base_pts[:10])
        pg.name = self.lineage
        return pg
        
    def to_lines(self):
        pg = [Segment(self.base_pts[0],self.base_pts[5]),Segment(self.base_pts[8],self.base_pts[3])]
        return pg
"""
class AmmannA3Tile(object):
    '''
    Ammann A3
    http://tilings.math.uni-bielefeld.de/substitution_rules/ammann_a3
    '''
    
    tau = (1 + math.sqrt(5)) / 2         #= 1.61803399

    def __init__(self,xf=Xform(), lineage="RT"):
        self.lineage = lineage
        self.xf = xf

        self._xf_scale = Xform.scale(1/tau) #the amount to scale down at each inflation = 0.447213595
    
    def _cs_from_base_pts(self,pt_o=0,pt_x=1,pt_y=2):
        '''
        Returns a CS oriented to an idealized tile's base points.  
        Multiply result by this_tile.xf and you'll get a coordinate system oriented to the postition of this tile in the world
        pt_0: index of origin point
        pt_x: index of a point on the desired x-axis
        pt_y: index of a point on the desired y-axis
        '''
        return CS(self._base_pts[pt_o],self._base_pts[pt_x]-self._base_pts[pt_o],self._base_pts[pt_y]-self._base_pts[pt_o])
    
    @property
    def base_pts(self):
        '''
        world base points for this tile
        returns the ideal Ammann Tile's base points transformed by this tile's xform
        '''
        return [p*self.xf for p in self._base_pts]
        
class AmmannA3TileA(AmmannA3Tile):
    @property
    def _base_pts(self):
        return [ 
            Point(0.0, 0.0),
            Point(tau**3, 0.0),
            Point(tau**3, tau**2),
            Point(tau**3-tau**2, tau**2),
            Point(tau**3-tau**2, tau),
            Point(0, tau)
            ]
            
    def inflate(self):
        
        cs = self._cs_from_base_pts(0,1,5)
        b0 = AmmannA3TileB(self.xf * cs.xform * self._xf_scale,self.lineage+",b0")
        
        cs = self._cs_from_base_pts(1,2,0)
        a0 = AmmannA3TileA(self.xf * cs.xform * self._xf_scale,self.lineage+",a0")
        
        return [b0,a0]
        
    def to_pgon(self):
        pg = PGon(self.base_pts)
        pg.name = self.lineage
        return pg
        
class AmmannA3TileB(AmmannA3Tile):
    @property
    def _base_pts(self):
        return [ 
            Point(0.0, 0.0),
            Point(tau**2-tau,0),
            Point(2*tau**2-(tau+1), 0.0),
            Point(2*tau**2, 0.0),
            Point(2*(tau**2), tau),
            Point((2*(tau**2))-1, tau),
            Point((2*(tau**2))-1, tau+tau**2),
            Point((2*(tau**2))-1-tau, tau+tau**2),
            Point((2*(tau**2))-1-tau, tau**2),
            Point(tau**2-tau, tau**2),
            Point(0, tau**2),
            Point(0,tau),
            Point(tau**2+tau-1, tau**2)
            ]
    def inflate(self):
        
        cs = self._cs_from_base_pts(10,0,9)
        a0 = AmmannA3TileA(self.xf * cs.xform * self._xf_scale,self.lineage+",a0")
        
        cs = self._cs_from_base_pts(2,3,8)
        a1 = AmmannA3TileA(self.xf * cs.xform * self._xf_scale,self.lineage+",a1")
        
        cs = self._cs_from_base_pts(5,6,11)
        a2 = AmmannA3TileA(self.xf * cs.xform * self._xf_scale,self.lineage+",a2")
        
        cs = self._cs_from_base_pts(12,10,1)
        c0 = AmmannA3TileC(self.xf * cs.xform * self._xf_scale,self.lineage+",c0")
        
        return [a0,a1,a2,c0]
        
    def to_pgon(self):
        pg = PGon(self.base_pts[:11])
        pg.name = self.lineage
        return pg

class AmmannA3TileC(AmmannA3Tile):
    @property
    def _base_pts(self):
        
        return [ 
            Point(1+tau**2, 0.0),
            Point(1+tau**2, tau),
            Point((1+tau**2)-1, tau),
            Point((1+tau**2)-1, tau+tau**2),
            Point((1+tau**2)-1-tau, tau+tau**2),
            Point((1+tau**2)-1-tau, tau+1),
            Point(1-tau, tau+1),
            Point(1-tau, tau),
            Point(0, tau),
            Point(0.0, 0.0),
            Point((1+tau**2)-(tau+1),0),
            Point((1+tau**2)-(tau+1)+(tau-1),tau+1)
                ]
                
    def inflate(self):
    
        cs = self._cs_from_base_pts(10,0,5)
        a0 = AmmannA3TileA(self.xf * cs.xform * self._xf_scale,self.lineage+",a0")
        
        cs = self._cs_from_base_pts(2,3,7)
        a1 = AmmannA3TileA(self.xf * cs.xform * self._xf_scale,self.lineage+",a1")
               
        cs = self._cs_from_base_pts(11,5,10)
        c0 = AmmannA3TileC(self.xf * cs.xform * self._xf_scale,self.lineage+",c0")
        
        return [a0,a1,c0]
        
    def to_pgon(self):
        pg = PGon(self.base_pts[:10])
        pg.name = self.lineage
        return pg
"""