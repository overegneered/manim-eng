import numpy as np
from manim import Scene

from manim_eng import (
    LED,
    VDD,
    VSS,
    Ammeter,
    Antenna,
    Bell,
    BottomRail,
    Buzzer,
    CapacitiveSensor,
    Capacitor,
    Cell,
    ControlledCurrentSource,
    ControlledVoltageSource,
    CurrentSource,
    Diode,
    DoubleCell,
    Earth,
    FrequencyMeter,
    Fuse,
    Galvanometer,
    Ground,
    InductiveSensor,
    Inductor,
    Lamp,
    Microphone,
    NChannelJFET,
    NChannelMOSFET,
    NPNTransistor,
    Ohmmeter,
    OpAmp,
    PChannelJFET,
    PChannelMOSFET,
    Photodiode,
    PNPTransistor,
    PolarizedCapacitor,
    PushToBreakSwitch,
    PushToMakeSwitch,
    QuadrupleCell,
    Resistor,
    SchottkyDiode,
    Speaker,
    Switch,
    Thermistor,
    TopRail,
    TripleCell,
    TunnelDiode,
    VariableCapacitor,
    VariableInductor,
    VariableResistor,
    VoltageSource,
    Voltmeter,
    ZenerDiode,
    config_eng,  # Configurations
)
from manim_eng.components.base import Component


class AllComponents(Scene):
    """Displays all components in this library."""

    def construct(self) -> None:
        scale = 0.5
        grid = [
            np.array([x, y, 0.0])
            for y in np.linspace(3, -3, 7)
            for x in np.linspace(-6, 6, 12)
        ]
        all_components: list[Component] = [
            Ground(),
            Earth(),
            TopRail(),
            BottomRail(),
            VDD(),
            VSS(),
            Resistor(),
            VariableResistor(),
            Thermistor(),
            Capacitor(),
            PolarizedCapacitor(),
            VariableCapacitor(),
            CapacitiveSensor(),
            Inductor(),
            VariableInductor(),
            InductiveSensor(),
            VoltageSource(),
            ControlledVoltageSource(),
            CurrentSource(),
            ControlledCurrentSource(),
            Cell(),
            DoubleCell(),
            TripleCell(),
            QuadrupleCell(),
            Diode(),
            LED(),
            Photodiode(),
            SchottkyDiode(),
            TunnelDiode(),
            ZenerDiode(),
            NPNTransistor(),
            PNPTransistor(),
            PChannelJFET(),
            NChannelJFET(),
            NChannelMOSFET(),
            NChannelMOSFET(channel_type="depletion"),
            PChannelMOSFET(),
            PChannelMOSFET(channel_type="depletion"),
            OpAmp(),
            Switch(),
            Switch().close(),
            PushToMakeSwitch(),
            PushToMakeSwitch().close(),
            PushToBreakSwitch(),
            PushToBreakSwitch().close(),
            Lamp(),
            Bell(),
            Buzzer(),
            Speaker(),
            Microphone(),
            Fuse(),
            Antenna(),
            Voltmeter(),
            Ammeter(),
            Galvanometer(),
            Ohmmeter(),
            FrequencyMeter(),
        ]
        for component, position in zip(all_components, grid, strict=False):
            component.scale(scale).move_to(position)
        self.add(*all_components)


class AllComponentsANSI(AllComponents):
    def construct(self) -> None:
        config_eng.symbol.resistor_standard = "ANSI"
        config_eng.symbol.fuse_standard = "ANSI"
        super().construct()
