import React from 'react';

interface SVGGridProps {
  width: number;
  height: number;
  gridSize?: number;
}

const SVGGrid: React.FC<SVGGridProps> = ({ width, height, gridSize = 25 }) => {
  const lines = [];
  for (let x = 0; x <= width; x += gridSize) {
    lines.push(<line key={`vx${x}`} x1={x} y1={0} x2={x} y2={height} stroke="#e0e0e0" strokeWidth={1} />);
  }
  for (let y = 0; y <= height; y += gridSize) {
    lines.push(<line key={`hz${y}`} x1={0} y1={y} x2={width} y2={y} stroke="#e0e0e0" strokeWidth={1} />);
  }
  return <g>{lines}</g>;
};

export default SVGGrid;
