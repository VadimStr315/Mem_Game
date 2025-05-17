import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import styles from './cards.module.scss'
import BottomControlsContainer from '../../components/bottomControls/bottomControls'
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-expect-error
import 'swiper/css';
import { Swiper, SwiperRef, SwiperSlide } from 'swiper/react';
import { useEffect, useRef, useState } from 'react';
import { CollectionWithCards } from '../../types/collection';
import axios, { PagesURl } from '../../services/api';
import { FullCard } from '../../types/card';
import PopupContainer from '../../components/popupContainer/popupContainer';

export default function Cards () {

  const swiper = useRef<SwiperRef>(null);
  const [allCollections, setAllCollections] = useState<CollectionWithCards[]>()
  const [allCardCollectionId, setAllCardCollectionId] = useState<number>()
  const [isOpenedMenu, setIsOpenedMenu] = useState(false)

  const [activeCollection, setActiveCollection] = useState<CollectionWithCards>()

  const [displayCollectionPopup, setDisplayCollectionPopup] = useState<string>()
  const [collectionIdToDelete, setCollectionIdToDelete] = useState<number>()

  const [cardToAdd, setCardToAdd] = useState<FullCard>()

  const [searchParams] = useSearchParams();
  const searchCollectionId = searchParams.get('cardId'); 

  const navigate = useNavigate()

  function moveAllCardsToMiddle(array: CollectionWithCards[]) {
    const allCardsIndex = array.findIndex(item => item.name === 'Все карточки');
    if (allCardsIndex === -1) {
      return array;
    }
    const [allCardsItem] = array.splice(allCardsIndex, 1);
    const middleIndex = Math.floor(array.length / 2);
    array.splice(middleIndex, 0, allCardsItem);
    return array;
  }

  const getValidValueNewCard = () => {
    if (!allCollections) {
      return `Новая коллекция`
    }
    const maxId = allCollections.reduce((max, item) => Math.max(max, item.id), 0);
    return `Новая коллекция ${maxId + 1}`
  }

  const canAddCardToCollection = (collectionId: number) => {
    if (!cardToAdd) {
      return true
    }
    return !cardToAdd.collection_ids.includes(collectionId)
  }

  const handleGetAllCollections = async (isCreatedNew?: boolean) => {
    const {data} = await axios.get<CollectionWithCards[]>(PagesURl.COLLECTION + '/all')
    const newData = moveAllCardsToMiddle(data)
    setAllCollections(newData.map((item)=>({...item, cards: item.cards.slice(0,5)})))
    setAllCardCollectionId(newData.find(item => item.name === 'Все карточки')?.id)
    if (isCreatedNew) {
      swiper.current?.swiper.slideTo(newData.length - 1)
      setActiveCollection(newData.find(item => item.name === 'Новая коллекция'))
    }
  } 
  const handleCreateCollection = async () => {
    try {
      await axios.post(PagesURl.COLLECTION + '/create_collection', {
        name: getValidValueNewCard()
      })
      handleGetAllCollections(true)
    } catch {
      alert('Такая карточка уже существует')
    }
  }
  const handleCreateCard = async (collectionId: number) => {
    const collectionIds = collectionId === allCardCollectionId ? [collectionId] : [collectionId, allCardCollectionId]
    const {data} = await axios.post<FullCard>(PagesURl.CARD + '/create', {
      collection_ids: collectionIds,
      text: 'Введите текст ситуации'
    })
    navigate(`/game?cardId=${data.id}`)
  }
  const handleGetCard = async (cardId: number) => {
    const {data} = await axios.get<FullCard>(PagesURl.CARD + `/${cardId}`)
    setCardToAdd(data)
  }
  const handleDeleteCollection = async (collectionId: number) => {
    await axios.delete(PagesURl.COLLECTION + `/${collectionId}`)
    handleGetAllCollections()
    setCollectionIdToDelete(undefined)
  }
  const handleEditCollection = async (collection: CollectionWithCards) => {
    try {
      await axios.patch(PagesURl.COLLECTION + '/update_collection', {
        id: collection.id,
        name: collection.name
      })
      setActiveCollection(undefined)
      handleGetAllCollections()
    } catch {
      alert('Коллекция с таким именем уже существует')
    }
  }

  const onAddCardToCollection = async (collectionId: number) => {
    if (!cardToAdd) {
      handleCreateCard(collectionId)
      return
    }
    if (!allCollections) return
    await axios.patch(PagesURl.CARD + `/update`, {
      id: cardToAdd.id,
      text: cardToAdd.text,
      collection_ids: [...cardToAdd.collection_ids, collectionId]
    })
    setDisplayCollectionPopup(allCollections.find(item => item.id === collectionId)?.name)
    setTimeout(() => setDisplayCollectionPopup(undefined), 3000)
    handleGetAllCollections()
    navigate('/cards')
  }

  const startGame = () => {
    if (swiper.current?.swiper.activeIndex === undefined) return
    navigate(`/game?collectionId=${allCollections?.[swiper.current?.swiper.activeIndex].id}`)
  }

  const editCollection = () => {
    if (!allCollections || !swiper.current?.swiper.activeIndex) return
    setActiveCollection(allCollections[swiper.current?.swiper.activeIndex])
  }

  useEffect(()=> {
    handleGetAllCollections()
    if (searchCollectionId) {
      handleGetCard(parseInt(searchCollectionId))
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])

  if (!allCollections) {
    return <></>
  }
 
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <img src='/logo.svg' />
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
              <Link className={styles.header__link} to={'/cards'}>Мои подборки</Link>
              <Link className={styles.header__link} to={''}>Правила игры</Link>
            </div>
            <p className={styles.menu__textBy}>created by irit-rtf</p>
          </div>
        </div>}
      </header>
      <main className={styles.main}>
        <img className={styles.main__background} src='/background/background_game.svg'/>
        <div className={styles.main__content}>
          <Swiper
            ref={swiper}
            className={styles.main__swiper}
            style={{padding:'20px'}}
            spaceBetween={'40px'}
            breakpoints={{
              1024: {
                direction: 'horizontal',
                slidesPerView: 3.5,
                centeredSlides: true
              },
              0: {
                direction: 'vertical',
                autoHeight: false,
                spaceBetween: 32,
                slidesPerView: 'auto',
              }
            }}
          >
            {allCollections.map((collection)=>(
              <SwiperSlide key={collection.id} className={styles.main__swiper__slide}>
                <div className={styles.main__slide}>
                {activeCollection?.id === collection.id ? <input onBlur={()=>handleEditCollection(activeCollection)} onChange={(e) => setActiveCollection({...collection, name: e.target.value})} className={styles.main__slide__input} autoFocus value={activeCollection.name}/> :
                  <p onClick={() => collection.name !== 'Все карточки' && setActiveCollection(collection)} className={styles.main__slide__title}>{collection.name}</p>}
                  {collection.cards.map((card, index) => (
                    <p key={card.id} style={index === collection.cards.length - 1 ? { marginBottom: '100px' } : {}} className={styles.main__slide__text}>{card.text}</p>
                  ))}
                  <div className={styles.main__slide__controls}>
                    <p className={styles.main__slide__controls__text}>{collection.amount_of_cards} карточек</p>
                    <div>
                      {canAddCardToCollection(collection.id) &&<img style={{ marginRight: '16px', cursor: 'pointer' }} onClick={()=>onAddCardToCollection(collection.id)} width={31} height={31} src='/icons/new.svg' />}
                      {allCardCollectionId !== collection.id && <img onClick={()=>setCollectionIdToDelete(collection.id)} style={{ cursor: 'pointer' }} width={28} height={31} src='/icons/delete.svg' />}
                    </div>
                  </div>
                </div>
              </SwiperSlide>
            ))}
          </Swiper>
        </div>
        <BottomControlsContainer>
          <> 
            <img width={64} height={64} onClick={handleCreateCollection} src='/icons/new.svg'/>
            <img width={100} height={100} onClick={startGame} src='/icons/start.svg'/>
            <img width={64} height={64} onClick={editCollection} src='/icons/edit.svg'/>
          </>
        </BottomControlsContainer>
      </main>
      {displayCollectionPopup !== undefined && 
        <PopupContainer>
          <div className={styles.popup}>
            <p className={styles.popup__title}>Добавлено в подборку</p>
            <p className={styles.popup__text}>{displayCollectionPopup}</p>
          </div>
        </PopupContainer>
      }
      {collectionIdToDelete !== undefined && 
        <PopupContainer>
          <div className={styles.popup}>
            <p className={styles.popup__title}>хотите удалить коллекцию?</p>
            <div className={styles.popup__buttons}>
              <button className={`${styles.popup__button} ${styles.popup__button_confirm} `} onClick={()=>handleDeleteCollection(collectionIdToDelete)}>Удалить</button>
              <button className={`${styles.popup__button}`}  onClick={()=>setCollectionIdToDelete(undefined)}>Отмена</button>
            </div>
          </div>
        </PopupContainer>
      }
    </div>
  )
}