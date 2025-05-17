import { useEffect } from 'react';

const useOutsideClick = (ref: React.RefObject<HTMLElement | null>, handler: (event: MouseEvent) => void) => {
  useEffect(() => {
    if (!ref) return;
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        handler(event);
      }
    };

    document.addEventListener('click', handleClickOutside);

    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [ref, handler]);
};

export default useOutsideClick;