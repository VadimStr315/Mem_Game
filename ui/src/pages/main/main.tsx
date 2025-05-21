import { Link, useNavigate } from 'react-router-dom'
import styles from './main.module.scss'
import RepeatingTextLine from '../../components/repeatingTextLine/repeatingTextLine'
import { useState } from 'react'

function Main() {

  const navigate = useNavigate()

  const [isOpenedMenu, setIsOpenedMenu] = useState(false)

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <img src='/logo.svg' onClick={()=>navigate('/')}/>
        <div className={styles.header__links}>
          <Link className={styles.header__link} to={''}>О нас</Link>
          <Link className={styles.header__link} to={''}>Правила игры</Link>
          <button onClick={() => navigate('/game')} className={styles.header__button}>начать игру</button>
        </div>
        <div onClick={() => setIsOpenedMenu(true)} className={styles.header__burger}></div>
        {isOpenedMenu && <div className={styles.menu}>
          <div className={styles.menu__content}>
            <div className={styles.menu__first}>
              <p className={styles.menu__title}>МЕНЮ</p>
              <img onClick={() => setIsOpenedMenu(false)} style={{ cursor: 'pointer' }} src='/icons/close.svg' />
            </div>
            <div className={styles.menu__links}>
              <Link className={styles.header__link} to={''}>О нас</Link>
              <Link className={styles.header__link} to={''}>Правила игры</Link>
              <button onClick={() => navigate('/game')} className={styles.header__button}>начать игру</button>
            </div>
            <p className={styles.menu__textBy}>created by irit-rtf</p>
          </div>
        </div>}
      </header>
      <main className={styles.main}>
        <img className={styles.main__background} src='/background/background_main.svg'/>
        <img className={styles.main__background_m} src='/background/background_main_m.svg'/>
        <div className={styles.main__content}>
          <p className={styles.main__textBy}>created by irit-rtf</p>
          <h1 className={styles.main__title}>Какой ты мем?</h1>
          <p className={styles.main__text}>
            Игра от проектного практикума ИРИТ-РТФ. Добавляй свои карточки-ситуации из студенческой жизнь, создавай уникальные подборки, чтобы покачать игру на максимум!
          </p>
          <div className={styles.main__buttonContainer}>
            <button onClick={() => navigate('/game')} className={styles.main__button}>начать игру</button>
          </div>
        </div>
        <RepeatingTextLine styles={styles.main__repeatingText} text={'Какой ты мем?'}/>
      </main>
    </div>
  )
}

export default Main
