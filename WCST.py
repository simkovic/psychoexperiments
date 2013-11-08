import numpy as np
from psychopy import visual,core,monitors,event,gui
"""
Instruction: Select one of the four cards displayed at the top of the screen
    such that the selected card matches the card displayed at the bottom
    of the screen. The cards can be matched based on three dimensions - color,
    number of objects or the shape of the objects they display. You will be
    given feedback whether the selected card was 'Right' or 'Wrong'.
    Use the feedback to determine which dimension is targeted by feedback and
    based on it select the right card. The targeted dimension may change from
    to time without notice.

"""

X=0;Y=1
def pointInTriangle(t1,t2,t3,pt):
    """ determines whether point PT is located inside
        triangle with vertices at points T1, T2 and T3
    """
    def sign(p1,p2,p3):
        return (p1[X]-p3[X])*(p2[Y]-p3[Y])-(p2[X]-p3[X])*(p1[Y]-p3[Y])
    b1=sign(pt,t1,t2)<0
    b2=sign(pt,t2,t3)<0
    b3=sign(pt,t3,t1)<0
    return b1==b2 and b2==b3

def drawTriangle(M,t,value=1):
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if pointInTriangle(t[0],t[1],t[2],(i,j)):
                M[i,j]=value
    return M

def drawCircle(M,pos,radius,value=1):
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if np.sqrt((i-pos[X])**2+(j-pos[Y])**2)<radius:
                M[i,j]=value
    return M
def drawStar(M,pos,nv, ocr,icr):
    """ pos - location of the star
        nv - number of vertices
        ocr - radius of outer circle
        icr - radius of inner circle
    """
    M=drawCircle(M,pos,icr)
    phi=np.linspace(0,2*np.pi,nv+1)[:-1]
    ops=np.array([np.cos(phi)*ocr,np.sin(phi)*ocr])+np.array(pos,ndmin=2).T
    phi+= phi[1]/2.0
    ips=np.array([np.cos(phi)*icr,np.sin(phi)*icr])+np.array(pos,ndmin=2).T
    for i in range(phi.size):
        M=drawTriangle(M,[ips[:,i-1],ips[:,i],ops[:,i]])
    return M
# setup masks of different shape
N=128
mid=N/2-0.5
CIRCLE=np.ones((N,N))*-1
CIRCLE=drawCircle(CIRCLE,(mid,mid),N/2)

CROSS=np.ones((N,N))*-1
w=N/4
for i in range(CROSS.shape[0]):
    for j in range(CROSS.shape[1]):
        if i>mid-w/2 and i<mid+w/2 or j>mid-w/2 and j<mid+w/2 :
            CROSS[i,j]=1
STAR=np.ones((N,N))*-1
STAR=drawStar(STAR,(mid,mid),5,N/2,N/5)
SQUARE=np.ones((N,N))

# Settings
MON=monitors.Monitor('dell', width=37.8, distance=50); MON.setSizePix((1280,1024))
TPOS=(0,-10)# position of the target card 
CARDY=10# vertical position of choice cards
CARDX=1 # horizontal space between choice cards
CARDW=4 # card width
CARDH=6 # card height
CLRS=['red','green','blue','orange']
SHAPES=[CIRCLE,SQUARE,STAR,CROSS]
SPOS = [[[0,0],[np.nan,np.nan],[np.nan,np.nan],[np.nan,np.nan]],
        [[0,CARDH/4.0],[0,-CARDH/4.0],[np.nan,np.nan],[np.nan,np.nan]],
        [[-CARDW/4.0,CARDH/3.0],[-CARDW/4.0,-CARDH/3.0],[CARDW/4.0,0],[np.nan,np.nan]],
        [[-CARDW/4.0,CARDH/4.0],[-CARDW/4.0,-CARDH/4.0],
         [CARDW/4.0,-CARDH/4.0],[CARDW/4.0,CARDH/4.0]]]

class Experiment():
    def __init__(self):
        myDlg = gui.Dlg(title="Wisconsin Card Sorting Task",pos=(0,0))     
        myDlg.addField('Subject ID:',1)
        myDlg.addField('Number of Trials:',128)
        myDlg.show()#show dialog and wait for OK or Cancel
        vpInfo = myDlg.data
        self.vp=vpInfo[0]
        self.T=vpInfo[1]

        self.win=visual.Window(size=(1000,1000),units='deg',fullscr=False,monitor=MON)
        self.mouse = event.Mouse(False,None,self.win)        
        self.cards=[]
        self.elems=[]
        for i in range(4):
            self.cards.append(visual.Rect(self.win,CARDW,CARDH,fillColor='white',
                        pos=((i-1.5)*(CARDX+CARDW),CARDY),lineColor='black',interpolate=False))
            self.elems.append(visual.ElementArrayStim(self.win,nElements=4,sizes=1.5,colors='black',
                         fieldPos=((i-1.5)*(CARDX+CARDW),CARDY),elementTex=None))
        self.cards.append(visual.Rect(self.win,CARDW,CARDH,fillColor='white',
            pos=TPOS,lineColor='black',interpolate=False))  
        self.elems.append(visual.ElementArrayStim(self.win,nElements=4,sizes=1.5,colors='black',
            fieldPos=TPOS,elementTex=None))
        self.text=visual.TextStim(self.win,pos=TPOS,height=2)
        self.output=open('vp%03d.res'%self.vp,'w')
    
    def runTrial(self,t):
        choice=[]
        for i in range(3):
            choice.append(np.random.permutation(4))
        choice=(np.array(choice).T).tolist()
        target=np.random.randint(4,size=3)
        # display problem
        for i in range(4):
            self.cards[i].draw()
            self.elems[i].setColors(CLRS[choice[i][0]])
            self.elems[i].setMask(SHAPES[choice[i][1]])
            self.elems[i].setXYs(SPOS[choice[i][2]]) 
            self.elems[i].draw()
        self.cards[4].setPos(TPOS)
        self.cards[4].draw()
        self.elems[4].setFieldPos(TPOS)
        self.elems[4].setColors(CLRS[target[0]])
        self.elems[4].setMask(SHAPES[target[1]])
        self.elems[4].setXYs(SPOS[target[2]]) 
        self.elems[4].draw()
        self.win.flip()
        # wait for response
        self.mouse.clickReset()
        while True:
            mkey=self.mouse.getPressed()
            if sum(mkey)>0:
                card=-1;mpos=self.mouse.getPos()
                for i in range(4):
                    if self.cards[i].contains(mpos):
                        card=i
                if card>-1: break
                else: self.mouse.clickReset()
            for key in event.getKeys():
                if key in ['escape']:
                    self.win.close()
                    core.quit()
        # display choice
        self.cards[4].setPos((self.cards[card].pos[X],0)) 
        self.elems[4].setFieldPos((self.cards[card].pos[X],0))
        for i in range(5):
            self.cards[i].draw()
            self.elems[i].draw()
        self.win.flip()
        core.wait(1)
        # write self.output and display feedback
        self.output.write('%d\t%d\t%d\t%d\t'%(self.vp,t,card,self.rule))
        if target[self.rule]==choice[card][self.rule]:
            self.text.setText('RIGHT')
            self.corstreak+=1
            self.output.write('1\t')
        else:
            self.text.setText('WRONG')
            self.corstreak=0
            self.output.write('0\t')
            
        for i in range(5):
            self.cards[i].draw()
            self.elems[i].draw()
            if i<4:self.output.write('%d\t%d\t%d\t'%tuple(choice[i]))
        self.output.write('%d\t%d\t%d\n'%tuple(target))
        self.output.flush()
        self.text.draw()
        self.win.flip()
        core.wait(2)
    def run(self):
        self.rule=np.random.randint(3)
        self.corstreak=0
        for t in range(self.T):
            if self.corstreak>=10:
                sel=range(3)
                sel.remove(self.rule)
                self.rule=sel[np.random.randint(2)]
            self.runTrial(t)
        self.output.close()
        self.win.close()

if __name__ == '__main__':
    E=Experiment()
    E.run()
