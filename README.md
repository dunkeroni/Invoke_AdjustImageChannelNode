# Invoke_AdjustImageChannelNode  
An expanded implementation of the Adjust Saturations/Luminosity nodes from Invoke 3.1.0 able to handle arbitrary format/channel as well as negative multipliers.  
Supports RGB, RGBA, CYMK, YCbCr, LAB, HSV  

Channel may be an integer between 0 and 3. If the selected format only has 3 channels, then the value will be clipped from 3 to 2 if entered.  

## Offset Method:  
Adds/Subtracts the adjustment value, limiting the result into the range [0,255].  
Offsetting by -255 will make make the entire channel 0.  

## Multiply Method:  
Multiplies by the adjustment value, limits the result into the range [-255,255], then modulo by 256.  
Multiplying by a value of -1.0 will invert the channel.  
