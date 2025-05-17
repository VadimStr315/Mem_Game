import { JSX } from 'react'
import styles from './popupContainer.module.scss'

type PopupContainerProps = {
  children: JSX.Element
}

export default function PopupContainer({children}: PopupContainerProps) {
  return (
    <div className={styles.popupContainer}>
      {children}
    </div>
  )
}