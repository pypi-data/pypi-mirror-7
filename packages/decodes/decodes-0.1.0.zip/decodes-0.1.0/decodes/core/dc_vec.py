from decodes.core import *
from . import dc_base #here we may only import modules that have been loaded before this one.    see core/__init__.py for proper order

import math, random
if VERBOSE_FS: print "vec.py loaded"


class Vec(Geometry):
    """
    a simple vector class
    """

    def __init__(self, a=0, b=0, c=0):
        """ Vector Constructor. 

            :param a: a value.
            :type a: float
            :param b: b value
            :type b: float
            :param c: c value
            :type c: float
            :result: Vector object.
            :rtype: Vec
            
            ::
            
                my_vec=Vec(1,1,1)
                
                vec_1=Vec(Point(1,1,1))
                
                vec_2=Vec(Point(0,0,0), Point(1,1,1))

        """
        if a is None : a = 0
        if b is None : b = 0
        if c is None : c = 0

        if all( hasattr(a,i) and hasattr(b,i) for i in ['x','y','z'] ) :
            # we've been passed two things that act like points
            self._x = b.x - a.x
            self._y = b.y - a.y
            self._z = b.z - a.z    
        elif all([hasattr(a,'x'),hasattr(a,'y'),hasattr(a,'z')]):
            # we've been passed one thing that acts like a vec
            self._x = a.x
            self._y = a.y
            self._z = a.z
        else :
            self._x = a
            self._y = b
            self._z = c

    @property
    def x(self): 
        """ Returns the x-value of this vector. 

            :result: x value.
            :rtype: float
        """
        return self._x
    @x.setter
    def x(self,value): self._x = value
    
    @property
    def y(self): 
        """ Returns the y-value of this vector. 

            :result: y value.
            :rtype: float
        """
        return self._y
    @y.setter
    def y(self,value): self._y = value
    
    @property
    def z(self): 
        """ Returns the z-value of this vector. 

            :result: z value.
            :rtype: float
        """
        return self._z
    @z.setter
    def z(self,value): self._z = value


    @property
    def tup(self):
        """ Returns x, y, and z values of a vector.
            
            :result: x, y and z values.
            :rtype: float
        """
        return self._x,self._y,self._z

    def __add__(self, vec):
        """| Overloads the addition **(+)** operator. 
           | Returns a new vector that results from adding this vector's world coordinates to the other vector's world coordinates.
        
           :param vec: Vec to be added.
           :type vec: Vec
           :result: New Vec.
           :rtype: Vec
           
           ::
           
                my_vec + vec_1
        """    
        return Vec(self.x+vec.x , self.y+vec.y, self.z+vec.z)
    
    def __sub__(self, vec): 
        """| Overloads the subtraction **(-)** operator. 
           | Returns a new vector that results from subtracting this vector's world coordinates from the other vector's world coordinates.
        
           :param vec: Vec to be subtracted.
           :type vec: Vec
           :result: New Vec.
           :rtype: Vec
           
           ::
           
                my_vec - vec_1          
        """    
        return Vec(self.x-vec.x , self.y-vec.y, self.z-vec.z)
    
    def __truediv__(self,other):
        return self.__div__(other)
    
    def __div__(self, scalar): 
        """| Overloads the division **(/)** operator. 
           | Returns a new vector that results from dividing this vector's world coordinates by a given scalar.
        
           :param scalar: Number to divide by
           :type scalar: float
           :result: New Vec.
           :rtype: Vec
           
           ::
           
                my_vec / 2           
        """  
        return Vec(self.x/float(scalar), self.y/float(scalar), self.z/float(scalar))
    
    def __invert__(self): 
        """| Overloads the inversion **(-vec)** operator. 
           | Inverts the direction of the vector.
           | Returns a new inverted vector.
        
           :result: Inverted Vec.
           :rtype: Vec
           
           ::
                
                my_vec.__invert__()
                
        """  
        return self.inverted()

    def __neg__(self): 
        """| Overloads the arithmetic negation **(-vec)** operator. 
           | Inverts the direction of the vector.
           | Returns a new inverted vector.
        
           :result: Inverted Vec.
           :rtype: Vec
           
        """  
        return self.inverted()

    def __mul__(self, other):
        """| Overloads the multiplication **(*)** operator. 
           | If given a scalar, returns a new vector that results from multiplying this vector by the scalar.
           | If given a vector, returns the cross product of this vector and the other vector.
        
           :param other: Scalar or Vec to be multiplied.
           :type other: float or Vec
           :result: New Vec.
           :rtype: Vec
           
           ::
           
                my_vec * vec_1
        """  
        from .dc_xform import Xform
        if isinstance(other, Xform) :
            return other*self
        else : 
            if isinstance(other, Vec) : return self.cross(other)
            return Vec(self.x * other, self.y * other, self.z * other)
    

    def __repr__(self): 
        return "vec[{0},{1},{2}]".format(self.x,self.y,self.z)
    
    def to_tuple(self): 
        """ Returns a tuple of the Vec components.
        
            :result: Tuple of Vec values.
            :rtype: tuple
        """  
        return (self.x,self.y,self.z)

    def __lt__(self, other): 
        """ Overloads the less than **(<)** operator for vector length.
        
            :param other: Vec to be compared.
            :type other: Vec
            :result: Boolean result of comparison.
            :rtype: bool
            
            ::
            
                my_vec < (vec_1)
        """
        return self.length2 < other.length2
    def __le__(self, other):
        """ Overloads the less than or equal to **(<=)** operator for vector length.
        
            :param other: Vec to be compared.
            :type other: Vec
            :result: Boolean result of comparison.
            :rtype: bool
        """
        return self.length2 <= other.length2
    def __eq__(self, other):
        """ Overloads the equal **(==)** operator for vector identity.
        
            :param other: Vec to be compared.
            :type other: Vec
            :result: Boolean result of comparison.
            :rtype: bool

        """    
        return self.is_identical(other)
    def __ne__(self, other): 
        """ Overloads the not equal **(!=)** operator for vector length.
        
            :param other: Vec to be compared.
            :type other: Vec
            :result: Boolean result of comparison.
            :rtype: bool

        """
        return not self.is_identical(other)
    def __gt__(self, other): 
        """ Overloads the greater than **(>)** operator for vector length.
        
            :param other: Vec to be compared.
            :type other: Vec
            :result: Boolean result of comparison.
            :rtype: bool
        """
        return self.length2 > other.length2
    def __ge__(self, other): 
        """ Overloads the greater or equal **(>=)** operator for vector length.
        
            :param other: Vec to be compared.
            :type other: Vec
            :result: Boolean result of comparison.
            :rtype: bool
        """
        return self.length2 >= other.length2
    
    def is_identical(self,other,tol=False): 
        """ Returns True if the vectors are equal.
        
            :param other: Vec to be compared.
            :type other: Vec
            :param tol: Tolerance of difference.
            :type tol: float
            :result: Boolean result of comparison.
            :rtype: bool
            
            ::
            
                my_vec.is_identical(vec_1)
        """   
        try:
            if not tol:
                return all([self.x==other.x,self.y==other.y,self.z==other.z])
            else :
                return all([abs(self.x-other.x)<tol,abs(self.y-other.y)<tol,abs(self.z-other.z)<tol])
        except:
            return False
            
    def is_coincident(self,other): 
        """ Returns True if the vectors have equal direction.
        
            :param other: Vec to be compared.
            :type other: Vec
            :result: Boolean result of comparison.
            :rtype: bool
            
            ::
            
                my_vec.is_coincident(vec_1)
        """   
        return self.normalized().is_identical( other.normalized() )
    
    def is_parallel(self,other): 
        """ Returns True if the vectors have equal or opposite direction.
        
            :param other: Vec to be compared.
            :type other: Vec
            :result: Boolean result of comparison.
            :rtype: bool
            
            ::
            
                my_vec.is_parallel(vec_1)
        """   
        return self.is_coincident(other) or self.inverted().is_coincident(other)


    @property
    def is_2d(self): 
        """ Returns True if the vector is 2d.
        
            :result: True if 2d.
            :rtype: bool
            
            ::
            
                my_vec.is_2d
        """   
        return True if (self.z==0) else False
    
    @property
    def length(self): 
        """ Returns the length of this vector. Use vec.length2 when possible, as it is cheaper to calculate.
        
            :result: Length of the Vec.
            :rtype: float
            
            ::
            
                my_vec.length
        """
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    @property 
    def length2(self):
        """ Length squared. Cheaper to calculate than vec.length.
        
            :result: Length of the Vec.
            :rtype: float
            
            ::
            
                my_vec.length2
        """
        return self.x ** 2 + self.y ** 2 + self.z ** 2
    
    @length.setter
    def length(self,value): 
        """ Sets the length of this vector.
        
            :param value: New length of vector.
            :type values: float
            :result: Sets the length of Vec.
        """
        factor = value / self.length
        self.x *= factor
        self.y *= factor
        self.z *= factor
    
    @staticmethod
    def interpolate(v0,v1,t=0.5):
        """ Interpolates between vectors v0 and v1 at param t.
        
            :param v0: First Vec.
            :type v0: Vec
            :param v1: Second Vec.
            :type v1: Vec
            :param t: Parameter to interpolate at between the vectors.
            :type t: float
            :result: Interpolated vector.
            :rtype: Vec
            
            ::
            
                Vec.interpolate(vec_1, vec_2)
        """
        x = (1-t) * v0.x + t * v1.x
        y = (1-t) * v0.y + t * v1.y
        z = (1-t) * v0.z + t * v1.z
        return Vec(x,y,z)

    @staticmethod
    def random(interval = None,normalize=True,constrain2d=False):
        """ Returns a random vector within a given interval.
        
            :param interval: Interval to get the random values from.
            :type interval: Interval
            :param normalize: If True, unitizes the Vec.
            :type normalize: bool
            :param constrain2d: If True, the Vec is constrained to 2d space. 
            :type constrain2d: bool
            :result: Random vector.
            :rtype: Vec
            
            ::
                            
                Vec.random(Interval(1,10))
        """
        if interval is None:
            interval = Interval(-1,1)
        x = random.uniform(interval.a,interval.b)
        y = random.uniform(interval.a,interval.b)
        z = random.uniform(interval.a,interval.b)
        v = Vec(x,y) if constrain2d else Vec(x,y,z)
        if normalize : return v.normalized()
        return v

    @staticmethod
    def average(vecs):
        """ Returns the average of a list of vectors.
        
            :param vecs: List of vectors to average. 
            :type vecs: list
            :result: Averaged vector.
            :rtype: Vec
            
            ::
            
                Vec.average(my_vec, vec_1)
        """
        return Vec( 
            sum([float(v.x) for v in vecs])/len(vecs) , 
            sum([float(v.y) for v in vecs])/len(vecs) , 
            sum([float(v.z) for v in vecs])/len(vecs) 
        )

    @staticmethod
    def bisector(v0,v1): 
        """ Returns the normalized bisector of two vectors.
        
            :param v0: First vector to get the bisector from.
            :type v0: Vec
            :param v1: Second vector to get the bisector from.
            :type v1: Vec
            :result: Bisector vector.
            :rtype: Vec
            
            ::
            
                Vec.bisector(vec_1, vec_2)
        """
        return Vec.average([v0.normalized(),v1.normalized()])            

    def normalized(self, length=1.0):
        """ Return a new vector in the same direction, but given length (default 1.0).
        
            :param length: New length for the Vec (default 1.0)
            :type length: float
            :result: Normalized vector.
            :rtype: Vec
            
            ::
            
                my_vec.normalized()
        """
        if self.length == 0 : raise GeometricError("Cannot normalize a vector of length zero: %s"%(self))
        factor = length / self.length
        return Vec(self.x * factor, self.y * factor, self.z * factor)        

    def inverted(self):
        """ Return a new vector pointing in the opposite direction.
        
            :result: Inverted vector.
            :rtype: Vec
            
            ::
            
                my_vec.inverted()
        """ 
        return Vec(-self.x,-self.y,-self.z)
    
    def rounded(self,n=0): 
        """ Returns a new vector with coords rounded to n-digits (defaults to 0 digits (nearest int). 
        
            :param n: Number of digits to round the Vec's coordinates.
            :type n: int
            :result: Rounded vector. 
            :rtype: Vec
            
            ::
            
                my_vec.rounded()
        """
        return Vec(round(self.x,n),round(self.y,n),round(self.z,n))
    
    def limited(self,n=1.0): 
        """ Returns a new vector limited to a given length.
        
            :param n: Value to limit the Vec's length.
            :type n: float
            :result: Limited vector.
            :rtype: Vec
            
            ::
            
                my_vec.limited()
                
        """
        if self.length2 < n**2 : return Vec(self.x,self.y,self.z)
        return self.normalized(n)    
    
    def dot(self,other): 
        """ Computes the dot product of this vector and the other vector.
        
            :param other: Second vector to compute dot product.
            :type other: Vec
            :result: Dot product.
            :rtype: float
            
            ::
            
                my_vec.dot(vec_2)
            
        """
        return float(self.x * other.x + self.y * other.y + self.z * other.z)

    def projected_length(self,other): 
        """ Returns the length of the vector which results from projecting a vector onto a destination vector.
        
            :param other: Destination vector.
            :type other: Vec
            :result: Projected vector length.
            :rtype: float
            
            ::
            
                my_vec.projected_length(vec_2)
        """
        return self.dot(other.normalized())

    def projected(self,other): 
        """ Returns a new vector projected onto a destination vector.
        
            :param other: Destination vector.
            :type other: Vec
            :result: Projected vector.
            :rtype: Vec
            
            ::
            
                my_vec.projected(vec_2)
        """
        return other * ( self.dot(other) / other.dot(other) )

    def cross(self, other):
        """| Return a new vector, the cross product.
           | a x b = (a2b3 - a3b2, a3b1 - a1b3, a1b2 - a2b1)
           | This will be at right angles to both self and other, with a length.
        
           :param other: Second vector to calculate cross product. 
           :type other: Vec
           :result: New vector.
           :rtype: Vec

           ::
            
                len(self) * len(other) * sin(angle_between_them)
                
                my_vec.cross(vec_1)
            
        """
        return Vec(
                self.y * other.z - self.z * other.y,
                self.z * other.x - self.x * other.z,
                self.x * other.y - self.y * other.x
        )

    def angle(self,other):
        """ Returns the angle in radians between this vector and the other vector. Return value is constrained to the range [-PI,PI].
        
            :param other: Second vector for angle calculation.
            :type other: Vec
            :result: Angle in radians.
            :rtype: float
            
            ::
            
                my_vec.angle(vec_1)
        """
        vdot = self.dot(other) / (self.length * other.length)
        if vdot>1.0 : vdot = 1.0
        if vdot<-1.0 : vdot = -1.0
        return math.acos(vdot)
        
    def angle_deg(self,other): 
        """ Returns the angle in degrees between this vector and the other vector.
        
            :param other: Second vector to for angle calculation.
            :type other: Vec
            :result: Angle in degrees.
            :rtype: float
        """
        return math.degrees(self.angle(other))

    def to_ray(self,pt=None):
        """ Returns a ray from a given point along this vector.
            
            :param pt: Point along this vector.
            :type pt: Point
            :result: Ray from Point
            :rtype: Ray
            
            ::
            
                my_vec.to_ray(Point(1,1,1))
                
        """
        from .dc_line import Ray
        from .dc_point import Point
        if pt is None: pt = Point()
        return Ray(pt,Vec(self))
    
    def to_line(self,pt=None):
        """ Returns a line from a given point along this vector.
            
            :param pt: Point along this vector.
            :type pt: Point
            :result: Line from Point.
            :rtype: Line
            
            ::
            
                my_vec.to_line(Point(1,1,1))
        """
        from .dc_line import Line
        from .dc_point import Point
        if pt is None: pt = Point()
        return Line(pt,Vec(self))

    @staticmethod
    def ux(length=1.0):
        """ Returns unit vector (length = 1.0) in the x-direction.
        
            :result: Unit Vec in the x-axis.
            :rtype: Vec
        """
        return Vec(length,0,0)

    @staticmethod
    def uy(length=1.0):
        """ Returns unit vector (length = 1.0) in the y-direction.
            
            :result: Unit Vec in the y-axis.
            :rtype: Vec
        """
        return Vec(0,length,0)

    @staticmethod
    def uz(length=1.0):
        """ Returns unit vector (length = 1.0) in the z-direction.
        
            :result: Unit vec in the z-axis.
            :rtype: Vec
        """
        return Vec(0,0,length)