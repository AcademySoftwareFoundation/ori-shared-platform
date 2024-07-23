#extension GL_ARB_shading_language_420pack : enable
#extension GL_ARB_shader_storage_buffer_object : enable

layout (binding = 0) uniform sampler2D mask[32];

struct ColorCorrection
{
    // Color Timer
    float[3] slope;
    float[3] offset;
    float[3] power;
    float saturation;

    // Grade
    float[3] blackpoint;
    float[3] whitepoint;
    float[3] lift;
    float[3] gain;
    float[3] multiply;
    float[3] gamma;
};

layout (binding = 16) buffer ssbo_data
{
    ColorCorrection clip_cc;
    ColorCorrection frame_cc;
    int region_ccs_count;
    ColorCorrection region_ccs[];
};

vec3 applyColorTimer(vec3 color, const ColorCorrection cc)
{
    const vec3 lumaCoefficients = vec3(0.2126, 0.7152, 0.0722);

    vec3 slope = vec3(cc.slope[0], cc.slope[1], cc.slope[2]);
    vec3 offset = vec3(cc.offset[0], cc.offset[1], cc.offset[2]);
    vec3 power = vec3(cc.power[0], cc.power[1], cc.power[2]);
    float saturation = cc.saturation;

    // apply slope and offset
    color = color * slope + offset;
    color = clamp(color, 0.0, 1.0);

    // apply power
    color = pow(color, power);

    // apply saturation
    vec3 luma = color * lumaCoefficients;
    color = color * vec3(saturation) + vec3(luma.r + luma.g + luma.b) * vec3(1.0 - saturation);
    color = clamp(color, 0.0, 1.0);

    return color;
}

vec3 applyGrade(vec3 color, const ColorCorrection cc)
{
    vec3 blackpoint = vec3(cc.blackpoint[0], cc.blackpoint[1], cc.blackpoint[2]);
    vec3 whitepoint = vec3(cc.whitepoint[0], cc.whitepoint[1], cc.whitepoint[2]);
    vec3 lift = vec3(cc.lift[0], cc.lift[1], cc.lift[2]);
    vec3 gain = vec3(cc.gain[0], cc.gain[1], cc.gain[2]);
    vec3 multiply = vec3(cc.multiply[0], cc.multiply[1], cc.multiply[2]);
    vec3 gamma = vec3(cc.gamma[0], cc.gamma[1], cc.gamma[2]);

    // apply blackpoint, whitepoint, lift, gain, and multiply
    color = (color - blackpoint) * ((gain - lift) / (whitepoint - blackpoint)) * multiply + lift;
    color = clamp(color, 0.0, 1.0);

    // apply gamma
    color = pow(color, gamma);

    return color;
}

vec3 applyColorCorrection(vec3 color, const ColorCorrection cc)
{
    color = applyColorTimer(color, cc);
    color = applyGrade(color, cc);
    return color;
}

vec4 main(const in inputImage in0, const in int refresh)
{
    vec2 uv = in0.st / in0.size();
    vec4 color = in0();

    color.rgb = applyColorCorrection(color.rgb, clip_cc);
    color.rgb = applyColorCorrection(color.rgb, frame_cc);

    for (int i = 0; i < region_ccs_count; ++i)
    {
        float alpha = texture(mask[16 + i], uv).x;
        vec3 c = applyColorCorrection(color.rgb, region_ccs[i]);
        color.rgb = alpha * c + (1.0 - alpha) * color.rgb;
    }

    return color;
}
