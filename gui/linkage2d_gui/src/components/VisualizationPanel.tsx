
import React, { useEffect, useRef, useState } from 'react';
import SVGGrid from './SVGGrid';

interface LinkageData {
  links: Array<{
    id: string;
    points: Array<{ id: string; position: [number, number] }>;
  }>;
  joints: Array<any>;
}

const WIDTH = 700;
const HEIGHT = 500;

const VisualizationPanel: React.FC = () => {
  const [linkage, setLinkage] = useState<LinkageData | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    fetch('/four_bar.json')
      .then(res => res.json())
      .then(setLinkage);
  }, []);

  const handleLinkClick = (id: string) => {
    setSelected(id);
  };

  return (
    <svg
      ref={svgRef}
      width={WIDTH}
      height={HEIGHT}
      style={{ width: '100%', height: '100%', background: 'white', cursor: 'pointer' }}
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
    >
      <SVGGrid width={WIDTH} height={HEIGHT} gridSize={25} />
      {/* Render links as lines */}
      {linkage && linkage.links.map(link => (
        <g key={link.id}>
          {link.points.length >= 2 && (
            <line
              x1={link.points[0].position[0]}
              y1={link.points[0].position[1]}
              x2={link.points[1].position[0]}
              y2={link.points[1].position[1]}
              stroke={selected === link.id ? '#1976d2' : '#333'}
              strokeWidth={selected === link.id ? 5 : 3}
              onClick={e => {
                e.stopPropagation();
                handleLinkClick(link.id);
              }}
              style={{ cursor: 'pointer' }}
            />
          )}
          {/* Draw points */}
          {link.points.map((pt, idx) => (
            <circle
              key={pt.id}
              cx={pt.position[0]}
              cy={pt.position[1]}
              r={7}
              fill={selected === link.id ? '#1976d2' : '#fff'}
              stroke="#1976d2"
              strokeWidth={2}
              onClick={e => {
                e.stopPropagation();
                handleLinkClick(link.id);
              }}
              style={{ cursor: 'pointer' }}
            />
          ))}
        </g>
      ))}
    </svg>
  );
};

export default VisualizationPanel;
