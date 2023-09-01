# Copyright (c) 2022 Kyle Schouviller (https://github.com/kyle0654)

from typing import Literal

import numpy
from PIL import Image

from invokeai.app.invocations.primitives import ImageField, ImageOutput

from ..models.image import ImageCategory, ResourceOrigin
from .baseinvocation import BaseInvocation, InputField, InvocationContext, invocation

@invocation(
    "img_channel_adjust",
    title="Adjust Image Channel",
    tags=["image", "red", "green", "blue", "alpha", "cyan", "magenta", "yellow", "black", "hue", "saturation", "luminosity", "value", "RGB", "RGBA", "CYMK", "YCbCr", "LAB", "HSV", "HSL"],
    category="image",
)
class ImageChannelAdjustmentInvocation(BaseInvocation):
    """Adjusts any channel of an image in any format."""

    image: ImageField = InputField(description="The image to adjust")
    mode: Literal["RGB", "RGBA", "CYMK", "YCbCr", "LAB", "HSV"] = InputField(description="The color mode to convert to before adjusting")
    channel: int = InputField(default=0, ge=0, le=3, description="Which channel to adjust")
    method: Literal["Multiply", "Offset"] = InputField(description="The type of adjustment to perform")
    adjustment: float = InputField(default=1.0, ge=-255, le=255, description="The amount to adjust the channel by")

    def invoke(self, context: InvocationContext) -> ImageOutput:
        pil_image = context.services.images.get_pil_image(self.image.image_name)

        # limit to 3 channels unless RGBA or CMYK
        if not (self.mode == "RGBA" or self.mode == "CMYK"):
            self.channel = min(self.channel, 2)

        # Convert PIL image to new format
        converted_image = numpy.array(pil_image.convert(self.mode))
        image_channel = converted_image[:, :, self.channel]

        # Adjust the channel value
        if self.method == "Offset":
            image_channel = numpy.clip(image_channel + self.adjustment, 0, 255)
        else:
            image_channel = numpy.clip(image_channel * self.adjustment, -255, 255) % 256
        
        # Put the channel back into the image
        converted_image[:, :, self.channel] = image_channel

        # Convert back to RGBA format and output
        pil_image = Image.fromarray(converted_image, mode=self.mode).convert("RGBA")

        image_dto = context.services.images.create(
            image=pil_image,
            image_origin=ResourceOrigin.INTERNAL,
            image_category=ImageCategory.GENERAL,
            node_id=self.id,
            is_intermediate=self.is_intermediate,
            session_id=context.graph_execution_state_id,
            workflow=self.workflow,
        )

        return ImageOutput(
            image=ImageField(
                image_name=image_dto.image_name,
            ),
            width=image_dto.width,
            height=image_dto.height,
        )