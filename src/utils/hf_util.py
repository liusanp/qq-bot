from gradio_client import Client, file, handle_file


def req_img2img(structure_image, style_image, prompt="", depth_strength=15, style_strength=0.15, hf_token=None):
    client = Client("multimodalart/flux-style-shaping", hf_token=hf_token)
    result = client.predict(
            prompt=prompt,
            structure_image=handle_file(structure_image),
            style_image=handle_file(style_image),
            depth_strength=depth_strength,
            style_strength=style_strength,
            api_name="/generate_image"
    )
    return result


def req_text2img(endpoint, prompt, width, height, seed=0, hf_token=None):
    client = Client(endpoint, hf_token=hf_token)
    result = client.predict(
            prompt=prompt,
            seed=seed,
            width=width,
            height=height,
            api_name="/generate_image"
    )
    return result