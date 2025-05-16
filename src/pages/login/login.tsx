import { useState } from "react"
import axios, { PagesURl } from '../../services/api';
import { LoginResponse } from "../../types/login";
import { setTokensToCookies } from "../../services/token";
import { useNavigate } from "react-router-dom";
import styles from './login.module.scss'
import RepeatingTextLine from "../../components/repeatingTextLine/repeatingTextLine";

export default function Login() {

  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')

  const [isDisplayPassword, setIsDisplayPassword] = useState(false)

  const navigate = useNavigate()

  const onLogin = async () => {
    const {data} = await axios.post<LoginResponse>(PagesURl.USER + '/token', {
      username:login, 
      password
    },
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
    })
    setTokensToCookies(data.access_token, 'access');
    setTokensToCookies(data.refresh_token, 'refresh');
    navigate('/')
  }

  return (
    <div className={styles.page}>
      <img className={styles.page__logo} src='/logo_white.svg'/>
      <div className={styles.container}>
        <img className={styles.container__background} src='/background/background_login.svg'/>
        <form onSubmit={(e)=>{e.preventDefault(); onLogin()}} className={styles.content}>
          <h1 className={styles.content__title}>Какой ты мем?</h1>
          <p className={styles.content__text}>created by irit-rtf</p>
          <p className={styles.content__label}>Логин</p>
          <div className={styles.content__inputContainer}>
            <input required className={styles.content__input} value={login} onChange={(e) => setLogin(e.target.value)}/>
          </div>
          <p className={styles.content__label}>Пароль</p>
          <div className={styles.content__inputContainer}>
            <input type={isDisplayPassword ? 'text' : 'password'} required className={styles.content__input} value={password} onChange={(e) => setPassword(e.target.value)}/>
            <svg onClick={() => setIsDisplayPassword(!isDisplayPassword)} className={styles.content__input_icon} width="28" height="20" viewBox="0 0 28 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 19.9981C11.7038 20.0273 9.43138 19.5217 7.3556 18.5198C5.74657 17.7188 4.30171 16.6126 3.0982 15.2603C1.8234 13.8621 0.819654 12.2303 0.14 10.451L0 9.99965L0.147 9.54829C0.827141 7.77061 1.82873 6.1392 3.0996 4.73903C4.30268 3.38683 5.74705 2.28064 7.3556 1.47953C9.4314 0.477672 11.7038 -0.0279323 14 0.00119035C16.2962 -0.027882 18.5686 0.47772 20.6444 1.47953C22.2535 2.28046 23.6983 3.38666 24.9018 4.73903C26.179 6.13533 27.1831 7.76766 27.86 9.54829L28 9.99965L27.853 10.451C25.6567 16.2841 20.1239 20.0972 14 19.9981ZM14 2.85789C9.23422 2.70553 4.85999 5.53619 2.9638 9.99965C4.85968 14.4634 9.23411 17.2942 14 17.1414C18.7657 17.2934 23.1397 14.4628 25.0362 9.99965C23.1425 5.53402 18.7666 2.70232 14 2.85789ZM14 14.2847C11.9803 14.2984 10.2331 12.8526 9.82935 10.8335C9.42559 8.81439 10.478 6.7859 12.3415 5.99122C14.2051 5.19654 16.3593 5.85763 17.484 7.56932C18.6086 9.28102 18.3895 11.5652 16.961 13.022C16.1788 13.8294 15.1127 14.2841 14 14.2847Z" fill="#C1C1C1" />
            </svg>
          </div>
          <button type="submit" className={styles.content__button}>Войти</button>
          <button className={styles.content__losePassword}>Забыли пароль?</button>
        </form>
      </div>
      <RepeatingTextLine text="Какой ты мем?" styles={styles.bottomText}/>
    </div>
  )
}