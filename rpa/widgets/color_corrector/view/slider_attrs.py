from rpa.widgets.color_corrector.utils import \
    SliderAttrs, Slider

def build_slider_attrs():
    slider_attrs = SliderAttrs()

    slider_attrs.set_value(
        Slider.OFFSET, {
            'default': 0.0,
            'slider':"True",
            'sensitivity':'0.01',
            'slidermin':'-1.0',
            'slidercenter':'0.0',
            'slidermax':'1.0',
            'sliderexponent':'0.75',
            })
    
    slider_attrs.set_value(
        Slider.POWER, {
            'default': 1.0,
            'slider':"True",
            'sensitivity':'0.001',
            'slidermin':'0.0',
            'slidercenter':'1.0',
            'slidermax':'2.0',
            'sliderexponent':'0.5',
            })
    
    slider_attrs.set_value(
        Slider.SLOPE, {
            'default': 1.0,
            'slider':"True",
            'sensitivity':'0.001',
            'slidermin':'0.0',
            'slidercenter':'1.0',
            'slidermax':'2.0',
            'sliderexponent':'0.5',
            })

    slider_attrs.set_value(
        Slider.SAT, {
            'default': 1.0,
            'slider':"True",
            'sensitivity':'0.001',
            'slidermin':'0.0',
            'slidermax':'2.0',
            'slidercenter':'1.0',
            })

    slider_attrs.set_value(
        Slider.FALLOFF, {
            'default': 0,
            'slider': "True",
            'sensitivity': '1',
            'slidermin': '0',
            'slidermax': '300',
            })
    
    slider_attrs.set_value(
        Slider.GAMMA, {
            'default': 1.0,
            'slider':"True",
            'sensitivity':'0.001',
            'slidermin':'0.01',
            'slidercenter':'1.0',
            'slidermax':'2.6',
            'sliderexponent':'0.5',
             })

    slider_attrs.set_value(
        Slider.BLACKPOINT, {
            'default': 0.0,
            'slider':"True",
            'sensitivity':'0.001',
            'slidermin':'0.0',
            'slidermax':'1.0',
            })

    slider_attrs.set_value(
        Slider.WHITEPOINT, {
            'default': 1.0,
            'slider':"True",
            'sensitivity':'0.001',
            'slidermin':'0.0',
            'slidermax':'1.0',
            })

    slider_attrs.set_value(
        Slider.FSTOP, {
            'default': 1.0,
            'slider':"True",
            'sensitivity':'0.001',
            'slidermin':'-2.0',
            'slidercenter':'0.0',
            'slidermax':'2.0',
            })
    
    slider_attrs.set_value(
        Slider.LIFT, {
            'default': 0.0,
            'slider':"True",
            'sensitivity':'0.001',
            'slidermin':'0.0',
            'slidermax':'1.0',
            })

    return slider_attrs
