using System.Collections;
using System.Collections.Generic;

public class HairTransformData
{
    public HairTransformData(float headWidthMinScale, float headWidthMaxScale, float headHeightMinScale, float headHeightMaxScale, float headHeightMinPosition, float headHeightMaxPosition)
    {
        this.headWidthMinScale = headWidthMinScale;
        this.headWidthMaxScale = headWidthMaxScale;
        this.headHeightMinScale = headHeightMinScale;
        this.headHeightMaxScale = headHeightMaxScale;
        this.headHeightMinPosition = headHeightMinPosition;
        this.headHeightMaxPosition = headHeightMaxPosition;
    }
    //head width
    public float headWidthMinScale;
    public float headWidthMaxScale;
    //head height
    public float headHeightMinScale;
    public float headHeightMaxScale;
    public float headHeightMinPosition;
    public float headHeightMaxPosition;
}

