class CameraRep(object):
    def __init__(self, x):
        print("CameraRep")
        self.x = 1

class Camera(CameraRep):
    def __init__(self, x, x_max):
        #CameraRep.__init__(self, x)
        print(Camera.__mro__)
        super().__init__(x)
        print("Camera")
        self.x_max = x_max

class MobileCamRep(CameraRep):
    def __init__(self, x, vx):
        #CameraRep.__init__(self, x)
        super().__init__(x)
        print("MobileCamRep")
        self.vx = vx

class MobileCam(Camera, MobileCamRep):
    def __init__(self, x, x_max, vx, vx_max):
        print(MobileCam.__mro__)
        Camera.__init__(self, x, x_max)
        MobileCamRep.__init__(self, x, vx)
        print("MobileCam")
        self.vx_max = vx_max

mobileCam = MobileCam(1, 10, 2, 20)
#Camera(1, 10)
print(mobileCam.x)
print(mobileCam.x_max)
print(mobileCam.vx)
print(mobileCam.vx_max)


