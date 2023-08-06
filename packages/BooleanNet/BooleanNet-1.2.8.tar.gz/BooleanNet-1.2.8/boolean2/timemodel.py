import util
import ruleparser
from boolmodel import BoolModel

class TimeModel( BoolModel ):

    def initialize(self, missing=None, defaults={} ):
        "Initializes the TimeModel"
        self.mode = ruleparser.TIME
        BoolModel.initialize( self, missing=missing, defaults=defaults )
        
        if not self.label_tokens:
            util.error( 'this mode of operation requires time labels for rules' )
        
        self.gcd   = util.list_gcd( self.ranks )
        self.step  = 0
        self.times = [ 0 ]

    def next(self):
        "Generates the updates based on the next simulation step"
        self.step += 1
        timestep = self.step * self.gcd             
        lines = [ timestep ]
        for rank in self.ranks:
            if timestep % rank == 0:
                line = self.update_lines[rank]
                lines.extend( line )                
        
        return lines

    def shuffler(self, *args, **kwds):
        "A shuffler that returns the current update rules"
        while 1:
            
            # skip ahead until something valid
            value = self.next()
            tstep = value[0]
            rules = value[1:]
            if rules:
                self.times.append( tstep )
                break

        return rules

    def iterate( self, steps, shuffler=None, **kwds ):
        """
        Iterates over the lines 'steps' times. 
        """
        shuffler = shuffler or self.shuffler
        for index in xrange(steps):
            self.parser.RULE_START_ITERATION( index, self )
            BoolModel.state_update(self)
            lines = shuffler( )
            map( self.local_parse, lines ) 

if __name__ == '__main__':
    

    text = """
    A  =  B =  C = False
    D  = True
    
    5:  A* = C and (not B)
    10: B* = A
    15: C* = D
    20: D* = B 
    """

    model = TimeModel( mode='time', text=text )
    model.initialize(  )
    
    #for i in range(5):
        #print model.next()
    #    print model.shuffler()

    from itertools import count

    c = count(0)
    model.iterate( steps=12 )
    for state in model.states:
        t = c.next() * 5
        tstamp = 'T=%d ' % t
        data = [ tstamp ] + map(int, (state.A, state.B, state.C, state.D))
        data = map(str, data)
        print '\t'.join(data)
