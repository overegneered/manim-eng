from manim import *
from manim_eng import *


class CreateResistor(Scene):
    def construct(self):
        resistor_1 = Resistor(debug=True)
        #resistor_2 = Thermistor().shift(RIGHT * 4 + UP * 2)
        #self.add(resistor_2)
        # resistor_3 = VariableResistor().shift(LEFT * 2)
        self.play(Create(resistor_1))
        self.play(resistor_1.animate.set_label("R_{12}"))
        self.wait()
        self.play(Rotate(resistor_1, 0.25*PI))
        #self.play(resistor_1.animate.set_value("R", (UP + LEFT) / np.sqrt(2)))
        self.wait()
        self.play(Rotate(resistor_1, 0.25*PI))
        #self.play(resistor_1.animate.set_value("R", LEFT))
        self.wait(5)
        test = Circle()


if __name__ == "__main__":
    with tempconfig({"quality": "low_quality", "preview": True}):
        scene = CreateResistor()
        scene.render()
