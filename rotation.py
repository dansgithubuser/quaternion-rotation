import Tkinter
import math

#=====classes=====#
class Pair:
	def __init__(self, x, y):
		self.x=x
		self.y=y
	
	def __str__(self):#allows pairs to be easily printed with print
		return "("+str(self.x)+", "+str(self.y)+")"

class Triplet:
	def __init__(self, x, y, z):
		self.x=x
		self.y=y
		self.z=z
	
	def __str__(self):#allows triplets to be easily printed with print
		return "("+str(self.x)+", "+str(self.y)+", "+str(self.z)+")"
	
	def dot(self, other):
		return self.x*other.x+self.y*other.y+self.z*other.z
	
	def cross(self, other):
		rx=self.y*other.z-self.z*other.y;
		ry=self.z*other.x-self.x*other.z;
		rz=self.x*other.y-self.y*other.x;
		return Triplet(rx, ry, rz)
	
	def add(self, other):
		return Triplet(self.x+other.x, self.y+other.y, self.z+other.z)
	
	def multiply(self, scalar):
		return Triplet(scalar*self.x, scalar*self.y, scalar*self.z)
	
	def subtract(self, other):
		return Triplet(self.x-other.x, self.y-other.y, self.z-other.z)
	
	def magnitudeSquared(self):
		return self.x*self.x+self.y*self.y+self.z*self.z
	
	def projectToScreen(self, screenWidth, screenHeight, screenDistance):
		#screen distance should be approximately the length from eye to screen in pixels
		return Pair(screenDistance*self.x/self.z+screenWidth/2, -screenDistance*self.y/self.z+screenHeight/2)

class Quaternion:
	def __init__(self, a, b, c, d):
		self.s=a
		self.v=Triplet(b, c, d)
	
	def __str__(self):#allows quaternions to be easily printed with print
		return str(self.s)+("%+di"%self.v.x)+("%+dj"%self.v.y)+("%+dk"%self.v.z)
	
	def conjugate(self):
		return Quaternion(self.s, -self.v.x, -self.v.y, -self.v.z)
	
	def multiply(self, other):
		result=Quaternion(0, 0, 0, 0)
		result.s=self.s*other.s-self.v.dot(other.v)
		result.v=self.v.cross(other.v).add(other.v.multiply(self.s)).add(self.v.multiply(other.s))
		return result
	
	def divide(self, scalar):
		self.s/=scalar
		self.v=self.v.multiply(1/scalar)
	
	def rotate(self, p):
		quaternionP=Quaternion(0, p.x, p.y, p.z)
		quaternionQ=self.multiply(quaternionP).multiply(self.conjugate())
		return quaternionQ.v

#=====global variables=====#
objects=[]
viewer=Triplet(0.0, 0.0, 0.0)#start the viewer at the origin
rotation=Quaternion(1.0, 0.0, 0.0, 0.0)#no rotation, ie facing the +z axis with +y above and +x to the right
screenWidth=640
screenHeight=480

#=====functions=====#
def draw():
	global objects
	global viewer
	global rotation
	canvas.delete(Tkinter.ALL)
	for object in objects:
		t=object.subtract(viewer)#translate so viewer is at origin
		t=rotation.rotate(t)
		if t.z<1.0: continue#don't draw if too close or behind, and especially if t.z is 0
		p=t.projectToScreen(screenWidth, screenHeight, 500)
		canvas.create_rectangle(p.x-2, p.y-2, p.x+2, p.y+2, fill="#ffffff")

def keyboardCallback(event):
	global viewer
	global rotation
	#rotate opposite to how you'd rotate the world to find which direction the viewer is going
	#that is, rotate by the conjugate
	if   event.char=='w': viewer=viewer.add(rotation.conjugate().rotate(Triplet( 0,  0,  1)))
	elif event.char=='s': viewer=viewer.add(rotation.conjugate().rotate(Triplet( 0,  0, -1)))
	elif event.char=='d': viewer=viewer.add(rotation.conjugate().rotate(Triplet( 1,  0,  0)))
	elif event.char=='a': viewer=viewer.add(rotation.conjugate().rotate(Triplet(-1,  0,  0)))
	elif event.char=='r': viewer=viewer.add(rotation.conjugate().rotate(Triplet( 0,  1,  0)))
	elif event.char=='f': viewer=viewer.add(rotation.conjugate().rotate(Triplet( 0, -1,  0)))
	#make a new rotation that is the current rotation rotated by a small rotation in the desired direction and set the current rotation to that
	#if you did that backward, you end up with a small rotation in the desired direction rotated by the current rotation, which is a different result
	elif event.char=='i': rotation=Quaternion(.999, -0.0447101778, 0, 0).multiply(rotation)
	elif event.char=='k': rotation=Quaternion(.999,  0.0447101778, 0, 0).multiply(rotation)
	elif event.char=='l': rotation=Quaternion(.999, 0, -0.0447101778, 0).multiply(rotation)
	elif event.char=='j': rotation=Quaternion(.999, 0,  0.0447101778, 0).multiply(rotation)
	elif event.char=='o': rotation=Quaternion(.999, 0, 0,  0.0447101778).multiply(rotation)
	elif event.char=='u': rotation=Quaternion(.999, 0, 0, -0.0447101778).multiply(rotation)
	#renormalize the rotation quaternion to prevent decay from floating point error
	divisor=math.sqrt(rotation.s**2+rotation.v.magnitudeSquared())
	rotation.divide(divisor)
	#update the screen
	draw()

#return a list of triplets that lie on a sphere with radius r centered at specified center
#the function has nothing to do with quaternions
def dotSphere(r, latitudeResolution, longitudeResolution, centerX, centerY, centerZ):
	dots=[]
	for i in range(1, latitudeResolution+1):
		max=2*longitudeResolution/(1+abs(i-(latitudeResolution+1)/2))
		for j in range(max):
			x=centerX+r*math.cos(2*math.pi*j/max)*math.sin(math.pi*i/(latitudeResolution+1))
			y=centerY+r*math.sin(2*math.pi*j/max)*math.sin(math.pi*i/(latitudeResolution+1))
			z=centerZ+r*math.cos(math.pi*i/(latitudeResolution+1))
			dots.append(Triplet(x, y, z))
	return dots

#=====main=====#
objects+=dotSphere(50, 5, 10, 0, 0, 200)
objects+=dotSphere(50, 5, 7, 50, 50, 300)
root=Tkinter.Tk()
canvas=Tkinter.Canvas(root, width=screenWidth, height=screenHeight)
canvas.pack()
canvas.bind("<Key>", keyboardCallback)
canvas.focus_set()
canvas.configure(background="#003f3f")
draw()
root.mainloop()
