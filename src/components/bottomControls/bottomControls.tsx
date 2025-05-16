import { JSX } from 'react';
import styles from './bottomControls.module.scss';

type BottomControlsContainerProps = {
  children: JSX.Element
}

export default function BottomControlsContainer({children}: BottomControlsContainerProps) {
  return (
    <div className={styles.bottomControls}>
      {children}
    </div>
  )
}