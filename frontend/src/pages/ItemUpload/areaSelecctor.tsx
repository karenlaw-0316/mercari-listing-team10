import React, { useState } from "react";
import "react-image-crop/dist/ReactCrop.css";

import ReactCrop, {
	centerCrop,
	makeAspectCrop,
	Crop,
	PixelCrop,
} from "react-image-crop";

const AreaSelector = (src: any) => {
	console.log(src);
	const [crop, setCrop] = useState<Crop>();
	return (
		<ReactCrop crop={crop} onChange={(c) => setCrop(c)}>
			<img src={src} />
		</ReactCrop>
	);
};

export default AreaSelector;
