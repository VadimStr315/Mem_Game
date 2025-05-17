import { useState, useEffect, useRef} from 'react';
import classes from './repeatingTextLine.module.scss'

type RepeatingTextLineProps = {
  text: string
  styles: string
}

const RepeatingTextLine = ({text, styles}:RepeatingTextLineProps) => {
  const [copies, setCopies] = useState<number>(1);
  const containerRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const calculateCopies = () => {
      if (containerRef.current && textRef.current) {
        const containerWidth = containerRef.current.offsetWidth;
        const textWidth = textRef.current.offsetWidth;
        const neededCopies = Math.ceil(containerWidth / textWidth) + 2;
        setCopies(neededCopies);
      }
    };

    calculateCopies();
    window.addEventListener('resize', calculateCopies);

    return () => {
      window.removeEventListener('resize', calculateCopies);
    };
  }, []);

  return (
    <div 
      ref={containerRef}
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        width: '100%',
        overflow: 'hidden',
        whiteSpace: 'nowrap',
        paddingBottom: '10px',
        zIndex: 999,
      }}
    >
      <span 
        ref={textRef}
        className={`${styles} ${classes.text}`}
      >
        {text}
      </span>
      
      {Array.from({ length: copies }).map((_, i) => (
        <span 
          key={i}
          className={`${styles} ${classes.text}`}
        >
          {text}
        </span>
      ))}
    </div>
  );
};

export default RepeatingTextLine;