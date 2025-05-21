import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import styles from './game.module.scss'
import BottomControlsContainer from '../../components/bottomControls/bottomControls'
import { useEffect, useState } from 'react'
import { FullCard } from '../../types/card'
import axios, { PagesURl } from '../../services/api';
import PopupContainer from '../../components/popupContainer/popupContainer'
export default function Game() {

  const DEFAULT_COLLECTION_ID = parseInt(import.meta.env.VITE_DEFAULT_COLLECTION_ID ? import.meta.env.VITE_DEFAULT_COLLECTION_ID : '1')

  const navigate = useNavigate()

  const [editCard, setEditCard] = useState<FullCard>()
  const [isOpenedMenu, setIsOpenedMenu] = useState(false)
  const [activeCard, setActiveCard] = useState<FullCard | null>()
    const [cardIdToDelete, setCardIdToDelete] = useState<number>()

  const [searchParams] = useSearchParams();
  const cardId = searchParams.get('cardId');
  const collectionId = searchParams.get('collectionId'); 

  const handleGetCard = async (cardId?: number) => {
    try {
      if (cardId) {
        const { data } = await axios.get<FullCard>(PagesURl.CARD + `/${cardId}`)
        setEditCard(data)
        setActiveCard(data)
        return
      }
      const intCollectionId = collectionId ? parseInt(collectionId) : DEFAULT_COLLECTION_ID
      const { data } = await axios.get<FullCard>(PagesURl.CARD + `/random_card/${intCollectionId}`)
      setActiveCard(data)
    } catch {
      setActiveCard(null)
    }
  }

  const handleEditCard = async () => {
    if (!editCard) return
    await axios.patch(PagesURl.CARD + `/update`, {
      ...editCard
    })
    setActiveCard(editCard)
    setEditCard(undefined)
  }
  const handleCreateCard = async () => {
    const intCollectionId = collectionId ? parseInt(collectionId) : undefined
    const {data} = await axios.post<FullCard>(PagesURl.CARD + '/create', {
      collection_ids: intCollectionId ? [DEFAULT_COLLECTION_ID, intCollectionId] : [DEFAULT_COLLECTION_ID],
      text: 'Введите текст ситуации'
    })
    setEditCard(data)
    setActiveCard(data)
  }

  const reloadCard = () => {
    handleGetCard()
  }
  const deleteCard = async () => {
    if (!activeCard) return
    await axios.delete(PagesURl.CARD + `/${activeCard.id}`)
    handleGetCard()
    setCardIdToDelete(undefined)
  }

  const addToCollection = () => {
    navigate(`/cards?cardId=${activeCard?.id}`)
  }

  useEffect(() => {
    handleGetCard(cardId && parseInt(cardId) ? parseInt(cardId) : undefined)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (activeCard === undefined) {
    return <></>
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <img src='/logo.svg' onClick={()=>navigate('/')}/>
        <div className={styles.header__links}>
          <Link className={styles.header__link} to={'/cards'}>мои подборки</Link>
          <Link className={styles.header__link} to={''}>О нас</Link>
          <Link className={styles.header__link} to={''}>Правила игры</Link>
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
              <Link className={styles.header__link} to={'/cards'}>мои подборки</Link>
              <Link className={styles.header__link} to={''}>Правила игры</Link>
            </div>
            <p className={styles.menu__textBy}>created by irit-rtf</p>
          </div>
        </div>}
      </header>
      <main className={styles.main}>
        <img className={styles.main__background} src='/background/background_game.svg'/>
        <div className={styles.main__situation}>
          <h1 className={styles.main__title}>Ситуация:</h1>
          {editCard ? 
            <div className={styles.main__edit}>
              <textarea onBlur={handleEditCard} autoFocus className={styles.main__input} value={editCard.text} onChange={(e) => setEditCard({...editCard, text: e.target.value})}/>
            </div> : 
            activeCard && <p className={styles.main__text}>{activeCard.text}</p>
          }
        </div>
        <BottomControlsContainer>
          <> 
            <img className={styles.main__icon} onClick={addToCollection} src='/icons/my.svg'/>
            <img className={styles.main__icon} onClick={handleCreateCard} src='/icons/new.svg'/>
            <img className={styles.main__icon_big} width={100} height={128} onClick={reloadCard} src='/icons/reload.svg'/>
            <img className={styles.main__icon} onClick={()=>activeCard && setEditCard(activeCard)} src='/icons/edit.svg'/>
            <img className={styles.main__icon} onClick={()=>setCardIdToDelete(activeCard?.id)} src='/icons/delete.svg'/>
          </>
        </BottomControlsContainer>
      </main>
      {cardIdToDelete !== undefined && 
        <PopupContainer>
          <div className={styles.popup}>
            <p className={styles.popup__title}>хотите удалить карточку?</p>
            <div className={styles.popup__buttons}>
              <button className={`${styles.popup__button} ${styles.popup__button_confirm} `} onClick={deleteCard}>Удалить</button>
              <button className={`${styles.popup__button}`}  onClick={()=>setCardIdToDelete(undefined)}>Отмена</button>
            </div>
          </div>
        </PopupContainer>
      }
    </div>
  )
}