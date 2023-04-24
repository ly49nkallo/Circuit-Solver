# Circuit-Solver
Solve arbitrary circuits for resistance, current, and voltage across all components.

Define a circuit using the following syntax:
```python
c5 = Circuit(
        Series(
            Resistor('R1', R=4),
            Parellel(
                Resistor('R2', R=4),
                Resistor('R3', R=4),
            ),
            V = 12
        )
    )
```
You can solve a circuit and print the solve to the terminal with 
```python
c5.solve()
```

Any component can be assigned an initial voltage, current, and/or resistance value.
The algorithm will attempt to solve the circuit using various formulas and properties of circuits.

Additionally, the program will output the steps and reasoning required to obtain the solution. If the circuit is unsolvable, the program will attempt to solve as much of the circuit as possible.

For example, on the above circuit, the program would output

```
==========BEGIN SOLVE==========
max iter: 10

Parellel: Set R = 2 from property of Parellel (1/R = 1/R_1 + 1/R_2 + ... + 1/R_N)
Series: Set R = 6 from property of Series (R = R_1 + R_2 + ... + R_N)
Series: Set I = 2 from formula I = V/R
Series: Set I = 2 from property of Series (I = I_1 = I_2 = ... = I_N)
Series: Set I = 2 from property of Series (I = I_1 = I_2 = ... = I_N)
Resistor(R1): Set V = 8 from formula V = IR
Parellel: Set V = 4 from formula V = IR
Parellel: Set V = 4 from property of Parellel (V = V_1 = V_2 = ... = V_N)
Parellel: Set V = 4 from property of Parellel (V = V_1 = V_2 = ... = V_N)
Resistor(R2): Set I = 1 from formula I = V/R
Resistor(R3): Set I = 1 from formula I = V/R
Iterations Required: 4

==========SOLVED CIRCUIT==========
Circuit(
        Series(R = 6, I = 2, V = 12
                Resistor(name = R1, R = 4, I = 2, V = 8)        
                Parellel(R = 2, I = 2, V = 4
                        Resistor(name = R2, R = 4, I = 1, V = 4)

                        Resistor(name = R3, R = 4, I = 1, V = 4)

                        )
                )
        )

Elapsed time: 0.00801
```

