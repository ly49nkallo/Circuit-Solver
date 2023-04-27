'''Solve an circuit for resistance, current, and voltage across all resistors'''

#import numpy
from typing import Optional
import time
from fractions import Fraction

'''
Circuit Formalism
Ex. 
myCircuit = Circuit(
        Series(
            Resistor('R1', R=4),
            Parellel(
                Resistor('R2', R=4),
                Resistor('R3', R=4),
            ),
            V = 12
        )
    )


Importantly, Circuit, Parellel, and Resistors inherit from a base class that tracks a resistance, current, and voltage

Circuit will be solved recursively through wavefunction collapse
'''

class Module:
    def __init__(self, 
                 m_type:str,
                 *args,
                 name:Optional[str] = None,
                 R:Optional[float]=None, 
                 I:Optional[float]=None, 
                 V:Optional[float]=None
                 ):
        assert all([isinstance(i, float) or isinstance(i, int) or i is None for i in [R, I, V]]), \
                        f"Input to module must be a float or None, recieved R:{type(R)}, I:{type(I)}, V:{type(V)}" 
        assert isinstance(name, str) or name is None, f"name must be a string or None, recieved name:{type(name)}"
        assert isinstance(m_type, str), f"m_type must be a string, recieved type:{type(m_type)}"
        assert all([isinstance(i, Module) for i in args]), f'All input modules must inherit from Module class got {[type(i) for i in args]}'
        # instantiate self
        self.m_type = m_type
        self.name = name
        self.R = R
        self.I = I
        self.V = V
        self.children = args

    def solve(self):
        # V = IR 
        # ensure that exactly one variable is unknown
        if sum([int(i is None) for i in [self.R, self.I, self.V]]) == 1:
            print(f"{self.m_type}",end='')
            if self.name is not None: print(f"({self.name})",end='')
            print(": ", end='')
            if self.R == None:
                # R = V/I
                self.R = self.V / self.I
                print(f"Set R = {Fraction(self.R).limit_denominator(200)} from formula R = V/I")
            elif self.I == None:
                # I = V/R
                self.I = self.V / self.R
                print(f"Set I = {Fraction(self.I).limit_denominator(200)} from formula I = V/R")
            elif self.V == None:
                # V = IR
                self.V = self.I * self.R
                print(f"Set V = {Fraction(self.V).limit_denominator(200)} from formula V = IR")
        
        for child in self.children:
            child.solve()
    
    def solved(self) -> bool:
        return all([c.solved() for c in self.children]) and \
            self.I is not None and self.R is not None and self.V is not None
    
    def _repr(self, tabs) -> str:
        '''Pretty print'''
        out = f'{self.m_type}('
        if self.name is not None: out += f'name = {self.name}, '
        if self.R is not None: out += f'R = {Fraction(float(self.R)).limit_denominator(max_denominator=200)}, '
        if self.I is not None: out += f'I = {Fraction(float(self.I)).limit_denominator(max_denominator=200)}, '
        if self.V is not None: out += f'V = {Fraction(float(self.V)).limit_denominator(max_denominator=200)}, '
        if out[-2:] == ', ': out = out[:-2]
        if len(self.children) != 0: out += '\n'
        for child in self.children:
            out += '\t'*tabs
            out += child._repr(tabs+1)
            out += '\n'
        if len(self.children) != 0: out += '\t'*tabs
        out += ')'
        return out
    
    
class Resistor(Module):
    def __init__(self, name:str, R:Optional[float]=None, I:Optional[float]=None, V:Optional[float]=None) -> None:
        super().__init__('Resistor', name=name, R=R, I=I, V=V)

    def __repr__(self) -> str:
        return super()._repr(1)
    
    def solve(self):
        return super().solve()

class Circuit(Module):
    def __init__(self, *args, max_iter:int = 50) -> None:
        assert isinstance(max_iter, int)
        assert len(args) == 1, f'Circuit only accepts one module as input, recieved {len(args)} instead.'
        self.max_iter = max_iter
        super().__init__('Circuit', *args)

    def __repr__(self) -> str:
        return super()._repr(1)
    
    #override solve
    def solved(self) -> bool: return all([c.solved() for c in self.children])
    
    def solve(self):
        stime = time.time()
        print('='*10 + "BEGIN SOLVE" + '='*10)
        print('max iter:', self.max_iter)
        print()
        cntr = self.max_iter
        while cntr > 0 and not self.solved():
            cntr -= 1
            super().solve()
        print('Iterations Required:', self.max_iter - cntr)
        print()
        if cntr == 0:
            print("!"*10 + "FAILED TO SOLVE CIRCUIT" + "!"*10)
            print("="*10 + "PARTIALLY SOLVED CIRCUIT" + "="*10)
            print(self)
        else:
            print("="*10 + "SOLVED CIRCUIT" + "="*10)
            print(self)
        print()
        print("Elapsed time:", round(time.time() - stime,5))


class Series(Module):
    def __init__(self, *args, R:Optional[float]=None, I:Optional[float]=None, V:Optional[float]=None):
        super().__init__('Series', *args, R=R, I=I, V=V)

    def __repr__(self) -> str:
        return super()._repr(1)

    '''
    Properties of Series:
    R = R_1 + R_2 ... 
    I = I_1 = I_2 ...
    V = V_1 + V_2 ...
    '''
    def solve(self):

        '''R = R_1 + R_2 ...'''
        if all([c.R is not None for c in self.children]) and self.R is None:
            self.R = sum([c.R for c in self.children])
            print(f"Series: Set R = {Fraction(self.R).limit_denominator(200)} from property of Series (R = R_1 + R_2 + ... + R_N)")

        # One unknown child
        if sum([int(i.R is None) for i in self.children]) == 1 and self.R is not None:
            for c in self.children:
                if c.R is not None: continue
                c.R = self.R - sum([i.R for i in self.children if i.R is not None])
                print(f"{c.m_type}: Set R = {Fraction(c.R).limit_denominator(200)} from property of Series (R = R_1 + R_2 + ... + R_N)")

        '''I = I_1 = I_2'''
        if any([c.I is not None for c in self.children]) and self.I is None:
            self.I = [c.I for c in self.children if c.I is not None][0]
            print(f"Series: Set I = {Fraction(self.I).limit_denominator(200)} from property of Series (I = I_1 = I_2 = ... = I_N)")

        if self.I is not None:
            for c in self.children:
                if c.I is not None: continue
                c.I = self.I
                print(f"{self.m_type}",end='')
                if self.name is not None: print(f"({self.name})",end='')
                print(": ", end='')
                print(f"Set I = {Fraction(self.I).limit_denominator(200)} from property of Series (I = I_1 = I_2 = ... = I_N)")

        '''V = V_1 + V_2 ...'''
        if all([c.V is not None for c in self.children]) and self.V is None:
            self.V = sum([c.V for c in self.children])
            print(f"Series: Set V = {Fraction(self.V).limit_denominator(200)} from property of Series (V = V_1 + V_2 + ... + V_N)")

        # One unknown child
        if sum([int(i.V is None) for i in self.children]) == 1 and self.V is not None:
            for c in self.children:
                if c.V is not None: continue
                c.V = self.V - sum([i.V for i in self.children if i.V is not None])
                print(f"{c.m_type}: Set V = {Fraction(c.V).limit_denominator(200)} from property of Series (V = V_1 + V_2 + ... + V_N)")
        
        super().solve()


class Parellel(Module):
    def __init__(self, *args, R:Optional[float]=None, I:Optional[float]=None, V:Optional[float]=None):
        super().__init__('Parellel', *args, R=R, I=I, V=V)

    def __repr__(self) -> str:
        return super()._repr(1)
    
    '''
    Properties of Parellel:
    1/R = 1/R_1 + 1/R_2 ...
    V = V_1 = V_2 ...
    I = I_1 + I_2 ...
    '''
    def solve(self):

        '''1/R = 1/R_1 + 1/R_2 ...'''
        if all([c.R is not None for c in self.children]) and self.R is None:
            self.R = 1/sum([1/c.R for c in self.children])
            print(f"Parellel: Set R = {Fraction(self.R).limit_denominator(200)} from property of Parellel (1/R = 1/R_1 + 1/R_2 + ... + 1/R_N)")

        # One unknown child
        if sum([int(i.R is None) for i in self.children]) == 1 and self.R is not None:
            for c in self.children:
                if c.R is not None: continue
                print((1/self.R) - sum([1/i.R for i in self.children if i.R is not None]))
                print((1/self.R))
                print(sum([1/i.R for i in self.children if i.R is not None]))
                print(self.R)
                print([i.R for i in self.children if i.R is not None])
                print(c)
                c.R = 1/((1/self.R) - sum([1/i.R for i in self.children if i.R is not None]))
                print(f"{c.m_type}: Set R = {Fraction(c.R).limit_denominator(200)} from property of Parellel (1/R = 1/R_1 + 1/R_2 + ... + 1/R_N)")

        '''V = V_1 = V_2'''
        if any([c.V is not None for c in self.children]) and self.V is None:
            self.V = [c.V for c in self.children if c.V is not None][0]
            print(f"Parellel: Set V = {Fraction(self.V).limit_denominator(200)} from property of Parellel (V = V_1 = V_2 = ... = V_N)")

        if self.V is not None:
            for c in self.children:
                if c.V is not None: continue
                c.V = self.V
                print(f"{self.m_type}",end='')
                if self.name is not None: print(f"({self.name})",end='')
                print(": ", end='')
                print(f"Set V = {Fraction(self.V).limit_denominator(200)} from property of Parellel (V = V_1 = V_2 = ... = V_N)")

        '''I = I_1 + I_2'''
        if all([c.I is not None for c in self.children]) and self.I is None:
            self.I = sum([c.I for c in self.children])
            print(f"Parellel: Set I = {Fraction(self.I).limit_denominator(200)} from property of Parellel (I = I_1 + I_2 + ... + I_N)")
        
        # One unknown child
        if sum([int(i.I is None) for i in self.children]) == 1 and self.I is not None:
            for c in self.children:
                if c.I is not None: continue
                c.I = self.I - sum([i.I for i in self.children if i.I is not None])
                print(f"{c.m_type}: Set I = {Fraction(c.I).limit_denominator(200)} from property of Parellel (I = I_1 + I_2 + ... + I_N)")
        
        super().solve()


def main():
    c3 = Circuit(
        Series(
            Resistor('R1', R=2),
            Resistor('R2', R=4),
            Resistor('R3', R=6),
            V=12
        )
    )
    c3.solve()
    c4 = Circuit(
        Parellel(
            Resistor('R1', R=2),
            Resistor('R2', R=3),
            Resistor('R3', R=6),
            V=12
        )
    )
    c4.solve()
    c5 = Circuit(
        Series(
            Parellel(
                Series(Resistor('R1', R=5), Resistor('R2', V=3.5)),
                Resistor('R3', I=1.5)
            ),
            Parellel(
                Resistor('R4', V=4), Resistor('R5', I=1)
            ),
            Resistor('R6', R=2),
            I=2
        )
    )
    c5.solve()

if __name__ == '__main__':
    main()
