from manim import DEGREES, DOWN, LEFT, RIGHT, UP, Create, Scene, Uncreate

from manim_eng import LED, Battery, Circuit, Lamp, Node, Resistor, Switch


class ExampleAnimation(Scene):
    """An example animation."""

    def construct(self) -> None:
        battery = Battery().rotate(90 * DEGREES).shift(LEFT)
        switch = Switch().shift(UP)
        resistor = Resistor().rotate(90 * DEGREES).shift(RIGHT)
        led = LED().flip().shift(DOWN)
        node1 = Node().shift(UP + RIGHT)
        node2 = Node().shift(DOWN + RIGHT)
        lamp = Lamp().rotate(90 * DEGREES).shift(RIGHT * 2)

        # Create the circuit
        circuit = (
            Circuit(battery, switch, resistor, led, node1, node2, lamp)
            .connect(battery.right, switch.left)
            .connect(switch.right, node1.left)
            .connect(node1.down, resistor.right)
            .connect(resistor.left, node2.up)
            .connect(node2.left, led.left)
            .connect(led.right, battery.left)
            .connect(node1.right, lamp.right)
            .connect(node2.right, lamp.left)
        )
        self.play(Create(circuit))
        self.wait(1)

        # Close the switch, light up the lamp and the LED
        self.play(
            switch.animate.close(), lamp.animate.light_up(), led.animate.light_up()
        )
        self.wait(1)

        # Animate the battery current and LED voltage drop
        voltage_drop = led.voltage("left", "right", r"V_{\text{drop}}").set_clockwise()
        self.play(
            battery.right.animate.set_current("I", out=True), Create(voltage_drop)
        )
        self.wait(1)

        # Open the switch, extinguish the lamp and the LED
        self.play(
            switch.animate.open(), lamp.animate.extinguish(), led.animate.extinguish()
        )
        self.wait(1)

        # Uncreate the scene
        self.play(Uncreate(circuit), Uncreate(voltage_drop))
        self.wait(1)
