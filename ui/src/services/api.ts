import axios from 'axios';
import { getTokenFromCookie, removeTokensFromCookies, setTokensToCookies } from './token';


const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

export const PagesURl = {
  USER: '/users',
  CARD: '/card',
  COLLECTION: '/collections',
}

const REQUEST_TIMEOUT = 10000;


const instance = axios.create({
  baseURL: BACKEND_URL,
  timeout: REQUEST_TIMEOUT
});

let isRefreshing = false;

async function refreshAccessToken() {
  try {
    isRefreshing = true
    const refreshToken = getTokenFromCookie('refresh');
    if (!refreshToken){
      window.location.pathname = '/login'
    }
    const response = await axios.post(BACKEND_URL + PagesURl.USER + '/refresh', {
      "refresh_token": refreshToken
    });
    setTokensToCookies(response.data.access_token, 'access');
    setTokensToCookies(response.data.refresh_token, 'refresh');
    isRefreshing = false
    return response.data.access_token;
  } catch {
    removeTokensFromCookies('access');
    removeTokensFromCookies('refresh');
  }
}


instance.interceptors.response.use(
  response => response,
  async error => {
    if (error.response && error.response.status === 401 && !isRefreshing) {
      try {
        const newAccessToken = await refreshAccessToken();
        const originalRequestConfig = error.config;
        originalRequestConfig.headers['Authorization'] = 'Bearer ' + newAccessToken;
        return axios(originalRequestConfig);
      } catch {
        removeTokensFromCookies('access');
        removeTokensFromCookies('refresh');
      }
    }

    if (error.message === `timeout of ${REQUEST_TIMEOUT}ms exceeded`) {
      console.log(error);
    } else {
      switch (error.response?.status) {
        case 404:
          console.log(error);
          break;
        case 403:
          //window.location.href = '/';
          break;
        case 400:
          break;
        case 401:
          window.location.href = '/login';
          break
        default:
          console.log(error);
          if (error.code === 'ECONNABORTED') {
            window.location.href = 'error';
          }
      }
    }

    return Promise.reject(error);
  }
);

instance.interceptors.request.use(
  config => {
    config.timeout = REQUEST_TIMEOUT;
    config.headers.Authorization = 'Bearer ' + getTokenFromCookie('access');
    if (config.url){
      {
        config.params = {
          ...config.params,
        }
      }
    }
    //console.log(config)
    return config;
  },
/*   error => Promise.reject(error) */
);

export default instance;