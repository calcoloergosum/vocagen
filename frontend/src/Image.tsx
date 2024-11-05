/*
Show different image based on aspect ratio.
*/
import React from 'react';
import { CSSProperties } from 'react';

export const AspectRatioImage = ({ srcVertical, srcHorizontal, parentRef, style }:
    { srcVertical: string, srcHorizontal: string, parentRef: React.RefObject<HTMLDivElement>, style: CSSProperties }) => {
    const [isVertical, setIsVertical] = React.useState(false);
    React.useEffect(() => {
        const parent = parentRef.current;
        if (!parent) return;
        const observer = new ResizeObserver(() => {
            setIsVertical(parent.clientHeight > parent.clientWidth);
        });
        observer.observe(parent);
        return () => observer.disconnect();
    }, [parentRef]);
    return <img style={style} src={isVertical ? srcVertical : srcHorizontal} alt="image" />;
}
