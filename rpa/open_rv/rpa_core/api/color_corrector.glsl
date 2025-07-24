#extension GL_ARB_shading_language_420pack : enable
#extension GL_ARB_shader_storage_buffer_object : enable

layout (binding = 0) uniform sampler2D mask[32];

layout (binding = 16) buffer ssbo_data
{
    int ccs_count;
    float data[];
};

// Define constants for color correct types
const float COLORTIMER = 0.0;
const float GRADE = 1.0;
const float REGION = 1.0;

vec3 applyColorTimer(vec3 color, int index)
{
    float mute = data[index + 10];
    if (mute == 0.0) {
        return color;
    }
    const vec3 lumaCoefficients = vec3(0.2126, 0.7152, 0.0722);

    vec3 slope = vec3(data[index + 0], data[index + 1], data[index + 2]);
    vec3 offset = vec3(data[index + 3], data[index + 4], data[index + 5]);
    vec3 power = vec3(data[index + 6], data[index + 7], data[index + 8]);
    float saturation = data[index + 9];

    // apply slope and offset
    color = color * slope + offset;

    // apply power
    color = pow(color, 1.0 / power);

    // apply saturation
    vec3 luma = color * lumaCoefficients;
    color = color * vec3(saturation) + vec3(luma.r + luma.g + luma.b) * vec3(1.0 - saturation);
    return color;
}

vec3 applyGrade(vec3 color, int index)
{
    float mute = data[index + 18];
    if (mute == 0.0) {
        return color;
    }
    vec3 blackpoint = vec3(data[index + 0], data[index + 1], data[index + 2]);
    vec3 whitepoint = vec3(data[index + 3], data[index + 4], data[index + 5]);
    vec3 lift = vec3(data[index + 6], data[index + 7], data[index + 8]);
    vec3 gain = vec3(data[index + 9], data[index + 10], data[index + 11]);
    vec3 multiply = vec3(data[index + 12], data[index + 13], data[index + 14]);
    vec3 gamma = vec3(data[index + 15], data[index + 16], data[index + 17]);

    // apply blackpoint, whitepoint, lift, gain, and multiply
    color = (color - blackpoint) * ((gain - lift) / (whitepoint - blackpoint)) * multiply + lift;

    // apply gamma
    color = pow(color, 1.0 / gamma);

    return color;
}

vec4 main(const in inputImage in0, const in int refresh)
{
    vec2 uv = in0.st / in0.size();
    vec4 color = in0();
    int cc_index = 0;
    int index = 0;
    vec3 c = color.rgb;
    while (cc_index < ccs_count)
    {
        float is_region = data[index];
        float alpha = 1.0;
        if (is_region == REGION)
        {
            alpha = texture(mask[16 + cc_index], uv).x;
        }
        index++;
        int cc_nodes_count = int(data[index]);
        index++;
        for (int i = 0; i < cc_nodes_count; ++i)
        {
            float type = data[index];
            index++;
            if (type == COLORTIMER)
            {
                c = applyColorTimer(color.rgb, index);
                index += 11;
            }
            else if (type == GRADE)
            {
                c = applyGrade(color.rgb, index);
                index += 19;
            }
            color.rgb = alpha * c + (1.0 - alpha) * color.rgb;
        }
        cc_index++;
    }
    return color;
}
