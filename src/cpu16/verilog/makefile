SIM=build/sim

all:
	iverilog -g2012 -o $(SIM) src/*.sv sim/*.sv
	vvp $(SIM)

clean:
	rm -f build/*