SIM=build/sim

all:
	iverilog -g2012 -o $(SIM) src/*.v sim/*.v
	vvp $(SIM)

clean:
	rm -f build/*